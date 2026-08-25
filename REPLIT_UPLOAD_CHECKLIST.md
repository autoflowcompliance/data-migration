# Replit Upload Checklist

## 📋 Files to Upload to Replit

### Required Files (Root Directory):
- [ ] `app.py` - Main Streamlit application
- [ ] `requirements.txt` - Python dependencies  
- [ ] `.replit` - Replit configuration file
- [ ] `REPLIT_DEPLOYMENT.md` - Deployment guide

### Required Folders:
- [ ] `.streamlit/` folder with `config.toml` inside
- [ ] `data_migration_tool/` - Complete tool directory

### data_migration_tool/ Contents:
- [ ] `__init__.py`
- [ ] `admin.py` - Admin system
- [ ] `pipeline.py` - Core processing
- [ ] `transforms.py` - Data transformations
- [ ] `auditors/` folder with all files
- [ ] `cleaners/` folder with all files
- [ ] `mappers/` folder with all files
- [ ] `reporters/` folder with all files
- [ ] `validators/` folder with all files
- [ ] `configs/` folder with CRM configs
- [ ] `templates/` folder with HTML templates
- [ ] `samples/` folder with sample data
- [ ] `tests/` folder (optional)

## 🚀 Quick Upload Steps

1. **Create new Python Replit**
2. **Upload root files** (app.py, requirements.txt, .replit)
3. **Create .streamlit folder** and upload config.toml
4. **Upload data_migration_tool folder** (drag and drop entire folder)
5. **Install dependencies**: `pip install -r requirements.txt`
6. **Click Run button**
7. **Verify app loads in web preview**

## ✅ Verification Checklist

After upload, verify:
- [ ] All files appear in Replit file explorer
- [ ] Folder structure matches exactly
- [ ] No missing files or folders
- [ ] Dependencies install without errors
- [ ] App starts when you click Run
- [ ] Web preview shows the application
- [ ] Design system renders properly
- [ ] Branding shows your name and email

## 🎯 Ready to Deploy!

Once all items are checked, your Replit deployment is ready to go!