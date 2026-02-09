# Participant Guide - Building Agentic AI Applications in Snowflake

## Welcome to the Multi-User Cortex AI Lab! 🚀

This comprehensive guide will walk you through building an intelligent AI agent that can answer questions about both structured data (sales analytics) and unstructured data (product documents and images).

## Before You Start

### Prerequisites Checklist
- [ ] Received lab credentials (username, password, account URL)
- [ ] Downloaded the lab repository to your local machine
- [ ] Can access Snowflake with your assigned `SNOWCAMP` role
- [ ] Have a text editor or IDE for viewing/editing files

### What You'll Build
By the end of this lab, you'll have:
1. **Document Processing Pipeline** - Extract insights from PDFs and images
2. **Sales Analytics Dataset** - Structured data for business intelligence
3. **AI-Powered Search** - Semantic search across all your data
4. **Conversational Interface** - Deploy your Agent in Snowflake Intelligence for natural language questions

---

## Part 1: Environment Setup (15 minutes)

### Step 1.1: Login and Verify Access

1. **Login to Snowflake**
   - Use the account URL provided by your instructor
   - Username: Your assigned email address
   - Password: Temporary password (you'll be prompted to change it)

2. **Verify Your Role**
   ```sql
   SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_WAREHOUSE();
   ```
   - You should see `SNOWCAMP` as your role
   - Database should be `SNOWCAMP_DB`
   - Warehouse should be `SNOWCAMP_WHS`

### Step 1.2: Create Your Workspace

1. **Choose Your Schema Name**
   - Pick a unique identifier (e.g., `USER01`, `JOHN_DOE`, `TEAM_A`)
   - Remember this name - you'll use it throughout the lab

2. **Run the Setup Script**
   - Open `setup.sql` in your downloaded repository
   - **IMPORTANT**: Replace `USER01` with your chosen schema name
   - Execute the entire script in Snowflake

3. **Verify Setup**
   ```sql
   SELECT CURRENT_SCHEMA();
   SHOW STAGES;
   ```
   - You should see your schema name
   - Two stages should exist: `docs` and `semantic_files`

### Step 1.3: Upload Files

**Method 1: Using Snowsight (Recommended)**

1. **Upload Document Files**
   - Navigate to: Data → Databases → CORTEX_LAB_SHARED → [Your Schema] → Stages
   - Click on the `docs` stage
   - Click "Upload Files"
   - Select ALL files from the `docs/` folder in your downloaded repository
   - Wait for upload to complete

2. **Upload Semantic Files**
   - Click on the `semantic_files` stage
   - Upload `semantic.yaml` from the config folder

**Method 2: Using SnowSQL (Alternative)**

```bash
# Connect to your account
snowsql -a [account] -u [username]

# Upload document files
PUT file://path/to/docs/* @docs/;

# Upload semantic files
PUT file://semantic*.yaml @semantic_files/;
```

3. **Verify Uploads**
   ```sql
   SELECT * FROM DIRECTORY('@docs');
   SELECT * FROM DIRECTORY('@semantic_files');
   ```

---

## Part 2: Document Processing (30 minutes)

### Step 2.1: Open the Lab Notebook

1. **Launch Jupyter/Notebook Environment**
   - Navigate to: Projects → Notebooks
   - Click on the dropdown next to "+Notebook"
   - Import .ipynb file 
   - Select SETUP_TOOLS.ipynb in the lab-materials folder
   - Select "Run on warehouse" and "Snowflake Warehouse Runtime 2.0" and the "Snowcamp_WHS" as query warehouse. Use the system warehouse for running the notebook. 
   - Click on Create

### Step 2.2: Process PDF Documents

**What you're doing**: Extracting text from product specification PDFs using AI

1. **Preview Your Documents**
   ```sql
   SELECT * FROM DIRECTORY('@docs') WHERE RELATIVE_PATH LIKE '%.pdf';
   ```

2. **Extract Text from PDFs**
   - Run the `AI_PARSE_DOCUMENT` cell
   - This uses Snowflake's AI to extract structured text from PDFs
   - **Expected result**: Text content from all PDF files

3. **Create Text Chunks**
   - Run the text chunking cell
   - This breaks documents into searchable pieces
   - **Expected result**: `DOCS_CHUNKS_TABLE` with thousands of text chunks

### Step 2.3: Process Images

**What you're doing**: Generating descriptions of product images using multimodal AI

1. **Generate Image Descriptions**
   - Run the image processing cell
   - This uses Claude to describe each product image
   - **Expected result**: Descriptive text added to your chunks table

2. **Classify Content**
   - Run the classification cell
   - AI automatically categorizes content as "Bike" or "Snow" products
   - **Expected result**: All chunks have category labels

### Step 2.4: Create Search Service

**What you're doing**: Setting up semantic search across all your content

1. **Create Cortex Search Service**
   ```sql
   CREATE OR REPLACE CORTEX SEARCH SERVICE DOCS
   ON chunk
   ATTRIBUTES relative_path, category
   WAREHOUSE = SNOWCAMP_WHS
   TARGET_LAG = '1 hour'
   EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
   AS (
       SELECT chunk, chunk_index, relative_path, category
       FROM docs_chunks_table
   );
   ```

2. **Test Your Search**
   ```sql
   SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
       'DOCS', 
       'mountain bike specifications'
   );
   ```

---

## Part 3: Sales Analytics Setup (20 minutes)

### Step 3.1: Create Business Data

**What you're doing**: Building a realistic sales dataset for analytics

1. **Create Product Catalog**
   - Run the `DIM_ARTICLE` creation cell
   - This creates a table of bikes and ski products with prices

2. **Generate Customer Data**
   - Run the `DIM_CUSTOMER` creation cell
   - This creates 5,000 synthetic customers with demographics

3. **Create Sales Transactions**
   - Run the `FACT_SALES` creation cell
   - This generates 10,000 sales transactions over 3 years

### Step 3.2: Setup Analytics Search

**What you're doing**: Enabling natural language queries on your sales data

1. **Create Article Name Search**
   ```sql
   CREATE OR REPLACE CORTEX SEARCH SERVICE ARTICLE_NAME_SEARCH
     ON ARTICLE_NAME
     WAREHOUSE = CORTEX_LAB_WH
     TARGET_LAG = '1 hour'
     EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
   AS (
     SELECT DISTINCT ARTICLE_NAME
     FROM DIM_ARTICLE
   );
   ```

2. **Verify Your Data**
   ```sql
   SELECT 
       COUNT(*) as total_sales,
       SUM(total_price) as total_revenue,
       COUNT(DISTINCT customer_id) as unique_customers
   FROM FACT_SALES;
   ```

---

## Part 4: Create your Agent in Snowsight

### Step 4.1: Explore Semantic Model

The semantic model maps business terminology to the structured data and adds contextual meaning. It allows Cortex Analyst to generate the correct SQL for a question asked in natural language.

- In Snowsight, navigate to: AI&ML → Cortex Analyst
- Click on Snowcamp_DB -> [Your Schema]
- Select Semantic_Files stage and Click on the existing semantic.yaml

### Step 4.2: Test Semantic Model

Let's ask these analytical questions to test the semantic file:

- What is the average revenue per transaction per sales channel?
- What products are often bought by the same customers?

Cortex Analyst and Cortex Search can be integrated for improved retrieval of values of a column without listing them all in the semantic model file: 
- Click on DIM_ARTICLE -> Dimensions and edit ARTICLE_NAME. Here you will see that some sample values have been provided.
- Then ask the question: 

"What are the total sales for the carvers?" 

Seems as it's not sure what you are talking about right? 

Now let's integrate the ARTICLE_NAME dimension with the SNOWCAMP_DB.[Your Schema].ARTICLE_NAME_SEARCH Cortex Search Service we created in the Notebook: 
- Remove the sample values provided
- Click on + Search Service and add ARTICLE_NAME_SEARCH
- Click on Save, also save your semantic file (top right)

Now ask it again: 

"What are the total sales for the carvers?" 

This time Cortex Analyst gets it right? Also note that we asked for "Carvers", but the literal article name is "Carver Skis." *cool emoji with sunglasses on* 

### Step 4.3: Create your first Agent 

An agent is an intelligent entity within Snowflake Intelligence that acts on behalf of the user. Agents are configured with specific tools and orchestration logic to answer questions and perform tasks on top of your data.

- In Snowsight, on the left hand navigation menu, select AI&ML → Agents
- Click on Create agent → Schema: SNOWFLAKE_INTELLIGENCE.AGENTS → Create this agent for Snowflake Intelligence
- Choose a name for agent object and for display (e.g. username)

Select the agent you just created. 

This is where you can edit and monitor your agent. Let's add some tools and instructions:

Click on Edit in the top right corner. 

**Under About Tab**

Add a high-level description: 
- Here is an example "This agent helps users explore bike and ski products, sales data, and customer analytics from structured and unstructured data."

Add the following starter questions under Example questions:
- "Show me monthly sales revenue trends by product category over the past 2 years."
- "What is the guarantee of the premium bike?"
- "What is the length of the carver skis?"
- "Is there any brand in the frame of the downhill bike?"
- "How many carvers are we selling per year in the North region?"

**Add Tools**

- Add Cortex Analyst: Choose Semantic model file → Database: Snowcamp_DB -> [Your Schema] → Stage: SEMANTIC_FILES
- Click on semantic.yaml
- Name it "Sales_Data"
- Add a description: 

"This retail sales analytics semantic model from DASH_CORTEX_AGENTS.DATA database provides comprehensive sales transaction analysis capabilities through a star schema connecting customer demographics, product catalog, and sales facts. The model enables detailed reporting on sales performance across multiple dimensions including customer segments (Premium, Regular, Occasional), product categories (Bikes, Ski Boots, Skis), sales channels (Online, In-Store, Partner), and time periods. The central FACT_SALES table captures transaction details including quantities, pricing, and promotional information, while linking to DIM_CUSTOMER for demographic analysis and DIM_ARTICLE for product performance insights. The system supports advanced product search functionality and is specifically designed to answer sales-related questions about product performance, customer behavior, and revenue analysis while excluding product specifications or usage information." 

- Warehouse: User's default 
- Query timeout: 60 (seconds)
- Click on Add

- Add Cortex Search Services: Choose Semantic model file → Database: Snowcamp_DB -> [Your Schema] → Choose: SNOWCAMP_DB.[Your Schema].DOCS
- ID column: CHUNK_INDEX
- Title column: RELATIVE_PATH
- Name: Docs
- Add a description: 

"Searches through product specifications, user guides, and images for bikes and ski equipment. Use this tool when users ask about product features, technical specifications, colors, designs, or any information contained in product documentation and images."
- Click on Add

**Orchestration**

- Choose the whatever model you find available
- Add Orchestration instructions: 
"Whenever you can answer visually with a chart, always choose to generate a chart even if the user didn't specify to." 
- You can also add response instructions. At the end of the lab and there is time left, play around with these instructions and observe the differences. 

** IMPORTANT TO HIT SAVE NOW IN THE RIGHT UPPER CORNER **

## Part 5: Snowflake Intelligence

Now, let's launch Snowflake Intelligence. You will find it under AI&ML → Snowflake Intelligence.  
- Make sure you're signed into the right account. If you're not sure, click on your name in the bottom left » Sign out and sign back in. Also note that your role should be set to

**Try these example queries:**

**Unstructured Data Queries** :
- "What is the guarantee of the premium bike?"
- "What is the length of the carver skis?"
- "Is there any brand in the frame of the downhill bike?"

**Structured Data Queries** :
- "Show me monthly sales revenue trends by product category over the past 2 years."
- "How many carvers are we selling per year in the North region?"
- "How many infant bikes are we selling per month?"
- "What are the top 5 customers buying the carvers?"

**Mixed Queries** (uses both data types):
- "What are the best-selling bike models and their specifications?"
- "Compare sales performance of different ski brands"

---

## Part 5: Explore and Experiment (20 minutes)

### Advanced Features to Try

1. **Additional Custom Tool**
   - Add the send_email store procedure as a custom tool to send summarising emails from Snowflake Intelligence. 
   - Add Custom Tool: Choose Snowcamp_DB -> [Your Schema]
   - Custom tool identifier: Snowcamp_DB.[Your Schema].SEND_EMAIL()
   - Parameter: body 
      - Description: Use HTML-Syntax for this. If the content you get is in markdown, translate it to HTML. If body is not provided, summarize the last question and use that as content for the email.
   - Parameter: recipient_email
      - Description: If the email is not provided, send it to YOUR_EMAIL_ADDRESS_GOES_HERE.
   - Parameter: subject
      - Description: If subject is not provided, use "Snowflake Intelligence".
   - Warehouse: SNOWCAMP_WHS
   - Query timeout: 60

   Obs: If there is no email in your profile, this step will not be possible. Check if there is an email attached to your profile by clicking on your profile in lower left corner -> Settings
      - If there is an email but it says "Please verify your email address. Resend verification", click on the Resend verification.

2. **Custom Prompts**
   - Modify the response instructions in your Agent.
   - Try different conversation styles or focus areas. 

3. **Additional Data**
   - Add your own documents to the `@docs` stage
   - Create additional product categories or customer segments

4. **Enhanced Analytics**
   - Create new calculated fields in your semantic model
   - Add time-based filters or geographic analysis


### Troubleshooting Common Issues

**"Schema not found" errors**
- Verify you're in the correct schema: `USE SCHEMA [your_schema_name];`

**"Stage not found" errors**
- Check file uploads: `SELECT * FROM DIRECTORY('@docs');`
- Re-upload files if necessary

**"Warehouse not available" errors**
- Verify warehouse access: `USE WAREHOUSE CORTEX_LAB_WH;`

**Cortex functions not working**
- Check your role has proper permissions
- Contact instructor if persistent issues

### Key Technologies Used

- **Snowflake Cortex AI**: LLM functions for text processing and analysis
- **Cortex Search**: Semantic search across unstructured data
- **Cortex Analyst**: Natural language to SQL conversion
- **Streamlit**: Web application framework for the user interface
- **Snowpark**: Python integration with Snowflake

### Business Value

This architecture enables:
- **Unified Data Access**: Query both structured and unstructured data in natural language
- **Rapid Insights**: Get answers without writing SQL or searching through documents
- **Scalable AI**: Leverage enterprise-grade AI within your data platform
- **Cost Efficiency**: Process and analyze data without moving it outside Snowflake

---

## Next Steps

### Immediate Actions
1. **Save Your Work**: Export any custom queries or modifications
2. **Document Learnings**: Note what worked well and what could be improved
3. **Share Results**: Show colleagues what you built

### Continued Learning
1. **Explore Cortex AI Functions**: Try other AI capabilities in Snowflake
2. **Production Deployment**: Learn about scaling this architecture
3. **Advanced Features**: Investigate agents, fine-tuning, and custom models

### Resources
- [Snowflake Cortex AI Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex)

---

## Feedback

Your feedback helps improve this lab! Please share:
- What worked well?
- What was confusing?
- What would you like to see added?
- How would you use this in your work?

**Contact**: henry.faegnell@snowflake.com & tatiana.petrache@snowflake.com

---

**Congratulations!** 🎉 You've successfully built an intelligent AI agent that can reason across multiple data types. This foundation can be extended and customized for countless business applications.

Happy building! 🚀
