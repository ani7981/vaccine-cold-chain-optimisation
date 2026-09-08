/**
 * VaxKavach Demo Tour — driver.js v1 integration
 * CSS is injected via <link> tag so it works both in Vite dev and standalone.
 */

import { driver } from 'driver.js';

// Inject driver.js CSS once, safely
function ensureDriverCSS() {
  if (document.getElementById('driver-css')) return;
  const link = document.createElement('link');
  link.id = 'driver-css';
  link.rel = 'stylesheet';
  // Try local first (Vite dev), fall back gracefully
  link.href = '/node_modules/driver.js/dist/driver.css';
  link.onerror = () => {
    // CDN fallback
    link.href = 'https://cdn.jsdelivr.net/npm/driver.js@1.3.5/dist/driver.css';
  };
  document.head.appendChild(link);
}

// ─── Tour step definitions per page ─────────────────────────────────────────

const OVERVIEW_STEPS = [
  {
    popover: {
      title: '👋 Welcome to VaxKavach',
      description: 'This is the live operations desk for India\'s simulated vaccine cold-chain network. Let\'s walk through the key controls.',
      side: 'bottom',
      align: 'start',
    }
  },
  {
    element: '[data-tour="nav-rail"]',
    popover: {
      title: 'Tactical Navigation Rail',
      description: 'Jump between Shipments, Live Map, Problems Queue, History, Fleet, and Technical views. One click from anywhere.',
      side: 'right',
    }
  },
  {
    element: '[data-tour="brand"]',
    popover: {
      title: 'VaxKavach System Identity',
      description: 'The VaxKavach shield marks this as an autonomous pharmaceutical cold-chain operations desk — not a generic dashboard.',
      side: 'right',
    }
  },
  {
    element: '#btn-walkthrough-tour',
    popover: {
      title: 'Demo Tour Button',
      description: 'You clicked this to start the tour! You can restart it any time from here, or append ?tour=true to any URL.',
      side: 'bottom',
    }
  },
  {
    element: 'main section:first-child',
    popover: {
      title: 'Live Network Health',
      description: 'Fleet-wide status at a glance — 12 shipments, 9 healthy, 2 needing attention, 1 active temperature excursion.',
      side: 'bottom',
    }
  },
  {
    element: 'main section:nth-child(2)',
    popover: {
      title: 'Active Incident — VK-1042',
      description: 'Shipment VK-1042 (Chennai → Vellore) has a developing thermal excursion. 5 correlated signals triggered this alert.',
      side: 'top',
    }
  },
  {
    element: '#vk-theme-toggle',
    popover: {
      title: '☀️ Light / Dark Mode',
      description: 'Click to switch between the clinical dark theme and the ivory light mode. Your preference is saved automatically.',
      side: 'left',
    }
  }
];

const PROBLEMS_STEPS = [
  {
    popover: {
      title: '⚠️ Problems Queue',
      description: 'All active temperature excursions surface here, sorted by severity. Each card shows evidence, signals, MKT impact and recommended action.',
      side: 'bottom',
    }
  },
  {
    element: 'main section, main .bg-\\[\\#1E1D1A\\], article',
    popover: {
      title: 'Incident Cards',
      description: 'Click any card to open the full investigation — temperature trace, GPS history, door state, and the reroute recommendation.',
      side: 'right',
    }
  }
];

const SHIPMENTS_STEPS = [
  {
    popover: {
      title: '📦 Shipments Directory',
      description: 'Every vaccine shipment currently moving through the network. Filter by status, corridor or search by ID.',
      side: 'bottom',
    }
  }
];

const MAP_STEPS = [
  {
    popover: {
      title: '🗺️ Live Logistics Map',
      description: 'Real-time GPS positions, corridor overlays, and nearest-depot reroute recommendations plotted on India\'s logistics network.',
      side: 'bottom',
    }
  }
];

const GENERIC_STEPS = [
  {
    popover: {
      title: '👋 VaxKavach Operations',
      description: 'For the full walkthrough, visit the Overview page and click "Walkthrough Tour", or open /overview.html?tour=true',
      side: 'bottom',
    }
  }
];

// ─── Build step list based on current page ───────────────────────────────────

function getStepsForPage() {
  const page = location.pathname.split('/').pop() || 'overview.html';
  const map = {
    'overview.html': OVERVIEW_STEPS,
    'index.html':    OVERVIEW_STEPS,
    'problems.html': PROBLEMS_STEPS,
    'shipments.html': SHIPMENTS_STEPS,
    'map.html': MAP_STEPS,
  };
  const steps = map[page] || GENERIC_STEPS;
  // Filter out steps whose element doesn't exist on this page
  return steps.filter(s => {
    if (!s.element) return true;
    return !!document.querySelector(s.element);
  });
}

// ─── Public API ──────────────────────────────────────────────────────────────

let driverInstance = null;

export function startDemoTour() {
  ensureDriverCSS();

  const steps = getStepsForPage();

  if (driverInstance) {
    try { driverInstance.destroy(); } catch (_) {}
  }

  driverInstance = driver({
    popoverClass: 'vk-tour-popover',
    showProgress: true,
    progressText: '{{current}} / {{total}}',
    nextBtnText: 'Next →',
    prevBtnText: '← Back',
    doneBtnText: '✓ Done',
    animate: true,
    overlayOpacity: 0.55,
    smoothScroll: true,
    allowClose: true,
    steps,
  });

  driverInstance.drive();
}

// Auto-start if ?tour=true in URL
if (typeof window !== 'undefined' && new URLSearchParams(location.search).get('tour') === 'true') {
  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', () => setTimeout(startDemoTour, 1000));
  } else {
    setTimeout(startDemoTour, 1000);
  }
}
