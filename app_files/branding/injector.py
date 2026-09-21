"""Re-skin a rendered report with the agency's branding.

The core reporter is frozen and its Jinja template is rendered without any
branding variables supplied, so the ``{{BRAND_*}}`` placeholders survive into
the finished HTML as literal text. This module replaces them after the fact,
exactly like ``profiling/report.py`` injects the scorecard. The post-processing
is what keeps the frozen core untouched.
"""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path

from app_files.branding.settings import Branding

_MIME_BY_SUFFIX = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}


def logo_data_uri(logo_path: str | Path | None) -> str:
    """Inline a logo as a data URI, or return an empty string.

    Inlining rather than linking means the report stays a single portable file
    with no broken-image icon when it is emailed or opened offline.
    """
    if not logo_path:
        return ""
    path = Path(logo_path).expanduser()
    if not path.is_file():
        return ""
    mime = _MIME_BY_SUFFIX.get(path.suffix.lower(), "image/png")
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return ""
    return f"data:{mime};base64,{encoded}"


def build_masthead(branding: Branding) -> str:
    """A branded header block: logo, company name and contact details."""
    uri = logo_data_uri(branding.logo_path)
    logo_html = (
        f'<img src="{uri}" alt="{escape(branding.company_name)}" '
        'style="max-height:44px;max-width:200px;display:block;">'
        if uri
        else ""
    )
    contact = " &middot; ".join(
        part
        for part in (
            escape(branding.contact_email) if branding.contact_email else "",
            escape(branding.website) if branding.website else "",
        )
        if part
    )
    contact_html = (
        f'<div style="color:#6b7280;font-size:12px;margin-top:6px;">{contact}</div>'
        if contact
        else ""
    )
    return (
        '<div style="display:flex;align-items:center;gap:14px;'
        "padding-bottom:16px;margin-bottom:18px;"
        f'border-bottom:3px solid {escape(branding.accent_color)};">'
        f"{logo_html}"
        f'<div style="font-size:20px;font-weight:700;">{escape(branding.company_name)}</div>'
        f"</div>{contact_html}"
    )


def build_powered_by(branding: Branding) -> str:
    if not branding.show_powered_by:
        return ""
    return (
        '<footer style="color:#6b7280;font-size:12px;margin-top:36px;'
        'padding-top:12px;border-top:1px solid #e5e7eb;">Powered by DataFlow</footer>'
    )


def inject_branding(html: str, branding: Branding | dict | None = None) -> str:
    """Apply branding to a rendered report.

    Two paths, because the core reporter is frozen and its template does not
    carry ``{{BRAND_*}}`` placeholders. If a report *does* contain them (a
    custom template, or one from a future reporter), they are substituted. If
    it does not — which is every report the shipped reporter produces — the
    branding is instead injected structurally: a masthead above the report
    title, an accent rule, and a footer.

    Without the structural fallback, white-label would silently do nothing on
    the only reports the product actually generates.
    """
    if branding is None:
        from app_files.branding.settings import load_branding

        branding = load_branding()
    if isinstance(branding, dict):
        branding = Branding.from_dict(branding)

    if any(marker in html for marker in _PLACEHOLDERS):
        return _replace_placeholders(html, branding)
    return _inject_structurally(html, branding)


_PLACEHOLDERS = (
    "{{BRAND_LOGO}}",
    "{{BRAND_NAME}}",
    "{{BRAND_EMAIL}}",
    "{{BRAND_WEBSITE}}",
    "{{BRAND_ACCENT}}",
    "{{POWERED_BY}}",
)


def _replace_placeholders(html: str, branding: Branding) -> str:
    """Substitute the ``{{BRAND_*}}`` markers in a template that opts in."""
    uri = logo_data_uri(branding.logo_path)
    logo_html = (
        f'<img src="{uri}" alt="{escape(branding.company_name)}" '
        'style="max-height:48px;max-width:220px;">'
        if uri
        else ""
    )
    replacements = {
        "{{BRAND_LOGO}}": logo_html,
        "{{BRAND_NAME}}": escape(branding.company_name),
        "{{BRAND_EMAIL}}": escape(branding.contact_email or ""),
        "{{BRAND_WEBSITE}}": escape(branding.website or ""),
        "{{BRAND_ACCENT}}": escape(branding.accent_color),
        "{{POWERED_BY}}": build_powered_by(branding),
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    return html


def _inject_structurally(html: str, branding: Branding) -> str:
    """Rebrand the shipped reporter's output, which has no placeholders."""
    masthead = build_masthead(branding)
    style = (
        "<style>"
        f".sheet h1 {{ color: {escape(branding.accent_color)}; }}"
        f".sheet {{ border-top: 4px solid {escape(branding.accent_color)}; }}"
        "</style>"
    )

    if "<h1" in html:
        index = html.index("<h1")
        html = html[:index] + masthead + html[index:]
    elif "<body" in html:
        index = html.index(">", html.index("<body")) + 1
        html = html[:index] + masthead + html[index:]
    else:
        html = masthead + html

    if "</head>" in html:
        html = html.replace("</head>", f"{style}</head>", 1)

    footer = build_powered_by(branding)
    if footer:
        if "</body>" in html:
            html = html.replace("</body>", f"{footer}</body>", 1)
        else:
            html += footer
    return html


def inject_branding_into_bytes(data: bytes, branding: Branding | dict | None = None) -> bytes:
    """``inject_branding`` for a UTF-8 HTML payload."""
    return inject_branding(data.decode("utf-8"), branding).encode("utf-8")


_WATERMARK_BADGE = (
    '<div style="position:fixed;top:16px;right:16px;z-index:9999;'
    "background:#F3E3D0;color:#8A5420;border:1px solid #C97A2E;"
    "border-radius:9999px;padding:6px 14px;font:600 12px/1.4 Inter,sans-serif;"
    'letter-spacing:.02em;">DEMO — unlicensed output</div>'
)


def inject_demo_watermark(html: str, note: str = "") -> str:
    """Stamp a demo badge onto a report, plus any row-trim note.

    The badge marks the output as unlicensed. The optional note explains a row
    trim in the rare mode that caps rows — the demo no longer does, so an
    ordinary run is stamped with the badge alone.
    """
    badge = _WATERMARK_BADGE
    if note:
        badge = badge.replace(
            "DEMO — unlicensed output", f"DEMO &middot; {escape(note)}"
        )
    if "</body>" in html:
        return html.replace("</body>", f"{badge}</body>", 1)
    return html + badge