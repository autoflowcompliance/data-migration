"""FastAPI web application for the AutoFlow data migration tool.

Deployed to Netlify Functions for serverless deployment.
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path
from typing import Optional

import chardet
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Add the data_migration_tool directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_migration_tool.auditors import audit_import
from data_migration_tool.cleaners import CleaningConfig
from data_migration_tool.mappers import available_crms, load_mapping_config
from data_migration_tool.pipeline import run_pipeline
from data_migration_tool.reporters import render_audit_report

# --------------------------------------------------------------------------
# FastAPI app setup
# --------------------------------------------------------------------------
app = FastAPI(title="Data Migration Tool", version="1.0.0")

MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200MB in bytes
MAX_DEMO_ROWS = 500


def get_brand_config() -> dict[str, str]:
    """Load white-label branding configuration from environment or defaults."""
    return {
        "brand_name": os.getenv("BRAND_NAME", "AutoFlow"),
        "tool_name": os.getenv("TOOL_NAME", "Data Migration Tool"),
        "operator_name": os.getenv("OPERATOR_NAME", "Neo Dlamini"),
        "contact_email": os.getenv("CONTACT_EMAIL", "autoflowcomliance@outlook.com"),
    }


brand = get_brand_config()


def read_upload(upload: UploadFile) -> pd.DataFrame:
    """Read uploaded CSV with automatic encoding detection."""
    raw = upload.file.read()
    result = chardet.detect(raw)
    encoding = result["encoding"] or "utf-8"
    return pd.read_csv(io.BytesIO(raw), dtype=str, encoding=encoding, keep_default_na=False)


# --------------------------------------------------------------------------
# Data models
# --------------------------------------------------------------------------
class ProcessingRequest(BaseModel):
    crm: str
    remove_duplicates: bool = True
    standardize_dates: bool = True
    standardize_phones: bool = True
    fix_scientific: bool = True
    normalize_unicode: bool = False
    missing_strategy: str = "flag"
    region: str = "US"
    date_first: bool = False
    brand_name: Optional[str] = None
    tool_name: Optional[str] = None
    project_name: str = "Client migration"


class ProcessingResponse(BaseModel):
    success: bool
    message: str
    quality_score: int
    rows_in: int
    rows_out: int
    duplicates_removed: int
    errors: int
    warnings: int


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "tool": brand["tool_name"],
        "brand": brand["brand_name"],
        "operator": brand["operator_name"],
        "contact": brand["contact_email"],
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "crms": "/crms",
            "process": "/process",
            "upload": "/upload"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "data-migration-tool"}


@app.get("/crms")
async def get_crms():
    """Get available CRM systems."""
    return {"crms": available_crms()}


@app.get("/crm/{crm_name}")
async def get_crm_config(crm_name: str):
    """Get configuration for a specific CRM."""
    if crm_name not in available_crms():
        raise HTTPException(status_code=404, detail="CRM not found")
    
    config = load_mapping_config(crm_name)
    return {
        "crm": crm_name,
        "fields": [
            {
                "name": f.name,
                "required": f.required,
                "unique": f.unique,
                "transform": f.transform or ""
            }
            for f in config.fields
        ]
    }


@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    crm: str = Form(...),
    remove_duplicates: bool = Form(True),
    standardize_dates: bool = Form(True),
    standardize_phones: bool = Form(True),
    fix_scientific: bool = Form(True),
    normalize_unicode: bool = Form(False),
    missing_strategy: str = Form("flag"),
    region: str = Form("US"),
    date_first: bool = Form(False),
    brand_name: Optional[str] = Form(None),
    tool_name: Optional[str] = Form(None),
    project_name: str = Form("Client migration")
):
    """Process a CSV file and return cleaned data."""
    
    # Validate CRM
    if crm not in available_crms():
        raise HTTPException(status_code=400, detail="Invalid CRM system")
    
    # Check file size
    if file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    try:
        # Read and process file
        source = read_upload(file)
        
        # Apply demo limit
        if len(source) > MAX_DEMO_ROWS:
            original_rows = len(source)
            source = source.head(MAX_DEMO_ROWS)
            demo_notice = f"Demo mode: Processing {MAX_DEMO_ROWS} of {original_rows} rows. Contact {brand['operator_name']} ({brand['contact_email']}) for full processing."
        else:
            demo_notice = None
        
        # Set branding
        os.environ["BRAND_NAME"] = brand_name or brand["brand_name"]
        os.environ["TOOL_NAME"] = tool_name or brand["tool_name"]
        
        # Run pipeline
        result = run_pipeline(
            source=source,
            crm=crm,
            cleaning_config=CleaningConfig(
                remove_duplicates=remove_duplicates,
                standardize_dates=standardize_dates,
                standardize_phones=standardize_phones,
                fix_scientific_notation=fix_scientific,
                normalize_unicode=normalize_unicode,
                missing_value_strategy=missing_strategy,
                default_region=region.upper() or "US",
                date_first=date_first,
            ),
            project_name=project_name,
            source_filename=file.filename,
        )
        
        summary = result.summary()
        
        return ProcessingResponse(
            success=True,
            message="File processed successfully" + (f". {demo_notice}" if demo_notice else ""),
            quality_score=int(round(summary["quality_score"])),
            rows_in=summary["rows_in"],
            rows_out=summary["rows_out"],
            duplicates_removed=summary["duplicates_removed"],
            errors=summary["errors"],
            warnings=summary["warnings"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/upload")
async def upload_and_process(
    file: UploadFile = File(...),
    crm: str = Form(...),
    remove_duplicates: bool = Form(True),
    standardize_dates: bool = Form(True),
    standardize_phones: bool = Form(True),
    fix_scientific: bool = Form(True),
    normalize_unicode: bool = Form(False),
    missing_strategy: str = Form("flag"),
    region: str = Form("US"),
    date_first: bool = Form(False),
    brand_name: Optional[str] = Form(None),
    tool_name: Optional[str] = Form(None),
    project_name: str = Form("Client migration")
):
    """Upload and process file, return cleaned CSV."""
    
    # Validate CRM
    if crm not in available_crms():
        raise HTTPException(status_code=400, detail="Invalid CRM system")
    
    # Check file size
    if file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    try:
        # Read and process file
        source = read_upload(file)
        
        # Apply demo limit
        if len(source) > MAX_DEMO_ROWS:
            original_rows = len(source)
            source = source.head(MAX_DEMO_ROWS)
            demo_notice = f"Demo mode: Processing {MAX_DEMO_ROWS} of {original_rows} rows."
        else:
            demo_notice = None
        
        # Set branding
        os.environ["BRAND_NAME"] = brand_name or brand["brand_name"]
        os.environ["TOOL_NAME"] = tool_name or brand["tool_name"]
        
        # Run pipeline
        result = run_pipeline(
            source=source,
            crm=crm,
            cleaning_config=CleaningConfig(
                remove_duplicates=remove_duplicates,
                standardize_dates=standardize_dates,
                standardize_phones=standardize_phones,
                fix_scientific_notation=fix_scientific,
                normalize_unicode=normalize_unicode,
                missing_value_strategy=missing_strategy,
                default_region=region.upper() or "US",
                date_first=date_first,
            ),
            project_name=project_name,
            source_filename=file.filename,
        )
        
        # Return cleaned CSV
        cleaned_csv = result.clean_frame.to_csv(index=False)
        
        return HTMLResponse(
            content=cleaned_csv,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=clean_{file.filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/info")
async def get_info():
    """Get system information."""
    return {
        "tool": brand["tool_name"],
        "brand": brand["brand_name"],
        "operator": brand["operator_name"],
        "contact": brand["contact_email"],
        "demo_limit": MAX_DEMO_ROWS,
        "max_upload_size_mb": MAX_UPLOAD_SIZE // (1024*1024),
        "available_crms": available_crms()
    }


# Netlify Functions handler (optional, for local testing)
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    handler = app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)