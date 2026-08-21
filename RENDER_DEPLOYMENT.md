# Render Deployment Guide

## 🚀 Deploy Your Gradio Demo to Render

This guide will help you deploy the professional Gradio interface to Render for stable, free hosting.

### 📋 Prerequisites
- GitHub account
- Render account (free at render.com)
- Your project files pushed to GitHub

### 🎯 Step-by-Step Deployment

#### 1. Create a Render Account
1. Go to [render.com](https://render.com)
2. Click "Sign Up" 
3. Sign up using GitHub (recommended) or email
4. Authorize Render to access your GitHub repositories

#### 2. Prepare Your GitHub Repository
1. Ensure your repository is on GitHub
2. Make sure `render.yaml` is in the root directory
3. Verify `app.py`, `demo_gradio.py`, and `requirements.txt` are present
4. Confirm `data_migration_tool/` folder is included

#### 3. Create a New Web Service on Render
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select your `data-migration` repository
5. Render will automatically detect the `render.yaml` configuration

#### 4. Configure the Service
Render will automatically use the configuration from `render.yaml`:
- **Name**: data-migration-demo
- **Runtime**: Python 3.10
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Plan**: Free tier

#### 5. Deploy Your Service
1. Click "Create Web Service"
2. Render will start the deployment process:
   - Clone your repository
   - Install dependencies from requirements.txt
   - Start the Gradio application
3. Watch the deployment logs (2-5 minutes)
4. Wait for the green "Live" status

#### 6. Access Your Live Demo
1. Once deployed, click the service URL
2. Your demo will be available at: `https://data-migration-demo.onrender.com`
3. Share this URL with prospects for lead generation

### 🔧 Configuration Details

#### render.yaml File
```yaml
services:
  - type: web
    name: data-migration-demo
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: PYTHON_VERSION
        value: "3.10"
      - key: PORT
        value: "10000"
```

#### app.py Entry Point
The `app.py` file serves as the entry point and handles:
- PORT environment variable for Render
- Graceful fallback for local development
- Gradio demo launch

### 🎨 Customization Options

#### Update Service Name
Edit `render.yaml` to change the service name:
```yaml
name: your-custom-name
```

#### Add Custom Domain
1. Go to your service settings in Render
2. Click "Domains" → "Add Domain"
3. Add your custom domain
4. Configure DNS settings as instructed

#### Environment Variables
Add custom environment variables in Render dashboard:
- BRAND_NAME (for white-labeling)
- TOOL_NAME (for custom tool names)
- Other custom settings

### 🔄 Two-Tier System Overview

| Tier | Purpose | Tool | Hosting |
|------|---------|------|---------|
| **Tier 1: Demo** | Lead generation (500 rows) | Gradio | Render (Free) |
| **Tier 2: Admin** | Client fulfillment (full files) | CLI script | Your local machine |

### 📋 Workflow for Your Business

#### For Prospects (Demo)
1. Send them the Render URL
2. They upload their CSV and test 500 rows
3. They see the quality and results
4. They contact you for full file processing

#### For Clients (Full Processing)
1. They pay via your preferred method
2. They send the full CSV via Google Drive/email
3. You run the CLI admin tool locally:
   ```bash
   python -m streamlit run data_migration_tool/admin.py
   ```
4. You process their full file (no limits)
5. You email them the ZIP package with deliverables

### 🔒 Privacy & Security

**Render Demo:**
- Files processed in memory only
- Automatic deletion after processing
- No data storage on servers
- Privacy guarantee built into UI

**CLI Admin:**
- Files processed on your local machine
- You control all data
- Complete privacy for client data
- You can delete files after delivery

### 💰 Pricing Information (Built into UI)

The Gradio interface includes pricing tiers:
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
   - Run `python -m streamlit run data_migration_tool/admin.py`
   - Process a full client file
   - Verify ZIP package generation
   - Test branding customization

### 🔄 Updates and Maintenance

**To update the demo:**
1. Make changes to your code
2. Push to GitHub
3. Render auto-deploys (via GitHub integration)
4. Or manually trigger redeploy in Render dashboard

**To update the pipeline:**
1. Make changes to `data_migration_tool/` code
2. Update both local and GitHub versions
3. Test thoroughly before deployment
4. Push changes for automatic deployment

### 📊 Monitoring

**Render Dashboard:**
- Monitor service health
- View deployment logs
- Check resource usage
- Set up alerts

**Performance:**
- Free tier includes 750 hours/month
- Automatic scaling if needed
- SSL certificates included
- Custom domains supported

### 🔧 Troubleshooting

**Deployment Fails:**
- Check deployment logs in Render dashboard
- Verify `render.yaml` syntax
- Ensure all dependencies are in requirements.txt
- Check Python version compatibility

**App Not Loading:**
- Wait for deployment to complete fully
- Check service status in Render dashboard
- Review logs for errors
- Verify PORT configuration

**File Upload Issues:**
- Check file size limits (Render free tier has limits)
- Verify Gradio file handling configuration
- Monitor memory usage in Render dashboard

### 📞 Support

- Render documentation: [render.com/docs](https://render.com/docs)
- Gradio documentation: [gradio.app](https://gradio.app)
- Your local admin tool: See `data_migration_tool/docs/admin_guide.md`

### 🎉 Success Checklist

- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Service created with render.yaml
- [ ] Deployment successful (green status)
- [ ] Demo interface loads correctly
- [ ] Sample file processes successfully
- [ ] 500-row limit working
- [ ] Downloads functional
- [ ] Admin CLI tested locally
- [ ] Business workflow established
- [ ] Privacy guarantees communicated

### 💡 Pro Tips

**Performance:**
- Free tier may have cold starts (30-60 seconds first load)
- Consider upgrading to paid tier for better performance
- Monitor resource usage in Render dashboard

**Security:**
- Keep your Render dashboard secure
- Use GitHub branches for testing
- Review logs regularly for issues
- Set up uptime monitoring

**Business:**
- Add custom domain for professional appearance
- Monitor usage with Render analytics
- Set up automatic backups for client data
- Create FAQ for common client questions

Your professional data migration service is now live on Render! 🚀