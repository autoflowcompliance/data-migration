# Hugging Face Space Setup - Web Interface Guide

## 🚀 Step-by-Step Web Interface Setup

### Step 1: Create Your Hugging Face Account (if needed)
1. Go to [huggingface.co](https://huggingface.co)
2. Click "Sign Up" if you don't have an account
3. Sign up using email, Google, or GitHub
4. Verify your email if required

### Step 2: Create a New Space
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in the Space details:
   - **Space Name**: `data-migration-tool` (or your preferred name)
   - **License**: MIT (recommended for open-source projects)
   - **SDK**: Gradio (important - select this!)
   - **Visibility**: Public (for demo) or Private
   - **Space Hardware**: CPU basic (free tier is sufficient)
3. Click "Create Space"

### Step 3: Upload Your Files
Once your Space is created, you'll see a "Files" tab. Upload these files from your `huggingface_demo/` folder:

**Required Files:**
1. `app.py` - Hugging Face entry point
2. `demo_gradio.py` - Main Gradio interface
3. `requirements.txt` - Python dependencies
4. `data_migration_tool/` - Entire folder (upload as a folder)

**Optional Files:**
- `README.md` - Documentation for your Space

**How to Upload:**
1. Click the "Files" tab in your Space
2. Click "Upload files" button
3. Select the individual files (app.py, demo_gradio.py, requirements.txt)
4. For the `data_migration_tool/` folder:
   - Click "Upload files"
   - Select the entire `data_migration_tool` folder
   - Or upload files one by one maintaining the folder structure

### Step 4: Watch the Build Process
1. Go to the "Logs" tab in your Space
2. You'll see the build process:
   - Installing dependencies from requirements.txt
   - Setting up the Gradio environment
   - Building your Space
3. Wait for the green checkmark (usually 2-5 minutes)

### Step 5: Access Your Live Demo
1. Once the build is complete, go to the main Space page
2. Your demo will be live at the URL shown
3. Format: `https://huggingface.co/spaces/your-username/data-migration-tool`

### Step 6: Test Your Demo
1. Upload a sample CSV file
2. Select a target CRM (HubSpot, Salesforce, Pipedrive)
3. Click "Process Data Migration"
4. Verify:
   - Processing works correctly
   - 500-row limit is enforced
   - Downloads work
   - UI looks professional

## 🎨 Customization Options

### Change Space Theme
1. Go to your Space's "Settings" tab
2. Under "Theme", click "Customize"
3. Choose colors that match your brand
4. Save changes

### Update Space Information
1. Go to "Settings" → "General"
2. Update the Space description
3. Add tags (gradio, data-cleaning, crm, migration)
4. Add a card image if desired

## 📋 Your Deployment Checklist

**Before Upload:**
- [ ] All files in `huggingface_demo/` are ready
- [ ] `requirements.txt` includes all dependencies
- [ ] `app.py` and `demo_gradio.py` are in the same folder
- [ ] `data_migration_tool/` folder is complete

**After Upload:**
- [ ] Space created successfully
- [ ] All files uploaded without errors
- [ ] Build process completes (green checkmark)
- [ ] Demo interface loads correctly
- [ ] Sample file processes successfully
- [ ] 500-row limit working
- [ ] Downloads functional
- [ ] UI looks professional

## 🔧 Troubleshooting

**Build Fails:**
- Check the "Logs" tab for error messages
- Ensure all dependencies are in requirements.txt
- Verify file structure is correct

**Files Not Uploading:**
- Try uploading files one at a time
- Check file sizes (there may be limits)
- Ensure folder structure is maintained

**Demo Not Loading:**
- Wait for build to complete fully
- Refresh the page
- Check browser console for errors

## 🎉 Success!

Once your Space is live, you can:
- Share the URL with prospects for lead generation
- Embed it in your website
- Monitor usage through Hugging Face analytics
- Update easily by uploading new files

Your professional data migration demo is now hosted on stable, free infrastructure! 🚀