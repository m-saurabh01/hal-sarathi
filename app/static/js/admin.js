(() => {
  const form = document.getElementById('uploadForm');
  const result = document.getElementById('result');
  const busy = document.getElementById('busy');
  const btn = document.getElementById('uploadBtn');

  function renderStatus(payload) {
    if (payload.errors) {
      const items = payload.errors.map(e => `<li>${e}</li>`).join('');
      result.innerHTML = `<div class="alert alert-danger"><strong>Validation errors</strong><ul class="mb-0">${items}</ul></div>`;
      return;
    }
    const s = payload.stats || {};
    result.innerHTML = `<div class="alert alert-success">Applied. Added: <strong>${s.added||0}</strong>, Updated: <strong>${s.updated||0}</strong>, Removed: <strong>${s.removed||0}</strong>.</div>`;
  }

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    result.textContent = '';
    busy.classList.remove('d-none');
    btn.disabled = true;
    try {
      const data = new FormData(form);
      const res = await fetch('/admin/upload', {
        method: 'POST',
        body: data
      });
      const payload = await res.json().catch(() => ({ error: 'Invalid JSON response' }));
      if (!res.ok) {
        renderStatus(payload);
      } else {
        renderStatus(payload);
      }
    } catch (err) {
      result.innerHTML = `<div class="alert alert-danger">Upload failed. ${err?.message||err}</div>`;
    } finally {
      busy.classList.add('d-none');
      btn.disabled = false;
      form.reset();
    }
  });
})();
