#!/usr/bin/env python
"""Simple test to diagnose admin.py issues"""
import sys
from pathlib import Path

print("Python version:", sys.version)
print("Working directory:", Path.cwd())
print()

# Test 1: Import admin module
print("Test 1: Importing admin module...")
try:
    import admin
    print("✓ admin module imported successfully")
except Exception as e:
    print(f"✗ Failed to import admin: {e}")
    sys.exit(1)

# Test 2: Check if functions exist
print("\nTest 2: Checking admin functions...")
try:
    assert hasattr(admin, 'main'), "main() not found"
    assert hasattr(admin, 'process_new_job'), "process_new_job() not found"
    assert hasattr(admin, 'run_audit_flow'), "run_audit_flow() not found"
    assert hasattr(admin, 'view_job_log'), "view_job_log() not found"
    print("✓ All required functions found")
except AssertionError as e:
    print(f"✗ {e}")
    sys.exit(1)

# Test 3: Check app_files imports
print("\nTest 3: Testing app_files imports...")
try:
    from app_files import pipeline, cleaners, mappers
    print("✓ app_files modules imported successfully")
except Exception as e:
    print(f"✗ Failed to import app_files modules: {e}")
    sys.exit(1)

# Test 4: Check deliveries directory
print("\nTest 4: Checking deliveries directory...")
try:
    deliveries_dir = Path.cwd() / "deliveries"
    deliveries_dir.mkdir(exist_ok=True)
    print(f"✓ Deliveries directory ready: {deliveries_dir}")
except Exception as e:
    print(f"✗ Failed to create deliveries directory: {e}")
    sys.exit(1)

print("\n✅ All diagnostic tests passed!")
print("\nYou can now run: python admin.py")
