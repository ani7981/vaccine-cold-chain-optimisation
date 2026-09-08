// In Vite dev server (port 5173/3000), API runs on 8001; in Docker/production, reverse-proxied at /api
const isDev = typeof window !== 'undefined' && (location.port === '5173' || location.port === '3000');
export const API_BASE = isDev ? `${location.protocol}//${location.hostname}:8001/api` : '/api';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {headers: {'Content-Type': 'application/json'}, ...options});
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || `Request failed (${res.status})`);
  return res.json();
}
export const fetchShipments = () => request('/shipments/');
export const fetchShipment = id => request(`/shipments/${encodeURIComponent(id)}`);
export const fetchTelemetry = id => request(`/shipments/${encodeURIComponent(id)}/telemetry`);
export const fetchProblems = id => id ? request(`/shipments/${encodeURIComponent(id)}/problems`) : request('/problems/');
export const fetchProblem = id => request(`/problems/${encodeURIComponent(id)}`);
export const fetchFleet = () => request('/fleet/');
export const fetchAudit = () => request('/audit/');
export const verifyAudit = () => request('/audit/verify', {method: 'POST'});
export const startSimulation = () => request('/simulation/start', {method: 'POST'});
export const rerouteShipment = (id, target_depot_id) => request(`/shipments/${encodeURIComponent(id)}/reroute`, {method:'POST', body: JSON.stringify({target_depot_id})});
export const acknowledgeProblem = id => request(`/problems/${encodeURIComponent(id)}/acknowledge`, {method:'POST', body:'{}'});
export const overrideProblem = (id, note) => request(`/problems/${encodeURIComponent(id)}/override`, {method:'POST', body:JSON.stringify({note})});
export const resolveProblem = (id, resolution) => request(`/problems/${encodeURIComponent(id)}/resolve`, {method: 'POST', body: JSON.stringify(resolution)});
export const transitionProblem = (id, transition) => request(`/problems/${encodeURIComponent(id)}/transition`, {method: 'POST', body: JSON.stringify(transition)});
export const fetchProblemHistory = id => request(`/problems/${encodeURIComponent(id)}/history`);
export const fetchVehicles = status => request(status ? `/fleet/vehicles?status=${encodeURIComponent(status)}` : '/fleet/vehicles');
export const fetchVehicle = id => request(`/fleet/vehicles/${encodeURIComponent(id)}`);
export const fetchAiModelInfo = () => request('/analytics/ai-model-info');
export const fetchAiInsights = id => request(`/analytics/ai-insights/${encodeURIComponent(id)}`);
export const fetchRerouteCandidates = id => request(`/routing/reroute-candidates/${encodeURIComponent(id)}`);
export const fetchCorridors = () => request('/routing/corridors');
export const fetchSensorDiagnostics = id => request(`/telemetry/diagnostics/${encodeURIComponent(id)}`);
export const ingestTelemetry = packet => request('/telemetry/ingest', {method: 'POST', body: JSON.stringify(packet)});
export const ingestTelemetryBatch = packets => request('/telemetry/ingest-batch', {method: 'POST', body: JSON.stringify(packets)});
export const fetchMerkleRoot = () => request('/audit/merkle-root');
export const fetchMerkleProof = eventId => request(`/audit/merkle-proof/${encodeURIComponent(eventId)}`);
export const verifyMerkleProof = (leafHash, proofPath, expectedRoot) => request('/audit/verify-proof', {
  method: 'POST',
  body: JSON.stringify({leaf_hash: leafHash, proof_path: proofPath, expected_root: expectedRoot})
});
export const simulateAuditTamper = (targetIndex = 0) => request('/audit/simulate-tamper', {
  method: 'POST',
  body: JSON.stringify({target_index: targetIndex})
});
export const fetchBatchCertificate = (shipmentId, actor = "Chief_Regulatory_Officer") => 
  request(`/audit/certificate/${encodeURIComponent(shipmentId)}?actor=${encodeURIComponent(actor)}`);
export const fetchSimulationStatus = () => request('/simulation/status');
export const injectSimulationChaos = (shipmentId, incidentType, durationSeconds = 300) => request('/simulation/inject-incident', {
  method: 'POST',
  body: JSON.stringify({ shipment_id: shipmentId, incident_type: incidentType, duration_seconds: durationSeconds })
});
export const clearSimulationChaos = (shipmentId) => request(
  shipmentId ? `/simulation/clear-incidents?shipment_id=${encodeURIComponent(shipmentId)}` : '/simulation/clear-incidents',
  { method: 'POST' }
);



