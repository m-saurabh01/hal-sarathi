/**
 * HAL Sarathi Chatbot Widget
 * Usage: <hal-chatbot endpoint="http://localhost:8000"></hal-chatbot>
 */
(function(){
  const CSS = `
:host{--c:#0b2447;--bg:#fff;--bgl:#f8fafc;--bdr:#e5e7eb;--txt:#0b1220;--shd:0 4px 24px rgba(0,0,0,.18);font:14px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
*{box-sizing:border-box;margin:0;padding:0}
.tr{position:fixed;bottom:20px;right:20px;width:60px;height:60px;border-radius:50%;background:var(--bg);border:2px solid var(--bdr);cursor:pointer;box-shadow:var(--shd);display:flex;align-items:center;justify-content:center;z-index:9998;animation:br 2.5s ease-in-out infinite}
.tr:hover{animation:none;transform:scale(1.1)}
.tr img{width:48px;height:48px;object-fit:contain}
.tr.h{display:none}
@keyframes br{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}
.gr{position:fixed;bottom:90px;right:20px;background:var(--bg);color:var(--txt);padding:12px 16px;border-radius:12px;box-shadow:var(--shd);font-size:14px;max-width:220px;z-index:9997;opacity:0;transform:translateY(10px) scale(.9);pointer-events:none;transition:.3s}
.gr.s{opacity:1;transform:none;pointer-events:auto}
.gr::after{content:'';position:absolute;bottom:-8px;right:24px;border:8px solid transparent;border-top-color:var(--bg)}
.gr-x{position:absolute;top:4px;right:6px;background:0;border:0;color:#6b7280;cursor:pointer;font-size:14px}
.pn{position:fixed;bottom:20px;right:20px;width:380px;height:520px;max-height:calc(100vh - 40px);max-width:calc(100vw - 40px);background:var(--bg);border-radius:16px;box-shadow:var(--shd);display:flex;flex-direction:column;z-index:9999;overflow:hidden;transform:scale(.8) translateY(20px);opacity:0;pointer-events:none;transition:.25s}
.pn.o{transform:none;opacity:1;pointer-events:auto}
.hd{background:var(--c);color:#fff;padding:14px 16px;display:flex;align-items:center;gap:12px}
.hd-lg{width:36px;height:36px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;overflow:hidden}
.hd-lg img{width:30px;height:30px;object-fit:contain}
.hd-i{flex:1}
.hd-t{font-weight:600;font-size:16px}
.hd-s{font-size:11px;opacity:.85;margin-top:2px}
.cl{background:rgba(255,255,255,.1);border:0;color:#fff;cursor:pointer;padding:6px;border-radius:6px;display:flex}
.cl:hover{background:rgba(255,255,255,.2)}
.ms{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px;background:#f9fafb}
.m{display:flex;gap:10px;align-items:flex-start}
.m.u{flex-direction:row-reverse}
.av{width:32px;height:32px;border-radius:50%;background:var(--bg);border:1px solid var(--bdr);display:flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0}
.av img{width:28px;height:28px;object-fit:contain}
.m.u .av{background:0;border:0}
.bb{max-width:75%;padding:10px 14px;border-radius:14px;background:var(--bg);border:1px solid var(--bdr);color:var(--txt);word-wrap:break-word}
.m.u .bb{background:#1e40af;border-color:#1e40af;color:#fff}
.bb p{margin:0 0 8px}.bb p:last-child{margin:0}
.bb ul,.bb ol{margin:8px 0;padding-left:20px}
.bb li{margin:4px 0}
.bb strong{font-weight:600}
.bb code{background:rgba(0,0,0,.06);padding:2px 6px;border-radius:4px;font:12px Monaco,Menlo,monospace}
.bb pre{background:#1e293b;color:#e2e8f0;padding:10px 12px;border-radius:8px;overflow-x:auto;margin:8px 0}
.bb pre code{background:0;padding:0}
.bb a{color:var(--c);text-decoration:underline}
.m.u .bb a{color:#fff}
.sg{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.sg button{background:var(--bgl);border:1px solid var(--bdr);border-radius:16px;padding:5px 12px;font-size:12px;cursor:pointer;color:var(--txt);transition:.15s}
.sg button:hover{background:var(--c);border-color:var(--c);color:#fff}
.ia{padding:12px 14px;border-top:1px solid var(--bdr);display:flex;gap:10px;background:var(--bg)}
.ia input{flex:1;border:1px solid var(--bdr);border-radius:10px;padding:10px 14px;font-size:14px;outline:0}
.ia input:focus{border-color:var(--c)}
.ia button{background:var(--c);color:#fff;border:0;border-radius:10px;padding:10px 18px;cursor:pointer;font:500 14px inherit}
.ia button:hover{background:#0a1f3d}
.ia button:disabled{opacity:.5;cursor:not-allowed}
.tp{display:flex;gap:4px;padding:4px 0}
.tp span{width:6px;height:6px;background:#9ca3af;border-radius:50%;animation:tb 1.4s infinite ease-in-out both}
.tp span:nth-child(1){animation-delay:-.32s}
.tp span:nth-child(2){animation-delay:-.16s}
@keyframes tb{0%,80%,100%{transform:scale(.8);opacity:.5}40%{transform:scale(1);opacity:1}}
@media(max-width:420px){.pn{width:calc(100vw - 16px);height:calc(100vh - 100px);bottom:8px;right:8px;border-radius:12px}.tr{bottom:12px;right:12px;width:52px;height:52px}.tr img{width:40px;height:40px}}`;

  class HalChatbot extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({mode:'open'});
      this._ep = '';
      this._open = false;
    }
    static get observedAttributes() { return ['endpoint']; }
    attributeChangedCallback(n,o,v) { if(n==='endpoint') this._ep = v; }
    connectedCallback() {
      this._ep = this.getAttribute('endpoint') || '';
      this._render();
      this._events();
    }
    _logo() { return this._ep + '/static/img/chat-logo.png'; }
    _user() { return this._ep + '/static/img/user.svg'; }
    _render() {
      const l = this._logo();
      this.shadowRoot.innerHTML = `<style>${CSS}</style>
<div class="gr"><button class="gr-x">×</button>Hi! How can I help you today?</div>
<button class="tr"><img src="${l}" alt="Chat"/></button>
<div class="pn" role="dialog">
  <div class="hd">
    <div class="hd-lg"><img src="${l}" alt=""/></div>
    <div class="hd-i"><div class="hd-t">HAL Sarathi</div><div class="hd-s">AI Assistant</div></div>
    <button class="cl"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
  </div>
  <div class="ms"><div class="m bot"><div class="av"><img src="${l}" alt=""/></div><div class="bb">Hi! How can I help you today?</div></div></div>
  <form class="ia"><input type="text" placeholder="Type your message..." required/><button type="submit">Send</button></form>
</div>`;
    }
    _events() {
      const $ = s => this.shadowRoot.querySelector(s);
      const tr=$('.tr'), pn=$('.pn'), cl=$('.cl'), fm=$('.ia'), ip=$('.ia input'), ms=$('.ms'), gr=$('.gr'), gx=$('.gr-x');
      let gd=false;
      const showG=()=>{if(!this._open&&!gd){gr.classList.add('s');setTimeout(()=>gr.classList.remove('s'),5000);}};
      const hideG=()=>gr.classList.remove('s');
      setTimeout(showG,2000);
      setInterval(showG,30000);
      gx.onclick=e=>{e.stopPropagation();hideG();gd=true;};
      gr.onclick=()=>{hideG();this._openChat();};
      tr.onclick=()=>{hideG();this._openChat();};
      cl.onclick=()=>this._closeChat();
      fm.onsubmit=async e=>{e.preventDefault();const t=ip.value.trim();if(!t)return;ip.value='';this._addMsg('u',t);await this._send(t);};
      ms.onclick=async e=>{if(e.target.classList.contains('sg')&&e.target.tagName==='BUTTON'){const t=e.target.textContent;this._addMsg('u',t);await this._send(t);}};
    }
    _openChat() {
      const tr=this.shadowRoot.querySelector('.tr'), pn=this.shadowRoot.querySelector('.pn'), ip=this.shadowRoot.querySelector('.ia input');
      tr.classList.add('h'); pn.classList.add('o'); this._open=true; setTimeout(()=>ip.focus(),100);
    }
    _closeChat() {
      const tr=this.shadowRoot.querySelector('.tr'), pn=this.shadowRoot.querySelector('.pn');
      pn.classList.remove('o'); tr.classList.remove('h'); this._open=false;
    }
    _addMsg(r,t,sg=[]) {
      const ms=this.shadowRoot.querySelector('.ms'), isB=r==='bot';
      const d=document.createElement('div'); d.className='m '+(isB?'bot':'u');
      const av=document.createElement('div'); av.className='av';
      av.innerHTML=`<img src="${isB?this._logo():this._user()}" alt=""/>`;
      const bb=document.createElement('div'); bb.className='bb'; bb.innerHTML=this._md(t);
      d.appendChild(av); d.appendChild(bb); ms.appendChild(d);
      if(isB&&sg.length){const s=document.createElement('div');s.className='sg';sg.forEach(x=>{const b=document.createElement('button');b.textContent=x;b.onclick=()=>{this._addMsg('u',x);this._send(x);};s.appendChild(b);});bb.appendChild(s);}
      ms.scrollTop=ms.scrollHeight;
      return d;
    }
    _addTyping() {
      const ms=this.shadowRoot.querySelector('.ms');
      const d=document.createElement('div'); d.className='m bot';
      d.innerHTML=`<div class="av"><img src="${this._logo()}" alt=""/></div><div class="bb"><div class="tp"><span></span><span></span><span></span></div></div>`;
      ms.appendChild(d); ms.scrollTop=ms.scrollHeight; return d;
    }
    _md(t) {
      if(!t) return '';
      let h=t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      h=h.replace(/```(\w*)\n?([\s\S]*?)```/g,'<pre><code>$2</code></pre>');
      h=h.replace(/`([^`]+)`/g,'<code>$1</code>');
      h=h.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
      h=h.replace(/\*([^*]+)\*/g,'<em>$1</em>');
      h=h.replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank">$1</a>');
      const ln=h.split('\n'), rs=[];
      let inL=false, lt='ul';
      for(const l of ln){
        const tr=l.trim();
        if(/^[-*•]\s/.test(tr)){if(!inL||lt!=='ul'){if(inL)rs.push(lt==='ul'?'</ul>':'</ol>');rs.push('<ul>');inL=true;lt='ul';}rs.push('<li>'+tr.replace(/^[-*•]\s/,'')+'</li>');}
        else if(/^\d+[.)]\s/.test(tr)){if(!inL||lt!=='ol'){if(inL)rs.push(lt==='ul'?'</ul>':'</ol>');rs.push('<ol>');inL=true;lt='ol';}rs.push('<li>'+tr.replace(/^\d+[.)]\s/,'')+'</li>');}
        else{if(inL){rs.push(lt==='ul'?'</ul>':'</ol>');inL=false;}if(tr)rs.push('<p>'+tr+'</p>');}
      }
      if(inL) rs.push(lt==='ul'?'</ul>':'</ol>');
      return rs.join('');
    }
    async _send(t) {
      const btn=this.shadowRoot.querySelector('.ia button'), ip=this.shadowRoot.querySelector('.ia input');
      btn.disabled=true; ip.disabled=true;
      const tp=this._addTyping();
      try {
        const r=await fetch(this._ep+'/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
        const d=await r.json(); tp.remove();
        await this._typeMsg(d.reply||'Sorry, something went wrong.',d.suggestions||[]);
      } catch(e) { tp.remove(); await this._typeMsg('Unable to connect.',[]); }
      btn.disabled=false; ip.disabled=false; ip.focus();
    }
    async _typeMsg(t,sg) {
      const ms=this.shadowRoot.querySelector('.ms');
      const d=document.createElement('div'); d.className='m bot';
      const av=document.createElement('div'); av.className='av';
      av.innerHTML=`<img src="${this._logo()}" alt=""/>`;
      const bb=document.createElement('div'); bb.className='bb';
      const p=document.createElement('p'); p.style.margin='0'; bb.appendChild(p);
      d.appendChild(av); d.appendChild(bb); ms.appendChild(d); ms.scrollTop=ms.scrollHeight;
      const ch=t.split(''); let i=0;
      const sp=Math.max(20,Math.min(40,1500/ch.length));
      await new Promise(r=>{const n=()=>{if(i<ch.length){p.textContent+=ch[i++];ms.scrollTop=ms.scrollHeight;setTimeout(n,sp);}else r();};n();});
      p.remove(); bb.innerHTML=this._md(t);
      if(sg.length){const s=document.createElement('div');s.className='sg';sg.forEach(x=>{const b=document.createElement('button');b.textContent=x;b.onclick=()=>{this._addMsg('u',x);this._send(x);};s.appendChild(b);});bb.appendChild(s);ms.scrollTop=ms.scrollHeight;}
      return d;
    }
  }
  if(!customElements.get('hal-chatbot')) customElements.define('hal-chatbot',HalChatbot);
  const sc=document.currentScript;
  if(sc&&sc.dataset.endpoint) document.addEventListener('DOMContentLoaded',()=>{const w=document.createElement('hal-chatbot');w.setAttribute('endpoint',sc.dataset.endpoint);document.body.appendChild(w);});
})();
