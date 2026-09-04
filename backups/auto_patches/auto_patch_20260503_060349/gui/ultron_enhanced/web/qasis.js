// QASIS Playground JS
const modelSelect = document.getElementById('modelSelect');
const modelInfo = document.getElementById('modelInfo');
const chatArea = document.getElementById('chatArea');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const diagnosticsBar = document.getElementById('diagnosticsBar');

let currentModel = null;
let currentProvider = null;
let models = [];

function addMessage(text, sender) {
  const msg = document.createElement('div');
  msg.className = 'chat-message ' + sender;
  msg.textContent = text;
  chatArea.appendChild(msg);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function setDiagnostics(msg, isError = false) {
  diagnosticsBar.textContent = msg;
  diagnosticsBar.style.display = msg ? 'block' : 'none';
  diagnosticsBar.style.color = isError ? '#ff4e4e' : '#ffb347';
}

function updateModelInfo() {
  if (!currentModel) {
    modelInfo.textContent = 'Select a model to begin.';
    return;
  }
  const m = models.find(x => x.name === currentModel && x.provider === currentProvider);
  if (!m) return;
  modelInfo.textContent = `${m.name} (${m.provider}) - ${m.description || ''}`;
}

function loadModels() {
  fetch('/api/llm/unified-models')
    .then(r => r.json())
    .then(data => {
      models = data.models || [];
      modelSelect.innerHTML = '';
      models.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.name + '|' + m.provider;
        opt.textContent = `${m.name} (${m.provider})`;
        modelSelect.appendChild(opt);
      });
      if (models.length) {
        const first = models[0];
        currentModel = first.name;
        currentProvider = first.provider;
        modelSelect.value = first.name + '|' + first.provider;
        updateModelInfo();
      }
    })
    .catch(e => setDiagnostics('Failed to load models: ' + e, true));
}

modelSelect.addEventListener('change', () => {
  const [name, provider] = modelSelect.value.split('|');
  fetch('/api/llm/unified-switch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: name, provider })
  })
    .then(r => r.json())
    .then(resp => {
      if (resp.status !== 'success') {
        setDiagnostics(resp.message || 'Model switch failed', true);
      } else {
        setDiagnostics('Model switched to ' + name + ' (' + provider + ')');
        currentModel = name;
        currentProvider = provider;
        updateModelInfo();
      }
    })
    .catch(e => setDiagnostics('Model switch error: ' + e, true));
});

sendBtn.addEventListener('click', sendPrompt);
chatInput.addEventListener('keydown', e => { if (e.key === 'Enter') sendPrompt(); });

function sendPrompt() {
  const prompt = chatInput.value.trim();
  if (!prompt) return;
  addMessage(prompt, 'user');
  chatInput.value = '';
  setDiagnostics('Thinking...');
  fetch('/api/llm/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: prompt })
  })
    .then(r => r.json())
    .then(resp => {
      if (resp.error) {
        setDiagnostics(resp.error, true);
        addMessage('❌ ' + resp.error, 'llm');
      } else {
        setDiagnostics('');
        addMessage(resp.response, 'llm');
      }
    })
    .catch(e => {
      setDiagnostics('Error: ' + e, true);
      addMessage('❌ ' + e, 'llm');
    });
}

window.onload = loadModels;
