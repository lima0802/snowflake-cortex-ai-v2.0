"""
DIA v2.0 Web Application - Streamlit Interface
Main entry point for the web application
"""

import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="DIA v2.0 - Direct Marketing Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📊 DIA v2.0 - Direct Marketing Analytics Intelligence")
st.markdown("**Powered by Snowflake Cortex AI**")

# Sidebar
with st.sidebar:
    st.header("Configuration")

    # Orchestrator URL
    orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8000")
    st.text_input("Orchestrator URL", value=orchestrator_url, disabled=True)

    # Snowflake connection info
    st.subheader("Snowflake Connection")
    st.text_input("Account", value=os.getenv("SNOWFLAKE_ACCOUNT", ""), disabled=True)
    st.text_input("Database", value=os.getenv("SNOWFLAKE_DATABASE", ""), disabled=True)
    st.text_input("Schema", value=os.getenv("SNOWFLAKE_SCHEMA", ""), disabled=True)

    st.divider()

    # Health check
    if st.button("🔍 Check Orchestrator Health"):
        try:
            response = requests.get(f"{orchestrator_url}/api/v1/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ Orchestrator is healthy")
                st.json(response.json())
            else:
                st.error(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Cannot connect to orchestrator: {str(e)}")

# Main content
st.header("Analytics Query Interface")

# Query input
query = st.text_area(
    "Enter your question:",
    placeholder="Example: What was the click rate in Spain last month?",
    height=100
)

# Query button
if st.button("🚀 Run Query", type="primary"):
    if query:
        with st.spinner("Processing query..."):
            try:
                response = requests.post(
                    f"{orchestrator_url}/api/v1/query",
                    json={"query": query},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success("Query completed!")
                    st.json(result)
                else:
                    st.error(f"Query failed: {response.status_code}")
                    st.json(response.json())
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a query")

# Example queries
st.divider()
st.subheader("Example Queries")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Descriptive Analytics:**")
    st.code("What was the YTD click rate?")
    st.code("Show me campaign performance for EX30")
    st.code("What are the top performing markets?")

with col2:
    st.markdown("**Diagnostic Analytics:**")
    st.code("Why did click rate drop in Q4?")
    st.code("What factors influenced bounce rate?")
    st.code("How does Germany compare to EMEA average?")

# Footer
st.divider()
st.caption("DIA v2.0 - Volvo Direct Marketing Analytics Intelligence | Powered by Snowflake Cortex AI")
