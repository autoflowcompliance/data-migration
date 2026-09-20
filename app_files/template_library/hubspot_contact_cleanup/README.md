# HubSpot Contact Cleanup

**Who it is for:** CRM agencies and HubSpot admins preparing a contact import.

**What it does**

- Splits a combined `Full Name` / `First Name` / `Last Name` into clean first and last names.
- Lower-cases every email so `JOHN@Email.com` and `john@email.com` match.
- Converts phone numbers to E.164 (`(617) 498-3000` becomes `+16174983000`).
- Standardises dates from mixed formats (`12/31/24`, `31-Dec-24`, `2024-11-05`) to ISO 8601.
- Removes exact duplicate rows.
- Flags contacts with no last name (error) and phones that did not reach E.164 (warning).

**How to use it**

1. Export your contacts from HubSpot as CSV.
2. Run the tool, choose the template, upload your file.
3. Download the clean data and the QA report.

**Column names it recognises**

`First Name`, `Last Name`, `Full Name`, `Email Address`, `E-mail`, `Phone 1`,
`Phone Number`, `Mobile`, `Company`, `Title`, `City`, `Country`, `Created Date`.
Extra columns are ignored; missing ones are left blank.
