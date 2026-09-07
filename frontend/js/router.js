const routes = {
  '/': { page: 'landing', shell: false },
  '/overview': { page: 'overview', shell: true, title: 'Overview', subtitle: 'Live view of vaccine shipments currently moving through the network.' },
  '/shipments': { page: 'shipments', shell: true, title: 'Shipments', subtitle: 'Global directory of active cold-chain transport.' },
  '/map': { page: 'map', shell: true, title: 'Network Map', subtitle: 'Geospatial distribution of active fleet and alerts.' },
  '/problems': { page: 'problems', shell: true, title: 'Incident Queue', subtitle: 'Real-time alert resolution queue.' },
  '/history': { page: 'history', shell: true, title: 'Audit History', subtitle: 'Cryptographic ledger of operational decisions.' },
  '/fleet': { page: 'fleet', shell: true, title: 'Fleet Monitoring', subtitle: 'Network capacity and active vehicle status.' },
  '/technical': { page: 'technical', shell: true, title: 'Technical Diagnostics', subtitle: 'Underlying determinism and rule-engine parameters.' },
  '/settings': { page: 'settings', shell: true, title: 'Settings', subtitle: 'Operational thresholds and configuration.' }
};

let shellLoaded = false;

async function router() {
  let path = window.location.pathname;
  if (path.endsWith('/') && path.length > 1) {
    path = path.slice(0, -1);
  }

  // Handle dynamic routes like /shipments/123 or /problems/456
  let matchedRoute = routes[path];
  let dynamicParam = null;

  if (!matchedRoute) {
    if (path.startsWith('/shipments/')) {
      matchedRoute = { page: 'shipment-detail', shell: true, title: 'Shipment Detail', subtitle: 'Telemetry and active parameters.' };
      dynamicParam = path.split('/')[2];
    } else if (path.startsWith('/problems/')) {
      matchedRoute = { page: 'problem-detail', shell: true, title: 'Incident Resolution', subtitle: 'Detailed excursion metrics and protocols.' };
      dynamicParam = path.split('/')[2];
    } else {
      matchedRoute = routes['/']; // 404 fallback
    }
  }

  const root = document.getElementById('root');

  if (matchedRoute.shell) {
    if (!shellLoaded) {
      const shellHtml = await fetch('/partials/app-shell.html').then(r => r.text());
      root.innerHTML = shellHtml;
      shellLoaded = true;
      setupShell();
    }
    
    // Update Header
    document.getElementById('header-title').innerText = matchedRoute.title;
    document.getElementById('header-subtitle').innerText = matchedRoute.subtitle;

    // Load page content
    const pageHtml = await fetch(`/pages/${matchedRoute.page}.html`).then(r => r.text());
    document.getElementById('page-content').innerHTML = pageHtml;
    
    updateNavUI(path);
  } else {
    // No shell (Landing page)
    shellLoaded = false;
    const pageHtml = await fetch(`/pages/${matchedRoute.page}.html`).then(r => r.text());
    root.innerHTML = pageHtml;
  }

  // Load associated JS if exists
  try {
    const pageModule = await import(`/js/pages/${matchedRoute.page}.js`);
    if (pageModule.init) {
      pageModule.init(dynamicParam);
    }
  } catch (e) {
    // module might not exist, or just log
    console.log(`No JS module found or error for ${matchedRoute.page}:`, e);
  }
}

function updateNavUI(path) {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    const route = btn.getAttribute('data-route');
    if (route && path.startsWith(route) && (route !== '/' || path === '/')) {
      btn.classList.add('bg-vk-cream', 'text-vk-background');
      btn.classList.remove('text-vk-muted', 'hover:text-vk-cream', 'hover:bg-vk-surface2');
    } else {
      btn.classList.remove('bg-vk-cream', 'text-vk-background');
      btn.classList.add('text-vk-muted', 'hover:text-vk-cream', 'hover:bg-vk-surface2');
    }
  });
}

function setupShell() {
  document.addEventListener('click', e => {
    const link = e.target.closest('a');
    if (link && link.href && link.href.startsWith(window.location.origin)) {
      e.preventDefault();
      history.pushState(null, '', link.href);
      router();
    }
  });
  
  // Basic clock
  setInterval(() => {
    const clock = document.getElementById('header-clock');
    if (clock) {
      const d = new Date();
      clock.innerText = d.toLocaleDateString('en-GB', {day:'2-digit', month:'short', year:'numeric'}) + ' · ' + d.toLocaleTimeString('en-GB', {hour:'2-digit', minute:'2-digit'});
    }
  }, 1000);
}

window.addEventListener('popstate', router);
document.addEventListener('DOMContentLoaded', router);
