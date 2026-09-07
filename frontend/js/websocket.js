let ws = null;

export function connectWebSocket(onMessage) {
  if (ws) ws.close();
  ws = new WebSocket('ws://localhost:8001/api/ws');
  
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
