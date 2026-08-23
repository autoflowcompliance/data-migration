# Streamlit Cloud Deployment Guide

## 🚀 Deploy Your Professional Data Migration Tool to Streamlit Cloud

Streamlit Cloud is the most reliable option for your Streamlit application.

### 📋 Prerequisites
- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)
- Your repository with app.py and requirements.txt

### 🎯 Step-by-Step Deployment

#### 1. Sign Up for Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign up"
3. Sign up with GitHub (recommended)
4. Authorize Streamlit to access your repositories

#### 2. Connect Your GitHub Repository
1. In Streamlit Cloud, click "New app"
2. Click "Connect with GitHub"
3. Select your repository: `autoflowcompliance/data-migration`
4. Select the branch: `main`
5. Click "Connect"

#### 3. Configure Your App
**Repository Details:**
- **Repository**: `autoflowcompliance/data-migration`
- **Branch**: `main`
- **Main file path**: `app.py`

**App Details:**
- **App name**: `data-migration-tool` (or your preferred name)
- **App URL**: Will be auto-generated

#### 4. Deploy Your App
1. Click "Deploy"
2. Streamlit Cloud will automatically:
   - Clone your repository
   - Install dependencies from requirements.txt
   - Launch your Streamlit app
3. Wait 2-3 minutes for deployment
4. Your app will be live at the provided URL

### 🔧 Configuration Files

**requirements.txt** (already created):
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

# User interface - Streamlit
streamlit>=1.40.0,<2.0.0
```

**.streamlit/config.toml** (for customization):
```toml
[theme]
primaryColor = "#1F9E8B"
backgroundColor = "#F7F6F3"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#14181F"
font = "sans serif"
```

### 🎨 Your Professional Design Features

**Current Design System:**
- Custom color palette (ink, paper, slate, teal)
- Professional typography (IBM Plex Mono + Inter)
- Pipeline rail visualization
- Professional header with branding
- Enhanced sidebar with dark theme
- Better buttons and metrics
- Responsive design

**Business Features:**
- 500-row demo limit
- Privacy guarantee
- Brand customization
- Contact information
- Professional footer

### 🔄 Your Two-Tier System

| Tier | Purpose | Tool | Hosting |
|------|---------|------|---------|
| **Demo** | Lead generation (500 rows) | Streamlit | Streamlit Cloud |
| **Admin** | Client fulfillment (full files) | CLI admin | Your local machine |

### 📋 Workflow for Your Business

**For Prospects (Demo):**
1. Send them the Streamlit Cloud URL
2. They test 500 rows for free
3. They see quality results
4. They contact you for full processing

**For Clients (Full Processing):**
1. They pay via your preferred method
2. Send full CSV via Google Drive
3. You run admin locally: `cd data_migration_tool && streamlit run admin.py`
4. Process unlimited files
5. Email them ZIP package

### 🔒 Privacy & Security

**Streamlit Cloud Demo:**
- Files processed in memory only
- Automatic deletion after processing
- No data storage on servers
- Privacy guarantee built into UI

**CLI Admin:**
- Files processed on your local machine
- You control all data
- Complete privacy for client data

### 💰 Pricing Information (Built into UI)

The Streamlit interface includes pricing tiers:
- **Starter ($600)** - Up to 10,000 records
- **Standard ($1,500)** - Up to 50,000 records  
- **Premium ($2,000)** - Unlimited records + priority support

### 🧪 Testing Your Deployment

1. **Test the demo interface:**
   - Upload a sample CSV
   - Verify processing works
   - Check 500-row limit is enforced
   - Test download functionality

2. **Test the admin system:**
   - Run `cd data_migration_tool && streamlit run admin.py`
   - Process a full client file
   - Verify ZIP package generation
   - Test branding customization

### 🔄 Updates and Maintenance

**To update the demo:**
1. Make changes to your code
2. Push to GitHub
3. Streamlit Cloud auto-deploys (via GitHub integration)
4. Or manually trigger redeploy in Streamlit Cloud dashboard

**To update the pipeline:**
1. Make changes to `data_migration_tool/` code
2. Update both local and GitHub versions
3. Test thoroughly before deployment
4. Push changes for automatic deployment

### 📊 Monitoring

**Streamlit Cloud Dashboard:**
- Monitor app health
- View deployment logs
- Check resource usage
- Set up alerts

**Performance:**
- Free tier available
- Automatic scaling if needed
- SSL certificates included
- Custom domains supported

### 🔧 Troubleshooting

**Deployment Fails:**
- Check deployment logs in Streamlit Cloud dashboard
- Verify requirements.txt has all dependencies
- Check that app.py is in the repository root
- Ensure all imports work correctly

**App Not Loading:**
- Wait for deployment to complete fully
- Check app status in Streamlit Cloud dashboard
- Review logs for errors
- Verify Streamlit version compatibility

**File Upload Issues:**
- Check file size limits (Streamlit Cloud has limits)
- Verify Streamlit file handling configuration
- Monitor memory usage in Streamlit Cloud dashboard

### 📞 Support

- Streamlit Cloud documentation: [docs.streamlit.io](https://docs.streamlit.io)
- Streamlit community: [discuss.streamlit.io](https://discuss.streamlit.io)
- Your local admin tool: See `data_migration_tool/docs/admin_guide.md`

### 🎉 Success Checklist

- [ ] Streamlit Cloud account created
- [ ] GitHub repository connected
- [ ] App deployed successfully
- [ ] Demo loads at URL
- [ ] Sample file processes successfully
- [ ] 500-row limit working
- [ ] Downloads functional
- [ ] Admin CLI tested locally
- [ ] Business workflow established
- [ ] Privacy guarantees communicated

### 💡 Pro Tips

**Performance:**
- Free tier may have some limitations
- Consider upgrading for better performance
- Monitor resource usage in Streamlit Cloud dashboard

**Security:**
- Keep your Streamlit Cloud dashboard secure
- Use GitHub branches for testing
- Review logs regularly for issues
- Set up uptime monitoring

**Business:**
- Add custom domain for professional appearance
- Monitor usage with Streamlit Cloud analytics
- Set up automatic backups for client data
- Create FAQ for common client questions

Your professional data migration service is now live on Streamlit Cloud! 🚀