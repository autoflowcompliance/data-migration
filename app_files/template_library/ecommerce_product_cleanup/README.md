# E-commerce Product Cleanup

**Who it is for:** e-commerce sellers preparing a catalogue upload (Shopify,
WooCommerce, Amazon, eBay).

**What it does**

- Upper-cases SKUs so `abc-1` and `ABC-1` are one product.
- Title-cases category and brand, and strips stray whitespace from names.
- Strips formatting from barcodes (`4.05E+14` style scientific notation is
  expanded first, then digits-only applied).
- Removes duplicate product rows.
- Flags missing SKUs (error), very short SKUs (warning) and missing prices.

**How to use it**

Export your catalogue as CSV, run it through this template, then upload the
clean file to your store.
