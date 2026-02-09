# 🧪 Lab Materials

This folder contains the core lab execution files that participants will use during the hands-on session.

## 📁 Contents

- **`SETUP_TOOLS.ipynb`** - Main lab notebook with step-by-step instructions
- **`streamlit_app.py`** - AI agent application for deployment

## 🎯 How to Use

### During the Lab

1. **Open** `SETUP_TOOLS.ipynb` in your Snowflake environment
2. **Follow** the notebook cells sequentially:
   - **Part 1**: Document processing (PDFs and images)
   - **Part 2**: Sales analytics data creation
   - **Part 3**: Cortex Search and Analyst setup
3. **Deploy** `streamlit_app.py` as your final AI agent

### Notebook Structure

The notebook is organized into clear sections:
- **Setup verification** - Confirm your environment is ready
- **Unstructured data processing** - Extract insights from documents and images
- **Structured data creation** - Build sales analytics dataset
- **AI services setup** - Configure Cortex Search and Analyst
- **Testing and validation** - Verify everything works

### Streamlit App

The `streamlit_app.py` creates an intelligent sales assistant that can:
- Answer questions about product specifications (from documents/images)
- Generate SQL queries for sales analytics (from structured data)
- Provide a conversational interface for both data types

## 🔧 Technical Requirements

- **Snowflake Role**: `SNOWCAMP`
- **Database**: `SNOWCAMP_DB` 
- **Warehouse**: `SNOWCAMP_WHS`
- **Schema**: Your individual schema (e.g., USER01)

## 📊 What You'll Build

By the end of this lab, you'll have:
- ✅ Processed 22 product documents and images
- ✅ Created a sales analytics dataset with 80,000+ records
- ✅ Set up semantic search across all your data
- ✅ Deployed a conversational AI agent
- ✅ Learned to build multi-modal AI applications in Snowflake

## 🚨 Troubleshooting

- **Notebook won't run**: Check you're in the correct database/schema
- **File not found errors**: Verify file uploads in `../participant-setup/`
- **Permission errors**: Confirm you're using the `SNOWCAMP` role
- **Warehouse issues**: Ensure `SNOWCAMP_WHS` is available
