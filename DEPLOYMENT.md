# Data Migration Tool - Deployment Guide

## 🚀 Deploy to Streamlit Cloud

### Prerequisites
1. A GitHub repository containing this code
2. A Streamlit Cloud account (free at https://streamlit.io/cloud)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Streamlit app for deployment"
git push origin main
```

### Step 2: Connect to Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your repository from the dropdown
4. Set the **main file path** to one of:
   - `streamlit_app.py` (recommended - root level)
   - `app.py` (if in root)
   - `data_migration_tool/app.py` (if in subdirectory)
5. Click "Deploy"

### Step 3: Configure Environment Variables
In the Streamlit Cloud dashboard:
1. Go to your app settings
2. Click "Secrets"
3. Add these environment variables:
```toml
BRAND_NAME = "AutoFlow"
TOOL_NAME = "Data Migration Tool"
OPERATOR_NAME = "Neo Dlamini"
CONTACT_EMAIL = "autoflowcomliance@outlook.com"
```

### Step 4: Customize Settings (Optional)
Edit `.streamlit/config.toml` to customize:
- Theme colors
- Font sizes
- Server settings
- Client behavior

---

## 🖥️ Run Locally

### Development
```bash
streamlit run app.py
```

### Admin (Local CLI)
```bash
python admin.py
```

### Admin (Streamlit Dashboard - Optional)
```bash
streamlit run admin.py
```

---

## 📋 File Structure
```
data-migration/
├── app.py                           # Main Streamlit app (public demo)
├── admin.py                         # Admin CLI (local processing)
├── streamlit_app.py                 # Cloud deployment wrapper
├── requirements.txt                 # Python dependencies
├── .streamlit/
│   └── config.toml                  # Streamlit configuration
├── data_migration_tool/             # Core package
│   ├── pipeline.py
│   ├── cleaners/
│   ├── mappers/
│   ├── validators/
│   ├── auditors/
│   ├── reporters/
│   └── configs/
└── README.md
```

---

## 🔐 Security Notes

### File Privacy
- **Streamlit Cloud**: Files are processed in memory and deleted after session ends
- **Local Admin**: Files are stored locally in the `deliveries/` directory
- **Never**: Logs are not stored in Streamlit Cloud free tier

### Best Practices
1. Use environment variables for sensitive data
2. Keep `admin.py` local (don't deploy to cloud)
3. Review the `.streamlit/config.toml` before deploying
4. Enable HTTPS (automatic on Streamlit Cloud)

---

## 🐛 Troubleshooting

### App won't deploy
- Check `requirements.txt` is in the root directory
- Ensure Python version is 3.8+
- Check for syntax errors in `app.py`

### Import errors
- Verify `data_migration_tool/` package structure
- Check all required files exist in `configs/` directory
- Ensure `__init__.py` files are present in all packages

### File upload fails
- Maximum file size: 200MB (Streamlit Cloud limitation)
- Check CSV encoding (UTF-8 preferred)
- Verify CSV format is valid

---

## 📞 Support
For questions or issues:
1. Check the app footer for contact information
2. Review error messages in Streamlit logs
3. Check the `data_migration_tool/` source code for details
