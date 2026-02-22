# Step 2.2: Implement Intent Classifier

**Phase:** 2 - Core Services Implementation  
**Goal:** Build logic to classify queries into descriptive/diagnostic/predictive/prescriptive  
**Status:** ⏳ Not Started

---

## Overview

The Intent Classifier determines what type of analytical question the user is asking, which drives routing to appropriate Cortex services.

**Intent Types:**
1. **Descriptive** - "What was/is...?" (Cortex Analyst)
2. **Diagnostic** - "Why did...?" (Cortex ML + Analyst)
3. **Predictive** - "What will...?" (Cortex ML Forecasting)
4. **Prescriptive** - "How can I improve...?" (Complete + recommendations)

---

## Prerequisites

- [ ] Step 2.1: Cortex services implemented
- [ ] Cortex Complete wrapper functional
- [ ] Understanding of query patterns

---

## Implementation

### File: `orchestrator/services/intent_classifier.py`

**Tasks:**
- [ ] Create `IntentClassifier` class
- [ ] Implement `classify()` method
- [ ] Use Cortex Complete for classification
- [ ] Define intent patterns (keywords, question types)
- [ ] Return `IntentClassification` Pydantic model
- [ ] Add confidence scores

### Classification Logic

```python
from enum import Enum
from pydantic import BaseModel
from services.cortex_complete import CortexComplete

class IntentType(str, Enum):
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"

class IntentClassification(BaseModel):
    intent: IntentType
    confidence: float
    reasoning: str
    suggested_services: list[str]

class IntentClassifier:
    def __init__(self):
        self.complete = CortexComplete()
    
    def classify(self, query: str) -> IntentClassification:
        """
        Classify user query into intent type
        """
        prompt = f"""
        Classify this query into ONE of these intent types:
        - descriptive: Questions about current/past state (what, how many, show me)
        - diagnostic: Questions about root causes (why, what caused)
        - predictive: Questions about future outcomes (forecast, predict, will be)
        - prescriptive: Questions about recommendations (how can I, should I, optimize)
        
        Query: "{query}"
        
        Respond in JSON format:
        {{
            "intent": "descriptive|diagnostic|predictive|prescriptive",
            "confidence": 0.0-1.0,
            "reasoning": "brief explanation"
        }}
        """
        
        response = self.complete.complete(prompt, temperature=0.1)
        # Parse JSON response
        classification = self._parse_response(response)
        
        # Add suggested services based on intent
        classification.suggested_services = self._get_services(classification.intent)
        
        return classification
    
    def _get_services(self, intent: IntentType) -> list[str]:
        """Map intent to Cortex services"""
        service_map = {
            IntentType.DESCRIPTIVE: ["analyst", "complete"],
            IntentType.DIAGNOSTIC: ["analyst", "ml", "complete"],
            IntentType.PREDICTIVE: ["ml", "complete"],
            IntentType.PRESCRIPTIVE: ["complete", "analyst"]
        }
        return service_map.get(intent, ["complete"])
```

---

## Test Queries

### Descriptive Intent (>90% confidence)
```python
test_cases = [
    "What was click rate in Spain last month?",
    "Show me total emails sent last week",
    "How many opens did we get in Germany?",
    "What is the average bounce rate by market?"
]

for query in test_cases:
    result = classifier.classify(query)
    assert result.intent == IntentType.DESCRIPTIVE
    assert result.confidence > 0.9
```

### Diagnostic Intent
```python
test_cases = [
    "Why did click rate drop in Germany?",
    "What caused the spike in unsubscribes?",
    "Why is bounce rate higher in France?",
    "What's driving the low open rate?"
]

for query in test_cases:
    result = classifier.classify(query)
    assert result.intent == IntentType.DIAGNOSTIC
```

### Predictive Intent
```python
test_cases = [
    "What will click rate be next month?",
    "Forecast email volume for Q2",
    "Predict unsubscribe rate trend",
    "What's the expected open rate next week?"
]

for query in test_cases:
    result = classifier.classify(query)
    assert result.intent == IntentType.PREDICTIVE
```

### Prescriptive Intent
```python
test_cases = [
    "How can I improve open rates?",
    "What should I do about high bounce rate?",
    "Recommend optimizations for Spain market",
    "How do I increase engagement?"
]

for query in test_cases:
    result = classifier.classify(query)
    assert result.intent == IntentType.PRESCRIPTIVE
```

---

## Testing Framework

Create `tests/test_intent_classifier.py`:

```python
import pytest
from orchestrator.services.intent_classifier import (
    IntentClassifier,
    IntentType
)

@pytest.fixture
def classifier():
    return IntentClassifier()

def test_descriptive_intent(classifier):
    query = "What was click rate last month?"
    result = classifier.classify(query)
    assert result.intent == IntentType.DESCRIPTIVE
    assert result.confidence > 0.8
    assert "analyst" in result.suggested_services

def test_diagnostic_intent(classifier):
    query = "Why did click rate drop?"
    result = classifier.classify(query)
    assert result.intent == IntentType.DIAGNOSTIC
    assert "ml" in result.suggested_services

def test_predictive_intent(classifier):
    query = "What will click rate be next month?"
    result = classifier.classify(query)
    assert result.intent == IntentType.PREDICTIVE
    assert "ml" in result.suggested_services

def test_prescriptive_intent(classifier):
    query = "How can I improve open rates?"
    result = classifier.classify(query)
    assert result.intent == IntentType.PRESCRIPTIVE
    assert "complete" in result.suggested_services
```

Run tests:
```powershell
docker exec dia-orchestrator pytest tests/test_intent_classifier.py -v
```

---

## Accuracy Testing

Create test suite with 75+ verified queries:

```python
# tests/intent_test_suite.py

TEST_CASES = [
    # Descriptive (30 tests)
    {"query": "What was click rate in Spain?", "expected": "descriptive"},
    {"query": "Show me emails sent last week", "expected": "descriptive"},
    # ... 28 more
    
    # Diagnostic (20 tests)
    {"query": "Why did bounce rate increase?", "expected": "diagnostic"},
    # ... 19 more
    
    # Predictive (15 tests)
    {"query": "Forecast next month's opens", "expected": "predictive"},
    # ... 14 more
    
    # Prescriptive (10 tests)
    {"query": "How to optimize send time?", "expected": "prescriptive"},
    # ... 9 more
]

def measure_accuracy():
    classifier = IntentClassifier()
    correct = 0
    total = len(TEST_CASES)
    
    for case in TEST_CASES:
        result = classifier.classify(case["query"])
        if result.intent == case["expected"]:
            correct += 1
    
    accuracy = (correct / total) * 100
    print(f"Accuracy: {accuracy:.2f}%")
    return accuracy

# Target: >90% accuracy
```

---

## Integration with API

Update `orchestrator/main.py`:

```python
from services.intent_classifier import IntentClassifier

classifier = IntentClassifier()

@app.post("/api/v1/query")
async def query(request: QueryRequest):
    # Step 1: Classify intent
    intent = classifier.classify(request.query)
    
    # Step 2: Route to appropriate services
    if intent.intent == IntentType.DESCRIPTIVE:
        # Use Cortex Analyst
        response = analyst.send_message(request.query)
    elif intent.intent == IntentType.DIAGNOSTIC:
        # Use Cortex ML + Analyst
        response = ml.detect_anomalies(...)
    # ... etc
    
    return {
        "query": request.query,
        "intent": intent.dict(),
        "response": response
    }
```

---

## Deliverables

- [ ] `orchestrator/services/intent_classifier.py` implemented
- [ ] Pydantic models for `IntentClassification`
- [ ] Test suite with 75+ verified queries
- [ ] Accuracy measurement framework
- [ ] >90% classification accuracy achieved
- [ ] Integration with main API
- [ ] Documentation

---

## Success Criteria

✅ Intent classifier with >90% accuracy on test suite  
✅ Confidence scores included  
✅ Proper service routing recommendations  
✅ Integration tested with API  

---

## Troubleshooting

### Low Accuracy (<90%)
**Solutions:**
- Refine classification prompt
- Add more examples (few-shot learning)
- Tune temperature parameter
- Add keyword-based fallback

### Slow Response Time
**Solutions:**
- Cache common patterns
- Use smaller/faster model
- Implement timeout handling

---

## Next Steps

- [ ] Proceed to Step 2.3: Response Enhancer
- [ ] Test integration with Cortex services
- [ ] Collect real user queries to improve accuracy

---

**Related Documentation:**
- [Step 2.1: Cortex Services](02_STEP_2.1_CORTEX_SERVICES.md)
- [Step 2.3: Response Enhancer](04_STEP_2.3_RESPONSE_ENHANCER.md)
- [DIA v2 Implementation Plan](../DIA_V2_IMPLEMENTATION_PLAN.md)

---

**Status:** Ready to implement ✅  
**Estimated Time:** 1-2 days  
**Last Updated:** February 22, 2026
