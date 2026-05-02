/* ================================================================
   FSB — Chat IA Script  |  static/js/chat.js
   ================================================================ */

let conversationId = null;
let agentType = 'assistant_admin';
let isTyping = false;

document.addEventListener('DOMContentLoaded', function () {

  /* Read initial values from data attributes on body */
  const chatEl = document.getElementById('chatApp');
  if (!chatEl) return;

  conversationId = chatEl.dataset.convId || null;
  agentType      = chatEl.dataset.agentType || 'assistant_admin';

  /* Scroll to bottom on load */
  scrollChat();

  /* Textarea auto-resize */
  const textarea = document.getElementById('chatInput');
  if (textarea) {
    textarea.addEventListener('input', function () {
      this.style.height = 'auto';
      this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
    textarea.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  /* Quick buttons */
  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const msg = this.dataset.msg;
      if (msg && textarea) {
        textarea.value = msg;
        sendMessage();
      }
    });
  });

});

/* ---- Send message ---- */
async function sendMessage() {
  const textarea = document.getElementById('chatInput');
  const messages = document.getElementById('chatMessages');
  if (!textarea || !messages) return;

  const text = textarea.value.trim();
  if (!text || isTyping) return;

  textarea.value = '';
  textarea.style.height = 'auto';

  /* Remove welcome screen if present */
  const welcome = document.getElementById('chatWelcome');
  if (welcome) welcome.remove();

  /* Append user message */
  appendMessage('user', text);

  /* Show typing indicator */
  showTyping(true);
  isTyping = true;

  try {
    const resp = await fetch('/ai/chat/send/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrf(),
      },
      body: JSON.stringify({
        message: text,
        agent_type: agentType,
        conversation_id: conversationId,
      }),
    });

    const data = await resp.json();
    showTyping(false);
    isTyping = false;

    if (data.response) {
      appendMessage('assistant', data.response);
      if (data.conversation_id) conversationId = data.conversation_id;
    } else {
      appendMessage('assistant', 'Désolé, une erreur est survenue. Veuillez réessayer.');
    }
  } catch (err) {
    showTyping(false);
    isTyping = false;
    appendMessage('assistant', 'Erreur de connexion. Vérifiez votre réseau.');
  }
}

/* ---- Append a message bubble ---- */
function appendMessage(role, text) {
  const container = document.getElementById('chatMessages');
  if (!container) return;

  const now = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  const initials = role === 'user' ? getUserInitials() : '🤖';

  const row = document.createElement('div');
  row.className = `msg-row ${role}`;
  row.style.animation = 'fadeUp 0.3s ease both';

  const avatarHTML = role === 'user'
    ? `<div class="msg-av user-av">${initials}</div>`
    : `<div class="msg-av bot-av" style="font-size:1rem">${initials}</div>`;

  row.innerHTML = `
    ${avatarHTML}
    <div>
      <div class="msg-bubble">${escapeHtml(text).replace(/\n/g, '<br>')}</div>
      <div class="msg-time">${now}</div>
    </div>
  `;

  /* Insert before typing indicator */
  const typing = document.getElementById('typingIndicator');
  if (typing) container.insertBefore(row, typing);
  else container.appendChild(row);

  scrollChat();
}

/* ---- Typing indicator ---- */
function showTyping(show) {
  const indicator = document.getElementById('typingIndicator');
  if (indicator) {
    indicator.style.display = show ? 'flex' : 'none';
    if (show) scrollChat();
  }
}

/* ---- Scroll to bottom ---- */
function scrollChat() {
  const el = document.getElementById('chatMessages');
  if (el) el.scrollTop = el.scrollHeight;
}

/* ---- Get user initials from DOM ---- */
function getUserInitials() {
  const av = document.querySelector('.topbar .user-av');
  return av ? av.textContent.trim() : 'ME';
}

/* ---- Escape HTML ---- */
function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

/* ---- CSRF helper (from fsb.js or inline) ---- */
function getCsrf() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}