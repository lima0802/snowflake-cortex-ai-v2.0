# File Upload Guide - Snowflake Cortex AI Lab

## Overview

This guide provides detailed instructions for uploading files to your Snowflake stages. Since this lab uses local file downloads instead of Git repository cloning, you'll need to manually upload the required files to your Snowflake workspace.

## Required Files

You need to upload two sets of files:

### 1. Document Files (to `@docs` stage)
**Location**: `docs/` folder in your downloaded repository  
**Files to upload**:
- `Carver Skis Specification Guide.pdf`
- `Mondracer_Infant_Bike.pdf`
- `OutPiste Skis Specification Guide.pdf`
- `Outpiste_Skis.jpeg`
- `Premium_Bicycle_1.jpeg`
- `Premium_Bicycle_2.jpeg`
- `Premium_Bicycle_3.jpeg`
- `Premium_Bicycle_4.jpeg`
- `Premium_Bicycle_User_Guide.pdf`
- `Racing_Fast_Skis.jpeg`
- `RacingFast Skis Specification Guide.pdf`
- `Ski_Boots_TDBootz_Special.jpg`
- `Ski_Boots_TDBootz_Special.pdf`
- `The_Ultimate_Downhill_Bike_1.jpeg`
- `The_Ultimate_Downhill_Bike_2.jpeg`
- `The_Ultimate_Downhill_Bike.pdf`
- `The_Xtreme_Road_Bike_1.jpeg`
- `The_Xtreme_Road_Bike_105_SL.pdf`
- `The_Xtreme_Road_Bike_2.jpeg`
- `The_Xtreme_Road_Bike_3.jpeg`
- `The_Xtreme_Road_Bike_4.jpeg`
- `The_Xtreme_Road_Bike_5.jpeg`

### 2. Semantic Model Files (to `@semantic_files` stage)
**Location**: Root of your downloaded repository  
**Files to upload**:
- `semantic.yaml`
- `semantic_search.yaml`

---

## Method 1: Snowsight Web Interface (Recommended)

### Step 1: Navigate to Your Stages

1. **Login to Snowflake** using your lab credentials
2. **Navigate to Data**:
   - Click "Data" in the left sidebar
   - Click "Databases"
   - Click "CORTEX_LAB_SHARED"
   - Click your schema name (e.g., "USER01")
   - Click "Stages"

### Step 2: Upload Document Files

1. **Select the docs stage**:
   - Click on the `docs` stage in the list

2. **Upload files**:
   - Click the "Upload Files" button (usually in the top right)
   - **Select ALL files** from the `docs/` folder in your downloaded repository
   - You can select multiple files at once using Ctrl+Click (Windows) or Cmd+Click (Mac)
   - Click "Upload" or "Open"

3. **Wait for upload**:
   - You'll see a progress indicator
   - Wait for all files to complete uploading
   - You should see a success message

4. **Verify upload**:
   - You should see all 22 files listed in the stage
   - File sizes should be greater than 0 bytes

### Step 3: Upload Semantic Files

1. **Select the semantic_files stage**:
   - Navigate back to the stages list
   - Click on the `semantic_files` stage

2. **Upload semantic files**:
   - Click "Upload Files"
   - Select `semantic.yaml` and `semantic_search.yaml` from the repository root
   - Click "Upload"

3. **Verify upload**:
   - You should see both YAML files in the stage
   - Files should have content (not 0 bytes)

### Step 4: Verification

Run these SQL commands to verify your uploads:

```sql
-- Check document files
SELECT 
    RELATIVE_PATH, 
    SIZE, 
    LAST_MODIFIED 
FROM DIRECTORY('@docs') 
ORDER BY RELATIVE_PATH;

-- Should return 22 files

-- Check semantic files
SELECT 
    RELATIVE_PATH, 
    SIZE, 
    LAST_MODIFIED 
FROM DIRECTORY('@semantic_files') 
ORDER BY RELATIVE_PATH;

-- Should return 2 files (semantic.yaml, semantic_search.yaml)
```

---

## Method 2: SnowSQL Command Line (Alternative)

### Prerequisites

1. **Install SnowSQL**: Download from [Snowflake Downloads](https://developers.snowflake.com/snowsql/)
2. **Configure Connection**: Set up your connection profile

### Step 1: Connect to Snowflake

```bash
# Connect using your lab credentials
snowsql -a [your-account-identifier] -u [your-username]

# Use your lab database and schema
USE DATABASE CORTEX_LAB_SHARED;
USE SCHEMA [your-schema-name];
```

### Step 2: Upload Files

```bash
# Upload all document files
PUT file://path/to/your/downloaded/repo/docs/* @docs/;

# Upload semantic files
PUT file://path/to/your/downloaded/repo/semantic.yaml @semantic_files/;
PUT file://path/to/your/downloaded/repo/semantic_search.yaml @semantic_files/;
```

**Note**: Replace `path/to/your/downloaded/repo` with the actual path to your downloaded repository.

### Step 3: Verify Uploads

```sql
-- Check uploads
LIST @docs;
LIST @semantic_files;
```

---

## Method 3: Python Script (Advanced)

If you're comfortable with Python, you can use this script:

```python
import snowflake.connector
import os
from pathlib import Path

# Connection parameters (replace with your details)
conn = snowflake.connector.connect(
    user='your-username',
    password='your-password',
    account='your-account-identifier',
    database='CORTEX_LAB_SHARED',
    schema='your-schema-name'
)

cursor = conn.cursor()

# Upload document files
docs_path = Path('path/to/your/repo/docs')
for file_path in docs_path.glob('*'):
    if file_path.is_file():
        cursor.execute(f"PUT file://{file_path} @docs/")
        print(f"Uploaded {file_path.name}")

# Upload semantic files
repo_path = Path('path/to/your/repo')
for yaml_file in ['semantic.yaml', 'semantic_search.yaml']:
    file_path = repo_path / yaml_file
    if file_path.exists():
        cursor.execute(f"PUT file://{file_path} @semantic_files/")
        print(f"Uploaded {yaml_file}")

cursor.close()
conn.close()
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Stage not found"
**Cause**: You haven't run the setup.sql script or created your schema  
**Solution**: 
1. Ensure you've run `setup.sql` completely
2. Verify you're in the correct schema: `USE SCHEMA [your-schema-name];`
3. Check stages exist: `SHOW STAGES;`

#### Issue: "Permission denied" during upload
**Cause**: Insufficient privileges on the stage  
**Solution**:
1. Verify you're using the `CORTEX_LAB_USER` role
2. Contact instructor if permissions are missing

#### Issue: Files show 0 bytes after upload
**Cause**: Upload was interrupted or failed  
**Solution**:
1. Delete the failed files: `REMOVE @docs/[filename];`
2. Re-upload the files
3. Check your internet connection stability

#### Issue: "File format not supported"
**Cause**: Trying to upload unsupported file types  
**Solution**:
1. Only upload the files listed in this guide
2. Ensure file extensions are correct (.pdf, .jpeg, .jpg, .yaml)

#### Issue: Upload is very slow
**Cause**: Large files or slow internet connection  
**Solution**:
1. Upload files in smaller batches
2. Use a stable internet connection
3. Try during off-peak hours

### Verification Commands

Use these SQL commands to troubleshoot:

```sql
-- Check if stages exist
SHOW STAGES;

-- Check current context
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_ROLE();

-- List files in stages
SELECT * FROM DIRECTORY('@docs');
SELECT * FROM DIRECTORY('@semantic_files');

-- Check file sizes (should not be 0)
SELECT 
    RELATIVE_PATH, 
    SIZE,
    CASE 
        WHEN SIZE = 0 THEN '❌ Empty file - re-upload needed'
        ELSE '✅ File OK'
    END as STATUS
FROM DIRECTORY('@docs')
ORDER BY SIZE;

-- Remove a specific file if needed
-- REMOVE @docs/filename.pdf;
```

### Getting Help

If you encounter issues:

1. **Check this guide** for common solutions
2. **Ask a neighbor** - they might have solved the same issue
3. **Contact instructor** for technical support
4. **Check Snowflake documentation** for SnowSQL issues

---

## File Upload Checklist

Before proceeding with the lab, ensure:

- [ ] You've downloaded the complete repository
- [ ] You can access Snowflake with your lab credentials
- [ ] You've run the `setup.sql` script successfully
- [ ] You can see your stages: `SHOW STAGES;`
- [ ] All 22 document files are uploaded to `@docs`
- [ ] Both semantic YAML files are uploaded to `@semantic_files`
- [ ] All files show non-zero sizes
- [ ] Verification queries return expected results

**Ready to continue?** Head back to the main lab guide and proceed with Part 2: Document Processing!

---

## Quick Reference

### File Counts
- **Document files**: 22 files (PDFs and images)
- **Semantic files**: 2 files (YAML configuration)
- **Total**: 24 files

### Stage Names
- **Documents**: `@docs`
- **Semantic models**: `@semantic_files`

### Verification Query
```sql
SELECT 
    'docs' as stage_name,
    COUNT(*) as file_count
FROM DIRECTORY('@docs')
UNION ALL
SELECT 
    'semantic_files' as stage_name,
    COUNT(*) as file_count
FROM DIRECTORY('@semantic_files');

-- Expected result:
-- docs: 22 files
-- semantic_files: 2 files
```
