let ws = null;

export function connectWebSocket(onMessage) {
  if (ws) ws.close();
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const isDev = location.port === '5173' || location.port === '3000';
  const wsUrl = isDev
    ? `${protocol}//${location.hostname}:8001/api/ws`
    : `${protocol}//${location.host}/api/ws`;
  ws = new WebSocket(wsUrl);

  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (onMessage) onMessage(data);
    } catch (e) {
      console.error("WS Parse error", e);
    }
  };

  ws.onclose = () => {
    setTimeout(() => connectWebSocket(onMessage), 2000);
  };
}
