/**
 * Formatting Agent - Number formatting agent for Calculator PoC
 */

import express from 'express';
import { randomUUID } from 'crypto';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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
app.post('/agent/message', async (req, res) => {
  const message = req.body;
  console.log(`📨 Received message: ${message.intent} from ${message.sender}`);

  // Handle format intent
  if (message.intent === 'format') {
    try {
      // Extract parameters
      const { value, locale, decimals, __workflow__ } = message.payload;

      if (value === undefined) {
        throw new Error('Missing parameter: value required');
      }

      // Format number
      const formatted = formatNumber(
        value,
        locale || 'en-US',
        decimals !== undefined ? decimals : 2
      );

      const result = {
        formatted,
        locale: locale || 'en-US',
        original: value,
      };
      
      // Check if this is part of a workflow chain
      if (__workflow__) {
        const workflow = __workflow__;
        const currentStep = workflow.current_step || 0;
        const totalSteps = workflow.total_steps || 0;
        const trace = workflow.trace || [];
        
        // Add current step to trace
        trace.push({
          step: currentStep + 1,
          agent: AGENT_ID,
          result: result,
          timestamp: new Date().toISOString(),
          duration_ms: 0
        });
        
        console.log(`\n🔗 Workflow step ${currentStep + 1}/${totalSteps} complete`);
        console.log(`   Result: ${JSON.stringify(result).substring(0, 100)}...`);
        
        // Check if this is the last step
        if (currentStep + 1 >= totalSteps) {
          // Last step - return to coordinator
          console.log(`✅ Final step complete, returning to coordinator`);
          const response = createMessage(
            'inform',
            AGENT_ID,
            [message.sender],
            'workflow_complete',
            {
              ...result,
              __workflow__: {
                ...workflow,
                trace,
                completed: true
              }
            }
          );
          return res.json(response);
        }
        
        // Not the last step - call next agent
        const nextStepIdx = currentStep + 1;
        const nextStep = workflow.steps[nextStepIdx];
        const nextAgentAddress = nextStep.agent_address;
        const nextIntent = nextStep.intent;
        const nextParams = { ...nextStep.params };
        
        console.log(`➡️  Calling next agent: ${nextStep.agent_id}`);
        
        // Auto-wire params from my result
        for (const [key, value] of Object.entries(result)) {
          if (!(key in nextParams) && typeof value !== 'object') {
            nextParams[key] = value;
          }
        }
        
        // Update workflow context
        const updatedWorkflow = {
          ...workflow,
          current_step: nextStepIdx,
          trace,
          previous_result: result
        };
        
        // Call next agent
        try {
          console.log(`📤 Delegating to ${nextAgentAddress}`);
          const axios = require('axios');
          const nextResponse = await axios.post(
            `${nextAgentAddress}/agent/message`,
            createMessage(
              'request',
              AGENT_ID,
              [nextStep.agent_id],
              nextIntent,
              {
                ...nextParams,
                __workflow__: updatedWorkflow
              }
            )
          );
          
          return res.json(nextResponse.data);
        } catch (error) {
          throw new Error(`Failed to call next agent: ${error.message}`);
        }
      }
      
      // Normal response (no workflow)
      const response = createMessage(
        'inform',
        AGENT_ID,
        [message.sender],
        'formatting_result',
        result
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
  try {
    const manifestPath = join(__dirname, '..', 'manifest.json');
    const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
    res.json(manifest);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load manifest' });
  }
});

// ========== Start Server ==========

app.listen(PORT, () => {
  console.log(`🚀 Formatting Agent running on port ${PORT}`);
  console.log(`   Agent ID: ${AGENT_ID}`);
  console.log(`   Health: http://localhost:${PORT}/health`);
  console.log(`   Manifest: http://localhost:${PORT}/manifest`);
});

