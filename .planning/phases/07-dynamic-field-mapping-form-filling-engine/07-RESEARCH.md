# Phase 07: Dynamic Field Mapping & Form Filling Engine — Research & Architecture

## Objective

Design and implement a Gemini 2.5 Flash-driven dynamic field mapping system and an asynchronous Playwright form action executor that autonomously populates text inputs, dropdowns, checkboxes, and Document Vault file attachments on government portal pages without hardcoded selectors.

---

## 1. Requirements Mapping

| ID | Requirement | Implementation Strategy |
|---|---|---|
| **AGENT-03** | Agent dynamically maps citizen profile fields to portal input elements using Gemini structured mapping | `DynamicFieldMapper` takes `SanitizedDOMTree` and `CitizenProfileBase`, prompting `gemini-2.5-flash` with `response_schema=FormFillPlan` to resolve semantic mappings. |
| **AGENT-04** | Agent autonomously populates text fields, radio buttons, dropdowns, and checkboxes on the portal | `FormActionExecutor` iterates through actions in `FormFillPlan`, executing `fill()`, `select_option()`, `set_checked()`, and `check()` on Playwright locators. |
| **AGENT-05** | Agent attaches required documents from citizen's vault into portal file upload fields | When `DOMElementNode.element_type == "file"`, mapper links document from vault, and executor invokes `page.locator().set_input_files(file_path)`. |

---

## 2. Dynamic Mapping Pipeline

```
[SanitizedDOMTree] (Phase 6)  +  [CitizenProfile] (Phase 2)  +  [Vault Documents] (Phase 3)
                                        │
                                        ▼
                  [DynamicFieldMapper (Gemini 2.5 Flash)]
               (Deterministic Semantic Fallback for Offline/CI)
                                        │
                                        ▼
                                 [FormFillPlan]
             - fill_text: #applicantName -> "Aarav Sharma"
             - select_option: #stateSelect -> "MH"
             - check_box: #consentCheck -> True
             - upload_file: #aadhaarUpload -> "storage/vault/aadhaar.pdf"
                                        │
                                        ▼
                             [FormActionExecutor]
               (Sequentially executes on Playwright Page)
                                        │
                                        ▼
                            [FormExecutionResult]
             - Post-fill verification screenshot (Base64)
             - Itemized action audit log (status, duration, error)
```

---

## 3. Schemas (`backend/app/models/form_filling.py`)

### `FieldActionType`
```python
FieldActionType = Literal[
    "fill_text",
    "select_option",
    "check_box",
    "select_radio",
    "upload_file",
    "click_element",
]
```

### `FieldAction`
```python
class FieldAction(BaseModel):
    action_type: FieldActionType
    target_locator: str
    element_name: Optional[str] = None
    field_label: Optional[str] = None
    value: str
    source_attribute: Optional[str] = None
    confidence: float = 0.95
    reasoning: str
```

### `FormFillPlan`
```python
class FormFillPlan(BaseModel):
    actions: List[FieldAction]
    unmapped_elements: List[str] = Field(default_factory=list)
    missing_mandatory_fields: List[str] = Field(default_factory=list)
    generated_at: datetime
```

### `FormExecutionResult`
```python
class ActionExecutionAudit(BaseModel):
    action_index: int
    action_type: FieldActionType
    target_locator: str
    field_label: Optional[str] = None
    value: str
    status: Literal["success", "failed", "skipped"]
    duration_ms: int
    error_message: Optional[str] = None

class FormExecutionResult(BaseModel):
    session_id: str
    total_actions: int
    successful_actions: int
    failed_actions: int
    action_results: List[ActionExecutionAudit]
    screenshot_base64: Optional[str] = None
    completed_at: datetime
```

---

## 4. Execution & Error Handling Strategy

1. **Typing & Interaction Cadence**: Add a subtle 25ms delay per keystroke to mirror natural citizen interaction and ensure portal dynamic JavaScript validations (e.g. `onchange`, `input` event listeners) trigger properly.
2. **Locator Fallback**: If the primary `suggested_locator` fails, fallback to:
   - `input[name="..."]`
   - `getByLabel("...")`
   - `getByRole(...)`
3. **Fault Tolerance**: A failure on a single non-mandatory field logs an error in `ActionExecutionAudit` with `status="failed"` but does not abort the remaining fields in the plan.
4. **Vault File Resolution**: Matches document types (`Aadhaar Card`, `Income Certificate`, `Marksheet`, `Caste Certificate`) to available files in `storage/vault/` and uploads them safely.
