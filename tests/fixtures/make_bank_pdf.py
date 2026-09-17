"""Build bank-statement PDFs in US, UK and ZA layouts for adapter testing.

These are generated at test time rather than committed as binaries so the
sample stays reviewable as data, and so the PDF adapter is exercised against
genuinely laid-out tables rather than a single hand-made file.
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# amount is signed: negative = money out.
US_ROWS = [
    ("01/03/2024", "ACME SUPPLIES INVOICE 1042", "1,500.00"),
    ("01/05/2024", "CLIENT PAYMENT SMITH", "3,200.00"),
    ("01/06/2024", "CARD PURCHASE OFFICE DEPOT", "(250.00)"),
    ("01/09/2024", "BANK FEES", "-180.00"),
    ("01/20/2024", "MYSTERY DEPOSIT UNKNOWN", "800.00"),
    ("01/22/2024", "PAYROLL RUN JAN", "4,500.00"),
    ("01/28/2024", "INSURANCE PREMIUM PAID", "(640.00)"),
]

US_HEADER = ["Date", "Description", "Amount"]

# US debit/credit split layout.
US_SPLIT_ROWS = [
    ("01/03/2024", "ACME SUPPLIES INVOICE 1042", "", "1,500.00", "1,500.00"),
    ("01/06/2024", "CARD PURCHASE OFFICE DEPOT", "250.00", "", "1,250.00"),
    ("01/09/2024", "BANK FEES", "180.00", "", "1,070.00"),
]
US_SPLIT_HEADER = ["Date", "Description", "Debit", "Credit", "Balance"]

UK_ROWS = [
    ("02/01/2024", "DD", "COUNCIL TAX", "150.00", "", "2,000.00"),
    ("03/01/2024", "BACS", "SALARY ACME LTD", "", "3,000.00", "5,000.00"),
    ("05/01/2024", "CARD", "TESCO STORES", "45.50", "", "4,954.50"),
]
UK_HEADER = ["Date", "Type", "Details", "Paid out", "Paid in", "Balance"]

ZA_ROWS = [
    ("2024/01/03", "ACME SUPPLIES INVOICE 1042", "", "1500.00", "1500.00"),
    ("2024/01/06", "CARD PURCHASE OFFICE DEPOT", "250.00", "", "1250.00"),
    ("2024/01/09", "BANK CHARGES", "180.00", "", "1070.00"),
    ("2024/01/20", "MYSTERY DEPOSIT UNKNOWN", "", "800.00", "1870.00"),
]
ZA_HEADER = ["Date", "Description", "Debit", "Credit", "Balance"]


def _table(header: list[str], rows: list[tuple[str, ...]]) -> Table:
    data = [list(header), *[list(row) for row in rows]]
    table = Table(data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    return table


def build(path: str | Path, layout: str = "us", pages: int = 1) -> Path:
    """Write a bank statement PDF in the requested layout."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("ACME BANK - STATEMENT OF ACCOUNT", styles["Title"]),
        Spacer(1, 12),
    ]

    if layout == "us":
        header, rows = US_HEADER, US_ROWS
    elif layout == "us_split":
        header, rows = US_SPLIT_HEADER, US_SPLIT_ROWS
    elif layout == "uk":
        header, rows = UK_HEADER, UK_ROWS
    elif layout == "za":
        header, rows = ZA_HEADER, ZA_ROWS
    else:
        raise ValueError(f"Unknown layout {layout!r}")

    # Split the rows across `pages` pages to exercise multi-page handling.
    chunk = max(1, -(-len(rows) // max(pages, 1)))
    chunks = [rows[i : i + chunk] for i in range(0, len(rows), chunk)]
    for index, page_rows in enumerate(chunks):
        if index:
            story.append(PageBreak())
            story.append(Paragraph("ACME BANK - STATEMENT (continued)", styles["Heading2"]))
            story.append(Spacer(1, 10))
        story.append(_table(header, page_rows))
        story.append(Spacer(1, 12))

    SimpleDocTemplate(str(path), pagesize=LETTER, title="Bank statement").build(story)
    return path


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: make_bank_pdf <output.pdf> [us|us_split|uk|za] [pages]", file=sys.stderr)
        return 2
    layout = argv[2] if len(argv) > 2 else "us"
    pages = int(argv[3]) if len(argv) > 3 else 1
    print(build(argv[1], layout, pages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))