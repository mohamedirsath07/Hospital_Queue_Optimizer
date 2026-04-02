from http.server import BaseHTTPRequestHandler
import json
import os
import re

# Get API key from environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Condition keywords for classification
CONDITION_KEYWORDS = {
    "CARDIAC": ["chest pain", "heart", "cardiac", "breathing difficulty", "breathless", "shortness of breath", "palpitation", "heart attack", "angina"],
    "TRAUMA": ["injury", "injured", "accident", "bleeding", "fracture", "broken", "wound", "cut", "burn", "fall", "trauma", "hit", "crash"],
    "NEURO": ["unconscious", "seizure", "convulsion", "stroke", "paralysis", "numbness", "headache severe", "fainting", "blackout", "fits"],
    "GENERAL": ["fever", "infection", "cold", "cough", "flu", "vomiting", "diarrhea", "stomach", "pain", "weakness", "fatigue"]
}

PRIORITY_LABELS = {1: "CRITICAL", 2: "URGENT", 3: "SEMI-URGENT", 4: "NON-URGENT"}
DISCLAIMER = "This is a triage assessment only, not a medical diagnosis. A qualified healthcare professional must evaluate you."

# Safety patterns
BLOCKED_PATTERNS = [
    (r"\b(what|which)\s+(disease|condition|illness)\s+(do\s+)?i\s+have", "diagnosis_request"),
    (r"\bdiagnose\s+(me|my|this)", "diagnosis_request"),
    (r"\bdo\s+i\s+have\s+\w+\s*(disease|syndrome|cancer)?", "diagnosis_request"),
    (r"\bwhat\s+(medication|medicine|drug)s?\s+should\s+i\s+(take|use)", "medication_request"),
    (r"\b(prescribe|recommend)\s+(me\s+)?(medication|medicine)", "medication_request"),
]

SAFE_RESPONSES = {
    "diagnosis_request": {"message": "I cannot provide diagnoses. I can only assess symptom urgency.", "action": "Please describe your symptoms for triage assessment."},
    "medication_request": {"message": "I cannot recommend medications. A healthcare provider must do that.", "action": "I can help assess how urgently you need care."}
}

SYSTEM_PROMPT = """You are a medical triage classification assistant. Your ONLY role is to classify the URGENCY of patient symptoms.

RULES (NEVER VIOLATE):
1. NEVER diagnose or name medical conditions
2. NEVER recommend medications or treatments
3. NEVER dismiss patient concerns
4. When uncertain, choose MORE urgent

PRIORITY LEVELS:
- 1 (CRITICAL): Life-threatening, immediate attention
- 2 (URGENT): Serious, needs prompt attention
- 3 (SEMI-URGENT): Needs attention within 1 hour
- 4 (NON-URGENT): Minor, can wait

Respond with ONLY valid JSON:
{
  "priority": <1-4>,
  "reason": "<brief symptom summary, NO diagnosis>",
  "action": "<what staff should do>",
  "queue": "<critical-care|urgent-care|standard-care|routine>",
  "confidence": <0.0-1.0>,
  "escalation_triggers": ["<warning sign to watch>"]
}"""


def classify_condition(symptoms):
    symptoms_lower = symptoms.lower()
    for condition, keywords in CONDITION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in symptoms_lower:
                return condition
    return "OTHER"


def check_input_safety(text):
    text_lower = text.lower()
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False, reason
    return True, None


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            symptoms = data.get('symptoms', '')
            if not symptoms:
                self.send_error_response({"error": "No symptoms provided"})
                return
            
            condition_category = classify_condition(symptoms)
            
            # Safety check
            is_safe, block_reason = check_input_safety(symptoms)
            if not is_safe:
                safe_response = SAFE_RESPONSES.get(block_reason, SAFE_RESPONSES["diagnosis_request"])
                response = {
                    "priority": 2,
                    "priority_label": "URGENT",
                    "reason": safe_response["message"],
                    "action": safe_response["action"],
                    "queue": "urgent-care",
                    "confidence": 1.0,
                    "escalation_triggers": [],
                    "disclaimer": DISCLAIMER,
                    "blocked": True,
                    "blocked_reason": block_reason,
                    "condition_category": condition_category
                }
                self.send_json_response(response)
                return
            
            # Call Groq API
            import urllib.request
            
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = json.dumps({
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Patient symptoms: {symptoms}\n\nClassify urgency. JSON only."}
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }).encode('utf-8')
            
            req = urllib.request.Request(GROQ_API_URL, data=payload, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
            
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            parsed = json.loads(content.strip())
            priority = parsed.get("priority", 3)
            
            response = {
                "priority": priority,
                "priority_label": PRIORITY_LABELS.get(priority, "SEMI-URGENT"),
                "reason": parsed.get("reason", "Evaluation required"),
                "action": parsed.get("action", "Staff assessment required"),
                "queue": parsed.get("queue", "standard-care"),
                "confidence": parsed.get("confidence", 0.7),
                "escalation_triggers": parsed.get("escalation_triggers", []),
                "disclaimer": DISCLAIMER,
                "blocked": False,
                "blocked_reason": None,
                "condition_category": condition_category
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Error: {e}")
            response = {
                "priority": 2,
                "priority_label": "URGENT",
                "reason": "System temporarily unavailable - defaulting to urgent for safety",
                "action": "Please seek immediate medical evaluation as a precaution",
                "queue": "urgent-care",
                "confidence": 0.0,
                "escalation_triggers": ["If symptoms worsen, call emergency services"],
                "disclaimer": DISCLAIMER,
                "blocked": False,
                "blocked_reason": None,
                "condition_category": "OTHER"
            }
            self.send_json_response(response)
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, data):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
