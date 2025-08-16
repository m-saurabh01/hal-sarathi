// reserved for future enhancements
// Chat UI behaviors (offline-friendly)
(function(){
  const form = document.getElementById('form');
  const input = document.getElementById('input');
  const chat = document.getElementById('chat');
  const chips = document.getElementById('chips');

  // Add message (bubble + optional suggestions) to chat
  function addMessage(role, html) {
    const row = document.createElement('div');
    row.className = `msg-row ${role}`;

    // Avatar/Icon
    const icon = document.createElement('div');
    icon.className = 'msg-icon';
    const img = document.createElement('img');
    img.src = role === 'user' ? '/static/img/user.svg' : '/static/img/chat-logo.png';
    img.alt = role === 'user' ? 'You' : 'Bot';
    icon.appendChild(img);

    // Content container (bubble + suggestions stacked)
    const content = document.createElement('div');
    content.className = 'msg-content'; // flex column via CSS

    // Message bubble
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerHTML = html;
    content.appendChild(bubble);

    // Append based on role
    if (role === 'user') {
      row.appendChild(content);
      row.appendChild(icon);
    } else {
      row.appendChild(icon);
      row.appendChild(content);
    }

    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;

    return { row, content, bubble }; // return content too for suggestions
  }

  // Add bot typing placeholder
  function addTypingPlaceholder() {
    const { content, bubble } = addMessage('bot', '');
    // Add placeholder HTML inside the bubble
    bubble.innerHTML = '<span class="placeholder-glow"><span class="placeholder col-8"></span><br><span class="placeholder col-5 mt-1"></span></span>';
    return bubble; // return bubble for typeInto
  }

  // Typing effect for bot
  function typeInto(el, text, speed=12){
    let i = 0;
    const timer = setInterval(()=>{
      i += Math.max(1, Math.round(text.length/120));
      el.innerHTML = text.slice(0, i);
      chat.scrollTop = chat.scrollHeight;
      if(i >= text.length){ clearInterval(timer); }
    }, speed);
  }

  // Format bot reply text (paragraphs / lists)
  function formatAnswer(text){
    const lines = text.replace(/\r\n/g, '\n').split('\n').map(s=>s.trim()).filter(Boolean);
    if(lines.length === 0) return '';
    const listy = lines.filter(l=>/^[-*\u2022]\s|^\d+[.)]\s/.test(l)).length >= Math.ceil(lines.length/2);
    if(listy){
      const items = lines.map(l=> l.replace(/^[-*\u2022]\s|^\d+[.)]\s/, '').trim()).filter(Boolean);
      return '<ul class="mb-0">' + items.map(it=> `<li>${escapeHTML(it)}</li>`).join('') + '</ul>';
    }
    return lines.map(p=> `<p class="mb-2">${escapeHTML(p)}</p>`).join('');
  }

  function escapeHTML(s){
    const div = document.createElement('div');
    div.innerText = s; 
    return div.innerHTML;
  }

  // Load sample chips
  async function loadSamples(){
    try{
      const res = await fetch('/samples');
      const data = await res.json();
      (data.samples || []).forEach(q => {
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'chip btn btn-sm btn-outline-secondary';
        b.textContent = q;
        b.addEventListener('click', ()=>{
          input.value = q; 
          form.dispatchEvent(new Event('submit'));
        });
        chips.appendChild(b);
      });
    }catch{}
  }
  loadSamples();

  // Handle user submitting message
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    // Add user message
    addMessage('user', escapeHTML(text));
    input.value = '';

    // Add bot typing placeholder
    const placeholder = addTypingPlaceholder();

    try {
      const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();

      // Render bot reply
      const html = formatAnswer(String(data.reply || ''));
      placeholder.innerHTML = '';
      typeInto(placeholder, html);

      // Render suggestions below the bubble in column
      const suggestions = Array.isArray(data.suggestions) ? data.suggestions : [];
      if(suggestions.length){
        const wrap = document.createElement('div');
        wrap.className = 'msg-suggestions';
        const list = document.createElement('div');
        list.className = 'd-flex flex-wrap gap-2';

        suggestions.forEach(q => {
          const b = document.createElement('button');
          b.type = 'button';
          b.className = 'chip btn btn-sm btn-outline-secondary suggestion-btn';
          b.textContent = q;
          b.addEventListener('click', (ev) => {
            ev.preventDefault();
            ev.stopPropagation();
            wrap.remove(); // remove current suggestions
            input.value = q;
            form.dispatchEvent(new Event('submit', { cancelable: true }));
          });
          list.appendChild(b);
        });

        wrap.appendChild(list);

        // Append suggestions to the content container
        const row = placeholder.closest('.msg-row');
        const content = row.querySelector('.msg-content');
        if(content){
          content.querySelectorAll('.msg-suggestions').forEach(el => el.remove());
          content.appendChild(wrap);
        }
      }

    } catch (err) {
      placeholder.innerHTML = 'Error: failed to reach server.';
    }
  });

})();
