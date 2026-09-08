// ============================================================================
// VAXKAVACH INDUSTRIAL TELEMETRY MAP ENGINE
// Professional-grade GIS Operations Command Center for Cold-Chain Reefers
// ============================================================================

import * as LModule from 'leaflet';
import 'leaflet/dist/leaflet.css';

const L = window.L || LModule.default || LModule;

// ----------------------------------------------------------------------------
// DATA: Pan-India Vaccine Logistics Network & Active Telemetry
// ----------------------------------------------------------------------------
export const DEPOTS = [
  { id: 'depot_chennai', name: 'Chennai Regional Vaccine Store', city: 'Chennai', coords: [13.0827, 80.2707], type: 'Regional Hub', capacity: '2.4M doses', temp: '4.1°C' },
  { id: 'depot_vellore_dh', name: 'Vellore District Hospital Cold Store', city: 'Vellore', coords: [12.9165, 79.1325], type: 'District Depot', capacity: '120k doses', temp: '3.8°C' },
  { id: 'depot_vellore_backup', name: 'Vellore Sub-District Depot (ILR Backup)', city: 'Ranipet-Vellore', coords: [12.9350, 79.2300], type: 'Emergency Backup', capacity: '45k doses', temp: '3.5°C' },
  { id: 'depot_blr', name: 'Bengaluru Central Vaccine Facility', city: 'Bengaluru', coords: [12.9716, 77.5946], type: 'Central Store', capacity: '3.8M doses', temp: '4.0°C' },
  { id: 'depot_delhi', name: 'Delhi GMSD National Vaccine Store', city: 'New Delhi', coords: [28.6139, 77.2090], type: 'Apex National Depot', capacity: '10.5M doses', temp: '3.9°C' },
  { id: 'depot_hyd', name: 'Hyderabad State Cold Storage Unit', city: 'Hyderabad', coords: [17.3850, 78.4867], type: 'State Unit', capacity: '1.9M doses', temp: '4.2°C' },
  { id: 'depot_mum', name: 'Mumbai Western Distribution Center', city: 'Mumbai', coords: [19.0760, 72.8777], type: 'Zonal Store', capacity: '4.2M doses', temp: '3.7°C' }
];

export const CORRIDORS = {
  'NH-48': {
    name: 'NH-48 Southern Vaccine Corridor (Chennai → Vellore → Bengaluru)',
    color: '#829A80',
    path: [
      [13.0827, 80.2707], // Chennai
      [13.0125, 80.0812], // Poonamallee
      [12.9675, 79.9427], // Sriperumbudur (Km 74.2 - Breach)
      [12.8342, 79.7036], // Kanchipuram
      [12.9272, 79.3330], // Ranipet
      [12.9350, 79.2300], // Backup Depot
      [12.9165, 79.1325], // Vellore DH
      [12.7904, 78.7166], // Ambur
      [12.6322, 78.4983], // Vaniyambadi
      [12.5186, 78.2137], // Krishnagiri
      [12.7409, 77.8253], // Hosur
      [12.9716, 77.5946]  // Bengaluru
    ]
  },
  'NH-44': {
    name: 'NH-44 Central Spine (Bengaluru → Anantapur → Kurnool → Hyderabad)',
    color: '#7BD0FF',
    path: [
      [12.9716, 77.5946], // Bengaluru
      [13.3409, 77.5376], // Doddaballapur
      [14.6819, 77.6006], // Anantapur
      [15.8281, 78.0373], // Kurnool
      [16.7488, 78.0035], // Mahbubnagar
      [17.3850, 78.4867]  // Hyderabad
    ]
  },
  'NH-19': {
    name: 'NH-19 Northern Arterial (Delhi → Agra → Kanpur → Patna)',
    color: '#A4875C',
    path: [
      [28.6139, 77.2090], // Delhi
      [27.8974, 77.6744], // Mathura
      [27.1767, 78.0081], // Agra
      [26.4499, 80.3319], // Kanpur
      [26.8467, 80.9462], // Lucknow
      [25.5941, 85.1376]  // Patna
    ]
  },
  'NH-48-WEST': {
    name: 'NH-48 Western Trunk (Mumbai → Pune → Satara → Kolhapur)',
    color: '#829A80',
    path: [
      [19.0760, 72.8777], // Mumbai
      [18.7546, 73.4062], // Lonavala
      [18.5204, 73.8567], // Pune
      [17.6805, 74.0183], // Satara
      [16.7050, 74.2433]  // Kolhapur
    ]
  }
};

export const REEFERS = [
  {
    code: 'VK-1042',
    vin: 'TN-4821-HX',
    rig: 'Tata Ultra Reefer',
    driver: 'K. Muthukrishnan (+91 94441 20982)',
    coords: [12.9675, 79.9427], // Sriperumbudur Km 74.2
    corridor: 'NH-48',
    status: 'problem',
    temp: 9.4,
    delta: '+1.4°C drift above 8.0°C ceiling',
    speed: '62 km/h',
    payload: '8,400 doses · Rotavirus + Pentavalent (Batch #IND-VR-2026)',
    compressor: 'Fault: RPM 940 (Nominal 2,200) · Ambient 38.5°C',
    battery: '88% reserve (4.2h buffer)',
    recommendation: 'Divert immediately to Vellore Sub-District Depot (14 km, 18 min ETA) before thermal buffer collapses.'
  },
  {
    code: 'VK-1047',
    vin: 'DL-01-AB-3301',
    rig: 'BharatBenz 1217C',
    driver: 'R. Sharma (+91 98110 55821)',
    coords: [27.1767, 78.0081], // Agra Expressway
    corridor: 'NH-19',
    status: 'attention',
    temp: 7.2,
    delta: '+0.8°C climb · Approaching 8.0°C ceiling',
    speed: '74 km/h',
    payload: '12,000 doses · Measles-Rubella (MR)',
    compressor: 'High Load: Ambient 41.2°C · Condenser fan strain',
    battery: '92% reserve',
    recommendation: 'Pre-chill compressor cycle; monitor next telemetry packet.'
  },
  {
    code: 'VK-1039',
    vin: 'KA-XX-4521',
    rig: 'Ashok Leyland Boss 1215',
    driver: 'S. Anand (+91 98450 11203)',
    coords: [12.7409, 77.8253], // Hosur bypass
    corridor: 'NH-44',
    status: 'okay',
    temp: 4.2,
    delta: 'WHO-PQS Optimal (2°C - 8°C)',
    speed: '58 km/h',
    payload: '18,000 doses · Rabies Vaccine',
    compressor: 'Nominal: 2,100 RPM · Cycle steady',
    battery: '96% reserve',
    recommendation: 'Corridor nominal. ETA on schedule.'
  },
  {
    code: 'VK-1045',
    vin: 'MH-XX-8821',
    rig: 'Eicher Pro 3019',
    driver: 'V. Patil (+91 98200 44901)',
    coords: [18.5204, 73.8567], // Pune
    corridor: 'NH-48-WEST',
    status: 'okay',
    temp: 4.8,
    delta: 'WHO-PQS Optimal',
    speed: '65 km/h',
    payload: '15,000 doses · BCG + bOPV',
    compressor: 'Nominal: Steady cooling cycle',
    battery: '94% reserve',
    recommendation: 'Proceeding on schedule.'
  },
  {
    code: 'VK-1050',
    vin: 'GJ-06-BC-7741',
    rig: 'Tata Ultra T.7',
    driver: 'J. Patel (+91 98980 66312)',
    coords: [22.3072, 73.1812], // Vadodara
    corridor: 'NH-48-WEST',
    status: 'okay',
    temp: 3.9,
    delta: 'WHO-PQS Optimal',
    speed: '70 km/h',
    payload: '9,500 doses · Hepatitis-B',
    compressor: 'Nominal: Auto-defrost completed',
    battery: '98% reserve',
    recommendation: 'All systems within CDSCO parameters.'
  },
  {
    code: 'VK-1052',
    vin: 'WB-02-KL-9011',
    rig: 'Ashok Leyland Ecomet',
    driver: 'B. Roy (+91 98300 77410)',
    coords: [25.0108, 88.1411], // Malda
    corridor: 'NH-19',
    status: 'okay',
    temp: 5.1,
    delta: 'WHO-PQS Optimal',
    speed: '55 km/h',
    payload: '22,000 doses · DPT Booster',
    compressor: 'Nominal: Secondary compressor standby',
    battery: '91% reserve',
    recommendation: 'Optimal thermal inertia.'
  },
  {
    code: 'VK-1033',
    vin: 'TN-09-CD-1982',
    rig: 'Eicher Pro Reefer',
    driver: 'M. Selvam (+91 94432 10928)',
    coords: [12.9272, 79.3330], // Ranipet
    corridor: 'NH-48',
    status: 'okay',
    temp: 4.4,
    delta: 'WHO-PQS Optimal',
    speed: '60 km/h',
    payload: '10,000 doses · IPV Fractional',
    compressor: 'Nominal: Inverter duty 45%',
    battery: '95% reserve',
    recommendation: 'Corridor nominal.'
  },
  {
    code: 'VK-1038',
    vin: 'AP-11-TG-4421',
    rig: 'Tata Prima 2828',
    driver: 'K. Reddy (+91 98490 22391)',
    coords: [15.8281, 78.0373], // Kurnool
    corridor: 'NH-44',
    status: 'okay',
    temp: 4.6,
    delta: 'WHO-PQS Optimal',
    speed: '68 km/h',
    payload: '14,000 doses · Pentavalent',
    compressor: 'Nominal',
    battery: '89% reserve',
    recommendation: 'On route.'
  },
  {
    code: 'VK-1041',
    vin: 'UP-32-BN-8819',
    rig: 'BharatBenz 1617R',
    driver: 'A. Yadav (+91 94150 99201)',
    coords: [26.4499, 80.3319], // Kanpur
    corridor: 'NH-19',
    status: 'okay',
    temp: 4.9,
    delta: 'WHO-PQS Optimal',
    speed: '62 km/h',
    payload: '16,500 doses · Rotavirus',
    compressor: 'Nominal',
    battery: '93% reserve',
    recommendation: 'Corridor nominal.'
  },
  {
    code: 'VK-1044',
    vin: 'MH-12-PQ-3309',
    rig: 'Mahindra Blazo X',
    driver: 'D. Shinde (+91 98220 11980)',
    coords: [17.6805, 74.0183], // Satara
    corridor: 'NH-48-WEST',
    status: 'okay',
    temp: 4.1,
    delta: 'WHO-PQS Optimal',
    speed: '64 km/h',
    payload: '8,000 doses · JE Vaccine',
    compressor: 'Nominal',
    battery: '97% reserve',
    recommendation: 'Corridor nominal.'
  },
  {
    code: 'VK-1048',
    vin: 'KA-04-DE-9102',
    rig: 'Tata Ultra 1014',
    driver: 'N. Gowda (+91 98440 33812)',
    coords: [14.6819, 77.6006], // Anantapur
    corridor: 'NH-44',
    status: 'okay',
    temp: 4.3,
    delta: 'WHO-PQS Optimal',
    speed: '66 km/h',
    payload: '11,200 doses · MR Vaccine',
    compressor: 'Nominal',
    battery: '90% reserve',
    recommendation: 'Corridor nominal.'
  },
  {
    code: 'VK-1051',
    vin: 'TN-01-GH-7711',
    rig: 'Ashok Leyland Partner',
    driver: 'V. Saravanan (+91 94440 88201)',
    coords: [12.7904, 78.7166], // Ambur
    corridor: 'NH-48',
    status: 'okay',
    temp: 4.5,
    delta: 'WHO-PQS Optimal',
    speed: '63 km/h',
    payload: '7,800 doses · Td Vaccine',
    compressor: 'Nominal',
    battery: '96% reserve',
    recommendation: 'Corridor nominal.'
  }
];

// ----------------------------------------------------------------------------
// Custom Leaflet DivIcons
// ----------------------------------------------------------------------------
function createReeferIcon(reefer) {
  const isProblem = reefer.status === 'problem';
  const isAttention = reefer.status === 'attention';

  const borderColor = isProblem ? '#B8756C' : isAttention ? '#A4875C' : '#829A80';
  const bgBadge = isProblem ? '#2A1617' : isAttention ? '#231E18' : '#162218';
  const textColor = isProblem ? '#E5A4A4' : isAttention ? '#D8BE8A' : '#9DBFA6';

  const pulseRing = isProblem
    ? `<span style="position: absolute; top: -5px; left: -5px; width: 34px; height: 34px; border-radius: 9999px; background: rgba(184, 117, 108, 0.5); animation: pulse-ring 1.8s cubic-bezier(0.215, 0.61, 0.355, 1) infinite; z-index: -1;"></span>`
    : '';

  const html = `
    <div style="position: relative; cursor: pointer; display: flex; flex-direction: column; align-items: center;">
      ${pulseRing}
      <div style="display: flex; align-items: center; gap: 5px; padding: 3px 8px; border-radius: 6px; background: ${bgBadge}; border: 1.5px solid ${borderColor}; box-shadow: 0 4px 14px rgba(0,0,0,0.85); white-space: nowrap;">
        <span style="width: 7px; height: 7px; border-radius: 9999px; background: ${borderColor}; display: inline-block;"></span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #F0E8D9;">${reefer.code}</span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: ${textColor}; padding-left: 2px;">${reefer.temp.toFixed(1)}°C</span>
      </div>
      <div style="width: 0; height: 0; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid ${borderColor}; margin-top: -1px;"></div>
    </div>
  `;

  return L.divIcon({
    className: 'custom-reefer-marker',
    html,
    iconSize: [110, 30],
    iconAnchor: [55, 30]
  });
}

function createDepotIcon(depot) {
  const isBackup = depot.type === 'Emergency Backup';
  const color = isBackup ? '#B8863A' : '#EDE5D8';
  const html = `
    <div style="display: flex; align-items: center; gap: 4px; padding: 2px 6px; border-radius: 5px; background: #171614; border: 1px dashed ${color}; box-shadow: 0 2px 8px rgba(0,0,0,0.85); white-space: nowrap;">
      <span style="font-size: 10px; color: ${color}; font-weight: bold;">✚</span>
      <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 10px; font-weight: 600; color: #EDE5D8;">${depot.city}</span>
    </div>
  `;

  return L.divIcon({
    className: 'custom-depot-marker',
    html,
    iconSize: [80, 20],
    iconAnchor: [40, 20]
  });
}

// ----------------------------------------------------------------------------
// Global Engine State
// ----------------------------------------------------------------------------
let activeMapInstance = null;

export function initLiveTelemetryMap() {
  const mapEl = document.getElementById('leaflet-map');
  if (!mapEl) return;

  // Prevent multiple initializations on same element
  if (activeMapInstance) {
    activeMapInstance.invalidateSize();
    return;
  }

  // --------------------------------------------------------------------------
  // Leaflet Map Initialization
  // --------------------------------------------------------------------------
  const map = L.map('leaflet-map', {
    center: [19.0, 78.5],
    zoom: 5,
    minZoom: 4,
    maxZoom: 17,
    zoomControl: false
  });
  activeMapInstance = map;

  // Tactical Dark Grid Tile Layer (High detail roads, towns, state borders)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18,
    className: 'tactical-dark-tiles'
  }).addTo(map);

  // Invalidate size immediately and after layout settle
  setTimeout(() => map.invalidateSize(), 50);
  setTimeout(() => map.invalidateSize(), 250);
  setTimeout(() => map.invalidateSize(), 600);
  window.addEventListener('resize', () => map.invalidateSize());

  // --------------------------------------------------------------------------
  // Draw Interstate Corridors
  // --------------------------------------------------------------------------
  const corridorLayers = [];
  Object.entries(CORRIDORS).forEach(([key, corr]) => {
    const line = L.polyline(corr.path, {
      color: corr.color,
      weight: 3.5,
      opacity: 0.75,
      dashArray: key === 'NH-48' ? null : '4, 6'
    }).addTo(map);
    line.bindTooltip(corr.name, { sticky: true, className: 'custom-leaflet-tooltip' });
    corridorLayers.push(line);

    // Highlight breached segment on NH-48 (Sriperumbudur to Ranipet)
    if (key === 'NH-48') {
      const breachSegment = L.polyline([
        [12.9675, 79.9427], // Sriperumbudur
        [12.8342, 79.7036], // Kanchipuram
        [12.9272, 79.3330], // Ranipet
        [12.9350, 79.2300]  // Backup Depot
      ], {
        color: '#B8756C',
        weight: 5.5,
        opacity: 0.95,
        dashArray: '8, 8'
      }).addTo(map);
      breachSegment.bindTooltip('NH-48 Active Thermal Excursion Corridor (Km 74.2)', { sticky: true, className: 'custom-leaflet-tooltip' });
      corridorLayers.push(breachSegment);
    }
  });

  // --------------------------------------------------------------------------
  // Depot Markers
  // --------------------------------------------------------------------------
  DEPOTS.forEach(depot => {
    const marker = L.marker(depot.coords, { icon: createDepotIcon(depot) }).addTo(map);
    marker.bindPopup(`
      <div style="font-family: 'Plus Jakarta Sans', sans-serif; padding: 2px 4px; color: #F0E8D9;">
        <strong style="font-size: 13px; color: #F0E8D9;">${depot.name}</strong><br>
        <span style="font-size: 11px; color: #A69F94;">Type: ${depot.type} · Capacity: ${depot.capacity}</span><br>
        <span style="font-size: 11px; font-weight: 600; color: #829A80; margin-top: 4px; display: inline-block;">ILR Cold Room Temp: ${depot.temp}</span>
      </div>
    `);
  });

  // --------------------------------------------------------------------------
  // Reefer Markers & Telemetry Drawer Binding
  // --------------------------------------------------------------------------
  const reeferMarkers = {};
  let currentSelectedReefer = REEFERS[0]; // VK-1042 default

  function updateDrawer(r) {
    currentSelectedReefer = r;
    const drawer = document.getElementById('map-telemetry-drawer');
    if (drawer && drawer.classList.contains('hidden')) {
      drawer.classList.remove('hidden');
      setTimeout(() => map.invalidateSize(), 50);
    }

    const codeEl = document.getElementById('drawer-shipment-code');
    const statusPill = document.getElementById('drawer-status-pill');
    const rigVin = document.getElementById('drawer-rig-vin');
    const tempVal = document.getElementById('drawer-temp-val');
    const deltaVal = document.getElementById('drawer-delta-val');
    const locVal = document.getElementById('drawer-loc-val');
    const speedVal = document.getElementById('drawer-speed-val');
    const payloadVal = document.getElementById('drawer-payload-val');
    const diagVal = document.getElementById('drawer-diag-val');
    const driverVal = document.getElementById('drawer-driver-val');
    const recText = document.getElementById('drawer-rec-text');
    const openProbBtn = document.getElementById('btn-drawer-open-problem');

    if (codeEl) codeEl.textContent = r.code;
    if (rigVin) rigVin.textContent = `${r.rig} · ${r.vin}`;
    if (tempVal) {
      tempVal.textContent = `${r.temp.toFixed(1)}°C`;
      tempVal.style.color = r.status === 'problem' ? '#B8756C' : r.status === 'attention' ? '#A4875C' : '#829A80';
    }
    if (deltaVal) {
      deltaVal.textContent = r.delta;
      deltaVal.style.color = r.status === 'problem' ? '#B8756C' : r.status === 'attention' ? '#A4875C' : '#829A80';
    }
    if (locVal) locVal.textContent = `${r.corridor} · ${r.status === 'problem' ? 'Km 74.2' : 'En Route'}`;
    if (speedVal) speedVal.textContent = `Speed: ${r.speed}`;
    if (payloadVal) payloadVal.textContent = r.payload;
    if (diagVal) diagVal.textContent = r.compressor;
    if (driverVal) driverVal.textContent = r.driver;
    if (recText) recText.textContent = r.recommendation;

    if (statusPill) {
      if (r.status === 'problem') {
        statusPill.className = 'px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-[#2A1617] text-[#B8756C] border border-[#B8756C]/40';
        statusPill.textContent = 'Thermal Breach';
      } else if (r.status === 'attention') {
        statusPill.className = 'px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-[#231E18] text-[#A4875C] border border-[#A4875C]/40';
        statusPill.textContent = 'Needs Attention';
      } else {
        statusPill.className = 'px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-[#162218] text-[#829A80] border border-[#829A80]/40';
        statusPill.textContent = 'Nominal Cold Chain';
      }
    }

    if (openProbBtn) {
      openProbBtn.style.display = r.status === 'problem' ? 'flex' : 'none';
    }
  }

  REEFERS.forEach(r => {
    const marker = L.marker(r.coords, { icon: createReeferIcon(r) }).addTo(map);
    reeferMarkers[r.code] = marker;

    marker.on('click', () => {
      updateDrawer(r);
      map.flyTo(r.coords, Math.max(map.getZoom(), 8.5), { duration: 0.8 });
    });
  });

  // --------------------------------------------------------------------------
  // Camera & Button Handlers
  // --------------------------------------------------------------------------
  document.getElementById('btn-zoom-in')?.addEventListener('click', () => map.zoomIn());
  document.getElementById('btn-zoom-out')?.addEventListener('click', () => map.zoomOut());

  function focusBreach() {
    updateDrawer(REEFERS[0]);
    map.flyTo([12.9675, 79.9427], 9.5, { duration: 1.0 });
  }

  document.getElementById('btn-focus-breach')?.addEventListener('click', focusBreach);
  document.getElementById('btn-top-focus-breach')?.addEventListener('click', focusBreach);

  document.getElementById('btn-fit-national')?.addEventListener('click', () => {
    const group = new L.featureGroup(Object.values(reeferMarkers));
    map.fitBounds(group.getBounds().pad(0.12), { duration: 0.9 });
  });

  let corridorsVisible = true;
  document.getElementById('btn-toggle-corridors')?.addEventListener('click', () => {
    corridorsVisible = !corridorsVisible;
    corridorLayers.forEach(l => {
      if (corridorsVisible) map.addLayer(l);
      else map.removeLayer(l);
    });
  });

  // Sidebar Toggle / Close
  const drawerEl = document.getElementById('map-telemetry-drawer');
  const toggleBtn = document.getElementById('btn-toggle-sidebar');
  const closeBtn = document.getElementById('btn-close-drawer');

  function toggleSidebar() {
    if (!drawerEl) return;
    drawerEl.classList.toggle('hidden');
    setTimeout(() => map.invalidateSize(), 80);
  }

  toggleBtn?.addEventListener('click', toggleSidebar);
  closeBtn?.addEventListener('click', toggleSidebar);

  // Wire Drawer Actions
  document.getElementById('btn-drawer-open-problem')?.addEventListener('click', () => {
    window.location.href = '/problem.html?id=prob_1';
  });

  document.getElementById('btn-drawer-inspect-shipment')?.addEventListener('click', () => {
    window.location.href = `/shipment.html?id=${currentSelectedReefer.code}`;
  });

  document.getElementById('btn-drawer-driver-comms')?.addEventListener('click', () => {
    if (window.driverCommsModal) {
      const name = currentSelectedReefer.driver.split('(')[0].trim();
      const phone = currentSelectedReefer.driver.match(/\+91 [0-9 ]+/)?.[0] || '+91 94441 20982';
      window.driverCommsModal(name, phone, `${currentSelectedReefer.code} Reefer`);
    } else {
      alert(`Dispatching radio/cellular call to ${currentSelectedReefer.driver}`);
    }
  });

  // --------------------------------------------------------------------------
  // Corridor & Status Filtering
  // --------------------------------------------------------------------------
  const corridorPills = document.querySelectorAll('.map-corridor-pill');
  corridorPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const selected = pill.getAttribute('data-corridor');
      corridorPills.forEach(p => {
        p.classList.remove('bg-[#F0E8D9]', 'text-[#171614]', 'font-semibold');
        p.classList.add('text-[#A69F94]');
      });
      pill.classList.remove('text-[#A69F94]');
      pill.classList.add('bg-[#F0E8D9]', 'text-[#171614]', 'font-semibold');

      const visibleMarkers = [];
      REEFERS.forEach(r => {
        const marker = reeferMarkers[r.code];
        const match = selected === 'ALL' || r.corridor.startsWith(selected);
        if (match) {
          if (!map.hasLayer(marker)) map.addLayer(marker);
          visibleMarkers.push(marker);
        } else {
          if (map.hasLayer(marker)) map.removeLayer(marker);
        }
      });

      if (visibleMarkers.length > 0) {
        const group = new L.featureGroup(visibleMarkers);
        map.fitBounds(group.getBounds().pad(0.15), { duration: 0.8 });
      }
    });
  });

  // Search filter
  const searchInput = document.getElementById('map-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.toLowerCase().trim();
      REEFERS.forEach(r => {
        const marker = reeferMarkers[r.code];
        const match = !q ||
          r.code.toLowerCase().includes(q) ||
          r.vin.toLowerCase().includes(q) ||
          r.corridor.toLowerCase().includes(q) ||
          r.driver.toLowerCase().includes(q);

        if (match) {
          if (!map.hasLayer(marker)) map.addLayer(marker);
        } else {
          if (map.hasLayer(marker)) map.removeLayer(marker);
        }
      });
    });
  }

  // Check URL params (?vehicle=... or ?shipment=... or ?id=...)
  const params = new URLSearchParams(window.location.search);
  const targetCode = params.get('vehicle') || params.get('shipment') || params.get('id');
  if (targetCode && reeferMarkers[targetCode]) {
    const found = REEFERS.find(r => r.code === targetCode);
    if (found) {
      updateDrawer(found);
      setTimeout(() => {
        map.flyTo(found.coords, 9.5, { duration: 1 });
      }, 300);
    }
  } else {
    updateDrawer(REEFERS[0]);
    setTimeout(() => {
      const group = new L.featureGroup(Object.values(reeferMarkers));
      map.fitBounds(group.getBounds().pad(0.12), { duration: 0.8 });
    }, 200);
  }
}