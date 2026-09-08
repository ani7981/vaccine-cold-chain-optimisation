/**
 * VaxKavach Demo Tour — driver.js v1 integration
 * Resilient loader: Works seamlessly with Vite, static servers, and standalone file serving.
 */

// Dynamically ensure Driver.js stylesheet is loaded
function ensureDriverCSS() {
  if (document.getElementById('driver-css')) return;
  const link = document.createElement('link');
  link.id = 'driver-css';
  link.rel = 'stylesheet';
  link.href = '/css/driver.css';
  link.onerror = () => {
    link.href = 'https://cdn.jsdelivr.net/npm/driver.js@1.3.5/dist/driver.css';
  };
  document.head.appendChild(link);
}

// Dynamically resolve or load driver function
async function loadDriver() {
  if (window.driver?.js?.driver) return window.driver.js.driver;
  if (window.driver?.driver) return window.driver.driver;
  if (typeof window.driver === 'function') return window.driver;

  ensureDriverCSS();

  // Try dynamic import (in Vite build / dev)
  try {
    const mod = await import('driver.js');
    if (mod?.driver) return mod.driver;
  } catch (e) {
    // Fall back to script tag injection
  }

  // Inject vendor script or CDN
  return new Promise((resolve) => {
    const s = document.createElement('script');
    s.src = '/js/vendor/driver.js';
    s.onload = () => {
      resolve(window.driver?.js?.driver || window.driver?.driver || window.driver || null);
    };
    s.onerror = () => {
      const s2 = document.createElement('script');
      s2.src = 'https://cdn.jsdelivr.net/npm/driver.js@1.3.5/dist/driver.iife.js';
      s2.onload = () => {
        resolve(window.driver?.js?.driver || window.driver?.driver || window.driver || null);
      };
      s2.onerror = () => resolve(null);
      document.head.appendChild(s2);
    };
    document.head.appendChild(s);
  });
}

// ─── Tour step definitions per page ─────────────────────────────────────────

const OVERVIEW_STEPS = [
  {
    popover: {
      title: '👋 Welcome to VaxKavach',
      description: 'The autonomous operations desk for India\'s cold-chain vaccine logistics network. Let\'s explore the live controls.',
      side: 'bottom',
      align: 'start',
    }
  },
  {
    element: '[data-tour="nav-rail"]',
    popover: {
      title: 'Tactical Navigation Rail',
      description: 'Switch between Overview, Shipments, Live Map, Problems Queue, Audit History, Fleet, and Diagnostics with a single click.',
      side: 'right',
    }
  },
  {
    element: '[data-tour="brand"]',
    popover: {
      title: 'VaxKavach System Identity',
      description: 'Autonomous pharmaceutical cold-chain intelligence ensuring Universal Immunization Programme compliance across transit corridors.',
      side: 'right',
    }
  },
  {
    element: '#btn-walkthrough-tour',
    popover: {
      title: 'Demo Tour',
      description: 'Restart this tour any time by clicking this button, or launch it with ?tour=true in any URL.',
      side: 'bottom',
    }
  },
  {
    element: 'main section:first-child',
    popover: {
      title: 'Live Network Health',
      description: 'Real-time corridor telemetry: 12 shipments tracked, 9 optimal, 2 requiring attention, 1 active thermal excursion.',
      side: 'bottom',
    }
  },
  {
    element: 'main section:nth-child(2)',
    popover: {
      title: 'Active Incident — VK-1042',
      description: 'Shipment VK-1042 (Chennai → Vellore) has breached the 8°C ceiling. Multi-sensor correlation detected door seal failure + compressor strain.',
      side: 'top',
    }
  },
  {
    element: '#vk-theme-toggle',
    popover: {
      title: '☀️ Light / Dark Mode',
      description: 'Switch between the dark charcoal operations theme and the clean ivory daylight mode. Persisted in your browser.',
      side: 'left',
    }
  }
];

const PROBLEMS_STEPS = [
  {
    popover: {
      title: '⚠️ Problems Operations Queue',
      description: 'All active and monitored cold-chain excursions triage here by severity with MKT impact, signal correlation, and automated action proposals.',
      side: 'bottom',
    }
  },
  {
    element: 'article',
    popover: {
      title: 'Incident Record — PR-1042',
      description: 'Correlated evidence: 9.4°C temp, door open timer, ambient 38°C, MKT 6.8°C. Reroute protocol to Vellore Sub-District Depot ready for dispatch.',
      side: 'bottom',
    }
  }
];

const SHIPMENTS_STEPS = [
  {
    popover: {
      title: '📦 Active Shipments Directory',
      description: 'Real-time telemetry and payload records for all live vaccine transit vehicles across interstate highways.',
      side: 'bottom',
    }
  }
];

const MAP_STEPS = [
  {
    popover: {
      title: '🗺️ Live Logistics Telemetry Map',
      description: 'Dynamic GPS positions, thermal corridor overlays, and nearest WHO-PQS depot reroute geometries plotted across India.',
      side: 'bottom',
    }
  }
];

const FLEET_STEPS = [
  {
    popover: {
      title: '🚛 Reefer Fleet Operations Command',
      description: 'Real-time telemetry and dispatch console for all national cold chain vehicles operating across Indian highway corridors.',
      side: 'bottom',
    }
  },
  {
    element: '#fleet-vehicle-list',
    popover: {
      title: 'Vehicle Roster & Status',
      description: 'Filter between Healthy, Warning, Critical, and Offline reefers. Click any vehicle to inspect its live refrigeration telemetry and cargo.',
      side: 'right',
    }
  },
  {
    element: '#fleet-topology-container',
    popover: {
      title: 'Interactive Topology Graph',
      description: 'Explore the 6-stage operational pipeline: Rig specs, Consignment, Biological payload, Corridor vector, IoT Sensor mesh, and Safety regulatory assurance.',
      side: 'left',
    }
  },
  {
    element: '#fleet-incident-panel',
    popover: {
      title: 'Incident Lifecycle & Audit',
      description: 'Track open excursions through Investigating, Action Required, and Resolved states. Log cryptographic audit events directly to the SHA-256 ledger.',
      side: 'left',
    }
  }
];

function getStepsForPage() {
  const page = location.pathname.split('/').pop() || 'overview.html';
  const map = {
    'overview.html': OVERVIEW_STEPS,
    'index.html':    OVERVIEW_STEPS,
    'problems.html': PROBLEMS_STEPS,
    'shipments.html': SHIPMENTS_STEPS,
    'map.html': MAP_STEPS,
    'fleet.html': FLEET_STEPS,
  };
  const steps = map[page] || OVERVIEW_STEPS;
  return steps.filter(s => {
    if (!s.element) return true;
    return !!document.querySelector(s.element);
  });
}

let driverInstance = null;

// Fallback interactive modal if driver.js fails
function showFallbackTour(steps) {
  let stepIndex = 0;
  const overlay = document.createElement('div');
  overlay.className = 'fixed inset-0 z-[100000] bg-black/75 backdrop-blur-sm flex items-center justify-center p-4';
  
  function renderStep() {
    const s = steps[stepIndex];
    overlay.innerHTML = `
      <div class="w-full max-w-md bg-[#16171D] border border-[#2A2C35] rounded-2xl p-6 shadow-2xl text-[#F4EFE6] flex flex-col gap-4">
        <div class="flex items-center justify-between border-b border-[#2A2C35] pb-3">
          <span class="text-xs font-mono text-[#8C8E99] uppercase tracking-wider">Step ${stepIndex + 1} of ${steps.length}</span>
          <button id="tour-fallback-close" class="text-[#8C8E99] hover:text-[#F4EFE6] text-lg font-bold">×</button>
        </div>
        <div>
          <h3 class="text-base font-bold mb-1.5 text-[#F4EFE6]">${s.popover.title}</h3>
          <p class="text-xs text-[#8C8E99] leading-relaxed">${s.popover.description}</p>
        </div>
        <div class="flex items-center justify-between pt-3 border-t border-[#2A2C35]">
          <button id="tour-fallback-prev" class="px-3 py-1.5 rounded-lg bg-[#1E2027] border border-[#2A2C35] text-xs font-medium text-[#F4EFE6] ${stepIndex === 0 ? 'opacity-40 pointer-events-none' : 'hover:bg-[#262832]'}">← Back</button>
          <button id="tour-fallback-next" class="px-4 py-1.5 rounded-lg bg-[#F4EFE6] text-[#111215] text-xs font-semibold hover:bg-white transition-colors">${stepIndex === steps.length - 1 ? 'Done ✓' : 'Next →'}</button>
        </div>
      </div>
    `;
    overlay.querySelector('#tour-fallback-close').onclick = () => overlay.remove();
    const prev = overlay.querySelector('#tour-fallback-prev');
    if (prev) prev.onclick = () => { if (stepIndex > 0) { stepIndex--; renderStep(); } };
    const next = overlay.querySelector('#tour-fallback-next');
    if (next) next.onclick = () => {
      if (stepIndex < steps.length - 1) { stepIndex++; renderStep(); }
      else overlay.remove();
    };
  }

  renderStep();
  document.body.appendChild(overlay);
}

export async function startDemoTour() {
  const steps = getStepsForPage();

  try {
    const driverFn = await loadDriver();
    if (!driverFn) {
      showFallbackTour(steps);
      return;
    }

    if (driverInstance) {
      try { driverInstance.destroy(); } catch (_) {}
    }

    driverInstance = driverFn({
      popoverClass: 'vk-tour-popover',
      showProgress: true,
      progressText: '{{current}} / {{total}}',
      nextBtnText: 'Next →',
      prevBtnText: '← Back',
      doneBtnText: '✓ Done',
      animate: true,
      overlayOpacity: 0.6,
      smoothScroll: true,
      allowClose: true,
      steps,
    });

    driverInstance.drive();
  } catch (err) {
    console.warn('Driver.js initialization fallback:', err);
    showFallbackTour(steps);
  }
}

// Make globally available on window
if (typeof window !== 'undefined') {
  window.startDemoTour = startDemoTour;

  // Auto-start if ?tour=true in URL
  if (new URLSearchParams(location.search).get('tour') === 'true') {
    if (document.readyState === 'loading') {
      window.addEventListener('DOMContentLoaded', () => setTimeout(startDemoTour, 900));
    } else {
      setTimeout(startDemoTour, 900);
    }
  }
}
