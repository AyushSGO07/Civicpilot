# Phase 05: AI Eligibility Assessment Engine — Research & Architecture

## Objective

Design and implement a Gemini 2.5 Flash-powered reasoning engine that evaluates citizen profiles against official government scheme criteria, returning structured determinations (`Likely Eligible`, `Likely Ineligible`, `More Information Required`), itemized condition comparisons, official citations, and missing profile attribute alerts.

---

## 1. Requirements Mapping

| ID | Requirement | Implementation Strategy |
|---|---|---|
| **ELIG-01** | User can query scheme eligibility and receive automated assessment | `POST /api/services/{service_id}/evaluate` runs multimodal/reasoning evaluation on citizen profile against scheme criteria. |
| **ELIG-02** | User receives determination: `Likely Eligible`, `Likely Ineligible`, or `More Information Required` | Strict Pydantic enum `EligibilityStatus` returned as the top-level classification. |
| **ELIG-03** | User sees itemized breakdown comparing profile data against official conditions | Structured list of `CriterionEvaluation` items comparing scheme rule vs citizen value with evaluation status (`Satisfied`, `Not Satisfied`, `Missing Info`). |
| **ELIG-04** | User is notified of missing profile fields required to complete evaluation | Explicit list `missing_fields` identifying unpopulated citizen attributes with direct remediation guidance. |
| **ELIG-05** | User sees citations to official scheme guidelines for every evaluation | Every criterion and summary includes specific citations to authoritative guidelines (e.g., *NSP PM-USP Guidelines Section 3.2* or *PM-KISAN Operational Guidelines Rev. 2024*). |

---

## 2. Model & SDK Integration

### SDK Choice
- SDK: `google-genai` (installed: `0.3.0`, officially supported).
- Model: `gemini-2.5-flash`.
- Output Mode: `response_mime_type="application/json"` with `response_schema=EligibilityEvaluationResponse`.

### Prompt Strategy
The prompt feeds:
1. Complete official scheme details (title, department, eligibility summary, structured criteria rules, official URLs).
2. Citizen profile attributes (personal, address/domicile, education, income, social category, disability status, etc.).
3. Strict instructions:
   - Zero hallucination.
   - If an essential criterion cannot be determined from profile data, mark it `Missing Info` and designate the overall status as `More Information Required`.
   - If any disqualifying criterion is explicitly violated (e.g., annual income ₹8,00,000 when max limit is ₹4,50,000), mark overall status as `Likely Ineligible`.
   - If all criteria are satisfied, mark overall status as `Likely Eligible`.
   - Provide genuine official policy/guideline citations for each evaluated criterion.

### Offline & CI Resilience Fallback
When `GEMINI_API_KEY` is not present (e.g., in CI pipelines or offline testing), the service falls back to a deterministic rule-based evaluation engine:
- Checks `annual_income <= max_annual_income`.
- Checks `education_level` compatibility.
- Checks `occupation` match.
- Checks `state` domicile compatibility.
- Checks `social_category` compatibility.
- Detects `None` values for required attributes and accurately outputs `More Information Required` with `missing_fields`.
- Attaches verified official citations.

---

## 3. Data Schemas

### `CriterionEvaluation`
```python
class CriterionEvaluation(BaseModel):
    criterion_name: str
    condition: str
    citizen_value: Optional[str] = None
    status: Literal["Satisfied", "Not Satisfied", "Missing Info"]
    reasoning: str
    official_citation: str
```

### `EligibilityEvaluationResponse`
```python
class EligibilityEvaluationResponse(BaseModel):
    service_id: str
    service_name: str
    status: Literal["Likely Eligible", "Likely Ineligible", "More Information Required"]
    summary: str
    confidence_score: float = Field(0.95, ge=0.0, le=1.0)
    criteria: List[CriterionEvaluation]
    missing_fields: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    disclaimer: str = Field(
        default="This automated evaluation is an advisory assessment based on official published guidelines and the information in your profile. Final eligibility is determined exclusively by the competent government authority upon application submission."
    )
```

---

## 4. Frontend Experience (`/services/[serviceId]`)

- **MakeMyTrip Aesthetic**:
  - Breadcrumb: `Services > {Service Name}`.
  - Header: Ministry badge, state badge, official portal link (`target="_blank" rel="noopener noreferrer"`).
  - Assessment Hero Card:
    - Status badge with high contrast:
      - `Likely Eligible`: Emerald green (`bg-emerald-50 text-emerald-700 border-emerald-200`)
      - `Likely Ineligible`: Rose red (`bg-rose-50 text-rose-700 border-rose-200`)
      - `More Information Required`: Amber (`bg-amber-50 text-amber-700 border-amber-200`)
    - Summary narrative.
    - Missing fields notification banner with 1-click navigation to `/profile`.
  - Criteria Comparison Matrix:
    - Condition vs Your Profile vs Status vs Citation.
  - Required Documents Checklist:
    - Shows documents needed with vault upload shortcuts.
  - Action Footer:
    - "Apply with CivicPilot AI" (prepares workflow for Phase 6-9).
    - "Apply on Official Portal" with external link.
