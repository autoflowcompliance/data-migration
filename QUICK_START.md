# 🚀 Quick Start - Streamlit Cloud Deployment

## 📋 **Setup Steps (5 minutes)**

### **1. Go to Streamlit Cloud**
- Visit: [share.streamlit.io](https://share.streamlit.io)
- Sign up with GitHub

### **2. Connect Your Repository**
- Click "New app"
- Click "Connect with GitHub"
- Select: `autoflowcompliance/data-migration`
- Branch: `main`
- Main file path: `app.py`

### **3. Deploy**
- Click "Deploy"
- Wait 2-3 minutes
- Your app will be live!

### **4. Access Your Demo**
- Your URL will be: `https://your-app-name.streamlit.app`
- Test with a sample CSV file

## 🎯 **Your Two-Tier System**

| Tier | Purpose | Tool | Hosting |
|------|---------|------|---------|
| **Demo** | Lead generation (500 rows) | Streamlit | Streamlit Cloud |
| **Admin** | Client fulfillment (full files) | CLI admin | Your local machine |

## 🔧 **Admin System (Local)**

**For client work, run locally:**
```bash
cd data_migration_tool
streamlit run admin.py
```

**This gives you:**
- No file size limits
- Full client file processing
- ZIP package generation
- Complete privacy (local processing)

## 📁 **Your Repository Structure**

```
data-migration/
├── app.py                    # Main demo for Streamlit Cloud
├── requirements.txt          # Dependencies
├── data_migration_tool/
│   ├── admin.py             # Private admin system
│   ├── pipeline.py          # Core processing engine
│   ├── configs/             # CRM configurations
│   └── .streamlit/
│       └── config.toml      # Streamlit settings
└── STREAMLIT_CLOUD_DEPLOYMENT.md  # Full guide
```

## ✅ **Ready to Deploy!**

Your repository is ready for Streamlit Cloud. The professional design system with the pipeline rail visualization will be live once deployed.

**Your Streamlit Cloud URL will be:** `https://data-migration-tool.streamlit.app` (or similar)