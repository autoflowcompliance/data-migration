# Streamlit Cloud deployment configuration
# Save this as streamlit_app.py at the root to deploy as the main file

"""Data Migration Tool - Streamlit App Wrapper for Cloud Deployment"""
import subprocess
import sys
from pathlib import Path

# Redirect to the actual app in data_migration_tool
if __name__ == "__main__":
    app_path = Path(__file__).parent / "data_migration_tool" / "app.py"
    sys.argv[0] = str(app_path)
    exec(open(app_path).read())
