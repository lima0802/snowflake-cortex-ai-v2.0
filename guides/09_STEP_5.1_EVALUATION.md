# Step 5.1: Implement Evaluation Framework

**Phase:** 5 - Testing & Refinement  
**Goal:** Three-tier evaluation system for accuracy and performance  
**Status:** ⏳ Not Started

---

## Overview

Build comprehensive evaluation framework with:
- **Tier 1:** Deterministic tests (exact matches)
- **Tier 2:** Heuristic evaluation (pattern matching)
- **Tier 3:** LLM-as-judge (semantic evaluation)

---

## Prerequisites

- [ ] Step 2.1-4.2: All core functionality implemented
- [ ] Test dataset prepared (30+ query-answer pairs)

---

## Evaluation Architecture

### File: `tests/evaluation/framework.py`

```python
from pydantic import BaseModel
from datetime import datetime
import json

class TestCase(BaseModel):
    query: str
    expected_intent: str
    expected_results: dict
    evaluation_tier: int  # 1, 2, or 3

class EvaluationResult(BaseModel):
    test_id: str
    passed: bool
    score: float  # 0.0 - 1.0
    actual_response: dict
    failure_reason: str | None
    execution_time_ms: float

class EvaluationFramework:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.test_cases = []
        self.results = []
    
    def load_test_cases(self, filepath: str):
        """Load test cases from JSON file"""
        with open(filepath) as f:
            data = json.load(f)
            self.test_cases = [TestCase(**tc) for tc in data]
    
    def run_evaluation(self) -> dict:
        """Run full evaluation suite"""
        print(f"Running {len(self.test_cases)} test cases...")
        
        for i, test_case in enumerate(self.test_cases):
            print(f"[{i+1}/{len(self.test_cases)}] Testing: {test_case.query[:50]}...")
            
            result = self.evaluate_single(test_case)
            self.results.append(result)
        
        return self.generate_report()
    
    def evaluate_single(self, test_case: TestCase) -> EvaluationResult:
        """Evaluate single test case"""
        start_time = time.time()
        
        # Query API
        response = requests.post(
            f"{self.api_url}/query",
            json={"query": test_case.query}
        ).json()
        
        execution_time = (time.time() - start_time) * 1000
        
        # Evaluate based on tier
        if test_case.evaluation_tier == 1:
            passed, score, reason = self.tier1_deterministic(response, test_case)
        elif test_case.evaluation_tier == 2:
            passed, score, reason = self.tier2_heuristic(response, test_case)
        else:
            passed, score, reason = self.tier3_llm_judge(response, test_case)
        
        return EvaluationResult(
            test_id=f"test_{len(self.results)}",
            passed=passed,
            score=score,
            actual_response=response,
            failure_reason=reason,
            execution_time_ms=execution_time
        )
    
    def tier1_deterministic(self, response: dict, test_case: TestCase) -> tuple[bool, float, str]:
        """Exact match evaluation"""
        # Check intent
        actual_intent = response.get("intent", {}).get("intent")
        if actual_intent != test_case.expected_intent:
            return False, 0.0, f"Intent mismatch: expected {test_case.expected_intent}, got {actual_intent}"
        
        # Check key results
        expected = test_case.expected_results
        actual = response.get("results", {})
        
        for key, expected_value in expected.items():
            if key not in actual:
                return False, 0.0, f"Missing key: {key}"
            if actual[key] != expected_value:
                return False, 0.0, f"Value mismatch for {key}: expected {expected_value}, got {actual[key]}"
        
        return True, 1.0, None
    
    def tier2_heuristic(self, response: dict, test_case: TestCase) -> tuple[bool, float, str]:
        """Pattern matching evaluation"""
        score = 0.0
        reasons = []
        
        # Intent check (40% weight)
        actual_intent = response.get("intent", {}).get("intent")
        if actual_intent == test_case.expected_intent:
            score += 0.4
        else:
            reasons.append(f"Intent mismatch")
        
        # Result structure check (30% weight)
        expected_keys = set(test_case.expected_results.keys())
        actual_keys = set(response.get("results", {}).keys())
        key_overlap = len(expected_keys & actual_keys) / len(expected_keys) if expected_keys else 0
        score += 0.3 * key_overlap
        if key_overlap < 1.0:
            reasons.append(f"Missing keys: {expected_keys - actual_keys}")
        
        # Enhancement check (30% weight)
        enhanced = response.get("enhanced_response", {})
        has_insights = len(enhanced.get("insights", [])) > 0
        has_recommendations = len(enhanced.get("recommendations", [])) > 0
        enhancement_score = (has_insights + has_recommendations) / 2
        score += 0.3 * enhancement_score
        
        passed = score >= 0.7
        reason = "; ".join(reasons) if reasons else None
        
        return passed, score, reason
    
    def tier3_llm_judge(self, response: dict, test_case: TestCase) -> tuple[bool, float, str]:
        """LLM-based semantic evaluation"""
        from services.cortex_complete import CortexComplete
        
        complete = CortexComplete()
        
        prompt = f"""
        Evaluate the quality of this AI assistant response.
        
        User Query: {test_case.query}
        Expected Intent: {test_case.expected_intent}
        Expected Results: {test_case.expected_results}
        
        Actual Response: {response}
        
        Rate the response on a scale of 0.0 to 1.0 based on:
        1. Intent accuracy (30%)
        2. Result correctness (40%)
        3. Insight quality (30%)
        
        Respond ONLY with a JSON object:
        {{
            "score": <float between 0 and 1>,
            "passed": <true if score >= 0.7>,
            "reasoning": "<brief explanation>"
        }}
        """
        
        judgment = complete.complete(prompt)
        result = json.loads(judgment)
        
        return result["passed"], result["score"], result["reasoning"]
    
    def generate_report(self) -> dict:
        """Generate evaluation report"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        avg_score = sum(r.score for r in self.results) / total
        avg_time = sum(r.execution_time_ms for r in self.results) / total
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total,
            "avg_score": avg_score,
            "avg_execution_time_ms": avg_time,
            "failures": [
                {
                    "query": self.test_cases[i].query,
                    "reason": r.failure_reason,
                    "score": r.score
                }
                for i, r in enumerate(self.results) if not r.passed
            ]
        }
```

---

## Test Dataset

### File: `tests/evaluation/test_cases.json`

```json
[
  {
    "query": "What was the click rate last month?",
    "expected_intent": "descriptive",
    "expected_results": {
      "metric": "click_rate",
      "period": "last_month"
    },
    "evaluation_tier": 1
  },
  {
    "query": "Compare ES and SE markets",
    "expected_intent": "descriptive",
    "expected_results": {
      "markets": ["ES", "SE"],
      "comparison": true
    },
    "evaluation_tier": 2
  },
  {
    "query": "Why did open rate drop in January?",
    "expected_intent": "diagnostic",
    "expected_results": {
      "metric": "open_rate",
      "analysis_type": "root_cause"
    },
    "evaluation_tier": 3
  }
]
```

---

## Running Evaluations

### Command Line

```bash
# Run full evaluation
python -m tests.evaluation.run_evaluation

# Run specific tier
python -m tests.evaluation.run_evaluation --tier 1

# Output report
python -m tests.evaluation.run_evaluation --output results.json
```

### API Endpoint

Add to `orchestrator/api/routes/admin.py`:

```python
@router.post("/evaluate")
async def run_evaluation():
    """Run evaluation suite"""
    framework = EvaluationFramework(api_url="http://localhost:8000/api/v1")
    framework.load_test_cases("tests/evaluation/test_cases.json")
    report = framework.run_evaluation()
    return report
```

---

## Continuous Evaluation

Set up scheduled evaluations:

```yaml
# .github/workflows/evaluation.yml
name: Weekly Evaluation

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Evaluation
        run: |
          docker-compose up -d
          python -m tests.evaluation.run_evaluation
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: evaluation-report
          path: results.json
```

---

## Deliverables

- [ ] Evaluation framework implemented
- [ ] All three tiers functional
- [ ] Test dataset created (30+ cases)
- [ ] Report generation working
- [ ] API endpoint for evaluation
- [ ] CI/CD integration (optional)

---

## Success Criteria

✅ Pass rate > 90% on tier 1 tests  
✅ Pass rate > 80% on tier 2 tests  
✅ Pass rate > 70% on tier 3 tests  
✅ Avg execution time < 2000ms  

---

**Next:** [Step 6.1: Production Deployment](10_STEP_6.1_DEPLOYMENT.md)  
**Estimated Time:** 2-3 days
