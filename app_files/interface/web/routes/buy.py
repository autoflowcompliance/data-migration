"""Purchase flow: ``/buy`` (lead form) and ``/buy/confirmed`` (payment instructions).

Bank details are read from environment variables, never hardcoded — this keeps
real account numbers out of source control entirely. Set these before running:

    PAYMENT_BENEFICIARY_NAME, PAYMENT_BANK_NAME, PAYMENT_ACCOUNT_NUMBER,
    PAYMENT_BRANCH_CODE, PAYMENT_SWIFT_CODE, PAYMENT_CONFIRM_EMAIL,
    PAYMENT_REFERENCE, PAYMENT_AMOUNT_USD, FORMSPREE_URL (optional)

The defaults below are placeholders on purpose: an unconfigured deployment
shows ``[YOUR BANK]`` rather than leaking somebody's account number, and
:func:`missing_payment_details` lets a test assert that.

If ``FORMSPREE_URL`` is unset, submissions are logged to stdout instead of
posted anywhere, and the success page still shows — useful for testing before
the form backend is wired up.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from nicegui import ui

from app_files.interface.web import components as c
from app_files.interface.web import theme

FORMSPREE_URL = os.environ.get("FORMSPREE_URL", "")

# Mirrors the app-wide nav (the same list every other route declares) so the
# purchase page is not a dead end and its Buy button shows the active state.
BUY_NAV = [
    ("Home", "/"),
    ("Upload", "/upload"),
    ("Templates", "/templates"),
    ("Settings", "/settings"),
    ("Buy", "/buy"),
    ("Verify", "/verify"),
]

PAYMENT_DEFAULTS = {
    "beneficiary": "[YOUR FULL NAME]",
    "bank": "[YOUR BANK]",
    "account": "[YOUR ACCOUNT NUMBER]",
    "branch": "[YOUR BRANCH CODE]",
    "swift": "[YOUR SWIFT CODE]",
    "email": "[YOUR EMAIL]",
    # A reference set here is only a fallback: a real buyer gets one derived
    # from their email by :func:`buy_reference`.
    "reference": "DF-2026-001",
    "amount": "2,000",
}

_ENV_KEYS = {
    "beneficiary": "PAYMENT_BENEFICIARY_NAME",
    "bank": "PAYMENT_BANK_NAME",
    "account": "PAYMENT_ACCOUNT_NUMBER",
    "branch": "PAYMENT_BRANCH_CODE",
    "swift": "PAYMENT_SWIFT_CODE",
    "email": "PAYMENT_CONFIRM_EMAIL",
    "reference": "PAYMENT_REFERENCE",
    "amount": "PAYMENT_AMOUNT_USD",
}


def _payment_details(env: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ if env is None else env
    return {
        field: env.get(env_key) or PAYMENT_DEFAULTS[field]
        for field, env_key in _ENV_KEYS.items()
    }


PAYMENT = _payment_details()


def missing_payment_details(env: dict[str, str] | None = None) -> list[str]:
    """The ``PAYMENT_*`` variables a deployment has not set.

    Exposed so a test can prove the module ships no real banking details, and
    so an operator can see at a glance what is still unconfigured.
    """
    env = os.environ if env is None else env
    return [env_key for env_key in _ENV_KEYS.values() if not env.get(env_key)]


def buy_reference(email: str) -> str:
    """A stable, unique payment reference for one buyer.

    Every submission used to carry the same static reference, which made the
    incoming payments impossible to reconcile against orders. Deriving it from
    the email gives each buyer their own code, and the same code on a repeat
    visit, so a bank statement line maps to exactly one customer enquiry.
    """
    email = (email or "").strip()
    if not email:
        return PAYMENT["reference"]
    suffix = hashlib.sha256(email.lower().encode("utf-8")).hexdigest()[:6].upper()
    return f"DF-{suffix}"


def _submit_lead(name: str, email: str, company: str, cleaning: str) -> None:
    payload = {"name": name, "email": email, "company": company, "cleaning": cleaning}
    if not FORMSPREE_URL:
        print(f"[lead capture — no FORMSPREE_URL set] {json.dumps(payload)}")
        return
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            FORMSPREE_URL,
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        # Don't block the buyer's flow on a form-backend hiccup — log it and
        # let them through; better to lose the lead notification than lose
        # the sale over a network blip.
        print(f"[lead capture] Formspree post failed: {e}. Payload was: {json.dumps(payload)}")


# Card styling only. The palette, the fonts and the Quasar brand override all
# come from ``theme.inject_theme()``, so this page cannot drift from the rest
# of the app the way a second hardcoded copy of the tokens would.
_PAGE_STYLE = f"""
<style>
  .we-card {{
      background:{theme.SURFACE}; border:1px solid {theme.LINE}; border-radius:10px;
      padding:32px 36px; max-width:560px; margin:48px auto;
  }}
  .we-title {{
      font-family:{theme.SERIF}; font-weight:600; font-size:1.6rem;
      color:{theme.INK}; margin-bottom:8px;
  }}
  .we-sub {{ color:{theme.SLATE}; font-size:.95rem; margin-bottom:24px; }}
  .we-row {{
      display:flex; justify-content:space-between; padding:10px 0;
      border-bottom:1px solid {theme.LINE}; font-size:.92rem;
  }}
  .we-row b {{ color:{theme.INK}; }}
  .we-row span:last-child {{ color:{theme.SLATE}; font-family:{theme.MONO}; }}
</style>
"""


def _page_chrome(active: str) -> None:
    """Shared head injection, the app nav, and the way back for both pages.

    ``nav_bar`` is the same bar every other route renders, so the purchase
    pages are not dead ends and the Buy button highlights while the buyer is
    here. The explicit back link stays as well: a buyer who landed on
    ``/buy/confirmed`` from a payment email has no history to go back through.
    """
    theme.inject_theme()
    ui.add_head_html(_PAGE_STYLE)
    c.nav_bar(BUY_NAV, active=active)
    ui.link("← Back to DataFlow", "/").classes("no-underline").style(
        f"display:block; max-width:560px; margin:16px auto -24px; color:{theme.SLATE};"
    )


@ui.page("/buy")
def buy_page() -> None:
    _page_chrome(active="/buy")
    with ui.column().classes("we-card"):
        ui.html('<div class="we-title">Get your data cleaned</div>')
        ui.html(
            '<div class="we-sub">Tell us a bit about what you need, '
            "and we'll send an invoice.</div>"
        )

        name_input = ui.input("Name *").classes("w-full")
        email_input = ui.input("Email *").classes("w-full")
        company_input = ui.input("Company (optional)").classes("w-full")
        cleaning_input = ui.input("What are you trying to clean? (optional)").classes("w-full")
        error_label = ui.label("").style(f"color:{theme.DANGER}; font-size:.85rem;")

        def on_submit() -> None:
            name, email = name_input.value.strip(), email_input.value.strip()
            if not name or not email:
                error_label.set_text("Name and email are required.")
                return
            _submit_lead(name, email, company_input.value.strip(), cleaning_input.value.strip())
            # The name is URL-encoded: unencoded, a name containing ``&``,
            # ``#``, ``?`` or a space silently truncates itself or swallows the
            # reference that follows it.
            ui.navigate.to(
                f"/buy/confirmed?name={urllib.parse.quote(name)}"
                f"&ref={urllib.parse.quote(buy_reference(email))}"
            )

        # theme.button, not ui.button: a raw Quasar button defaults to the
        # stock blue primary, whose layered ``!important`` utilities outrank
        # inline styling.
        theme.button("Request an invoice", on_click=on_submit).classes("w-full").style(
            "margin-top:12px;"
        )


@ui.page("/buy/confirmed")
def buy_confirmed_page(name: str = "", ref: str = "") -> None:
    _page_chrome(active="/buy")
    display_name = name or "there"
    reference = ref or PAYMENT["reference"]
    with ui.column().classes("we-card"):
        ui.html(f'<div class="we-title">Thanks, {display_name}.</div>')
        ui.html(
            f'<div class="we-sub">To complete your purchase, send '
            f'${PAYMENT["amount"]} USD via SWIFT:</div>'
        )
        rows = [
            ("Beneficiary", PAYMENT["beneficiary"]),
            ("Bank", PAYMENT["bank"]),
            ("Account", PAYMENT["account"]),
            ("Branch code", PAYMENT["branch"]),
            ("SWIFT/BIC", PAYMENT["swift"]),
            ("Reference", reference),
        ]
        for label, value in rows:
            ui.html(f'<div class="we-row"><b>{label}</b><span>{value}</span></div>')

        ui.html(
            '<div class="we-sub" style="margin-top:20px;">'
            f'Then email your proof of payment to <b>{PAYMENT["email"]}</b>.<br><br>'
            "Your license file and download link arrive within 24 hours.</div>"
        )
