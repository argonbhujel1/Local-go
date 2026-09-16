/* LocalGo core client utilities */
(function () {
  // Auto-dismiss toasts
  setTimeout(() => {
    document.querySelectorAll('.toast').forEach(t => t.remove());
  }, 4000);

  // CSRF helper for fetch
  window.getCsrf = function () {
    const m = document.querySelector('meta[name="csrf-token"]');
    if (m) return m.content;
    const input = document.querySelector('input[name="csrf_token"]');
    return input ? input.value : '';
  };

  window.api = async function (url, opts = {}) {
    const headers = Object.assign({
      'Content-Type': 'application/json',
      'X-CSRFToken': window.getCsrf(),
    }, opts.headers || {});
    const res = await fetch(url, Object.assign({}, opts, { headers }));
    return res.json();
  };

  // Socket.IO if available
  if (typeof io !== 'undefined') {
    window.socket = io({ transports: ['websocket', 'polling'] });
    window.socket.on('connect', () => console.log('[LocalGo] socket connected'));
    window.socket.on('notification', (data) => {
      if (Notification.permission === 'granted') {
        new Notification(data.title || 'LocalGo', { body: data.body });
      }
    });
  }

  // Request notification permission
  if ('Notification' in window && Notification.permission === 'default') {
    // Don't auto-prompt; let UI trigger
  }
})();