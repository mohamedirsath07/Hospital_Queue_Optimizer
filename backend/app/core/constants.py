"""
Hospital Filtering Configuration
Keywords and patterns for filtering and scoring hospitals.
"""

# Keywords that indicate NON-hospital places (to be filtered out)
EXCLUDED_KEYWORDS = [
    "diagnostic", "diagnostics", "lab", "laboratory", "laboratories",
    "scan", "scanning", "imaging", "pathology", "path lab",
    "x-ray", "xray", "mri", "ct scan", "ultrasound",
    "pharmacy", "medical store", "chemist",
    "dental", "dentist", "eye clinic", "optical",
    "physiotherapy", "physio", "rehab center",
    "nursing home", "old age", "hospice",
    "blood bank", "test", "testing"
]

# Keywords that indicate VALID hospitals
VALID_HOSPITAL_KEYWORDS = [
    "hospital", "medical center", "medical centre",
    "emergency", "trauma center", "trauma centre",
    "multi-speciality", "multispeciality", "multi-specialty", "multispecialty",
    "general hospital", "govt hospital", "government hospital"
]

# Condition categories and their keyword triggers
CONDITION_KEYWORDS = {
    "CARDIAC": [
        "chest pain", "heart", "cardiac", "breathing difficulty", "breathless",
        "shortness of breath", "palpitation", "heart attack", "angina"
    ],
    "TRAUMA": [
        "injury", "injured", "accident", "bleeding", "fracture", "broken",
        "wound", "cut", "burn", "fall", "trauma", "hit", "crash"
    ],
    "NEURO": [
        "unconscious", "seizure", "convulsion", "stroke", "paralysis",
        "numbness", "headache severe", "fainting", "blackout", "fits"
    ],
    "GENERAL": [
        "fever", "infection", "cold", "cough", "flu", "vomiting",
        "diarrhea", "stomach", "pain", "weakness", "fatigue"
    ]
}

# Hospital preferences by condition
CONDITION_HOSPITAL_PREFERENCES = {
    "CARDIAC": ["cardiac", "heart", "multi-speciality", "multispeciality", "general"],
    "TRAUMA": ["trauma", "emergency", "accident", "multi-speciality", "general"],
    "NEURO": ["neuro", "brain", "multi-speciality", "multispeciality", "general"],
    "GENERAL": ["general", "multi-speciality", "multispeciality", "hospital"],
    "OTHER": ["general", "multi-speciality", "hospital"]
}

# Priority labels mapping
PRIORITY_LABELS = {
    1: "CRITICAL",
    2: "URGENT",
    3: "SEMI-URGENT",
    4: "NON-URGENT"
}

# Disclaimer text
DISCLAIMER = "This is a triage assessment only, not a medical diagnosis. A qualified healthcare professional must evaluate you."
