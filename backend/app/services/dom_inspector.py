"""Semantic DOM Inspection Engine that prunes bloated HTML into an accessible interactive element tree."""

import re
from datetime import datetime, timezone
from typing import List, Optional
from bs4 import BeautifulSoup
from playwright.async_api import Page

from app.models.agent import (
    DOMElementNode,
    SanitizedDOMTree,
)


class DOMInspector:
    """Extracts, sanitizes, and normalizes interactive web elements from Playwright pages."""

    @classmethod
    async def inspect_page(cls, page: Page) -> SanitizedDOMTree:
        """Inspect active page, prune non-actionable markup, and produce accessible element tree (AGENT-02)."""
        url = page.url
        title = await page.title()

        # Extract current HTML snapshot from Playwright page
        html_content = await page.content()
        soup = BeautifulSoup(html_content, "html.parser")

        # Step 1: Remove noisy non-interactive tags
        for tag in soup(["script", "style", "noscript", "svg", "path", "meta", "link", "iframe"]):
            tag.decompose()

        forms = soup.find_all("form")
        forms_count = len(forms)

        elements: List[DOMElementNode] = []

        # Step 2: Query actionable elements (inputs, selects, textareas, buttons)
        candidates = soup.find_all(["input", "select", "textarea", "button"])

        for el in candidates:
            tag_name = el.name.lower()
            element_id = el.get("id")
            name = el.get("name")
            element_type = el.get("type", "text").lower() if tag_name == "input" else tag_name
            placeholder = el.get("placeholder")
            is_required = el.has_attr("required") or el.get("aria-required") == "true"
            is_disabled = el.has_attr("disabled") or el.get("aria-disabled") == "true"
            value = el.get("value")

            # Ignore hidden inputs unless name indicates meaningful form data (ignore analytics tokens)
            if element_type == "hidden":
                continue

            # Check style display:none or visibility:hidden in tag style
            style_attr = el.get("style", "").lower()
            if "display:none" in style_attr or "visibility:hidden" in style_attr:
                continue

            # Step 3: Resolve associated human-readable label
            label_text = cls._resolve_label(el, soup)

            # Step 4: Extract options for select dropdowns
            options: List[str] = []
            if tag_name == "select":
                for opt in el.find_all("option"):
                    opt_val = opt.get("value", "").strip()
                    opt_text = opt.get_text(strip=True)
                    if opt_text:
                        options.append(f"{opt_val}: {opt_text}" if opt_val else opt_text)

            # Step 5: Synthesize Playwright locator
            locator = cls._synthesize_locator(tag_name, element_id, name, element_type, label_text)

            node = DOMElementNode(
                tag=tag_name,
                element_id=element_id,
                name=name,
                element_type=element_type,
                label=label_text,
                placeholder=placeholder,
                value=value,
                is_required=is_required,
                is_disabled=is_disabled,
                options=options,
                suggested_locator=locator,
            )
            elements.append(node)

        return SanitizedDOMTree(
            url=url,
            title=title,
            forms_count=forms_count,
            interactive_elements_count=len(elements),
            elements=elements,
            extracted_at=datetime.now(timezone.utc),
        )

    @classmethod
    def _resolve_label(cls, el, soup: BeautifulSoup) -> Optional[str]:
        """Determine the most accurate semantic label for an interactive element."""
        # 1. aria-label attribute
        if el.get("aria-label"):
            return el.get("aria-label").strip()

        # 2. aria-labelledby attribute
        if el.get("aria-labelledby"):
            target_id = el.get("aria-labelledby")
            target = soup.find(id=target_id)
            if target:
                text = target.get_text(strip=True)
                if text:
                    return text

        # 3. Explicit <label for="id">
        element_id = el.get("id")
        if element_id:
            label_el = soup.find("label", attrs={"for": element_id})
            if label_el:
                text = label_el.get_text(strip=True)
                if text:
                    return text

        # 4. Enclosing parent <label>
        parent_label = el.find_parent("label")
        if parent_label:
            # Get text excluding the element's own text
            text = parent_label.get_text(strip=True)
            if text:
                return text

        # 5. Button or submit value / text
        if el.name in ["button", "input"] and el.get("type") in ["submit", "button", "reset"]:
            text = el.get_text(strip=True) or el.get("value")
            if text:
                return text.strip()

        # 6. Placeholder fallback
        if el.get("placeholder"):
            return el.get("placeholder").strip()

        # 7. Preceding sibling label or text
        prev = el.find_previous_sibling(["label", "span", "p"])
        if prev and prev.get_text(strip=True):
            cleaned = prev.get_text(strip=True)
            if len(cleaned) < 50:
                return cleaned

        return None

    @classmethod
    def _synthesize_locator(
        cls,
        tag: str,
        element_id: Optional[str],
        name: Optional[str],
        element_type: Optional[str],
        label: Optional[str],
    ) -> str:
        """Generate high-reliability Playwright-compatible locator string."""
        # 1. Unique ID selector (preferred if alphanumeric)
        if element_id and re.match(r"^[a-zA-Z0-9_\-]+$", element_id):
            return f"#{element_id}"

        # 2. Accessible role with name if button or submit
        if tag == "button" or element_type in ["submit", "button"]:
            if label:
                return f'getByRole("button", name="{label}")'
            return 'getByRole("button")'

        # 3. Label locator if label is clear
        if label and len(label) < 60:
            return f'getByLabel("{label}")'

        # 4. Input name locator
        if name:
            return f'{tag}[name="{name}"]'

        # 5. Fallback generic selector
        if element_id:
            return f'[id="{element_id}"]'

        return tag
