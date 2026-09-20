# Invoice Data Extraction

**Who it is for:** small businesses and bookkeepers turning invoice PDFs into a
spreadsheet they can import into accounting software.

**What it does**

- Maps the headers your invoice export uses onto a stable invoice-line shape.
- Converts invoice dates to ISO 8601.
- Title-cases customer names and upper-cases the currency code.
- Flags lines with no invoice number (error) or no line total (warning).

Read invoice PDFs directly with the ingestion layer (the tool extracts tables
from PDFs), or export a CSV from your accounting package and clean it here.
