# REPLIT AI DEPLOYMENT PROMPT

Copy and paste this entire prompt to the Replit AI assistant to deploy your data migration tool:

---

## DEPLOY DATA MIGRATION TOOL TO REPLIT

I need you to help me deploy a Python data migration tool to Replit. Here are the specific instructions:

### 1. CLONE THE GITHUB REPOSITORY
The code is available in this GitHub repository:
- **Repository**: `autoflowcompliance/data-migration`
- **Branch**: `main`

Please clone this repository instead of waiting for file uploads:
```bash
git clone https://github.com/autoflowcompliance/data-migration.git
cd data-migration
```

### 2. SET UP THE PROJECT STRUCTURE
After cloning, the repository should contain:
- `app.py` - FastAPI web application
- `requirements.txt` - Python dependencies  
- `.replit` - Replit configuration
- `data_migration_tool/` - Complete tool directory
- Various documentation files

### 3. REMOVE STREAMLIT FILES
Please delete these Streamlit-specific files:
- `.streamlit/` folder (entire folder)
- `admin_wrapper.py` (Streamlit-specific)
- Any other Streamlit-related files

### 4. INSTALL DEPENDENCIES
Run this command in the Shell:
```bash
pip install -r requirements.txt
```

### 5. START THE APPLICATION
The `.replit` file should contain:
```toml
[run]
command = "python -m uvicorn app:app --host 0.0.0.0 --port 5000"
```

Then click the "Run" button to start the FastAPI server on port 5000 (avoiding port 8080 conflicts).

### 6. VERIFY DEPLOYMENT
The application should:
- Start on port 8080
- Be accessible via the web preview
- Respond to GET requests at the root endpoint
- Show API documentation at the web preview URL

### 7. TEST THE API
Test these endpoints:
- GET `/` - Should return tool information
- GET `/health` - Should return health status
- GET `/crms` - Should return available CRM systems
- GET `/info` - Should return system information

### 8. PROVIDE API DOCUMENTATION
The FastAPI app includes automatic API documentation at:
- `/docs` - Swagger UI
- `/redoc` - ReDoc documentation

### IMPORTANT NOTES:
- This is a FastAPI application, NOT Streamlit
- We removed all Streamlit dependencies
- The app uses standard FastAPI endpoints
- The core data migration functionality remains in the `data_migration_tool/` folder
- The app processes CSV files and returns cleaned data via API endpoints
- The repository is `autoflowcompliance/data-migration` on GitHub

### EXPECTED OUTCOME:
- FastAPI server running on port 8080
- API accessible via web preview
- All data migration functionality working via API endpoints
- Automatic API documentation available
- Professional data migration service deployed

Please clone the repository and set this up. I don't need to upload individual files since everything is in the GitHub repository.