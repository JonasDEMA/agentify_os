// WebSocket connection to local agent server
let ws = null;
let isConnected = false;

// DOM elements
const chatContainer = document.getElementById('chatContainer');
const commandInput = document.getElementById('commandInput');
const sendButton = document.getElementById('sendButton');
const statusIndicator = document.getElementById('statusIndicator');

// Message type icons
const MESSAGE_ICONS = {
    'user_command': '👤',
    'agent_thinking': '💭',
    'agent_action': '⚡',
    'agent_progress': '📊',
    'agent_result': '✅',
    'agent_error': '❌',
    'agent_question': '❓',
};

// Connect to WebSocket
function connect() {
    ws = new WebSocket('ws://localhost:8765');
    
    ws.onopen = () => {
        console.log('Connected to agent');
        isConnected = true;
        statusIndicator.style.background = '#4CAF50';
        addSystemMessage('Connected to agent');
    };
    
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleAgentMessage(message);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        statusIndicator.style.background = '#f44336';
    };
    
    ws.onclose = () => {
        console.log('Disconnected from agent');
        isConnected = false;
        statusIndicator.style.background = '#ff9800';
        addSystemMessage('Disconnected from agent. Reconnecting...');
        
        // Reconnect after 3 seconds
        setTimeout(connect, 3000);
    };
}

// Send command to agent
function sendCommand() {
    const command = commandInput.value.trim();
    if (!command || !isConnected) return;
    
    // Add user message to chat
    addUserMessage(command);
    
    // Send to agent via WebSocket
    ws.send(JSON.stringify({
        message_type: 'user_command',
        command: command,
        timestamp: new Date().toISOString(),
    }));
    
    // Clear input
    commandInput.value = '';
    sendButton.disabled = true;
}

// Handle agent messages
function handleAgentMessage(message) {
    const messageType = message.message_type;
    
    switch (messageType) {
        case 'agent_thinking':
            addAgentMessage(message.message, 'thinking', MESSAGE_ICONS[messageType]);
            break;
        
        case 'agent_action':
            addAgentMessage(message.message, 'action', MESSAGE_ICONS[messageType]);
            break;
        
        case 'agent_progress':
            addProgressMessage(message);
            break;
        
        case 'agent_result':
            addAgentMessage(message.message, 'result', MESSAGE_ICONS[messageType]);
            sendButton.disabled = false;
            break;
        
        case 'agent_error':
            addAgentMessage(message.message, 'error', MESSAGE_ICONS[messageType]);
            sendButton.disabled = false;
            break;
        
        case 'agent_question':
            addAgentMessage(message.message, 'question', MESSAGE_ICONS[messageType]);
            break;
        
        default:
            console.log('Unknown message type:', messageType, message);
    }
}

// Add user message to chat
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-content">${escapeHtml(text)}</div>
        <div class="timestamp">${formatTime(new Date())}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add agent message to chat
function addAgentMessage(text, type = 'agent', icon = '🤖') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message agent ${type}`;
    messageDiv.innerHTML = `
        <div class="message-content">
            <span class="message-icon">${icon}</span>
            ${escapeHtml(text)}
        </div>
        <div class="timestamp">${formatTime(new Date())}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add progress message with progress bar
function addProgressMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent progress';
    
    let progressHtml = '';
    if (message.progress_percent !== null && message.progress_percent !== undefined) {
        progressHtml = `
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${message.progress_percent}%"></div>
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <span class="message-icon">📊</span>
            ${escapeHtml(message.message)}
            ${progressHtml}
        </div>
        <div class="timestamp">${formatTime(new Date())}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add system message
function addSystemMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';
    messageDiv.innerHTML = `
        <div class="message-content">
            <span class="message-icon">ℹ️</span>
            ${escapeHtml(text)}
        </div>
        <div class="timestamp">${formatTime(new Date())}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Event listeners
sendButton.addEventListener('click', sendCommand);
commandInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendCommand();
    }
});

// Connect on page load
connect();

