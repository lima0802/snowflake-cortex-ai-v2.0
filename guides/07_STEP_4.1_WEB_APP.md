# Step 4.1: Implement Web Application

**Phase:** 4 - Interface Layer  
**Goal:** Build Streamlit chat interface with visualizations  
**Status:** ⏳ Not Started

---

## Overview

Create user-friendly Streamlit web app for:
- Natural language queries
- Chat interface with history
- Data visualizations
- Benchmark displays

---

## Prerequisites

- [ ] Step 3.1-3.2: API routes and conversation management working
- [ ] Streamlit container running (Step 1.1)

---

## Main App Structure

### File: `web-app/app.py`

```python
import streamlit as st
import requests
from typing import Optional
import plotly.express as px

# Page config
st.set_page_config(
    page_title="DIA v2.0 - Marketing Intelligence",
    page_icon="📊",
    layout="wide"
)

# API endpoint
API_URL = "http://orchestrator:8000/api/v1"

def main():
    st.title("📊 DIA v2.0 - Marketing Intelligence Assistant")
    
    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        render_sidebar()
    
    # Main chat interface
    render_chat_interface()

def render_sidebar():
    st.header("Settings")
    
    # Session management
    if st.button("New Conversation"):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.rerun()
    
    # Sample queries
    st.subheader("Sample Queries")
    samples = [
        "What was the click rate last month?",
        "Compare ES vs SE markets",
        "Why did open rate drop?",
        "Predict clicks for next month",
        "How to improve engagement?"
    ]
    
    for sample in samples:
        if st.button(sample, key=f"sample_{sample}"):
            process_query(sample)
            st.rerun()

def render_chat_interface():
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.write(message["content"])
            else:
                render_assistant_message(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your marketing data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = process_query(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response})
                render_assistant_message(response)

def process_query(query: str) -> dict:
    """Send query to API and get response"""
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={
                "query": query,
                "session_id": st.session_state.session_id
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        # Update session ID
        if "session_id" in data:
            st.session_state.session_id = data["session_id"]
        
        return data
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return {"error": str(e)}

def render_assistant_message(response: dict):
    """Render assistant response with visualizations"""
    if "error" in response:
        st.error(response["error"])
        return
    
    # Display intent
    if "intent" in response:
        intent_type = response["intent"].get("intent")
        confidence = response["intent"].get("confidence", 0)
        st.caption(f"📌 Intent: {intent_type} (confidence: {confidence:.1%})")
    
    # Display results
    if "results" in response:
        results = response["results"]
        
        # Text summary
        if "summary" in results:
            st.write(results["summary"])
        
        # Data table
        if "data" in results and isinstance(results["data"], list):
            st.dataframe(results["data"])
    
    # Display enhanced response
    if "enhanced_response" in response:
        enhanced = response["enhanced_response"]
        
        # Benchmark comparison
        if "benchmark_comparison" in enhanced:
            render_benchmark_comparison(enhanced["benchmark_comparison"])
        
        # Insights
        if "insights" in enhanced and enhanced["insights"]:
            st.subheader("💡 Key Insights")
            for insight in enhanced["insights"]:
                st.info(insight)
        
        # Recommendations
        if "recommendations" in enhanced and enhanced["recommendations"]:
            st.subheader("🎯 Recommendations")
            for rec in enhanced["recommendations"]:
                st.success(rec)
        
        # Visualization
        if "visualization_config" in enhanced:
            render_visualization(enhanced["visualization_config"])

def render_benchmark_comparison(benchmark: dict):
    """Render benchmark comparison"""
    st.subheader("📊 Benchmark Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=benchmark.get("metric", "Metric"),
            value=f"{benchmark.get('actual_value', 0):.2f}",
            delta=f"{benchmark.get('difference_pct', 0):.1f}%"
        )
    
    with col2:
        st.metric(
            label="Industry Benchmark",
            value=f"{benchmark.get('benchmark_value', 0):.2f}"
        )
    
    with col3:
        status = benchmark.get("status", "")
        st.metric(
            label="Status",
            value=status.upper()
        )

def render_visualization(viz_config: dict):
    """Render charts based on config"""
    st.subheader("📈 Visualization")
    
    chart_type = viz_config.get("chart_type")
    
    if chart_type == "line":
        fig = px.line(
            x=viz_config.get("x_axis"),
            y=viz_config.get("y_axis"),
            title=viz_config.get("title", "")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "bar":
        fig = px.bar(
            x=viz_config.get("categories"),
            y=viz_config.get("values"),
            title=viz_config.get("title", "")
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
```

---

## Styling

### File: `web-app/.streamlit/config.toml`

```toml
[theme]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
```

---

## Testing

1. Start containers:
```bash
docker-compose up -d
```

2. Open browser: http://localhost:8501

3. Test scenarios:
- Ask simple query
- Ask follow-up question
- Check visualizations render
- Verify new conversation button works

---

## Deliverables

- [ ] Main Streamlit app implemented
- [ ] Chat interface functional
- [ ] Visualizations working (line, bar charts)
- [ ] Benchmark displays
- [ ] Session management
- [ ] Sample queries sidebar

---

## Success Criteria

✅ Clean, intuitive chat interface  
✅ Visualizations render correctly  
✅ Multi-turn conversations work  
✅ Responsive design  

---

**Next:** [Step 4.2: Integration Channels](08_STEP_4.2_INTEGRATIONS.md)  
**Estimated Time:** 2-3 days
