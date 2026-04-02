"""
Safety Filter
Input validation and safety patterns for medical triage.
"""

import re
from typing import Tuple, Optional


# Blocked input patterns that could lead to unsafe responses
BLOCKED_PATTERNS = [
    (r"\b(what|which)\s+(disease|condition|illness)\s+(do\s+)?i\s+have", "diagnosis_request"),
    (r"\bdiagnose\s+(me|my|this)", "diagnosis_request"),
    (r"\bdo\s+i\s+have\s+\w+\s*(disease|syndrome|cancer)?", "diagnosis_request"),
    (r"\bwhat\s+(medication|medicine|drug)s?\s+should\s+i\s+(take|use)", "medication_request"),
    (r"\b(prescribe|recommend)\s+(me\s+)?(medication|medicine)", "medication_request"),
    (r"\bhow\s+much\s+\w+\s+should\s+i\s+take", "medication_request"),
    (r"\b(dosage|dose)\s+(for|of)", "medication_request"),
]

# Safe responses for blocked patterns
SAFE_RESPONSES = {
    "diagnosis_request": {
        "message": "I cannot provide diagnoses. I can only assess symptom urgency.",
        "action": "Please describe your symptoms for triage assessment."
    },
    "medication_request": {
        "message": "I cannot recommend medications. A healthcare provider must do that.",
        "action": "I can help assess how urgently you need care."
    }
}


def check_input_safety(text: str) -> Tuple[bool, Optional[str]]:
    """
    Check if user input is safe for processing.
    
    Args:
        text: User input text to check
        
    Returns:
        Tuple of (is_safe, block_reason)
        - is_safe: True if input is safe, False if blocked
        - block_reason: Reason key if blocked, None if safe
    """
    text_lower = text.lower()
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False, reason
    return True, None


def get_safe_response(block_reason: str) -> dict:
    """
    Get the safe response for a blocked input.
    
    Args:
        block_reason: The reason key from check_input_safety
        
    Returns:
        Dictionary with 'message' and 'action' keys
    """
    return SAFE_RESPONSES.get(block_reason, SAFE_RESPONSES["diagnosis_request"])
