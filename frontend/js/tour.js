/**
 * VaxKavach Demo Tour — driver.js v1 integration
 * Provides a guided walkthrough of the operations desk.
 */

import 'driver.js/dist/driver.css';
import { driver } from 'driver.js';

// ─── Tour step definitions per page ─────────────────────────────────────────

const OVERVIEW_STEPS = [
  {
    element: '[data-tour="brand"]',
    popover: {
      title: 'VaxKavach Operations Desk',
      description: 'This is the command centre for India\'s simulated vaccine cold-chain network — watching, detecting, and recommending corrective action 24/7.',
    }
  },
  {
    element: '[data-tour="network-health"]',
    popover: {
      title: 'Live Network Health',
      description: 'Fleet-wide status at a glance. Green = healthy corridors. Amber = attention required. Red = active temperature excursion.',
    }
  },
  {
    element: '[data-tour="incident-card"]',
    popover: {
      title: 'Active Incident — VK-1042',
      description: 'Shipment VK-1042 (Chennai → Vellore) has a developing thermal excursion. The system has already correlated 5 contributing signals.',
    }
  },
  {
    element: '[data-tour="mkt-card"]',
    popover: {
      title: 'Haynes Arrhenius MKT',
      description: 'Mean Kinetic Temperature is calculated from the full temperature history — not just the current reading. This gives a cumulative thermal-stress picture.',
    }
  },
  {
    element: '[data-tour="corridors-table"]',
    popover: {
      title: 'Active Corridors Matrix',
      description: 'All live transit corridors with real-time status. Click any row to drill into that shipment\'s telemetry.',
    }
  },
  {
    element: '[data-tour="nav-rail"]',
    popover: {
      title: 'Tactical Navigation Rail',
      description: 'Jump between Shipments, Map, Problems, History, Fleet, and Technical views. Everything is one click away.',
    }
  },
  {
    element: '#vk-theme-toggle',
    popover: {
      title: 'Light / Dark Mode',
      description: 'Switch between the clinical dark theme and the lighter ivory mode. Your preference is saved automatically.',
    }
  }
];

const PROBLEMS_STEPS = [
  {
    element: '[data-tour="problem-queue"]',
    popover: {
      title: 'Problems Triage Queue',
      description: 'All active and recent temperature excursions surface here, sorted by severity. Click any card to open the full investigation.',
    }
  },
  {
    element: '[data-tour="problem-card"]',
    popover: {
      title: 'Incident Card — PR-1042',
      description: 'Each card shows: what happened, which signals triggered it, thermal impact (MKT), and the recommended corrective action.',
    }
  }
];

const SHIPMENTS_STEPS = [
  {
    element: '[data-tour="shipment-list"]',
    popover: {
      title: 'Active Shipment Directory',
      description: 'Every shipment moving through the network right now. Filter by status, corridor, or search by ID.',
    }
  }
];

const MAP_STEPS = [
  {
    element: '[data-tour="map-canvas"]',
    popover: {
      title: 'Live Logistics Map',
      description: 'Real-time GPS positions, corridor overlays, and nearest-depot reroute recommendations — plotted directly on India\'s logistics network.',
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
  // Filter out steps whose element doesn't exist on the current page
  const steps = map[page] || OVERVIEW_STEPS;
  return steps.filter(s => !s.element || document.querySelector(s.element));
}

// ─── Public API ──────────────────────────────────────────────────────────────

let driverInstance = null;

export function startDemoTour() {
  const steps = getStepsForPage();
  if (steps.length === 0) {
    // Redirect to overview if no steps for this page
    window.location.href = '/overview.html?tour=true';
    return;
  }

  driverInstance = driver({
    popoverClass: 'vk-tour-popover',
    showProgress: true,
    progressText: 'Step {{current}} of {{total}}',
    nextBtnText: 'Next →',
    prevBtnText: '← Back',
    doneBtnText: 'Done',
    animate: true,
    overlayOpacity: 0.6,
    smoothScroll: true,
    steps,
    onDestroyStarted: () => {
      driverInstance?.destroy();
    }
  });

  driverInstance.drive();
}

// Auto-start if ?tour=true in URL
if (new URLSearchParams(location.search).get('tour') === 'true') {
  // Wait for DOM + app data to load
  const tryStart = () => {
    if (document.readyState === 'complete') {
      setTimeout(startDemoTour, 800);
    } else {
      window.addEventListener('load', () => setTimeout(startDemoTour, 800), { once: true });
    }
  };
  tryStart();
}
