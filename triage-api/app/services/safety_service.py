"""Safety filtering service for pre and post LLM processing."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import structlog

from app.models import SafetyFlag, PriorityLevel

logger = structlog.get_logger()


class EscalationTier(Enum):
    """Keyword escalation tiers."""

    CRITICAL = 1
    EMERGENT = 2
    URGENT = 3


@dataclass
class KeywordRule:
    """Rule for keyword-based escalation."""

    rule_id: str
    tier: EscalationTier
    patterns: list[re.Pattern]
    requires: Optional[list[re.Pattern]] = None
    excludes: Optional[list[re.Pattern]] = None
    reasoning: str = ""


# Pre-compiled regex patterns for performance
CRITICAL_PATTERNS = [
    # Cardiovascular
    KeywordRule(
        rule_id="CARDIAC_001",
        tier=EscalationTier.CRITICAL,
        patterns=[re.compile(r"chest\s*pain", re.I), re.compile(r"chest\s*pressure", re.I)],
        requires=[re.compile(r"radiat|crush|severe|sudden|squeez|tight", re.I)],
        reasoning="Chest pain with concerning characteristics requires immediate evaluation",
    ),
    KeywordRule(
        rule_id="CARDIAC_002",
        tier=EscalationTier.CRITICAL,
        patterns=[re.compile(r"heart\s*attack", re.I)],
        reasoning="Patient reports suspected cardiac event",
    ),
    # Respiratory
    KeywordRule(
        rule_id="RESP_001",
        tier=EscalationTier.CRITICAL,
        patterns=[
            re.compile(r"can'?t\s*breathe", re.I),
            re.compile(r"unable?\s*to\s*breathe", re.I),
            re.compile(r"stopped?\s*breathing", re.I),
        ],
        reasoning="Respiratory distress is life-threatening",
    ),
    KeywordRule(
        rule_id="RESP_002",
        tier=EscalationTier.CRITICAL,
        patterns=[re.compile(r"choking", re.I), re.compile(r"airway\s*block", re.I)],
        reasoning="Airway obstruction requires immediate intervention",
    ),
    KeywordRule(
        rule_id="RESP_003",
        tier=EscalationTier.CRITICAL,
        patterns=[
            re.compile(r"(lips?|face|skin)\s*(turn|turning|is)?\s*blue", re.I),
            re.compile(r"cyanosis", re.I),
        ],
        reasoning="Cyanosis indicates severe oxygen deprivation",
    ),
    # Neurological
    KeywordRule(
        rule_id="NEURO_001",
        tier=EscalationTier.CRITICAL,
        patterns=[
            re.compile(r"face\s*droop", re.I),
            re.compile(r"arm\s*weak", re.I),
            re.compile(r"slurred\s*speech", re.I),
            re.compile(r"having\s*a\s*stroke", re.I),
        ],
        reasoning="Stroke symptoms require immediate intervention (time-critical)",
    ),
    KeywordRule(
        rule_id="NEURO_002",
        tier=EscalationTier.CRITICAL,
        patterns=[re.compile(r"unconscious", re.I), re.compile(r"unresponsive", re.I)],
        reasoning="Loss of consciousness requires immediate evaluation",
    ),
    KeywordRule(
        rule_id="NEURO_003",
        tier=EscalationTier.CRITICAL,
        patterns=[re.compile(r"worst\s*headache", re.I), re.compile(r"thunderclap", re.I)],
        reasoning="Sudden severe headache may indicate intracranial emergency",
    ),
    # Trauma
    KeywordRule(
        rule_id="TRAUMA_001",
        tier=EscalationTier.CRITICAL,
        patterns=[
            re.compile(r"severe\s*bleeding", re.I),
            re.compile(r"won'?t\s*stop\s*bleeding", re.I),
        ],
        reasoning="Uncontrolled hemorrhage is life-threatening",
    ),
    KeywordRule(
        rule_id="TRAUMA_002",
        tier=EscalationTier.CRITICAL,
        patterns=[
            re.compile(r"gunshot", re.I),
            re.compile(r"stabbed", re.I),
            re.compile(r"impaled", re.I),
        ],
        reasoning="Penetrating trauma requires immediate evaluation",
    ),
    # Mental Health
    KeywordRule(
        rule_id="MENTAL_001",
        tier=EscalationTier.CRITICAL,
        patterns=[
            re.compile(r"suicidal", re.I),
            re.compile(r"kill\s*(my)?self", re.I),
            re.compile(r"end\s*(my)?\s*life", re.I),
            re.compile(r"want\s*to\s*die", re.I),
        ],
        reasoning="Active suicidal ideation requires immediate intervention",
    ),
    KeywordRule(
        rule_id="MENTAL_002",
        tier=EscalationTier.CRITICAL,
        patterns=[re.compile(r"overdose", re.I), re.compile(r"took\s*too\s*many\s*pills", re.I)],
        reasoning="Suspected overdose requires immediate medical attention",
    ),
    # Allergic
    KeywordRule(
        rule_id="ALLERGY_001",
        tier=EscalationTier.CRITICAL,
        patterns=[
            re.compile(r"anaphyla", re.I),
            re.compile(r"throat\s*(is\s*)?(closing|swelling)", re.I),
            re.compile(r"severe\s*allergic", re.I),
        ],
        reasoning="Anaphylaxis is life-threatening",
    ),
]

EMERGENT_PATTERNS = [
    KeywordRule(
        rule_id="PAIN_001",
        tier=EscalationTier.EMERGENT,
        patterns=[
            re.compile(r"severe\s*pain", re.I),
            re.compile(r"worst\s*pain", re.I),
            re.compile(r"(10|ten)\s*(out\s*of|\/)\s*10", re.I),
            re.compile(r"excruciating", re.I),
            re.compile(r"unbearable\s*pain", re.I),
        ],
        reasoning="Severe pain requires prompt evaluation",
    ),
    KeywordRule(
        rule_id="RESP_004",
        tier=EscalationTier.EMERGENT,
        patterns=[
            re.compile(r"difficulty\s*breathing", re.I),
            re.compile(r"short\s*of\s*breath", re.I),
            re.compile(r"hard\s*to\s*breathe", re.I),
        ],
        reasoning="Respiratory difficulty requires urgent evaluation",
    ),
    KeywordRule(
        rule_id="RESP_005",
        tier=EscalationTier.EMERGENT,
        patterns=[re.compile(r"coughing\s*blood", re.I), re.compile(r"vomiting\s*blood", re.I)],
        reasoning="Hematemesis or hemoptysis requires urgent evaluation",
    ),
    KeywordRule(
        rule_id="NEURO_004",
        tier=EscalationTier.EMERGENT,
        patterns=[
            re.compile(r"sudden\s*confusion", re.I),
            re.compile(r"sudden\s*vision\s*loss", re.I),
            re.compile(r"sudden\s*numbness", re.I),
            re.compile(r"can'?t\s*move\s*(my\s*)?(arm|leg)", re.I),
        ],
        reasoning="Sudden neurological changes require urgent evaluation",
    ),
    KeywordRule(
        rule_id="PEDS_001",
        tier=EscalationTier.EMERGENT,
        patterns=[re.compile(r"(baby|infant|newborn)\s*.*(not\s*breathing|lethargic)", re.I)],
        reasoning="Pediatric respiratory or neurological concerns are high priority",
    ),
    KeywordRule(
        rule_id="PEDS_002",
        tier=EscalationTier.EMERGENT,
        patterns=[re.compile(r"(baby|infant|newborn)\s*.*high\s*fever", re.I)],
        reasoning="Febrile infant requires urgent evaluation",
    ),
]

URGENT_PATTERNS = [
    KeywordRule(
        rule_id="INFECT_001",
        tier=EscalationTier.URGENT,
        patterns=[
            re.compile(r"fever\s*.*(spreading\s*redness|swelling|pus)", re.I),
            re.compile(r"infected\s*wound", re.I),
        ],
        reasoning="Signs of infection require prompt evaluation",
    ),
    KeywordRule(
        rule_id="PAIN_002",
        tier=EscalationTier.URGENT,
        patterns=[
            re.compile(r"moderate\s*pain", re.I),
            re.compile(r"(7|8)\s*(out\s*of|\/)\s*10", re.I),
            re.compile(r"pain\s*(is\s*)?getting\s*worse", re.I),
        ],
        reasoning="Significant pain requires evaluation",
    ),
    KeywordRule(
        rule_id="DEHYDR_001",
        tier=EscalationTier.URGENT,
        patterns=[
            re.compile(r"can'?t\s*keep\s*(anything|food|water)\s*down", re.I),
            re.compile(r"vomiting\s*all\s*day", re.I),
        ],
        reasoning="Persistent vomiting may lead to dehydration",
    ),
]


# Output validation patterns
UNSAFE_OUTPUT_PATTERNS = [
    (re.compile(r"you\s+(have|may have|probably have|likely have)\s+\w+", re.I), "diagnosis"),
    (re.compile(r"this\s+(is|sounds like|appears to be)\s+(a\s+)?\w+itis", re.I), "diagnosis"),
    (re.compile(r"take\s+(an?\s+)?(aspirin|ibuprofen|tylenol|advil|acetaminophen)", re.I), "medication"),
    (re.compile(r"\d+\s*(mg|ml|gram)", re.I), "dosage"),
    (re.compile(r"you\s+should\s+take", re.I), "medication_advice"),
    (re.compile(r"apply\s+(ice|heat|pressure|cream|ointment)", re.I), "treatment"),
    (re.compile(r"don'?t\s+(need|have)\s+to\s+(see|worry)", re.I), "dismissive"),
    (re.compile(r"nothing\s+(serious|to worry)", re.I), "dismissive"),
    (re.compile(r"you'?re\s+(fine|okay|overreacting)", re.I), "dismissive"),
]


class SafetyService:
    """Service for pre and post-LLM safety filtering."""

    def __init__(self):
        self.all_rules = CRITICAL_PATTERNS + EMERGENT_PATTERNS + URGENT_PATTERNS

    def pre_filter(self, symptoms: str) -> tuple[Optional[int], list[SafetyFlag], str]:
        """
        Pre-LLM safety check for immediate escalation keywords.

        Returns:
            Tuple of (escalation_level, safety_flags, reasoning)
            escalation_level is None if no immediate escalation needed
        """
        symptoms_normalized = symptoms.lower().strip()
        flags: list[SafetyFlag] = []
        escalation_level: Optional[int] = None
        reasoning = ""

        # Check for adversarial/injection patterns
        if self._detect_injection(symptoms_normalized):
            flags.append(
                SafetyFlag(
                    code="SECURITY_001",
                    severity="high",
                    message="Potential prompt injection detected",
                )
            )
            logger.warning("Potential injection detected", input_preview=symptoms[:100])
            return PriorityLevel.EMERGENT, flags, "Input flagged for security review"

        # Check keyword rules
        for rule in self.all_rules:
            if self._check_rule(symptoms, rule):
                level = rule.tier.value
                if escalation_level is None or level < escalation_level:
                    escalation_level = level
                    reasoning = rule.reasoning

                flags.append(
                    SafetyFlag(
                        code=rule.rule_id,
                        severity="critical" if rule.tier == EscalationTier.CRITICAL else "high",
                        message=rule.reasoning,
                    )
                )
                logger.info(
                    "Keyword escalation triggered",
                    rule_id=rule.rule_id,
                    tier=rule.tier.name,
                )

        return escalation_level, flags, reasoning

    def post_filter(self, llm_response: dict) -> tuple[dict, list[SafetyFlag]]:
        """
        Post-LLM safety check to validate and sanitize output.

        Returns:
            Tuple of (sanitized_response, safety_flags)
        """
        flags: list[SafetyFlag] = []

        # Validate required fields
        required_fields = ["priority", "reason", "action", "queue"]
        for field in required_fields:
            if field not in llm_response:
                llm_response[field] = self._get_safe_default(field)
                flags.append(
                    SafetyFlag(
                        code="MISSING_FIELD",
                        severity="medium",
                        message=f"Missing field '{field}' - using safe default",
                    )
                )

        # Validate priority bounds
        if not isinstance(llm_response.get("priority"), int):
            llm_response["priority"] = PriorityLevel.URGENT
            flags.append(
                SafetyFlag(
                    code="INVALID_PRIORITY",
                    severity="high",
                    message="Invalid priority value - escalating to URGENT",
                )
            )
        elif llm_response["priority"] < 1 or llm_response["priority"] > 5:
            llm_response["priority"] = max(1, min(5, llm_response["priority"]))

        # Check for unsafe content in text fields
        for field in ["reason", "action"]:
            if field in llm_response and isinstance(llm_response[field], str):
                llm_response[field], field_flags = self._sanitize_text(llm_response[field])
                flags.extend(field_flags)

        # Ensure confidence is present and valid
        confidence = llm_response.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            llm_response["confidence"] = 0.5
            flags.append(
                SafetyFlag(
                    code="INVALID_CONFIDENCE",
                    severity="low",
                    message="Invalid confidence value - using default",
                )
            )

        return llm_response, flags

    def _check_rule(self, text: str, rule: KeywordRule) -> bool:
        """Check if a keyword rule matches the input text."""
        # Check if any primary pattern matches
        pattern_match = any(p.search(text) for p in rule.patterns)
        if not pattern_match:
            return False

        # Check required patterns (at least one must match)
        if rule.requires:
            requires_match = any(r.search(text) for r in rule.requires)
            if not requires_match:
                return False

        # Check excluded patterns (none must match)
        if rule.excludes:
            excludes_match = any(e.search(text) for e in rule.excludes)
            if excludes_match:
                return False

        return True

    def _detect_injection(self, text: str) -> bool:
        """Detect potential prompt injection attempts."""
        injection_patterns = [
            r"ignore\s*(previous|above|all)\s*instructions",
            r"disregard\s*(your|the)\s*(rules|instructions|guidelines)",
            r"you\s*are\s*now\s*a",
            r"pretend\s*(you'?re|to be)",
            r"act\s*as\s*(if|a)",
            r"system\s*prompt",
            r"<\s*\/?\s*system\s*>",
        ]
        return any(re.search(p, text, re.I) for p in injection_patterns)

    def _sanitize_text(self, text: str) -> tuple[str, list[SafetyFlag]]:
        """Remove unsafe content from text output."""
        flags: list[SafetyFlag] = []

        for pattern, issue_type in UNSAFE_OUTPUT_PATTERNS:
            if pattern.search(text):
                flags.append(
                    SafetyFlag(
                        code=f"UNSAFE_{issue_type.upper()}",
                        severity="high",
                        message=f"Removed potentially unsafe {issue_type} content",
                    )
                )
                # Don't remove - let human review, but flag it
                logger.warning("Unsafe content detected", issue_type=issue_type)

        return text, flags

    def _get_safe_default(self, field: str) -> str | int:
        """Get safe default values for missing fields."""
        defaults = {
            "priority": PriorityLevel.URGENT,
            "reason": "Requires professional evaluation",
            "action": "Staff assessment required",
            "queue": "urgent-care",
        }
        return defaults.get(field, "")

    def calculate_final_priority(
        self,
        llm_priority: int,
        pre_filter_priority: Optional[int],
        confidence: float,
        confidence_threshold: float,
    ) -> int:
        """
        Calculate final priority considering all factors.
        Always escalates when uncertain (fail-safe).
        """
        # Start with LLM priority
        final_priority = llm_priority

        # Pre-filter escalation takes precedence
        if pre_filter_priority is not None:
            final_priority = min(final_priority, pre_filter_priority)

        # Low confidence escalates by 1 level
        if confidence < confidence_threshold:
            final_priority = max(1, final_priority - 1)
            logger.info(
                "Low confidence escalation",
                original=llm_priority,
                final=final_priority,
                confidence=confidence,
            )

        return final_priority


# Singleton instance
safety_service = SafetyService()
