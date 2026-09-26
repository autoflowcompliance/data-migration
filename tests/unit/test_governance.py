"""Layer 13 — RBAC, the tamper-evident audit chain, and encryption at rest."""

from __future__ import annotations

import json
import os

import pytest

from app_files.governance import (
    ROLE_PERMISSIONS,
    AccessDenied,
    AuditChain,
    EncryptionError,
    Permission,
    Principal,
    Role,
    SecretStore,
    UserRegistry,
    check,
    decrypt_bytes,
    decrypt_text,
    encrypt_bytes,
    encrypt_text,
    require,
    role_for,
    verify_chain,
)
from app_files.governance.audit_chain import GENESIS, entry_hash, verify_records


class TestRoles:
    def test_every_role_is_ordered_by_privilege(self):
        assert ROLE_PERMISSIONS[Role.ADMIN] < ROLE_PERMISSIONS[Role.OWNER]
        assert ROLE_PERMISSIONS[Role.OPERATOR] < ROLE_PERMISSIONS[Role.ADMIN]
        assert ROLE_PERMISSIONS[Role.VIEWER] < ROLE_PERMISSIONS[Role.OPERATOR]

    def test_only_the_owner_may_manage_users(self):
        for role in Role:
            if role is Role.OWNER:
                assert Permission.MANAGE_USERS in ROLE_PERMISSIONS[role]
            else:
                assert Permission.MANAGE_USERS not in ROLE_PERMISSIONS[role]

    def test_a_viewer_cannot_export_data(self):
        # Export is the act that takes a copy out of the system.
        assert Permission.EXPORT_DATA not in ROLE_PERMISSIONS[Role.VIEWER]

    def test_an_operator_can_run_the_pipeline(self):
        assert Permission.RUN_PIPELINE in ROLE_PERMISSIONS[Role.OPERATOR]

    def test_a_client_can_only_read(self):
        assert ROLE_PERMISSIONS[Role.CLIENT] == frozenset(
            {Permission.READ_RESULTS, Permission.READ_REPORTS}
        )

    def test_a_role_string_is_coerced(self):
        assert role_for("admin") is Role.ADMIN

    def test_an_unknown_role_is_rejected(self):
        with pytest.raises(AccessDenied, match="Unknown role"):
            role_for("wizard")

    def test_an_unknown_permission_is_rejected(self):
        with pytest.raises(AccessDenied, match="Unknown permission"):
            Principal("x", Role.OWNER).can("launch_missiles")


class TestPrincipal:
    def test_can_answers_permission_questions(self):
        assert Principal("a", Role.ADMIN).can(Permission.MANAGE_LICENSE)
        assert not Principal("v", Role.VIEWER).can(Permission.RUN_PIPELINE)

    def test_a_scoped_principal_is_confined_to_its_client(self):
        principal = Principal("client-a", Role.CLIENT, scope="acme")
        assert principal.within_scope("acme")
        assert not principal.within_scope("other")

    def test_an_unscoped_principal_is_not_confined(self):
        assert Principal("admin", Role.ADMIN).within_scope("anything")

    def test_the_permission_set_follows_the_role(self):
        assert Principal("a", Role.OWNER).permissions == ROLE_PERMISSIONS[Role.OWNER]


class TestCheckAndRequire:
    def test_a_viewer_doing_an_admin_action_is_denied(self):
        with pytest.raises(AccessDenied, match="cannot 'manage_license'"):
            require(Principal("v", Role.VIEWER), Permission.MANAGE_LICENSE)

    def test_check_returns_false_rather_than_raising(self):
        assert check(Principal("v", Role.VIEWER), Permission.MANAGE_LICENSE) is False

    def test_an_authorised_action_passes(self):
        require(Principal("a", Role.ADMIN), Permission.MANAGE_LICENSE)

    def test_an_unauthenticated_principal_cannot_act(self):
        with pytest.raises(AccessDenied, match="not authenticated"):
            require(Principal("nobody", Role.OWNER, authenticated=False), Permission.RUN_PIPELINE)

    def test_check_rejects_an_unauthenticated_principal(self):
        assert check(Principal("n", Role.OWNER, authenticated=False), Permission.RUN_PIPELINE) is False

    def test_a_cross_scope_read_is_denied_even_when_the_role_allows_reading(self):
        principal = Principal("client-a", Role.CLIENT, scope="acme")
        assert check(principal, Permission.READ_REPORTS, client="acme") is True
        with pytest.raises(AccessDenied, match="scoped to 'acme'"):
            require(principal, Permission.READ_REPORTS, client="other")

    def test_the_cross_scope_message_names_both_clients(self):
        principal = Principal("client-a", Role.CLIENT, scope="acme")
        with pytest.raises(AccessDenied) as caught:
            require(principal, Permission.READ_RESULTS, client="other")
        assert "client-a" in str(caught.value)
        assert "other" in str(caught.value)

    def test_an_admin_reads_any_client(self):
        assert check(Principal("a", Role.ADMIN), Permission.READ_RESULTS, client="anyone")

    def test_a_permission_string_works_like_the_enum(self):
        require(Principal("a", Role.ADMIN), "manage_license")


class TestUserRegistry:
    def test_a_user_can_be_added_and_found(self):
        registry = UserRegistry()
        registry.add(Principal("sam", Role.OPERATOR))
        assert registry.get("sam").role is Role.OPERATOR

    def test_removing_a_user_reports_whether_they_existed(self):
        registry = UserRegistry()
        registry.add(Principal("sam", Role.OPERATOR))
        assert registry.remove("sam") is True
        assert registry.remove("sam") is False

    def test_the_registry_never_serialises_a_missing_user(self):
        registry = UserRegistry()
        registry.add(Principal("sam", Role.OPERATOR, scope="acme"))
        assert registry.as_dicts()[0]["scope"] == "acme"


class TestAuditChain:
    def test_an_appended_entry_chains_to_the_genesis(self, tmp_path):
        chain = AuditChain(tmp_path / "chain.jsonl")
        row = chain.append({"action": "run", "actor": "sam"})
        assert row["previous"] == GENESIS
        assert row["seq"] == 0

    def test_the_second_entry_chains_to_the_first(self, tmp_path):
        chain = AuditChain(tmp_path / "chain.jsonl")
        first = chain.append({"action": "run"})
        second = chain.append({"action": "run"})
        assert second["previous"] == first["hash"]

    def test_a_fresh_chain_verifies(self, tmp_path):
        chain = AuditChain(tmp_path / "chain.jsonl")
        for index in range(5):
            chain.append({"action": "run", "index": index})
        assert chain.verify().ok
        assert chain.verify().entries == 5

    def test_an_empty_chain_verifies(self, tmp_path):
        assert AuditChain(tmp_path / "chain.jsonl").verify().ok

    def test_the_chain_survives_a_reopen(self, tmp_path):
        path = tmp_path / "chain.jsonl"
        AuditChain(path).append({"action": "one"})
        reopened = AuditChain(path)
        reopened.append({"action": "two"})
        assert reopened.verify().ok

    def test_editing_an_entry_breaks_the_chain_at_that_entry(self, tmp_path):
        path = tmp_path / "chain.jsonl"
        chain = AuditChain(path)
        for index in range(3):
            chain.append({"action": "run", "index": index})
        lines = path.read_text().splitlines()
        record = json.loads(lines[1])
        record["payload"]["index"] = 99
        lines[1] = json.dumps(record)
        path.write_text("\n".join(lines) + "\n")
        result = verify_chain(path)
        assert not result.ok
        assert result.broken_at == 1
        assert "altered" in result.detail

    def test_dropping_an_entry_breaks_the_chain(self, tmp_path):
        path = tmp_path / "chain.jsonl"
        chain = AuditChain(path)
        for index in range(3):
            chain.append({"action": "run", "index": index})
        lines = path.read_text().splitlines()
        del lines[1]
        path.write_text("\n".join(lines) + "\n")
        result = verify_chain(path)
        assert not result.ok
        assert result.broken_at == 1

    def test_reordering_entries_breaks_the_chain(self, tmp_path):
        path = tmp_path / "chain.jsonl"
        chain = AuditChain(path)
        for index in range(3):
            chain.append({"action": "run", "index": index})
        lines = path.read_text().splitlines()
        lines[0], lines[2] = lines[2], lines[0]
        path.write_text("\n".join(lines) + "\n")
        assert not verify_chain(path).ok

    def test_a_tampered_previous_hash_is_caught(self, tmp_path):
        path = tmp_path / "chain.jsonl"
        chain = AuditChain(path)
        chain.append({"action": "one"})
        chain.append({"action": "two"})
        lines = path.read_text().splitlines()
        record = json.loads(lines[1])
        record["previous"] = GENESIS
        lines[1] = json.dumps(record)
        path.write_text("\n".join(lines) + "\n")
        result = verify_chain(path)
        assert not result.ok
        assert "does not match" in result.detail

    def test_an_entry_without_a_payload_is_reported(self):
        result = verify_records([{"hash": "x", "previous": GENESIS}])
        assert not result.ok
        assert "no payload" in result.detail

    def test_the_hash_depends_on_the_previous_hash(self):
        assert entry_hash({"a": 1}, GENESIS) != entry_hash({"a": 1}, "f" * 64)

    def test_the_hash_is_stable_across_key_order(self):
        assert entry_hash({"a": 1, "b": 2}, GENESIS) == entry_hash({"b": 2, "a": 1}, GENESIS)

    def test_the_verification_serialises(self, tmp_path):
        chain = AuditChain(tmp_path / "chain.jsonl")
        chain.append({"action": "run"})
        payload = chain.verify().as_dict()
        assert payload["ok"] is True and payload["entries"] == 1

    def test_the_verification_renders(self, tmp_path):
        assert "intact" in AuditChain(tmp_path / "chain.jsonl").verify().render()

    def test_an_export_is_verifiable_on_its_own(self, tmp_path):
        path = tmp_path / "chain.jsonl"
        chain = AuditChain(path)
        chain.append({"action": "run"})
        exported = chain.export(tmp_path / "exported.jsonl")
        assert verify_chain(exported).ok

    def test_an_audit_entry_dataclass_can_be_chained(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        from app_files.collaboration.audit_trail import AuditEntry
        from app_files.governance import append_to_chain

        entry = AuditEntry(
            timestamp="2024-01-01T00:00:00+00:00", input_name="in.csv", input_hash="a",
            config="hubspot", rows_in=10, rows_out=10, quality_score=99.0, output_hash="b",
        )
        append_to_chain(entry)
        assert verify_chain().ok
        assert verify_chain().entries == 1


class TestEncryption:
    def test_a_round_trip_recovers_the_text(self):
        key = SecretStore.generate_key()
        assert decrypt_text(encrypt_text("hello", key), key) == "hello"

    def test_a_round_trip_recovers_bytes(self):
        key = SecretStore.generate_key()
        blob = encrypt_bytes(b"\x00\x01\x02", key)
        assert decrypt_bytes(blob, key) == b"\x00\x01\x02"

    def test_the_ciphertext_does_not_contain_the_plaintext(self):
        key = SecretStore.generate_key()
        assert "secret-value" not in encrypt_text("secret-value", key)

    def test_each_encryption_uses_a_fresh_nonce(self):
        key = SecretStore.generate_key()
        assert encrypt_text("same", key) != encrypt_text("same", key)

    def test_the_wrong_key_fails_authentication(self):
        blob = encrypt_text("hello", SecretStore.generate_key())
        with pytest.raises(EncryptionError, match="authentication"):
            decrypt_text(blob, SecretStore.generate_key())

    def test_a_tampered_ciphertext_is_rejected(self):
        key = SecretStore.generate_key()
        ciphertext = encrypt_bytes(b"hello", key)
        body = bytearray(ciphertext.body)
        body[0] ^= 0xFF
        from app_files.governance import Ciphertext

        tampered = Ciphertext(ciphertext.nonce, bytes(body))
        with pytest.raises(EncryptionError):
            decrypt_bytes(tampered, key)

    def test_a_non_base64_key_is_rejected(self):
        with pytest.raises(EncryptionError, match="base64"):
            encrypt_text("x", "not base64 !!")

    def test_a_wrong_length_key_is_rejected(self):
        import base64

        short = base64.b64encode(b"tooshort").decode()
        with pytest.raises(EncryptionError, match="32 bytes"):
            encrypt_text("x", short)

    def test_a_foreign_blob_is_rejected(self):
        with pytest.raises(EncryptionError, match="Not a DataFlow ciphertext"):
            decrypt_bytes(b"PK\x03\x04 not ours", SecretStore.generate_key())

    def test_a_truncated_blob_is_rejected(self):
        import base64

        from app_files.governance.encryption import _MAGIC

        short = _MAGIC + base64.b64encode(b"short")
        with pytest.raises(EncryptionError, match="too short"):
            decrypt_bytes(short, SecretStore.generate_key())

    def test_unicode_survives_the_round_trip(self):
        key = SecretStore.generate_key()
        assert decrypt_text(encrypt_text("café — 東京", key), key) == "café — 東京"


class TestSecretStore:
    def test_a_generated_key_is_valid_base64_of_the_right_length(self):
        import base64

        assert len(base64.b64decode(SecretStore.generate_key())) == 32

    def test_an_injected_mapping_is_read(self):
        store = SecretStore({"default": SecretStore.generate_key()})
        assert store.has("default")

    def test_a_missing_key_raises(self):
        with pytest.raises(EncryptionError, match="No key named"):
            SecretStore({}).get("default")

    def test_the_env_fallback_covers_the_default_key(self, monkeypatch):
        key = SecretStore.generate_key()
        monkeypatch.setenv(SecretStore.ENV_KEY, key)
        assert SecretStore({}).get("default") == key

    def test_the_env_fallback_does_not_cover_a_named_key(self, monkeypatch):
        monkeypatch.setenv(SecretStore.ENV_KEY, SecretStore.generate_key())
        with pytest.raises(EncryptionError):
            SecretStore({}).get("other")

    def test_a_key_can_be_persisted_and_reloaded(self, tmp_path):
        path = tmp_path / "keys.json"
        store = SecretStore(path=path)
        store.set("default", SecretStore.generate_key(), persist=True)
        assert SecretStore(path=path).get("default") == store.get("default")

    def test_a_persisted_file_is_owner_only(self, tmp_path):
        path = tmp_path / "keys.json"
        SecretStore(path=path).set("default", SecretStore.generate_key(), persist=True)
        if os.name == "posix":
            assert os.stat(path).st_mode & 0o077 == 0

    def test_a_group_readable_file_is_refused(self, tmp_path):
        path = tmp_path / "keys.json"
        store = SecretStore(path=path)
        store.set("default", SecretStore.generate_key(), persist=True)
        if os.name != "posix":
            pytest.skip("permission model is POSIX-specific")
        os.chmod(path, 0o644)
        with pytest.raises(EncryptionError, match="readable by other users"):
            SecretStore(path=path)

    def test_a_malformed_key_cannot_be_stored(self, tmp_path):
        with pytest.raises(EncryptionError):
            SecretStore(path=tmp_path / "keys.json").set("default", "nonsense")

    def test_a_malformed_file_is_reported(self, tmp_path):
        path = tmp_path / "keys.json"
        path.write_text("{ not json")
        if os.name == "posix":
            os.chmod(path, 0o600)
        with pytest.raises(EncryptionError, match="not valid JSON"):
            SecretStore(path=path)

    def test_a_non_object_file_is_reported(self, tmp_path):
        path = tmp_path / "keys.json"
        path.write_text("[1, 2, 3]")
        if os.name == "posix":
            os.chmod(path, 0o600)
        with pytest.raises(EncryptionError, match="JSON object"):
            SecretStore(path=path)

    def test_serialising_hides_key_material_by_default(self):
        store = SecretStore({"default": SecretStore.generate_key()})
        assert store.as_dict()["keys"]["default"] == "(set)"

    def test_serialising_can_reveal_when_asked(self):
        key = SecretStore.generate_key()
        assert SecretStore({"default": key}).as_dict(reveal=True)["keys"]["default"] == key

    def test_the_store_defaults_under_autoflow_home(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        assert str(tmp_path) in str(SecretStore.default_path())

    def test_encrypting_a_file_round_trips(self, tmp_path):
        from app_files.governance import decrypt_file, encrypt_file

        key = SecretStore.generate_key()
        source = tmp_path / "plain.csv"
        source.write_text("a,b\n1,2\n")
        sealed = encrypt_file(source, tmp_path / "plain.enc", key)
        restored = decrypt_file(sealed, tmp_path / "restored.csv", key)
        assert restored.read_text() == source.read_text()
        assert b"1,2" not in sealed.read_bytes()
