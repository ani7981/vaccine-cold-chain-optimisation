export const API_BASE = 'http://localhost:8001/api';

export async function fetchShipments() {
  const res = await fetch(`${API_BASE}/shipments/`);
  return res.json();
}

export async function fetchShipment(id) {
  const res = await fetch(`${API_BASE}/shipments/${id}`);
  return res.json();
}

export async function fetchProblems(shipmentId) {
  const res = await fetch(`${API_BASE}/shipments/${shipmentId}/problems`);
  return res.json();
}

export async function fetchFleet() {
  const res = await fetch(`${API_BASE}/fleet/`);
  return res.json();
}

export async function fetchAudit() {
  const res = await fetch(`${API_BASE}/audit/`);
  return res.json();
}

export async function startSimulation() {
  const res = await fetch(`${API_BASE}/simulation/start`, { method: 'POST' });
  return res.json();
}
