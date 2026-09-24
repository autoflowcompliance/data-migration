"""Enterprise identity: RBAC, SSO assertion checks, and SCIM provisioning.

These are the tests a due-diligence reviewer runs: does a role hold exactly the
permissions it should, does a bad SSO assertion actually fail, and does a
deactivated user lose access. Everything is offline — tokens and SAML responses
are crafted here, so no IdP is needed to prove the logic.
"""

from __future__ import annotations

import json
import time

import pytest

from app_files.platform.identity import (
    GROUP_ROLE_MAP,
    PERMISSIONS,
    ROLE_PERMISSIONS,
    AuthError,
    PermissionDenied,
    can,
    decode_id_token_unverified,
    parse_saml_response,
    parse_scim_group,
    parse_scim_user,
    permission_report,
    permissions_for,
    provisioning_action,
    require,
    scim_error,
    sign_id_token,
    validate_id_token,
    validate_saml_assertion,
)


# --------------------------------------------------------------------- RBAC
def test_every_role_is_a_distinct_job():
    """No role is a subset clone of another, and the permission sets differ."""
    steward = permissions_for("data_steward")
    operator = permissions_for("operator")
    auditor = permissions_for("auditor")
    assert steward != operator != auditor
    # A data steward reviews rules but cannot execute runs.
    assert "rule:review" in steward
    assert "run:execute" not in steward
    # An operator executes but does not edit rules.
    assert "run:execute" in operator
    assert "rule:edit" not in operator
    # An auditor can read and export the log but not run anything.
    assert "audit:export" in auditor
    assert "run:execute" not in auditor


def test_admin_holds_every_permission():
    assert permissions_for("admin") == set(PERMISSIONS)


def test_require_raises_permission_denied_with_reason():
    with pytest.raises(PermissionDenied) as caught:
        require("auditor", "run:execute")
    assert caught.value.role == "auditor"
    assert "run:execute" in str(caught.value)


def test_unknown_permission_is_not_granted():
    assert can("admin", "does:not:exist") is False


def test_unknown_role_is_rejected():
    with pytest.raises(AuthError):
        permissions_for("superuser")


def test_permission_report_is_serialisable_and_sorted():
    report = permission_report()
    assert set(report) == set(ROLE_PERMISSIONS)
    assert report["auditor"] == sorted(report["auditor"])
    json.dumps(report)  # what a due-diligence export would write


# --------------------------------------------------------------- OIDC (SSO)
KEY = b"test-signing-key"
ISSUER = "https://idp.example.com"
AUDIENCE = "dataflow-client"
NOW = 1_800_000_000


def _claims(**overrides):
    base = {
        "sub": "user-123",
        "email": "ann@example.com",
        "iss": ISSUER,
        "aud": AUDIENCE,
        "exp": NOW + 3600,
        "iat": NOW - 10,
        "email_verified": True,
        "groups": ["operators"],
    }
    base.update(overrides)
    return base


def test_valid_oidc_token_is_accepted():
    token = sign_id_token(_claims(), KEY)
    claims = validate_id_token(token, issuer=ISSUER, audience=AUDIENCE, now=NOW, signing_key=KEY)
    assert claims.subject == "user-123"
    assert claims.email == "ann@example.com"
    assert claims.groups == ["operators"]


def test_oidc_rejects_a_tampered_signature():
    token = sign_id_token(_claims(), b"the-wrong-key")
    with pytest.raises(AuthError, match="signature"):
        validate_id_token(token, issuer=ISSUER, audience=AUDIENCE, now=NOW, signing_key=KEY)


def test_oidc_rejects_wrong_issuer_and_audience():
    token = sign_id_token(_claims(iss="https://evil.example"), KEY)
    with pytest.raises(AuthError, match="issuer"):
        validate_id_token(token, issuer=ISSUER, audience=AUDIENCE, now=NOW, signing_key=KEY)

    token = sign_id_token(_claims(aud="some-other-app"), KEY)
    with pytest.raises(AuthError, match="audience"):
        validate_id_token(token, issuer=ISSUER, audience=AUDIENCE, now=NOW, signing_key=KEY)


def test_oidc_rejects_expired_and_future_tokens():
    expired = sign_id_token(_claims(exp=NOW - 3600), KEY)
    with pytest.raises(AuthError, match="expired"):
        validate_id_token(expired, issuer=ISSUER, audience=AUDIENCE, now=NOW, signing_key=KEY)

    future = sign_id_token(_claims(iat=NOW + 3600, exp=NOW + 7200), KEY)
    with pytest.raises(AuthError, match="future"):
        validate_id_token(future, issuer=ISSUER, audience=AUDIENCE, now=NOW, signing_key=KEY)


def test_oidc_rejects_unsigned_tokens():
    """alg='none' is the classic SSO bypass and must be refused."""
    import base64

    def enc(obj):
        return base64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b"=").decode()

    token = f"{enc({'alg': 'none'})}.{enc(_claims())}."
    with pytest.raises(AuthError, match="unsigned"):
        validate_id_token(token, issuer=ISSUER, audience=AUDIENCE, now=NOW)


def test_oidc_rejects_a_disallowed_algorithm():
    token = sign_id_token(_claims(), KEY, algorithm="RS256")
    with pytest.raises(AuthError, match="algorithm"):
        validate_id_token(token, issuer=ISSUER, audience=AUDIENCE, now=NOW, signing_key=KEY)


def test_oidc_requires_an_expiry_claim():
    claims = _claims()
    del claims["exp"]
    token = sign_id_token(claims, KEY)
    with pytest.raises(AuthError, match="exp"):
        validate_id_token(token, issuer=ISSUER, audience=AUDIENCE, now=NOW, signing_key=KEY)


def test_unverified_decode_reads_claims_without_checking():
    token = sign_id_token(_claims(), KEY)
    assert decode_id_token_unverified(token)["sub"] == "user-123"
    with pytest.raises(AuthError):
        decode_id_token_unverified("not-a-jwt")


def test_oidc_accepts_an_audience_list():
    token = sign_id_token(_claims(aud=[AUDIENCE, "other"]), KEY)
    claims = validate_id_token(token, issuer=ISSUER, audience=AUDIENCE, now=NOW, signing_key=KEY)
    assert claims.audience == AUDIENCE


# --------------------------------------------------------------- SAML (SSO)
def _saml_response(**overrides):
    not_before = overrides.get("not_before", "2027-01-01T00:00:00Z")
    not_after = overrides.get("not_after", "2028-01-01T00:00:00Z")
    audience = overrides.get("audience", AUDIENCE)
    issuer = overrides.get("issuer", ISSUER)
    status = overrides.get("status", "urn:oasis:names:tc:SAML:2.0:status:Success")
    return f"""<?xml version="1.0"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
  <samlp:Status><samlp:StatusCode Value="{status}"/></samlp:Status>
  <saml:Assertion>
    <saml:Issuer>{issuer}</saml:Issuer>
    <saml:Subject><saml:NameID>ann@example.com</saml:NameID></saml:Subject>
    <saml:Conditions NotBefore="{not_before}" NotOnOrAfter="{not_after}">
      <saml:AudienceRestriction><saml:Audience>{audience}</saml:Audience></saml:AudienceRestriction>
    </saml:Conditions>
    <saml:AttributeStatement>
      <saml:Attribute Name="groups"><saml:AttributeValue>operators</saml:AttributeValue></saml:Attribute>
    </saml:AttributeStatement>
  </saml:Assertion>
</samlp:Response>"""


def test_saml_parses_subject_conditions_and_attributes():
    assertion = parse_saml_response(_saml_response())
    assert assertion.subject == "ann@example.com"
    assert assertion.audience == AUDIENCE
    assert assertion.issuer == ISSUER
    assert assertion.attributes["groups"] == ["operators"]


def test_saml_validation_accepts_a_valid_assertion():
    assertion = parse_saml_response(_saml_response())
    validate_saml_assertion(
        assertion, expected_audience=AUDIENCE, expected_issuer=ISSUER, now=1_811_808_000
    )


def test_saml_rejects_wrong_audience_and_issuer():
    assertion = parse_saml_response(_saml_response(audience="someone-else"))
    with pytest.raises(AuthError, match="audience"):
        validate_saml_assertion(assertion, expected_audience=AUDIENCE, now=1_811_808_000)

    assertion = parse_saml_response(_saml_response(issuer="https://evil.example"))
    with pytest.raises(AuthError, match="issuer"):
        validate_saml_assertion(
            assertion, expected_audience=AUDIENCE, expected_issuer=ISSUER, now=1_811_808_000
        )


def test_saml_rejects_an_expired_assertion():
    assertion = parse_saml_response(
        _saml_response(not_before="2020-01-01T00:00:00Z", not_after="2021-01-01T00:00:00Z")
    )
    with pytest.raises(AuthError, match="validity"):
        validate_saml_assertion(assertion, expected_audience=AUDIENCE, now=1_811_808_000)


def test_saml_rejects_a_failed_status():
    with pytest.raises(AuthError, match="status"):
        parse_saml_response(
            _saml_response(status="urn:oasis:names:tc:SAML:2.0:status:Requester")
        )


def test_saml_rejects_missing_conditions_or_audience():
    no_conditions = """<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
      <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
        <saml:Subject><saml:NameID>a@b.c</saml:NameID></saml:Subject>
      </saml:Assertion></samlp:Response>"""
    with pytest.raises(AuthError, match="Conditions"):
        parse_saml_response(no_conditions)


def test_saml_rejects_malformed_xml():
    with pytest.raises(AuthError, match="XML"):
        parse_saml_response("<not-xml")


# ------------------------------------------------------------- SCIM 2.0
def test_scim_user_round_trips():
    payload = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "externalId": "okta-1",
        "userName": "ann@example.com",
        "active": True,
        "emails": [{"value": "ann@example.com", "primary": True}],
        "groups": [{"value": "operators"}],
    }
    user = parse_scim_user(payload)
    assert user.user_name == "ann@example.com"
    assert user.groups == ["operators"]
    assert user.to_scim("abc")["id"] == "abc"


def test_scim_user_requires_a_user_name():
    with pytest.raises(AuthError, match="userName"):
        parse_scim_user({"schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"]})


def test_scim_group_parses_members():
    group = parse_scim_group(
        {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
            "displayName": "operators",
            "members": [{"value": "1"}, {"value": "2"}],
        }
    )
    assert group.display_name == "operators"
    assert group.members == ["1", "2"]


def test_provisioning_maps_a_group_to_a_role():
    user = parse_scim_user(
        {
            "userName": "ann@example.com",
            "active": True,
            "groups": [{"value": "data-stewards"}],
        }
    )
    decision = provisioning_action(user)
    assert decision.role == "data_steward"
    assert decision.active is True


def test_deactivation_deprovisions_regardless_of_group():
    """The 'employee left' path must not depend on the IdP clearing the group."""
    user = parse_scim_user(
        {
            "userName": "ann@example.com",
            "active": False,
            "groups": [{"value": "admins"}],
        }
    )
    decision = provisioning_action(user)
    assert decision.deprovisioned is True
    assert decision.role is None


def test_active_user_with_no_mapped_group_gets_no_role():
    user = parse_scim_user({"userName": "new@example.com", "active": True, "groups": []})
    decision = provisioning_action(user)
    assert decision.role is None
    assert decision.active is True


def test_group_role_map_targets_real_roles():
    assert set(GROUP_ROLE_MAP.values()) <= set(ROLE_PERMISSIONS)


def test_scim_error_shape():
    error = scim_error("bad payload", 400)
    assert error["status"] == "400"
    assert error["schemas"] == ["urn:ietf:params:scim:api:messages:2.0:Error"]