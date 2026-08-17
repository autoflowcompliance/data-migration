# Creating Custom CRM Mapping Configurations

This guide explains how to create a custom mapping configuration for a CRM that isn't included in the default set (HubSpot, Salesforce, Pipedrive).

## Quick Start

1. Copy the template file: `configs/mapping_template.yaml`
2. Rename it to your CRM name (e.g., `zoho.yaml`)
3. Edit the file to match your CRM's field structure
4. Place it in the `configs/` directory
5. The tool will automatically detect and use your new configuration

## Configuration Structure

Each CRM configuration is a YAML file with the following structure:

```yaml
crm: Your CRM Name
version: "1.0"
fields:
  - name: target_field_name
    required: true
    unique: true
    transform: email_lowercase
    aliases: ["Source Column Name", "Alternative Name", "Another Name"]
```

## Field Properties

### `name` (required)
The exact field name in the target CRM's import format.

### `required` (optional, default: false)
Set to `true` if this field must have a value for every record.

### `unique` (optional, default: false)
Set to `true` if values in this field must be unique across all records.

### `transform` (optional)
Apply a transformation to the data. Available transforms:
- `phone_e164`: Convert phone numbers to E.164 format (+15551234567)
- `email_lowercase`: Convert email addresses to lowercase
- `date_iso`: Convert dates to ISO format (YYYY-MM-DD)
- `trim`: Remove leading/trailing whitespace
- `title_case`: Convert to title case
- `upper_case`: Convert to uppercase
- `lower_case`: Convert to lowercase
- `digits_only`: Keep only digits
- `ascii`: Convert accented characters to ASCII
- `expand_scientific_notation`: Expand Excel scientific notation

### `aliases` (optional)
List of possible source column names. The tool will automatically match your source columns to target fields using these aliases.

### `source` (optional)
Explicitly specify which source column to use. This overrides automatic matching.

### `sources` (optional)
Combine multiple source columns into one target field:
```yaml
- name: full_name
  sources: ["First Name", "Last Name"]
  separator: " "
```

### `separator` (optional, default: " ")
Character used to join multiple source columns.

### `default` (optional)
Default value to use if no source column is found or the value is missing.

## Example: Zoho CRM Configuration

```yaml
crm: Zoho
version: "1.0"
fields:
  - name: First Name
    required: true
    aliases: ["First Name", "Given Name", "fname"]
  
  - name: Last Name
    required: true
    aliases: ["Last Name", "Surname", "Family Name", "lname"]
  
  - name: Email
    required: true
    unique: true
    transform: email_lowercase
    aliases: ["Email Address", "E-mail", "Primary Email", "Work Email"]
  
  - name: Phone
    transform: phone_e164
    aliases: ["Phone 1", "Phone Number", "Work Phone", "Telephone"]
  
  - name: Mobile
    transform: phone_e164
    aliases: ["Mobile Phone", "Cell", "Cell Phone"]
  
  - name: Account Name
    aliases: ["Company", "Company Name", "Organization", "Employer"]
  
  - name: Title
    aliases: ["Job Title", "Position", "Role"]
  
  - name: Mailing Street
    aliases: ["Street", "Address", "Address 1", "Street Address"]
  
  - name: Mailing City
    aliases: ["City", "Town"]
  
  - name: Mailing State
    aliases: ["State", "Province", "County", "Region"]
  
  - name: Mailing Zip
    aliases: ["Zip", "Zip Code", "Postcode", "Postal Code"]
  
  - name: Mailing Country
    aliases: ["Country", "Nation"]
  
  - name: Lead Source
    aliases: ["Source", "Lead Source", "Origin"]
  
  - name: Description
    aliases: ["Notes", "Comments", "Details"]
```

## How Field Matching Works

The tool uses a two-step matching process:

1. **Exact match**: First, it looks for an exact match (case-insensitive) between your source column names and the target field's aliases.

2. **Fuzzy match**: If no exact match is found, it uses a similarity algorithm to find the closest match.

If no match is found above the threshold (0.82), the field will be marked as "missing" in the mapping log.

## Testing Your Configuration

1. Create a sample CSV with data that matches your source system
2. Run the tool with your new configuration:
   ```bash
   python -m data_migration_tool.cli -i your_sample.csv -c your_crm_name
   ```
3. Check the `mapping_log.csv` to see how fields were matched
4. Review the `qa_report.html` to identify any issues

## Common Issues

### Field not matching
- Check that your aliases include all possible variations of the source column name
- Verify spelling and spacing (the tool is case-insensitive but requires exact spelling)
- Look at the mapping log to see what confidence score was achieved

### Transform not working
- Ensure the transform name is exactly as specified in the available transforms list
- Check that the data type is appropriate for the transform (e.g., phone_e164 requires phone-like data)

### Required fields causing errors
- If a required field is consistently missing, consider making it optional or adding a default value
- Check your source data to ensure the required information is available

## Advanced Features

### Combining Multiple Fields
Use the `sources` property to combine multiple source columns:
```yaml
- name: Full Name
  sources: ["First Name", "Last Name"]
  separator: " "
```

### Conditional Defaults
Set default values for optional fields:
```yaml
- name: Lead Status
  default: "New"
  aliases: ["Status", "Lead Status", "Stage"]
```

### Custom Validation
The tool automatically validates:
- Required fields (completeness)
- Unique fields (uniqueness)
- Email format (validity)
- Phone format (validity)
- Date format (consistency)

## Getting Help

If you need help creating a custom configuration or encounter issues:

1. Check the existing configurations in `configs/` for examples
2. Review the mapping log to understand how fields are being matched
3. Test with a small sample file before processing large datasets
4. Consult the main README.md for general tool usage

## Professional Services

If you need assistance creating complex custom configurations or have unique requirements, professional configuration services are available. Contact for details on custom CRM mapping development.
