"""Dynamic Field Mapping Service powered by Gemini 2.5 Flash with deterministic fallback."""

import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from app.models.agent import SanitizedDOMTree, DOMElementNode
from app.models.profile import CitizenProfileBase
from app.models.form_filling import (
    FieldAction,
    FormFillPlan,
    FieldActionType,
)


def _match_select_option(options: List[str], target_value: str) -> Optional[str]:
    """Find the best matching option value or label from select dropdown options."""
    if not options or not target_value:
        return None

    target_lower = target_value.lower().strip()

    # Exact match or colon-separated "VALUE: LABEL"
    for opt in options:
        opt_clean = opt.strip()
        if ":" in opt_clean:
            parts = opt_clean.split(":", 1)
            val, label = parts[0].strip(), parts[1].strip()
            if target_lower == label.lower() or target_lower == val.lower():
                return val or label
            if target_lower in label.lower():
                return val or label
        else:
            if target_lower == opt_clean.lower() or target_lower in opt_clean.lower():
                return opt_clean

    return None


def generate_fill_plan_fallback(
    dom_tree: SanitizedDOMTree,
    profile: CitizenProfileBase,
    vault_documents: Optional[List[Dict[str, Any]]] = None,
) -> FormFillPlan:
    """Deterministic rule-based field mapper for offline development and CI test suites."""
    actions: List[FieldAction] = []
    unmapped: List[str] = []
    missing_mandatory: List[str] = []

    docs = vault_documents or []

    for el in dom_tree.elements:
        label_text = (el.label or "").lower()
        name_text = (el.name or "").lower()
        id_text = (el.element_id or "").lower()
        combined = f"{label_text} {name_text} {id_text}"

        mapped = False

        # 1. File Upload Fields (AGENT-05)
        if el.element_type == "file" or el.tag == "file":
            # Match against documents in citizen vault
            matched_doc = None
            if "aadhaar" in combined:
                matched_doc = next(
                    (d for d in docs if "aadhaar" in d.get("document_type", "").lower() or "aadhaar" in d.get("file_name", "").lower()),
                    None,
                )
            elif "income" in combined:
                matched_doc = next(
                    (d for d in docs if "income" in d.get("document_type", "").lower() or "income" in d.get("file_name", "").lower()),
                    None,
                )
            elif "caste" in combined or "category" in combined:
                matched_doc = next(
                    (d for d in docs if "caste" in d.get("document_type", "").lower() or "caste" in d.get("file_name", "").lower()),
                    None,
                )
            elif "marksheet" in combined or "academic" in combined or "education" in combined or "10th" in combined or "12th" in combined:
                matched_doc = next(
                    (d for d in docs if "marksheet" in d.get("document_type", "").lower() or "academic" in d.get("document_type", "").lower()),
                    None,
                )
            elif "land" in combined or "khatauni" in combined or "jamabandi" in combined:
                matched_doc = next(
                    (d for d in docs if "land" in d.get("document_type", "").lower() or "khatauni" in d.get("file_name", "").lower()),
                    None,
                )

            # Fallback to any document if field is mandatory and no exact name match
            if not matched_doc and docs and el.is_required:
                matched_doc = docs[0]

            if matched_doc:
                file_target = matched_doc.get("file_path") or matched_doc.get("file_name") or matched_doc.get("id", "")
                actions.append(
                    FieldAction(
                        action_type="upload_file",
                        target_locator=el.suggested_locator,
                        element_name=el.name or el.element_id,
                        field_label=el.label,
                        value=str(file_target),
                        source_attribute=matched_doc.get("document_type", "Document Vault"),
                        confidence=0.96,
                        reasoning=f"Matched vault document '{matched_doc.get('document_type')}' to file upload input.",
                    )
                )
                mapped = True
            else:
                if el.is_required:
                    missing_mandatory.append(el.label or el.name or "File Upload")
                unmapped.append(el.label or el.name or "File Upload")
            continue

        # 2. Checkboxes (Consents & Declarations)
        if el.element_type == "checkbox":
            if any(term in combined for term in ["consent", "declare", "agree", "undertake", "confirm", "landholder"]):
                actions.append(
                    FieldAction(
                        action_type="check_box",
                        target_locator=el.suggested_locator,
                        element_name=el.name or el.element_id,
                        field_label=el.label,
                        value="true",
                        source_attribute="citizen_consent",
                        confidence=0.95,
                        reasoning="Checked statutory citizen declaration / consent checkbox.",
                    )
                )
                mapped = True
            continue

        # 3. Full Name
        if any(term in combined for term in ["name", "applicant", "candidate", "farmer", "student"]) and "institution" not in combined:
            if profile.full_name:
                actions.append(
                    FieldAction(
                        action_type="fill_text",
                        target_locator=el.suggested_locator,
                        element_name=el.name or el.element_id,
                        field_label=el.label,
                        value=profile.full_name,
                        source_attribute="full_name",
                        confidence=0.98,
                        reasoning=f"Mapped citizen full name '{profile.full_name}' to applicant name field.",
                    )
                )
                mapped = True

        # 4. Date of Birth
        elif any(term in combined for term in ["dob", "birth", "date of birth"]):
            if profile.date_of_birth:
                dob_str = profile.date_of_birth.strftime("%Y-%m-%d")
                actions.append(
                    FieldAction(
                        action_type="fill_text",
                        target_locator=el.suggested_locator,
                        element_name=el.name or el.element_id,
                        field_label=el.label,
                        value=dob_str,
                        source_attribute="date_of_birth",
                        confidence=0.98,
                        reasoning=f"Mapped date of birth '{dob_str}'.",
                    )
                )
                mapped = True

        # 5. Gender
        elif "gender" in combined or "sex" in combined:
            if profile.gender:
                if el.tag == "select":
                    opt_val = _match_select_option(el.options, profile.gender) or profile.gender
                    actions.append(
                        FieldAction(
                            action_type="select_option",
                            target_locator=el.suggested_locator,
                            element_name=el.name or el.element_id,
                            field_label=el.label,
                            value=opt_val,
                            source_attribute="gender",
                            confidence=0.95,
                            reasoning=f"Selected gender option '{opt_val}'.",
                        )
                    )
                else:
                    actions.append(
                        FieldAction(
                            action_type="fill_text",
                            target_locator=el.suggested_locator,
                            element_name=el.name or el.element_id,
                            field_label=el.label,
                            value=profile.gender,
                            source_attribute="gender",
                            confidence=0.95,
                            reasoning=f"Filled gender '{profile.gender}'.",
                        )
                    )
                mapped = True

        # 6. Mobile Contact
        elif any(term in combined for term in ["mobile", "phone", "contact"]) and "email" not in combined:
            if profile.contact_number:
                actions.append(
                    FieldAction(
                        action_type="fill_text",
                        target_locator=el.suggested_locator,
                        element_name=el.name or el.element_id,
                        field_label=el.label,
                        value=profile.contact_number,
                        source_attribute="contact_number",
                        confidence=0.97,
                        reasoning=f"Mapped 10-digit mobile number '{profile.contact_number}'.",
                    )
                )
                mapped = True

        # 7. State Domicile
        elif "state" in combined or "domicile" in combined:
            if profile.state:
                if el.tag == "select":
                    opt_val = _match_select_option(el.options, profile.state) or profile.state
                    actions.append(
                        FieldAction(
                            action_type="select_option",
                            target_locator=el.suggested_locator,
                            element_name=el.name or el.element_id,
                            field_label=el.label,
                            value=opt_val,
                            source_attribute="state",
                            confidence=0.95,
                            reasoning=f"Selected state option '{opt_val}' from dropdown.",
                        )
                    )
                else:
                    actions.append(
                        FieldAction(
                            action_type="fill_text",
                            target_locator=el.suggested_locator,
                            element_name=el.name or el.element_id,
                            field_label=el.label,
                            value=profile.state,
                            source_attribute="state",
                            confidence=0.95,
                            reasoning=f"Filled domicile state '{profile.state}'.",
                        )
                    )
                mapped = True

        # 8. District
        elif "district" in combined or "city" in combined:
            if profile.district:
                actions.append(
                    FieldAction(
                        action_type="fill_text",
                        target_locator=el.suggested_locator,
                        element_name=el.name or el.element_id,
                        field_label=el.label,
                        value=profile.district,
                        source_attribute="district",
                        confidence=0.95,
                        reasoning=f"Filled district '{profile.district}'.",
                    )
                )
                mapped = True

        # 9. PIN Code
        elif any(term in combined for term in ["pin", "pincode", "postal", "zip"]):
            if profile.pincode:
                actions.append(
                    FieldAction(
                        action_type="fill_text",
                        target_locator=el.suggested_locator,
                        element_name=el.name or el.element_id,
                        field_label=el.label,
                        value=profile.pincode,
                        source_attribute="pincode",
                        confidence=0.98,
                        reasoning=f"Filled postal PIN code '{profile.pincode}'.",
                    )
                )
                mapped = True

        # 10. Annual Income
        elif "income" in combined or "salary" in combined:
            if profile.annual_income is not None:
                inc_str = str(int(profile.annual_income))
                actions.append(
                    FieldAction(
                        action_type="fill_text",
                        target_locator=el.suggested_locator,
                        element_name=el.name or el.element_id,
                        field_label=el.label,
                        value=inc_str,
                        source_attribute="annual_income",
                        confidence=0.96,
                        reasoning=f"Filled annual income '₹{profile.annual_income:,.0f}'.",
                    )
                )
                mapped = True

        # 11. Social Category / Caste
        elif "category" in combined or "caste" in combined:
            if profile.social_category:
                if el.tag == "select":
                    opt_val = _match_select_option(el.options, profile.social_category) or profile.social_category
                    actions.append(
                        FieldAction(
                            action_type="select_option",
                            target_locator=el.suggested_locator,
                            element_name=el.name or el.element_id,
                            field_label=el.label,
                            value=opt_val,
                            source_attribute="social_category",
                            confidence=0.95,
                            reasoning=f"Selected reservation category '{opt_val}'.",
                        )
                    )
                else:
                    actions.append(
                        FieldAction(
                            action_type="fill_text",
                            target_locator=el.suggested_locator,
                            element_name=el.name or el.element_id,
                            field_label=el.label,
                            value=profile.social_category,
                            source_attribute="social_category",
                            confidence=0.95,
                            reasoning=f"Filled reservation category '{profile.social_category}'.",
                        )
                    )
                mapped = True

        # 12. Occupation
        elif "occupation" in combined or "profession" in combined:
            if profile.occupation:
                actions.append(
                    FieldAction(
                        action_type="fill_text",
                        target_locator=el.suggested_locator,
                        element_name=el.name or el.element_id,
                        field_label=el.label,
                        value=profile.occupation,
                        source_attribute="occupation",
                        confidence=0.95,
                        reasoning=f"Filled occupation '{profile.occupation}'.",
                    )
                )
                mapped = True

        # 13. Education / Institution
        elif any(term in combined for term in ["institution", "college", "university"]):
            if profile.institution_name:
                actions.append(
                    FieldAction(
                        action_type="fill_text",
                        target_locator=el.suggested_locator,
                        element_name=el.name or el.element_id,
                        field_label=el.label,
                        value=profile.institution_name,
                        source_attribute="institution_name",
                        confidence=0.95,
                        reasoning=f"Filled institution '{profile.institution_name}'.",
                    )
                )
                mapped = True

        elif any(term in combined for term in ["course", "degree", "education"]):
            edu_val = profile.course or profile.education_level
            if edu_val:
                actions.append(
                    FieldAction(
                        action_type="fill_text",
                        target_locator=el.suggested_locator,
                        element_name=el.name or el.element_id,
                        field_label=el.label,
                        value=edu_val,
                        source_attribute="course",
                        confidence=0.94,
                        reasoning=f"Filled academic program '{edu_val}'.",
                    )
                )
                mapped = True

        # 14. Buttons (Submit / Proceed) are intentionally NOT executed during mapping (handled by HIL Phase 10)
        elif el.tag == "button" or el.element_type in ["submit", "button"]:
            continue

        if not mapped:
            el_desc = el.label or el.name or el.element_id or el.tag
            unmapped.append(el_desc)
            if el.is_required:
                missing_mandatory.append(el_desc)

    return FormFillPlan(
        actions=actions,
        unmapped_elements=unmapped,
        missing_mandatory_fields=missing_mandatory,
        generated_at=datetime.now(timezone.utc),
    )


class DynamicFieldMapper:
    """Dynamic field mapping engine powered by Gemini 2.5 Flash with deterministic fallback."""

    @classmethod
    async def generate_fill_plan(
        cls,
        dom_tree: SanitizedDOMTree,
        profile: CitizenProfileBase,
        vault_documents: Optional[List[Dict[str, Any]]] = None,
    ) -> FormFillPlan:
        """Map citizen profile attributes to portal interactive elements using Gemini 2.5 Flash (AGENT-03)."""
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return generate_fill_plan_fallback(dom_tree, profile, vault_documents)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            profile_json = profile.model_dump_json(indent=2)
            dom_json = dom_tree.model_dump_json(indent=2)
            docs_json = json.dumps(vault_documents or [], indent=2)

            prompt = f"""You are the autonomous Government Portal Form Filling Engine for CivicPilot.
Generate a structured FormFillPlan mapping citizen profile data and verified vault documents to web form inputs.

SANITIZED PORTAL DOM TREE:
{dom_json}

CITIZEN PROFILE ATTRIBUTES:
{profile_json}

CITIZEN DOCUMENT VAULT FILES:
{docs_json}

MAPPING RULES:
1. Dynamically match interactive elements to profile attributes based on semantic meaning without hardcoded selectors.
2. For text inputs, set action_type='fill_text'.
3. For <select> dropdowns, inspect the element's options list and choose the option value matching the citizen's profile. Set action_type='select_option'.
4. For checkboxes representing citizen consents or declarations, set action_type='check_box' and value='true'.
5. For file inputs (type='file'), match the required document to a document in the vault list and set action_type='upload_file'.
6. Do NOT click submit buttons; submission requires human-in-the-loop approval.
7. Return high-confidence mappings with clear reasoning."""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=FormFillPlan,
                ),
            )

            if response.text:
                parsed = json.loads(response.text)
                return FormFillPlan(**parsed)
        except Exception:
            pass

        return generate_fill_plan_fallback(dom_tree, profile, vault_documents)
