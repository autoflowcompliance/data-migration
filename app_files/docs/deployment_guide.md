# Deployment Guide - Streamlit Cloud

This guide explains how to deploy the data migration tool to Streamlit Cloud for free, making it accessible as a web application.

## Prerequisites

- GitHub account (free)
- Streamlit Cloud account (free, sign in with GitHub)
- The data migration tool code in a GitHub repository

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign up/log in
2. Click the "+" icon in the top right and select "New repository"
3. Name it `data-migration-tool` (or your preferred name)
4. Make it **Public** (keeps it free)
5. Click "Create repository"

## Step 2: Push Code to GitHub

Open a terminal in your project folder and run:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit with full migration tool"

# Rename branch to main
git branch -M main

# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/data-migration-tool.git

# Push to GitHub
git push -u origin main
```

## Step 3: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in with GitHub"
3. Click "New app"
4. Select your repository (`data-migration-tool`)
5. For "Branch", select `main`
6. For "Main file path", type: `data_migration_tool/app.py`
7. Click "Deploy"

## Step 4: Configure Environment Variables (Optional)

1. Go to your app dashboard on share.streamlit.io
2. Click the "Settings" gear icon
3. Scroll to "Secrets"
4. Add environment variables for white-labeling:
   ```
   BRAND_NAME = "Your Agency Name"
   TOOL_NAME = "Migration Engine"
   LOGO_URL = "https://your-logo-url.png"
   ```

## Step 5: Access Your App

After 2-3 minutes of deployment, Streamlit will provide a URL like:
```
https://data-migration-tool-username.streamlit.app
```

This is your live web application that clients can access directly.

## Privacy & Security Features

The deployed app includes:

- **Privacy Guarantee**: Files are processed in memory only, not stored on servers
- **Automatic Deletion**: Files are deleted when the session ends
- **Size Limits**: 200MB upload limit to prevent server overload
- **Error Handling**: User-friendly error messages instead of technical traces

## Updating the App

To update your deployed app:

1. Make changes to your local code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
3. Streamlit Cloud will automatically redeploy within 2 minutes

## Troubleshooting

### Deployment Fails
- Check that the main file path is correct: `data_migration_tool/app.py`
- Ensure all dependencies are in `requirements.txt`
- Check the deployment logs in Streamlit Cloud for specific errors

### App Runs Locally but Not Online
- Ensure all file paths are relative (not absolute)
- Check that environment variables are set in Streamlit Cloud secrets
- Verify that all required files are committed to GitHub

### Performance Issues
- The 200MB file limit prevents memory issues
- Consider upgrading to Streamlit Cloud Pro for larger files or more resources

## Cost & Limits

**Free Tier (Streamlit Cloud Community):**
- Unlimited public apps
- 200MB file upload limit
- Community support
- Automatic redeployment on git push

**Paid Tier (Streamlit Cloud Pro):**
- Higher resource limits
- Priority support
- Custom domains
- Enhanced security features

## Next Steps

After deployment, refer to the [Professional Delivery Guide](./professional_delivery_guide.md) for:
- Setting up client file transfer systems
- Creating sales demo portfolios
- Privacy and trust building
- White-label delivery experiences
