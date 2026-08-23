# Quick Start - Streamlit Cloud Deployment

## 5-Minute Setup Guide

This guide will get your data migration tool deployed to Streamlit Cloud in minutes.

### 🚀 Deployment Steps

1. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign up with your GitHub account

2. **Create New App**
   - Click "New app" button
   - Authorize GitHub access if needed

3. **Configure Your App**
   - Repository: `autoflowcompliance/data-migration`
   - Branch: `main`
   - Main file path: `app.py`

4. **Deploy**
   - Click "Deploy" button
   - Wait for installation (typically 1-2 minutes)

5. **Access Your App**
   - Your app will be available at: `https://your-app-name.streamlit.app`

### 📋 Repository Structure

```
data-migration/
├── app.py                          # Main Streamlit app (for Streamlit Cloud)
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── data_migration_tool/
│   ├── admin.py                    # Admin system (local use only)
│   ├── requirements.txt            # Tool-specific dependencies
│   ├── .streamlit/
│   │   └── config.toml            # Admin-specific config
│   └── [other tool files]
└── [documentation files]
```

### 🎯 Two-Tier System

**Public Demo (Streamlit Cloud):**
- **Location**: `app.py` (repository root)
- **Purpose**: Public-facing demo with 500-row limit
- **Deployment**: Streamlit Cloud
- **Access**: Anyone can use the demo version

**Admin System (Local):**
- **Location**: `data_migration_tool/admin.py`
- **Purpose**: Paid client processing (no row limits)
- **Deployment**: Local machine only
- **Access**: Your private client fulfillment system

### 🔧 Local Admin System

To run the admin system for client work:

```bash
cd data_migration_tool
streamlit run admin.py
```

This gives you:
- Tier-based pricing (Starter $600, Standard $1500, Premium $2000)
- Full file processing (no row limits)
- Order logging and client tracking
- Delivery guarantee checking
- Professional ZIP package generation

### 🎨 Features

**Public Demo:**
- Professional design system with pipeline rail visualization
- 500-row processing limit
- Privacy guarantees
- Brand customization options
- Contact information for upgrades

**Admin System:**
- Tier-based pricing system
- Order logging and job tracking
- Delivery guarantee checking
- Post-import audit functionality
- Local file archiving

### 📞 Support

For detailed deployment instructions, see `STREAMLIT_CLOUD_DEPLOYMENT.md`

Your professional data migration service is ready for Streamlit Cloud deployment!