import { useState } from 'react'

// Priority configuration
const PRIORITY_CONFIG = {
  1: { label: 'CRITICAL', className: 'critical' },
  2: { label: 'URGENT', className: 'urgent' },
  3: { label: 'SEMI-URGENT', className: 'semi-urgent' },
  4: { label: 'NON-URGENT', className: 'non-urgent' },
  5: { label: 'NON-URGENT', className: 'non-urgent' },
}

// Icons
const HeartPulseIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
    <path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/>
  </svg>
)

const AlertIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
    <path d="M12 9v4"/>
    <path d="M12 17h.01"/>
  </svg>
)

const ClipboardIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="8" height="4" x="8" y="2" rx="1" ry="1"/>
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
  </svg>
)

const ErrorIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="m15 9-6 6"/>
    <path d="m9 9 6 6"/>
  </svg>
)

function App() {
  const [symptoms, setSymptoms] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!symptoms.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symptoms: symptoms.trim(),
          request_id: `ui-${Date.now()}`,
        }),
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Failed to analyze symptoms. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getPriorityConfig = (priority) => {
    return PRIORITY_CONFIG[priority] || PRIORITY_CONFIG[3]
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>
          <HeartPulseIcon />
          AI Triage
        </h1>
        <p>Symptom urgency assessment</p>
      </header>

      {/* Input Form */}
      <form onSubmit={handleSubmit}>
        <div className="input-card">
          <label htmlFor="symptoms">Describe your symptoms</label>
          <textarea
            id="symptoms"
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            placeholder="Example: I have a severe headache that started this morning, along with nausea and sensitivity to light..."
            disabled={loading}
          />
          <button
            type="submit"
            className="submit-btn"
            disabled={loading || !symptoms.trim()}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Analyzing...
              </>
            ) : (
              'Analyze Symptoms'
            )}
          </button>
        </div>
      </form>

      {/* Error State */}
      {error && (
        <div className="error-card">
          <ErrorIcon />
          <p>{error}</p>
        </div>
      )}

      {/* Result Card */}
      {result && (
        <div className="result-card">
          {/* Priority Header */}
          <div className={`priority-header ${getPriorityConfig(result.priority).className}`}>
            <div className="priority-badge">
              <span className="priority-dot" />
              <span className="priority-label">
                {result.priority_label || getPriorityConfig(result.priority).label}
              </span>
            </div>
            <span className="priority-level">Level {result.priority}</span>
          </div>

          {/* Result Body */}
          <div className="result-body">
            {/* Reason */}
            <div className="result-section">
              <h3>Assessment</h3>
              <p>{result.reason}</p>
            </div>

            {/* Action */}
            <div className="result-section">
              <h3>Recommended Action</h3>
              <p>{result.action}</p>
            </div>

            {/* Queue */}
            <div className="result-section">
              <h3>Queue Assignment</h3>
              <div className="queue-badge">
                <ClipboardIcon />
                {result.queue}
              </div>
            </div>

            {/* Confidence */}
            {result.confidence !== undefined && (
              <div className="result-section">
                <h3>Confidence</h3>
                <div className="confidence-section">
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{ width: `${result.confidence * 100}%` }}
                    />
                  </div>
                  <span className="confidence-value">
                    {Math.round(result.confidence * 100)}%
                  </span>
                </div>
              </div>
            )}

            {/* Escalation Triggers */}
            {result.escalation_triggers && result.escalation_triggers.length > 0 && (
              <div className="result-section">
                <h3>Seek immediate care if</h3>
                <ul style={{ paddingLeft: '1.25rem', fontSize: '0.875rem' }}>
                  {result.escalation_triggers.map((trigger, i) => (
                    <li key={i}>{trigger}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Disclaimer */}
            <div className="disclaimer">
              <span className="disclaimer-icon">
                <AlertIcon />
              </span>
              <span>
                {result.disclaimer ||
                  'This is a triage assessment only, not a medical diagnosis. A qualified healthcare professional must evaluate you.'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
