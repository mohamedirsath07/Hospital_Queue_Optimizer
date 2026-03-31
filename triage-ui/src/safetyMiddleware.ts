/**
 * Safety Middleware for AI Triage System (TypeScript/Frontend)
 *
 * Provides client-side input validation and output sanitization
 * as a defense-in-depth measure alongside backend validation.
 */

// =============================================================================
// TYPES
// =============================================================================

export enum BlockReason {
  DIAGNOSIS_REQUEST = 'diagnosis_request',
  MEDICATION_REQUEST = 'medication_request',
  TREATMENT_REQUEST = 'treatment_request',
  INJECTION_ATTEMPT = 'injection_attempt',
  DIAGNOSIS_OUTPUT = 'diagnosis_in_output',
  PRESCRIPTION_OUTPUT = 'prescription_in_output',
  OVERCONFIDENT_OUTPUT = 'overconfident_output',
  DISMISSIVE_OUTPUT = 'dismissive_output',
}

export enum SafetyAction {
  ALLOW = 'allow',
  BLOCK = 'block',
  REDIRECT = 'redirect',
  SANITIZE = 'sanitize',
  FLAG = 'flag',
}

export interface SafetyResult {
  isSafe: boolean;
  action: SafetyAction;
  reason?: BlockReason;
  message: string;
  flags: string[];
  confidence?: number;
}

export interface TriageResponse {
  priority: number;
  priority_label: string;
  reason: string;
  action: string;
  queue: string;
  confidence: number;
  escalation_triggers?: string[];
  disclaimer?: string;
  safety_flags?: Array<{ code: string; message: string }>;
}

export interface SafetyConfig {
  confidenceCeiling: number;
  minInputLength: number;
  maxInputLength: number;
  blockDiagnosisRequests: boolean;
  blockMedicationRequests: boolean;
  sanitizeOutputs: boolean;
}

// =============================================================================
// PATTERNS
// =============================================================================

const INPUT_PATTERNS = {
  diagnosisRequest: [
    /\b(what|which)\s+(disease|condition|illness)\s+(do\s+)?i\s+have\b/i,
    /\b(diagnose|diagnosis)\s+(me|my)\b/i,
    /\bwhat('s|s| is)\s+wrong\s+with\s+me\b/i,
    /\bdo\s+i\s+have\s+\w+\s*(disease|syndrome|cancer)?\b/i,
    /\btell\s+me\s+(what|if)\s+i\s+have\b/i,
  ],
  medicationRequest: [
    /\bwhat\s+(medication|medicine|drug)s?\s+should\s+i\s+(take|use)\b/i,
    /\b(prescribe|recommend)\s+(me\s+)?(a\s+)?(medication|medicine)\b/i,
    /\bwhat\s+(should|can)\s+i\s+take\s+for\b/i,
    /\bhow\s+much\s+\w+\s+should\s+i\s+take\b/i,
    /\b(dosage|dose)\s+(for|of)\b/i,
  ],
  treatmentRequest: [
    /\bhow\s+(do\s+i|can\s+i|to)\s+treat\b/i,
    /\bwhat('s| is)\s+the\s+(treatment|cure)\s+for\b/i,
    /\bhow\s+(do\s+i|can\s+i)\s+(cure|fix|heal)\b/i,
    /\bhome\s+remed(y|ies)\s+for\b/i,
  ],
  injectionAttempt: [
    /ignore\s+(all\s+)?(previous|prior)\s+instructions/i,
    /disregard\s+(your|the)\s+(rules|guidelines)/i,
    /you\s+are\s+now\s+(a|an)\b/i,
    /pretend\s+(you'?re|to\s+be)/i,
    /<\s*\/?system\s*>/i,
  ],
};

const OUTPUT_PATTERNS = {
  diagnosis: [
    /\byou\s+(have|are\s+suffering\s+from)\s+(?!symptoms|pain|discomfort)\w+/i,
    /\bthis\s+(is|appears\s+to\s+be|looks\s+like)\s+\w+itis\b/i,
    /\bdiagnosis:\s*\w+/i,
    /\bclassic\s+(signs?|symptoms?)\s+of\s+\w+/i,
  ],
  prescription: [
    /\btake\s+(\d+\s*)?(mg|ml|tablet|pill)/i,
    /\btake\s+(an?\s+)?(aspirin|ibuprofen|acetaminophen|tylenol)/i,
    /\b\d+\s*(mg|ml)\s+(of|every|daily)\b/i,
    /\byou\s+should\s+(take|use)\s+\w+\s+medication\b/i,
  ],
  overconfident: [
    /\bi('m| am)\s+(100%|completely|absolutely)\s+(certain|sure)/i,
    /\bthis\s+is\s+(definitely|certainly|undoubtedly)\b/i,
    /\bthere('s| is)\s+no\s+doubt\b/i,
    /\bi\s+can\s+guarantee\b/i,
  ],
  dismissive: [
    /\b(this\s+is\s+)?nothing\s+(serious|to\s+worry)\b/i,
    /\byou('re| are)\s+(fine|okay|overreacting)\b/i,
    /\bdon'?t\s+(need\s+to\s+)?worry\b/i,
    /\byou\s+don'?t\s+(need|have)\s+to\s+see\s+a\s+doctor\b/i,
    /\bthis\s+will\s+(go\s+away|pass)\s+(on\s+its\s+own)?\b/i,
  ],
};

// =============================================================================
// FALLBACK RESPONSES
// =============================================================================

const FALLBACK_RESPONSES: Record<BlockReason, { message: string; action: string }> = {
  [BlockReason.DIAGNOSIS_REQUEST]: {
    message: "I can't provide diagnoses. I can help assess the urgency of your symptoms.",
    action: "Please describe your symptoms for triage assessment.",
  },
  [BlockReason.MEDICATION_REQUEST]: {
    message: "I can't recommend medications. A healthcare provider can help with that.",
    action: "I can assess urgency to help you get appropriate care.",
  },
  [BlockReason.TREATMENT_REQUEST]: {
    message: "Treatment advice requires a healthcare professional.",
    action: "Let me help assess how urgently you should be seen.",
  },
  [BlockReason.INJECTION_ATTEMPT]: {
    message: "I can only help with symptom triage assessment.",
    action: "Please describe your symptoms if you need assistance.",
  },
  [BlockReason.DIAGNOSIS_OUTPUT]: {
    message: "Professional evaluation required.",
    action: "Healthcare provider assessment needed.",
  },
  [BlockReason.PRESCRIPTION_OUTPUT]: {
    message: "Medical evaluation required for treatment decisions.",
    action: "Healthcare provider will discuss options.",
  },
  [BlockReason.OVERCONFIDENT_OUTPUT]: {
    message: "Assessment requires professional verification.",
    action: "Staff evaluation recommended.",
  },
  [BlockReason.DISMISSIVE_OUTPUT]: {
    message: "Symptoms require professional evaluation.",
    action: "Staff will assess appropriately.",
  },
};

// =============================================================================
// SAFETY MIDDLEWARE CLASS
// =============================================================================

export class SafetyMiddleware {
  private config: SafetyConfig;

  constructor(config?: Partial<SafetyConfig>) {
    this.config = {
      confidenceCeiling: 0.95,
      minInputLength: 3,
      maxInputLength: 5000,
      blockDiagnosisRequests: true,
      blockMedicationRequests: true,
      sanitizeOutputs: true,
      ...config,
    };
  }

  // ---------------------------------------------------------------------------
  // INPUT VALIDATION
  // ---------------------------------------------------------------------------

  checkInput(input: string): SafetyResult {
    if (!input || typeof input !== 'string') {
      return {
        isSafe: false,
        action: SafetyAction.BLOCK,
        message: 'Invalid input',
        flags: ['invalid_input'],
      };
    }

    const trimmed = input.trim();

    // Length checks
    if (trimmed.length < this.config.minInputLength) {
      return {
        isSafe: true,
        action: SafetyAction.FLAG,
        message: 'Input too short for reliable assessment',
        flags: ['short_input'],
      };
    }

    if (input.length > this.config.maxInputLength) {
      return {
        isSafe: false,
        action: SafetyAction.BLOCK,
        message: 'Input too long',
        flags: ['input_too_long'],
      };
    }

    // Check for injection attempts (highest priority)
    if (this.matchesPatterns(input, INPUT_PATTERNS.injectionAttempt)) {
      console.warn('[Safety] Injection attempt detected');
      return {
        isSafe: false,
        action: SafetyAction.BLOCK,
        reason: BlockReason.INJECTION_ATTEMPT,
        message: 'Unable to process this request',
        flags: ['security_alert'],
      };
    }

    // Diagnosis request check
    if (this.config.blockDiagnosisRequests &&
        this.matchesPatterns(input, INPUT_PATTERNS.diagnosisRequest)) {
      return {
        isSafe: false,
        action: SafetyAction.REDIRECT,
        reason: BlockReason.DIAGNOSIS_REQUEST,
        message: FALLBACK_RESPONSES[BlockReason.DIAGNOSIS_REQUEST].message,
        flags: ['diagnosis_request'],
      };
    }

    // Medication request check
    if (this.config.blockMedicationRequests &&
        this.matchesPatterns(input, INPUT_PATTERNS.medicationRequest)) {
      return {
        isSafe: false,
        action: SafetyAction.REDIRECT,
        reason: BlockReason.MEDICATION_REQUEST,
        message: FALLBACK_RESPONSES[BlockReason.MEDICATION_REQUEST].message,
        flags: ['medication_request'],
      };
    }

    // Treatment request check
    if (this.matchesPatterns(input, INPUT_PATTERNS.treatmentRequest)) {
      return {
        isSafe: false,
        action: SafetyAction.REDIRECT,
        reason: BlockReason.TREATMENT_REQUEST,
        message: FALLBACK_RESPONSES[BlockReason.TREATMENT_REQUEST].message,
        flags: ['treatment_request'],
      };
    }

    return {
      isSafe: true,
      action: SafetyAction.ALLOW,
      message: 'Input validated',
      flags: [],
    };
  }

  // ---------------------------------------------------------------------------
  // OUTPUT VALIDATION
  // ---------------------------------------------------------------------------

  checkOutput(response: TriageResponse): SafetyResult {
    const flags: string[] = [];
    const textContent = `${response.reason || ''} ${response.action || ''}`.toLowerCase();

    // Check for diagnosis language
    if (this.matchesPatterns(textContent, OUTPUT_PATTERNS.diagnosis)) {
      flags.push('diagnosis_detected');
    }

    // Check for prescription/medication advice
    if (this.matchesPatterns(textContent, OUTPUT_PATTERNS.prescription)) {
      flags.push('prescription_detected');
    }

    // Check for overconfident language
    if (this.matchesPatterns(textContent, OUTPUT_PATTERNS.overconfident)) {
      flags.push('overconfidence_detected');
    }

    // Check confidence value
    if (response.confidence > this.config.confidenceCeiling) {
      flags.push('confidence_too_high');
    }

    // Check for dismissive language
    if (this.matchesPatterns(textContent, OUTPUT_PATTERNS.dismissive)) {
      flags.push('dismissive_detected');
    }

    if (flags.length > 0) {
      return {
        isSafe: false,
        action: SafetyAction.SANITIZE,
        message: `Output requires sanitization: ${flags.join(', ')}`,
        flags,
        confidence: Math.min(response.confidence, this.config.confidenceCeiling),
      };
    }

    return {
      isSafe: true,
      action: SafetyAction.ALLOW,
      message: 'Output validated',
      flags: [],
      confidence: response.confidence,
    };
  }

  // ---------------------------------------------------------------------------
  // SANITIZATION
  // ---------------------------------------------------------------------------

  sanitizeOutput(response: TriageResponse, safetyResult: SafetyResult): TriageResponse {
    if (!this.config.sanitizeOutputs || safetyResult.isSafe) {
      return response;
    }

    const sanitized = { ...response };

    for (const flag of safetyResult.flags) {
      switch (flag) {
        case 'diagnosis_detected':
          sanitized.reason = 'Requires professional medical evaluation';
          sanitized.action = 'Staff assessment needed';
          break;

        case 'prescription_detected':
          sanitized.reason = 'Medical evaluation required for treatment decisions';
          sanitized.action = 'Healthcare provider will discuss options';
          break;

        case 'overconfidence_detected':
        case 'confidence_too_high':
          sanitized.confidence = Math.min(sanitized.confidence, 0.85);
          break;

        case 'dismissive_detected':
          sanitized.reason = 'Symptoms require professional evaluation';
          sanitized.action = 'Staff will assess appropriately';
          // Escalate priority (lower number = higher urgency)
          sanitized.priority = Math.min(sanitized.priority, 3);
          break;
      }
    }

    // Ensure disclaimer
    sanitized.disclaimer =
      "This is a triage assessment only, not a medical diagnosis. " +
      "A qualified healthcare professional must evaluate the patient.";

    return sanitized;
  }

  // ---------------------------------------------------------------------------
  // FALLBACK RESPONSES
  // ---------------------------------------------------------------------------

  getInputFallback(safetyResult: SafetyResult): {
    blocked: true;
    reason: string;
    message: string;
    action: string;
  } {
    const fallback = safetyResult.reason
      ? FALLBACK_RESPONSES[safetyResult.reason]
      : { message: 'Unable to process request', action: 'Please describe your symptoms' };

    return {
      blocked: true,
      reason: safetyResult.reason || 'unsafe_input',
      message: fallback.message,
      action: fallback.action,
    };
  }

  getSafeFallbackResponse(priority: number = 2): TriageResponse {
    const labels: Record<number, string> = {
      1: 'CRITICAL',
      2: 'URGENT',
      3: 'SEMI-URGENT',
      4: 'NON-URGENT',
    };
    const queues: Record<number, string> = {
      1: 'critical-care',
      2: 'urgent-care',
      3: 'standard-care',
      4: 'routine',
    };

    return {
      priority,
      priority_label: labels[priority] || 'URGENT',
      reason: 'Symptoms require professional medical evaluation',
      action: 'Healthcare provider assessment recommended',
      queue: queues[priority] || 'urgent-care',
      confidence: 0.5,
      escalation_triggers: [
        'Worsening symptoms',
        'New severe symptoms',
        'Difficulty breathing',
      ],
      disclaimer:
        "This is a triage assessment only, not a medical diagnosis. " +
        "A qualified healthcare professional must evaluate the patient.",
    };
  }

  // ---------------------------------------------------------------------------
  // HELPERS
  // ---------------------------------------------------------------------------

  private matchesPatterns(text: string, patterns: RegExp[]): boolean {
    return patterns.some((pattern) => pattern.test(text));
  }
}

// =============================================================================
// SINGLETON & CONVENIENCE
// =============================================================================

let _instance: SafetyMiddleware | null = null;

export function getSafetyMiddleware(config?: Partial<SafetyConfig>): SafetyMiddleware {
  if (!_instance || config) {
    _instance = new SafetyMiddleware(config);
  }
  return _instance;
}

export function checkInputSafety(input: string): SafetyResult {
  return getSafetyMiddleware().checkInput(input);
}

export function checkOutputSafety(response: TriageResponse): SafetyResult {
  return getSafetyMiddleware().checkOutput(response);
}

export function sanitizeResponse(response: TriageResponse): TriageResponse {
  const middleware = getSafetyMiddleware();
  const result = middleware.checkOutput(response);
  return result.isSafe ? response : middleware.sanitizeOutput(response, result);
}
