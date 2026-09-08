// Docker exposes this project's API on 8001 so it does not collide with other local services.
export const API_BASE = `${location.protocol}//${location.hostname}:8001/api`;
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

