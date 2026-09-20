# Salesforce Lead Cleanup

**Who it is for:** Salesforce partners and admins loading a lead list.

**What it does**

- Splits combined names into `FirstName` / `LastName`.
- Lower-cases and validates email, and removes duplicate leads.
- Converts phones to E.164.
- Maps your source headers onto Salesforce API field names.
- Flags leads missing a last name or an email (both are errors in Salesforce).

**How to use it**

1. Export your leads (or the list you were given) as CSV.
2. Run the tool with this template.
3. Import the clean file with Data Loader or the Import Wizard.
