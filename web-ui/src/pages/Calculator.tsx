/**
 * Calculator Page Component
 */

import { useState } from 'react';
import { calculateRequest, pollJobStatus } from '../api/calculator';
import './Calculator.css';

export default function Calculator() {
  const [num1, setNum1] = useState<string>('');
  const [num2, setNum2] = useState<string>('');
  const [operator, setOperator] = useState<string>('add');
  const [locale, setLocale] = useState<string>('en-US');
  const [decimals, setDecimals] = useState<number>(2);
  const [result, setResult] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleCalculate = async () => {
    // Reset state
    setResult('');
    setError('');
    setLoading(true);

    try {
      // Validate inputs
      const n1 = parseFloat(num1);
      const n2 = parseFloat(num2);

      if (isNaN(n1) || isNaN(n2)) {
        throw new Error('Please enter valid numbers');
      }

      // Submit calculation request
      const response = await calculateRequest(n1, n2, operator, locale, decimals);

      // Poll for result
      const jobStatus = await pollJobStatus(response.job_id);

      if (jobStatus.status === 'done' && jobStatus.result) {
        setResult(jobStatus.result);
      } else if (jobStatus.status === 'failed') {
        setError(jobStatus.error || 'Calculation failed');
      } else {
        setError('Unexpected job status: ' + jobStatus.status);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleCalculate();
    }
  };

  return (
    <div className="calculator-container">
      <div className="calculator-card">
        <h1>🧮 Calculator POC</h1>
        <p className="subtitle">Agent-based calculation with LAM Protocol</p>

        <div className="calculator-form">
          <div className="input-row">
            <input
              type="number"
              value={num1}
              onChange={(e) => setNum1(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="First number"
              className="number-input"
              disabled={loading}
            />

            <select
              value={operator}
              onChange={(e) => setOperator(e.target.value)}
              className="operator-select"
              disabled={loading}
            >
              <option value="add">+</option>
              <option value="subtract">−</option>
              <option value="multiply">×</option>
              <option value="divide">÷</option>
            </select>

            <input
              type="number"
              value={num2}
              onChange={(e) => setNum2(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Second number"
              className="number-input"
              disabled={loading}
            />
          </div>

          <div className="options-row">
            <div className="option-group">
              <label>Locale:</label>
              <select
                value={locale}
                onChange={(e) => setLocale(e.target.value)}
                className="locale-select"
                disabled={loading}
              >
                <option value="en-US">English (US)</option>
                <option value="de-DE">German</option>
                <option value="fr-FR">French</option>
              </select>
            </div>

            <div className="option-group">
              <label>Decimals:</label>
              <input
                type="number"
                value={decimals}
                onChange={(e) => setDecimals(parseInt(e.target.value) || 0)}
                min="0"
                max="10"
                className="decimals-input"
                disabled={loading}
              />
            </div>
          </div>

          <button
            onClick={handleCalculate}
            disabled={loading || !num1 || !num2}
            className="calculate-button"
          >
            {loading ? 'Calculating...' : 'Calculate'}
          </button>

          {result && (
            <div className="result-box success">
              <div className="result-label">Result:</div>
              <div className="result-value">{result}</div>
            </div>
          )}

          {error && (
            <div className="result-box error">
              <div className="result-label">Error:</div>
              <div className="result-value">{error}</div>
            </div>
          )}
        </div>

        <div className="info-box">
          <p><strong>How it works:</strong></p>
          <ol>
            <li>UI sends request to Scheduler API</li>
            <li>Orchestrator calls Calculation Agent (LAM Protocol)</li>
            <li>Orchestrator calls Formatting Agent (LAM Protocol)</li>
            <li>Result is returned to UI</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

