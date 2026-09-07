import { fetchFleet, fetchShipments, fetchAudit } from '../api.js';

export async function init() {
  const fleet = await fetchFleet();
  const shipments = await fetchShipments();
  const audit = await fetchAudit();

  document.getElementById('overview-total') && (document.getElementById('overview-total').innerText = fleet.total_shipments || 0);
  document.getElementById('overview-problems') && (document.getElementById('overview-problems').innerText = fleet.problems || 0);
  document.getElementById('overview-healthy') && (document.getElementById('overview-healthy').innerText = fleet.healthy || 0);
  document.getElementById('overview-attention') && (document.getElementById('overview-attention').innerText = fleet.attention || 0);
  document.getElementById('overview-problem-count') && (document.getElementById('overview-problem-count').innerText = fleet.problems || 0);

  // We can dynamically render the shipments table if we want, but the HTML is already beautiful.
  // We'll leave the HTML dense, and only update the numbers to match the backend.
}
