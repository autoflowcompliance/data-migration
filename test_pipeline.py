#!/usr/bin/env python
"""Test script to validate the pipeline works end-to-end"""
import pandas as pd
from app_files import pipeline, cleaners

# Load sample data
sample_path = 'app_files/samples/messy_contacts.csv'
source = pd.read_csv(sample_path, dtype=str, keep_default_na=False)
print(f'✓ Loaded sample file: {len(source)} rows')

# Test pipeline
try:
    result = pipeline.run_pipeline(
        source=source,
        crm='hubspot',
        cleaning_config=cleaners.CleaningConfig(
            remove_duplicates=True,
            standardize_dates=True,
            standardize_phones=True,
            fix_scientific_notation=True,
            normalize_unicode=False,
            missing_value_strategy='flag',
            default_region='US',
            date_first=False,
        ),
        project_name='Test',
        source_filename='test.csv'
    )
    summary = result.summary()
    print('✓ Pipeline executed successfully')
    print(f'  - Rows in: {summary["rows_in"]}')
    print(f'  - Rows out: {summary["rows_out"]}')
    print(f'  - Quality: {summary["quality_score"]}%')
except Exception as e:
    print(f'✗ Pipeline error: {e}')
    import traceback
    traceback.print_exc()
