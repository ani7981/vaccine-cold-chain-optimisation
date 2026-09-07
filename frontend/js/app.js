import { fetchShipment, fetchFleet, fetchAudit } from './api.js';
import { connectWebSocket } from './websocket.js';

// Parse query params for detail screens
const urlParams = new URLSearchParams(window.location.search);
const activeId = urlParams.get('id') || 'VK-1042';

// 1. Initial REST Sync
async function initData() {
  try {
    const shipment = await fetchShipment('ship_1');
    if (shipment && shipment.current_temperature) {
      updateDOMTelemetry(shipment.current_temperature, shipment.shipment_code);
    }
  } catch (err) {
    console.warn('Initial REST fetch failed:', err);
  }

  // Populate audit ledger if on history page
  const auditTable = document.getElementById('audit-table-body');
  if (auditTable) {
    try {
      const audits = await fetchAudit();
      if (Array.isArray(audits) && audits.length > 0) {
        auditTable.innerHTML = audits.map(a => `
          <tr class="hover:bg-vk-surface/60 transition-colors">
            <td class="py-sm px-md font-mono text-[11px] text-vk-cream">${new Date(a.timestamp).toLocaleTimeString()}</td>
            <td class="py-sm px-md font-semibold text-vk-attention">${a.event_type}</td>
            <td class="py-sm px-md font-mono text-[11px] text-vk-text-muted">${a.shipment_id || 'SYSTEM'}</td>
            <td class="py-sm px-md font-mono text-[10px] text-vk-cream truncate max-w-xs">${a.hash || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}</td>
          </tr>
        `).join('');
      }
    } catch (err) {
      console.warn('Audit fetch failed:', err);
    }
  }
}

// 2. Real-Time WebSocket Telemetry Updates
function handleLiveUpdate(msg) {
  if (msg.type === 'TELEMETRY_UPDATE' && msg.payload) {
    const { temperature, shipment_code } = msg.payload;
    updateDOMTelemetry(temperature, shipment_code);
  }
}

function updateDOMTelemetry(temp, code) {
  const formattedTemp = typeof temp === 'number' ? `${temp.toFixed(1)}°C` : temp;
  
  document.querySelectorAll('.dyn-temp').forEach(el => {
    el.innerText = formattedTemp;
  });

  if (code) {
    document.querySelectorAll('.dyn-shipment-code').forEach(el => {
      el.innerText = code;
    });
  }
}

// 3. Connect WebSocket and start initial sync
initData();
connectWebSocket(handleLiveUpdate);
