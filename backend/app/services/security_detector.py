"""Security Challenge Detector for identifying CAPTCHA, SMS OTP, and MFA on government portals (HIL-04)."""

import re
from datetime import datetime, timezone
from typing import Optional, List

from app.models.agent import SanitizedDOMTree, DOMElementNode
from app.models.security_challenge import SecurityChallengeInfo

# Common regex patterns found on Indian government portals (NSP, PM-Kisan, PM-JAY, Parivahan)
CAPTCHA_ELEMENT_PATTERNS = [
    re.compile(r"captcha", re.IGNORECASE),
    re.compile(r"recaptcha", re.IGNORECASE),
    re.compile(r"hcaptcha", re.IGNORECASE),
    re.compile(r"turnstile", re.IGNORECASE),
    re.compile(r"security[_\s\-]?code", re.IGNORECASE),
    re.compile(r"txtcaptcha", re.IGNORECASE),
    re.compile(r"imgcaptcha", re.IGNORECASE),
]

OTP_ELEMENT_PATTERNS = [
    re.compile(r"otp", re.IGNORECASE),
    re.compile(r"one[_\s\-]?time[_\s\-]?password", re.IGNORECASE),
    re.compile(r"verification[_\s\-]?code", re.IGNORECASE),
    re.compile(r"sms[_\s\-]?otp", re.IGNORECASE),
    re.compile(r"aadhaar[_\s\-]?otp", re.IGNORECASE),
    re.compile(r"txtotp", re.IGNORECASE),
]

CAPTCHA_TEXT_PATTERNS = [
    re.compile(r"enter\s+(?:the\s+)?characters\s+(?:shown|below|above)", re.IGNORECASE),
    re.compile(r"enter\s+(?:the\s+)?captcha\s+code", re.IGNORECASE),
    re.compile(r"type\s+(?:the\s+)?text\s+from\s+(?:the\s+)?image", re.IGNORECASE),
    re.compile(r"image\s+verification", re.IGNORECASE),
    re.compile(r"security\s+code\s+verification", re.IGNORECASE),
]

OTP_TEXT_PATTERNS = [
    re.compile(r"enter\s+(?:\d+-digit\s+)?otp", re.IGNORECASE),
    re.compile(r"otp\s+has\s+been\s+sent\s+to", re.IGNORECASE),
    re.compile(r"one\s+time\s+password\s+(?:sent|verification)", re.IGNORECASE),
    re.compile(r"enter\s+verification\s+code", re.IGNORECASE),
    re.compile(r"resend\s+otp", re.IGNORECASE),
]


class SecurityChallengeDetector:
    """Detects security challenges requiring citizen intervention (CAPTCHA / OTP / MFA)."""

    @classmethod
    def detect_in_elements(cls, elements: List[DOMElementNode]) -> SecurityChallengeInfo:
        """Scan interactive DOM elements for CAPTCHA or OTP inputs."""
        now_iso = datetime.now(timezone.utc).isoformat()

        # Check for OTP inputs first (higher specificity)
        for el in elements:
            combined_desc = f"{el.name or ''} {el.element_id or ''} {el.label or ''} {el.placeholder or ''}"
            for pat in OTP_ELEMENT_PATTERNS:
                if pat.search(combined_desc):
                    locator = getattr(el, "suggested_locator", None) or (
                        f"input#{el.element_id}" if el.element_id else (f"input[name='{el.name}']" if el.name else "input")
                    )
                    return SecurityChallengeInfo(
                        detected=True,
                        challenge_type="otp",
                        element_locator=locator,
                        instructions=(
                            "An OTP verification code was sent to your registered mobile number or Aadhaar. "
                            "Please enter the OTP on the portal or solve it directly in the viewport."
                        ),
                        prompt_message=el.label or "Please enter the OTP verification code",
                        detected_at=now_iso,
                    )

        # Check for CAPTCHA inputs or containers
        for el in elements:
            combined_desc = f"{el.name or ''} {el.element_id or ''} {el.label or ''} {el.placeholder or ''}"
            for pat in CAPTCHA_ELEMENT_PATTERNS:
                if pat.search(combined_desc):
                    locator = getattr(el, "suggested_locator", None) or (
                        f"input#{el.element_id}" if el.element_id else (f"input[name='{el.name}']" if el.name else "input")
                    )
                    return SecurityChallengeInfo(
                        detected=True,
                        challenge_type="captcha",
                        element_locator=locator,
                        instructions=(
                            "A security CAPTCHA challenge is present on the government portal. "
                            "Please inspect the image in the live viewport and type the characters shown."
                        ),
                        prompt_message=el.label or "Please solve the security CAPTCHA challenge",
                        detected_at=now_iso,
                    )

        return SecurityChallengeInfo(detected=False)

    @classmethod
    def detect_in_text(cls, text: str) -> SecurityChallengeInfo:
        """Scan page textual content or alerts for challenge notices."""
        if not text:
            return SecurityChallengeInfo(detected=False)

        now_iso = datetime.now(timezone.utc).isoformat()

        for pat in OTP_TEXT_PATTERNS:
            match = pat.search(text)
            if match:
                return SecurityChallengeInfo(
                    detected=True,
                    challenge_type="otp",
                    instructions=(
                        "An SMS / Aadhaar OTP challenge was identified. "
                        "Please verify the code sent to your registered device."
                    ),
                    prompt_message=match.group(0),
                    detected_at=now_iso,
                )

        for pat in CAPTCHA_TEXT_PATTERNS:
            match = pat.search(text)
            if match:
                return SecurityChallengeInfo(
                    detected=True,
                    challenge_type="captcha",
                    instructions=(
                        "A CAPTCHA verification prompt was identified. "
                        "Please complete the challenge on the government portal."
                    ),
                    prompt_message=match.group(0),
                    detected_at=now_iso,
                )

        return SecurityChallengeInfo(detected=False)

    @classmethod
    def detect_challenge(
        cls,
        dom_tree: Optional[SanitizedDOMTree] = None,
        page_text: Optional[str] = None,
    ) -> SecurityChallengeInfo:
        """Composite detection scanning both interactive DOM elements and page text."""
        if dom_tree and dom_tree.elements:
            el_res = cls.detect_in_elements(dom_tree.elements)
            if el_res.detected:
                return el_res

        if page_text:
            text_res = cls.detect_in_text(page_text)
            if text_res.detected:
                return text_res

        return SecurityChallengeInfo(detected=False)
