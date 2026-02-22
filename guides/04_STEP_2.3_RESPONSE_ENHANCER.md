# Step 2.3: Implement Response Enhancer

**Phase:** 2 - Core Services Implementation  
**Goal:** Add context, recommendations, and formatting to Cortex responses  
**Status:** ⏳ Not Started

---

## Overview

The Response Enhancer takes raw Cortex service outputs and adds:
- Benchmark comparisons ("above/below industry average")
- Market context
- Actionable recommendations
- Formatted visualizations data

---

## Prerequisites

- [ ] Step 2.1: Cortex services implemented
- [ ] Step 2.2: Intent classifier functional
- [ ] Benchmark data loaded (Step 1.2)

---

## Implementation

### File: `orchestrator/services/response_enhancer.py`

```python
from pydantic import BaseModel
from services.cortex_complete import CortexComplete

class EnhancedResponse(BaseModel):
    original_data: dict
    benchmark_comparison: dict
    recommendations: list[str]
    insights: list[str]
    visualization_config: dict

class ResponseEnhancer:
    def __init__(self):
        self.complete = CortexComplete()
    
    def enhance(self, data: dict, intent: str, metric: str) -> EnhancedResponse:
        """Enhance response with context and recommendations"""
        
        # Add benchmark comparisons
        benchmark = self._add_benchmarks(data, metric)
        
        # Generate insights
        insights = self._generate_insights(data, intent, benchmark)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(intent, data, benchmark)
        
        # Prepare visualization config
        viz_config = self._format_for_visualization(data)
        
        return EnhancedResponse(
            original_data=data,
            benchmark_comparison=benchmark,
            recommendations=recommendations,
            insights=insights,
            visualization_config=viz_config
        )
    
    def _add_benchmarks(self, data: dict, metric: str) -> dict:
        """Compare against industry benchmarks"""
        # Query benchmark thresholds table
        # Return comparison dict
        pass
    
    def _generate_insights(self, data: dict, intent: str, benchmark: dict) -> list[str]:
        """Generate key insights using Cortex Complete"""
        pass
    
    def _generate_recommendations(self, intent: str, data: dict, benchmark: dict) -> list[str]:
        """Generate actionable recommendations"""
        if intent == "prescriptive":
            # Generate specific recommendations
            pass
        return []
    
    def _format_for_visualization(self, data: dict) -> dict:
        """Format data for charts/tables"""
        pass
```

---

## Enhancement Methods

### 1. Add Benchmarks

```python
def _add_benchmarks(self, data: dict, metric: str) -> dict:
    """
    Compare metric values against industry benchmarks
    """
    # Get benchmark from database
    benchmark = self._get_benchmark(metric)
    
    comparison = {
        "metric": metric,
        "actual_value": data.get(metric),
        "benchmark_value": benchmark.value,
        "difference_pct": self._calculate_diff_pct(data.get(metric), benchmark.value),
        "status": "above" if data.get(metric) > benchmark.value else "below",
        "interpretation": self._interpret_benchmark(data.get(metric), benchmark)
    }
    
    return comparison
```

### 2. Generate Recommendations

```python
def _generate_recommendations(self, intent: str, data: dict, benchmark: dict) -> list[str]:
    """
    Generate actionable recommendations based on intent
    """
    if intent == "prescriptive":
        prompt = f"""
        Based on this email marketing data:
        {data}
        
        Benchmark comparison:
        {benchmark}
        
        Generate 3-5 actionable recommendations to improve performance.
        Each recommendation should be specific and measurable.
        """
        
        recommendations_text = self.complete.complete(prompt)
        return self._parse_recommendations(recommendations_text)
    
    return []
```

### 3. Format for Visualization

```python
def _format_for_visualization(self, data: dict query_type: str) -> dict:
    """
    Format data for Streamlit/Plotly visualizations
    """
    if query_type == "time_series":
        return {
            "chart_type": "line",
            "x_axis": data.get("dates"),
            "y_axis": data.get("values"),
            "title": "Trend Over Time"
        }
    elif query_type == "comparison":
        return {
            "chart_type": "bar",
            "categories": data.get("categories"),
            "values": data.get("values"),
            "title": "Comparison by Category"
        }
    
    return {}
```

---

## Testing

```python
def test_response_enhancer():
    enhancer = ResponseEnhancer()
    
    # Sample data
    data = {
        "click_rate": 2.5,
        "market": "ES",
        "period": "2025-01"
    }
    
    # Enhance
    enhanced = enhancer.enhance(
        data=data,
        intent="descriptive",
        metric="click_rate"
    )
    
    assert enhanced.benchmark_comparison is not None
    assert len(enhanced.insights) > 0
    assert enhanced.visualization_config is not None
```

---

## Deliverables

- [ ] `orchestrator/services/response_enhancer.py` implemented
- [ ] Benchmark comparison functional
- [ ] Recommendation generation working
- [ ] Visualization config generator
- [ ] Tests passing
- [ ] Integration with API

---

## Success Criteria

✅ Response enhancer adding value to all query types  
✅ Benchmark comparisons accurate  
✅ Recommendations are actionable  
✅ Visualization configs work with frontend  

---

**Next:** [Step 3.1: API Routes](05_STEP_3.1_API_ROUTES.md)  
**Estimated Time:** 1-2 days
