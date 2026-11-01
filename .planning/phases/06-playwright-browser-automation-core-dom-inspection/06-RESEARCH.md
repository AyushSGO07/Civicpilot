# Phase 06: Playwright Browser Automation Core & DOM Inspection — Research & Architecture

## Objective

Design and implement an asynchronous Playwright Chromium engine and a semantic DOM inspection system that extracts accessible interactive element trees from government portals while strictly preventing zombie processes.

---

## 1. Requirements Mapping

| ID | Requirement | Implementation Strategy |
|---|---|---|
| **AGENT-01** | Backend launches asynchronous Playwright Chromium instance targeting official portal URL | `BrowserSessionManager` launches `playwright.async_api` Chromium with desktop viewport (`1280x800`), standard user agent, and isolated contexts per session. |
| **AGENT-02** | Agent inspects portal webpage structure and extracts sanitized semantic DOM element tree | `DOMInspector` extracts interactive elements (`<input>`, `<select>`, `<button>`, `<textarea>`, `<form>`), associating labels, placeholders, aria attributes, and Playwright locators. |
| **AGENT-07** | Agent terminates browser processes cleanly on completion, error, or session abort without zombie processes | Central session registry with async context managers, explicit termination methods, and FastAPI lifespan shutdown hooks. |

---

## 2. Browser Manager Architecture

### Session Isolation & Context Pooling
```
[FastAPI Application]
        │
        ▼
[BrowserSessionManager (Singleton)]
        │  launches & maintains
        ▼
[Chromium Browser Instance]
   ├── [Session Context A (UUID)] ──> [Page A] (e.g. scholarships.gov.in)
   ├── [Session Context B (UUID)] ──> [Page B] (e.g. pmkisan.gov.in)
   └── [Session Context C (UUID)] ──> [Page C]
```

### Key Browser Parameters
- **Viewport**: 1280x800 desktop resolution.
- **User Agent**: Realistic Windows Chromium desktop user agent.
- **Certificate Handling**: `ignore_https_errors=True` (crucial for government portals with non-standard SSL certificate chains).
- **Auto-wait & Navigation Timeout**: Default 30s with `domcontentloaded` wait strategy (preventing infinite hang on slow tracking scripts).
- **Headless Mode**: Defaults to `headless=True`, configurable via `BROWSER_HEADLESS=false` for visual development debugging.

---

## 3. Semantic DOM Extraction Algorithm

Government portals regularly deliver 50,000+ characters of HTML with redundant inline styles, external analytics, and deep nested divs. Feeding raw HTML into LLM contexts wastes tokens and introduces noise.

### Extraction Pipeline
1. **Interactive Element Filtering**: Query all form-bearing interactive nodes:
   - `input[type="text|email|tel|number|date|radio|checkbox|file|password"]`
   - `select` (extracting child `<option>` values and display text)
   - `textarea`
   - `button` and `input[type="submit|button"]`
   - Form containers (`<form>`, `<fieldset>`)
2. **Label Association**:
   - Explicit `<label for="elementId">` text.
   - Enclosing parent `<label>` text.
   - `aria-label` or `aria-labelledby`.
   - `placeholder` attribute.
   - Preceding table header / table cell text when inside tabular forms.
3. **Visibility & Interactivity Filter**:
   - Check `element.is_visible()`.
   - Filter out hidden inputs (`type="hidden"`) unless required for CSRF tokens.
4. **Accessible Locator Synthesis**:
   - Generate robust Playwright-compatible locators:
     - `page.locator("#id")` if id is clean and unique.
     - `page.get_by_role("button", name="...")` if role and name exist.
     - `page.get_by_label("...")` if label is unambiguous.
     - `page.locator("input[name='...']")` as fallback.

---

## 4. Schemas (`backend/app/models/agent.py`)

```python
class DOMElementNode(BaseModel):
    tag: str
    element_id: Optional[str] = None
    name: Optional[str] = None
    element_type: Optional[str] = None
    label: Optional[str] = None
    placeholder: Optional[str] = None
    value: Optional[str] = None
    is_required: bool = False
    is_disabled: bool = False
    options: List[str] = Field(default_factory=list)
    suggested_locator: str

class SanitizedDOMTree(BaseModel):
    url: str
    title: str
    forms_count: int
    interactive_elements_count: int
    elements: List[DOMElementNode]
    extracted_at: datetime
```

---

## 5. Zombie Prevention & Process Lifecycle (AGENT-07)

1. **Explicit Session Close**: `await session_manager.close_session(session_id)` closes the specific page and context.
2. **Global Application Lifespan**: In FastAPI lifespan, `yield` guarantees that on server termination, `await session_manager.shutdown()` closes all open contexts and the browser process.
3. **Context Manager Pattern**: `async with session_manager.session(session_id) as page:` automatically terminates resources on block exit or unhandled exceptions.
4. **Stale Session Sweeper**: Background periodic cleanup terminating sessions inactive for > 15 minutes.
