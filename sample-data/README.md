# 📊 Sample Data

This folder contains sample documents and images that participants will process during the lab.

## 📁 Contents

The `docs/` folder contains 22 files representing a bike and ski retail company's product catalog:

### 📄 PDF Documents (8 files)
- **Bike Specifications**:
  - `Mondracer_Infant_Bike.pdf`
  - `Premium_Bicycle_User_Guide.pdf` 
  - `The_Ultimate_Downhill_Bike.pdf`
  - `The_Xtreme_Road_Bike_105_SL.pdf`

- **Ski Equipment Specifications**:
  - `Carver Skis Specification Guide.pdf`
  - `OutPiste Skis Specification Guide.pdf`
  - `RacingFast Skis Specification Guide.pdf`
  - `Ski_Boots_TDBootz_Special.pdf`

### 🖼️ Product Images (14 files)
- **Bike Images**: Premium_Bicycle_*.jpeg, The_Ultimate_Downhill_Bike_*.jpeg, The_Xtreme_Road_Bike_*.jpeg
- **Ski Equipment Images**: Outpiste_Skis.jpeg, Racing_Fast_Skis.jpeg, Ski_Boots_TDBootz_Special.jpg

## 🎯 How This Data is Used

### During the Lab
1. **Upload**: All files go to your `@docs` stage in Snowflake
2. **Processing**: 
   - PDFs are parsed using `AI_PARSE_DOCUMENT` 
   - Images are described using `AI_COMPLETE` with Claude
   - Content is classified as "Bike" or "Snow" using `AI_CLASSIFY`
3. **Search**: Files are indexed by Cortex Search for semantic retrieval
4. **Querying**: Your AI agent can answer questions about any product

### What You'll Learn
- **Multi-modal AI**: Process both text (PDFs) and images simultaneously
- **Document Intelligence**: Extract structured information from unstructured data
- **Semantic Search**: Find relevant content using natural language queries
- **AI Classification**: Automatically categorize content

## 📋 File Upload Instructions

1. **Navigate** to your Snowflake environment
2. **Go to** Data → Databases → SNOWCAMP_DB → [Your Schema] → Stages → docs
3. **Upload** ALL files from the `docs/` folder
4. **Verify** upload with: `SELECT * FROM DIRECTORY('@docs');`

## 🔍 Sample Queries You'll Be Able to Ask

After processing this data, your AI agent will answer questions like:

**Product Specifications**:
- "What are the technical specifications of the Ultimate Downhill Bike?"
- "Show me all the ski products and their features"
- "What colors are available for the Premium Bicycle?"

**Visual Information**:
- "Describe the design of the Xtreme Road Bike"
- "What do the ski boots look like?"
- "Show me images of red bikes"

**Combined Analysis**:
- "Compare the features of all mountain bikes"
- "What's the difference between the ski models?"

## 📊 Data Statistics

- **Total Files**: 22
- **File Types**: PDF (8), JPEG/JPG (14)
- **Categories**: Bikes (60%), Ski Equipment (40%)
- **Content**: Technical specs, user guides, product images
- **Languages**: English
- **File Sizes**: Range from 50KB to 2MB

This sample dataset provides a realistic scenario for building AI agents that can reason across multiple data modalities!
