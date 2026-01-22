/**
 * Formatting Agent - Number formatting agent for Calculator PoC
 */

import express from 'express';
import { randomUUID } from 'crypto';

// ========== Constants ==========

const AGENT_ID = 'agent.calculator.formatting';
const PORT = process.env.PORT || 8001;
const START_TIME = new Date();

// ========== Express App ==========

const app = express();
app.use(express.json());

// ========== Formatting Logic ==========

/**
 * Format a number for display
 * @param {number} value - Number to format
 * @param {string} locale - Locale (e.g., 'en-US', 'de-DE')
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted number
 */
function formatNumber(value, locale = 'en-US', decimals = 2) {
  try {
    const num = parseFloat(value);
    if (isNaN(num)) {
      throw new Error('Invalid number');
    }

    return num.toLocaleString(locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  } catch (error) {
    throw new Error(`Formatting error: ${error.message}`);
  }
}

// ========== Message Handler ==========

/**
 * Create an agent message
 * @param {string} type - Message type
 * @param {string} sender - Sender agent ID
 * @param {string[]} to - Recipient agent IDs
 * @param {string} intent - Message intent
 * @param {object} payload - Message payload
 * @returns {object} Agent message
 */
function createMessage(type, sender, to, intent, payload) {
  return {
    id: randomUUID(),
    ts: new Date().toISOString(),
    type,
    sender,
    to,
    intent,
    payload,
  };
}

// ========== Endpoints ==========

/**
 * POST /agent/message
 * Handle incoming agent messages
 */
app.post('/agent/message', (req, res) => {
  const message = req.body;
  console.log(`📨 Received message: ${message.intent} from ${message.sender}`);

  // Handle format intent
  if (message.intent === 'format') {
    try {
      // Extract parameters
      const { value, locale, decimals } = message.payload;

      if (value === undefined) {
        throw new Error('Missing parameter: value required');
      }

      // Format number
      const formatted = formatNumber(
        value,
        locale || 'en-US',
        decimals !== undefined ? decimals : 2
      );

      // Return result
      const response = createMessage(
        'inform',
        AGENT_ID,
        [message.sender],
        'formatting_result',
        {
          formatted,
          locale: locale || 'en-US',
          original: value,
        }
      );

      return res.json(response);
    } catch (error) {
      // Return error
      const response = createMessage(
        'failure',
        AGENT_ID,
        [message.sender],
        'formatting_error',
        {
          error: error.message,
        }
      );

      return res.json(response);
    }
  }

  // Unknown intent
  const response = createMessage(
    'failure',
    AGENT_ID,
    [message.sender],
    'unknown_intent',
    {
      error: `Unknown intent: ${message.intent}`,
    }
  );

  return res.json(response);
});

/**
 * GET /health
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  const uptime = (new Date() - START_TIME) / 1000;
  res.json({
    status: 'healthy',
    agent_id: AGENT_ID,
    version: '1.0.0',
    uptime,
  });
});

/**
 * GET /manifest
 * Return agent manifest
 */
app.get('/manifest', (req, res) => {
  res.json({
    agent_id: AGENT_ID,
    name: 'Formatting Agent',
    version: '1.0.0',
    status: 'active',
    capabilities: ['formatting', 'localization'],
  });
});

// ========== Start Server ==========

app.listen(PORT, () => {
  console.log(`🚀 Formatting Agent running on port ${PORT}`);
  console.log(`   Agent ID: ${AGENT_ID}`);
  console.log(`   Health: http://localhost:${PORT}/health`);
  console.log(`   Manifest: http://localhost:${PORT}/manifest`);
});

