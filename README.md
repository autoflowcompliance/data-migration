# AutoFlow Data Migration Tool

A professional data migration and CRM cleanup tool that transforms messy CRM exports into clean, import-ready files.

## 🚀 Streamlit Cloud Deployment

### Demo App (Public)
- **Main file**: `app_files/app.py`
- **Row limit**: 500 rows (demo)
- **Access**: Public URL
- **Purpose**: Lead generation and demo

### Local Admin System (Private)
- **Main file**: `app_files/admin.py`
- **Row limit**: None (full file processing)
- **Access**: Local only - never deploy publicly
- **Purpose**: Paid client processing

## 📋 Deployment Instructions

### Streamlit Cloud Demo Deployment

1. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io
   - Connect your GitHub account

2. **Create New App**
   - Click "New app"
   - Select repository: `autoflowcompliance/data-migration`
   - Branch: `main`
   - Main file path: `app.py` (root level file)
   - Click "Deploy"

3. **Configuration**
   - The app will automatically use the `requirements.txt` file
   - Environment variables are optional (defaults are built-in)
   - No additional configuration needed

### Local Admin System Setup

To run the admin system locally:

```bash
# Navigate to project directory
cd autoflow

# Install dependencies
pip install -r requirements.txt

# Run admin system
streamlit run app_files/admin.py
```

## 🔒 Security Notes

- **Never deploy admin.py to Streamlit Cloud** - it's designed for local use only
- The admin system processes sensitive client data and should remain private
- Demo app has built-in 500-row limit for public use
- Admin system has no row limits for full client file processing

## 📦 Package Structure

```
autoflow/
├── app.py                 # Public demo (500-row limit) - Streamlit Cloud entry point
├── app_files/            # Main application package
│   ├── app.py           # Source Streamlit demo code
│   ├── admin.py         # Private admin (no limits)
│   ├── auditors/        # Post-import audit functionality
│   ├── cleaners/        # Data cleaning modules
│   ├── configs/         # CRM mapping configurations
│   ├── mappers/         # Field mapping logic
│   ├── reporters/       # Report generation
│   ├── templates/       # HTML report templates
│   ├── validators/      # Data validation
│   └── samples/         # Sample data for testing
├── .streamlit/          # Streamlit configuration
└── requirements.txt     # Python dependencies
```

## 🎯 Features

### Demo App
- 500-row processing limit
- Multi-CRM support (HubSpot, Salesforce, Pipedrive)
- Quality scoring and validation
- Downloadable clean CSV and QA reports
- Professional branding (AutoFlow / Neo Dlamini)

### Admin System
- No row limits (full file processing)
- Tier-based pricing system
- ZIP delivery packages
- Order logging and tracking
- Guarantee checking
- Post-import audit functionality
- Local-only processing (data security)

## 📞 Support

- **Operator**: Neo Dlamini
- **Contact**: autoflowcomliance@outlook.com
- **Documentation**: See app_files/docs/ for detailed guides