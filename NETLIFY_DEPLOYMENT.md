# Netlify Deployment Guide - Data Migration Tool

## 🚀 Complete Netlify Setup

This guide will help you deploy your data migration tool to Netlify Functions for a reliable demo.

### 📋 Prerequisites
- Netlify account (free at netlify.com)
- Git repository with your code
- Basic understanding of file upload

---

## 🎯 Step-by-Step Deployment

### 1. Prepare the File Structure

Your repository should have this structure:
```
your-repo/
├── app.py                    # Main FastAPI application
├── requirements.txt          # Python dependencies
├── netlify.toml             # Netlify configuration
├── api/                     # Netlify Functions directory
│   └── app.py              # Netlify function handler
└── data_migration_tool/     # Complete tool directory
    ├── __init__.py
    ├── admin.py
    ├── auditors/
    ├── cleaners/
    ├── configs/
    ├── mappers/
    ├── pipeline.py
    ├── reporters/
    ├── templates/
    ├── transforms.py
    ├── validators/
    └── [other tool files]
```

### 2. Upload Files to Your Repository

**Root Directory Files:**
- `app.py` - FastAPI application
- `requirements.txt` - Python dependencies
- `netlify.toml` - Netlify configuration
- `data_migration_tool/` - Complete tool directory

**Create api/ Directory:**
- Create an `api/` folder
- Copy `app.py` to `api/app.py` (this is the Netlify function handler)

### 3. Deploy to Netlify

**Option 1: Git Integration (Recommended)**
1. Push your repository to GitHub
2. Log in to Netlify
3. Click "Add new site" → "Import an existing project"
4. Select your GitHub repository
5. Netlify will auto-detect the configuration
6. Click "Deploy site"

**Option 2: Manual Drag & Drop**
1. Build your project locally
2. Drag the folder to Netlify dashboard
3. Configure build settings manually

### 4. Verify Deployment

Once deployed, test these endpoints:
- `https://your-site.netlify.app/` - API information
- `https://your-site.netlify.app/health` - Health check
- `https://your-site.netlify.app/crms` - Available CRMs
- `https://your-site.netlify.app/info` - System information

---

## 🔧 Configuration Files

### netlify.toml
```toml
[build]
  command = "pip install -r requirements.txt"

[build.environment]
  PYTHON_VERSION = "3.11"

[[redirects]]
  from = "/*"
  to = "/.netlify/functions/api/:splat"
  status = 200
  force = true

[functions]
  directory = "api"

[[functions]]
  name = "api"
  runtime = "python3.11"
```

### requirements.txt
```txt
# Core data processing
pandas>=2.0.0,<3.0.0
python-dateutil>=2.8.2

# Cleaning and validation
phonenumbers>=8.13.0
frictionless>=5.0.0,<6.0.0

# Encoding detection
chardet>=5.0.0

# Mapping configuration
PyYAML>=6.0

# Reporting
Jinja2>=3.1.2

# Web framework - FastAPI
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6

# Netlify Functions
mangum>=0.17.0
```

### api/app.py (Netlify Function Handler)
```python
"""Netlify Function handler for the AutoFlow data migration tool.

This is the entry point for Netlify Functions.
"""
from mangum import Mangum
from app import app

# ASGI to Lambda adapter
handler = Mangum(app)
```

---

## 🎨 Features Available on Netlify

**Public Demo:**
- ✅ FastAPI endpoints for data processing
- ✅ 500-row demo limit
- ✅ Your branding (Neo Dlamini, autoflowcomliance@outlook.com)
- ✅ Professional API structure
- ✅ Automatic scaling

**API Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `GET /crms` - Available CRM systems
- `GET /crm/{crm_name}` - CRM configuration
- `POST /process` - Process CSV file
- `POST /upload` - Upload and process file
- `GET /info` - System information

---

## 🔍 Troubleshooting

**Build fails:**
- Check that `requirements.txt` is in the root
- Verify Python version compatibility
- Check build logs in Netlify dashboard

**API not responding:**
- Verify the redirects in `netlify.toml`
- Check that the `api/` directory exists
- Ensure `api/app.py` has the Mangum handler

**Import errors:**
- Make sure `data_migration_tool/` folder is complete
- Verify all subdirectories are uploaded
- Check that `__init__.py` files exist

**Cold start delays:**
- Normal for serverless functions
- Should improve with subsequent requests
- Consider warming functions if needed

---

## 🚀 Advanced Configuration

**Custom Domain:**
1. In Netlify, go to "Domain settings"
2. Add your custom domain
3. Configure DNS records

**Environment Variables:**
1. In Netlify, go to "Site settings" → "Environment variables"
2. Add variables:
   - `BRAND_NAME`: Your brand name
   - `TOOL_NAME`: Your tool name
   - `OPERATOR_NAME`: Your name
   - `CONTACT_EMAIL`: Your email

---

## ✅ Deployment Checklist

- [ ] Repository has correct file structure
- [ ] `app.py` in root directory
- [ ] `requirements.txt` in root directory
- [ ] `netlify.toml` in root directory
- [ ] `api/` directory created
- [ ] `api/app.py` contains Mangum handler
- [ ] `data_migration_tool/` folder complete
- [ ] All subdirectories uploaded
- [ ] Repository pushed to GitHub
- [ ] Connected to Netlify
- [ ] Build succeeds
- [ ] API endpoints respond correctly
- [ ] Demo limit works (500 rows)
- [ ] Branding appears correctly

---

## 🎉 Success Indicators

Your deployment is successful when:
- ✅ Build completes without errors
- ✅ API responds to GET requests
- ✅ Health check returns healthy status
- ✅ CRM systems list loads
- ✅ File processing works
- ✅ Branding shows your name and email
- ✅ Demo limit enforced

---

## 📞 Support

If you encounter issues:
1. Check Netlify build logs
2. Verify file structure matches exactly
3. Ensure dependencies install successfully
4. Check API function logs
5. Test endpoints directly

Your data migration tool is now ready for Netlify deployment! 🚀