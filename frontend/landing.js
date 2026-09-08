/**
 * VaxKavach — High-Performance Glowing India Corridor Map Animation
 * Standalone Canvas 2D engine with smooth scroll interpolation and route telemetry.
 */

(function () {
  const canvas = document.querySelector('#cinema');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  canvas.classList.add('ready');

  // Dialog handling
  const dialog = document.querySelector('#how-dialog');
  const howBtn = document.querySelector('#how');
  if (howBtn && dialog) {
    howBtn.onclick = () => dialog.showModal();
    const closeBtn = dialog.querySelector('.close');
    if (closeBtn) closeBtn.onclick = () => dialog.close();
  }

  // Topbar scroll styling
  const topbar = document.querySelector('.topbar');
  window.addEventListener('scroll', () => {
    if (topbar) {
      if (window.scrollY > 40) topbar.classList.add('scrolled');
      else topbar.classList.remove('scrolled');
    }
  }, { passive: true });

  let width = 0;
  let height = 0;
  let dpr = 1;

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
  }
  resize();
  window.addEventListener('resize', resize);

  // Nodes (normalized India geographic coordinates: 0..1 scale inside bounding box)
  const NODES = {
    delhi:      { id: 'DEL', name: 'Delhi Core Store',   x: 0.35, y: 0.28, type: 'primary' },
    mumbai:     { id: 'BOM', name: 'Mumbai Gateway',     x: 0.22, y: 0.58, type: 'primary' },
    pune:       { id: 'PNQ', name: 'Serum Inst. Hub',    x: 0.25, y: 0.62, type: 'hub' },
    hyderabad:  { id: 'HYD', name: 'Bharat Biotech',     x: 0.38, y: 0.64, type: 'hub' },
    bengaluru:  { id: 'BLR', name: 'Karnataka Depot',    x: 0.34, y: 0.79, type: 'hub' },
    chennai:    { id: 'MAA', name: 'Chennai Reg. Store', x: 0.43, y: 0.78, type: 'primary' },
    kanchipuram:{ id: 'KCH', name: 'Kanchipuram Depot',  x: 0.40, y: 0.80, type: 'depot' },
    vellore:    { id: 'VLR', name: 'Vellore Hosp.',      x: 0.37, y: 0.81, type: 'depot' },
    kolkata:    { id: 'CCU', name: 'Kolkata East Hub',   x: 0.72, y: 0.45, type: 'primary' },
    patna:      { id: 'PAT', name: 'Bihar State Depot',  x: 0.61, y: 0.36, type: 'hub' },
    ahmedabad:  { id: 'AMD', name: 'Gujarat Store',      x: 0.19, y: 0.46, type: 'hub' },
  };

  // Major Corridors
  const CORRIDORS = [
    { from: 'chennai',   to: 'vellore',   active: true,  code: 'VK-1042', speed: 0.00045, color: '#6B9E7A', altColor: '#E27373' },
    { from: 'chennai',   to: 'kanchipuram', reroute: true, color: '#E5B869' },
    { from: 'bengaluru', to: 'hyderabad', active: true,  code: 'VK-1039', speed: 0.00032, color: '#6B9E7A' },
    { from: 'mumbai',    to: 'ahmedabad', active: true,  code: 'VK-1045', speed: 0.00038, color: '#6B9E7A' },
    { from: 'delhi',     to: 'patna',     active: true,  code: 'VK-1047', speed: 0.00028, color: '#E5B869' },
    { from: 'kolkata',   to: 'patna',     active: true,  code: 'VK-1051', speed: 0.00035, color: '#6B9E7A' },
    { from: 'pune',      to: 'hyderabad', active: true,  code: 'VK-1056', speed: 0.00030, color: '#6CB8D4' },
    { from: 'delhi',     to: 'ahmedabad', active: false, color: 'rgba(242,238,230,0.12)' },
    { from: 'mumbai',    to: 'bengaluru', active: false, color: 'rgba(242,238,230,0.12)' },
  ];

  // Vehicles / Shipment packets moving along corridors
  const PACKETS = [
    { corridorIndex: 0, progress: 0.25 },
    { corridorIndex: 2, progress: 0.65 },
    { corridorIndex: 3, progress: 0.40 },
    { corridorIndex: 4, progress: 0.80 },
    { corridorIndex: 5, progress: 0.15 },
    { corridorIndex: 6, progress: 0.50 },
  ];

  // Stylized India landmass polygon points (normalized)
  const INDIA_OUTLINE = [
    [0.32, 0.09], [0.37, 0.10], [0.43, 0.14], [0.40, 0.20], [0.48, 0.23],
    [0.55, 0.26], [0.63, 0.28], [0.73, 0.31], [0.82, 0.29], [0.87, 0.34],
    [0.83, 0.39], [0.75, 0.40], [0.71, 0.44], [0.73, 0.51], [0.63, 0.59],
    [0.54, 0.66], [0.48, 0.74], [0.42, 0.83], [0.38, 0.93], [0.35, 0.89],
    [0.32, 0.81], [0.26, 0.74], [0.22, 0.66], [0.20, 0.58], [0.15, 0.53],
    [0.17, 0.48], [0.22, 0.44], [0.25, 0.38], [0.28, 0.29], [0.30, 0.21],
    [0.32, 0.09]
  ];

  // Floating background data telemetry particles
  const PARTICLES = Array.from({ length: 26 }, () => ({
    x: Math.random(),
    y: Math.random(),
    vx: (Math.random() - 0.5) * 0.00015,
    vy: (Math.random() - 0.5) * 0.00015,
    size: Math.random() * 1.6 + 0.8,
    alpha: Math.random() * 0.4 + 0.1,
    text: Math.random() > 0.65 ? ['4.2°C', 'MKT: 4.8°C', 'UIP-SEAL', 'GPS:OK', '2.8°C'][Math.floor(Math.random() * 5)] : null,
  }));

  // Camera scroll states
  let currentZoom = 1;
  let currentCenterX = 0.5;
  let currentCenterY = 0.55;
  let targetZoom = 1;
  let targetCenterX = 0.5;
  let targetCenterY = 0.55;
  let excursionRatio = 0;

  function getScrollProgress() {
    const maxScroll = (document.documentElement.scrollHeight - window.innerHeight) || 1;
    return Math.max(0, Math.min(1, window.scrollY / maxScroll));
  }

  function updateCameraByScroll() {
    const p = getScrollProgress();
    if (p < 0.15) {
      targetZoom = 1;
      targetCenterX = 0.55;
      targetCenterY = 0.53;
      excursionRatio = 0;
    } else if (p < 0.45) {
      targetZoom = 1.35;
      targetCenterX = 0.42;
      targetCenterY = 0.68;
      excursionRatio = 0;
    } else if (p < 0.62) {
      targetZoom = 2.1;
      targetCenterX = 0.40;
      targetCenterY = 0.79;
      excursionRatio = (p - 0.45) / 0.17;
    } else if (p < 0.80) {
      targetZoom = 2.5;
      targetCenterX = 0.39;
      targetCenterY = 0.80;
      excursionRatio = 1;
    } else if (p < 0.92) {
      targetZoom = 2.0;
      targetCenterX = 0.40;
      targetCenterY = 0.79;
      excursionRatio = 1;
    } else {
      targetZoom = 1.05;
      targetCenterX = 0.5;
      targetCenterY = 0.54;
      excursionRatio = 0;
    }

    const readout = document.querySelector('#thermal-readout');
    if (readout) {
      if (p > 0.55 && p < 0.9) {
        readout.textContent = '8.7°C';
        readout.style.color = '#E27373';
      } else {
        readout.textContent = '4.2°C';
        readout.style.color = '#F2EEE6';
      }
    }
  }

  function toScreen(nx, ny) {
    const minDim = Math.min(width, height);
    const mapScale = minDim * 0.88 * currentZoom;
    const originX = (width * 0.5) + (nx - currentCenterX) * mapScale;
    const originY = (height * 0.5) + (ny - currentCenterY) * mapScale;
    return [originX, originY];
  }

  let lastTime = performance.now();
  let pulseTimer = 0;

  function render(time) {
    const dt = Math.min(time - lastTime, 64);
    lastTime = time;
    pulseTimer += dt * 0.0025;

    updateCameraByScroll();

    currentZoom += (targetZoom - currentZoom) * 0.05;
    currentCenterX += (targetCenterX - currentCenterX) * 0.05;
    currentCenterY += (targetCenterY - currentCenterY) * 0.05;

    ctx.save();
    ctx.scale(dpr, dpr);

    // Deep charcoal background fill
    ctx.fillStyle = '#0E0E0F';
    ctx.fillRect(0, 0, width, height);

    // Subtle tactical background grid
    ctx.strokeStyle = 'rgba(242, 238, 230, 0.025)';
    ctx.lineWidth = 1;
    const gridSize = 64;
    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Floating telemetry particles
    ctx.font = '9px "JetBrains Mono", monospace';
    PARTICLES.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0) p.x = 1; if (p.x > 1) p.x = 0;
      if (p.y < 0) p.y = 1; if (p.y > 1) p.y = 0;

      const [sx, sy] = toScreen(p.x, p.y);
      if (sx > 0 && sx < width && sy > 0 && sy < height) {
        ctx.fillStyle = `rgba(122, 122, 130, ${p.alpha * 0.5})`;
        ctx.beginPath();
        ctx.arc(sx, sy, p.size, 0, Math.PI * 2);
        ctx.fill();

        if (p.text && currentZoom < 1.8) {
          ctx.fillStyle = `rgba(200, 196, 188, ${p.alpha * 0.4})`;
          ctx.fillText(p.text, sx + 5, sy + 3);
        }
      }
    });

    // Draw stylized India landmass boundary
    ctx.beginPath();
    INDIA_OUTLINE.forEach((pt, idx) => {
      const [sx, sy] = toScreen(pt[0], pt[1]);
      if (idx === 0) ctx.moveTo(sx, sy);
      else ctx.lineTo(sx, sy);
    });
    ctx.closePath();
    ctx.fillStyle = 'rgba(242, 238, 230, 0.018)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(242, 238, 230, 0.09)';
    ctx.lineWidth = 1.2;
    ctx.stroke();

    // Draw Corridors
    CORRIDORS.forEach(c => {
      const nodeA = NODES[c.from];
      const nodeB = NODES[c.to];
      if (!nodeA || !nodeB) return;

      const [ax, ay] = toScreen(nodeA.x, nodeA.y);
      const [bx, by] = toScreen(nodeB.x, nodeB.y);

      const midX = (ax + bx) * 0.5 + (by - ay) * 0.08;
      const midY = (ay + by) * 0.5 - (bx - ax) * 0.08;

      ctx.beginPath();
      ctx.moveTo(ax, ay);
      ctx.quadraticCurveTo(midX, midY, bx, by);

      if (c.reroute) {
        if (excursionRatio > 0.4) {
          ctx.strokeStyle = `rgba(229, 184, 105, ${excursionRatio * 0.85})`;
          ctx.setLineDash([4, 4]);
          ctx.lineWidth = 2.0;
          ctx.stroke();
          ctx.setLineDash([]);
        }
        return;
      }

      let strokeColor = c.color;
      let strokeWidth = c.active ? 1.8 : 1.0;

      if (c.from === 'chennai' && c.to === 'vellore' && excursionRatio > 0) {
        strokeColor = `rgba(226, 115, 115, ${0.4 + excursionRatio * 0.6})`;
        strokeWidth = 2.2 + Math.sin(pulseTimer * 3) * 0.5;
      }

      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = strokeWidth;
      ctx.stroke();
    });

    // Animate Packets along active corridors
    PACKETS.forEach(p => {
      const corridor = CORRIDORS[p.corridorIndex];
      if (!corridor) return;

      p.progress += (corridor.speed || 0.0003) * dt;
      if (p.progress > 1) p.progress = 0;

      const nodeA = NODES[corridor.from];
      const nodeB = NODES[corridor.to];
      const [ax, ay] = toScreen(nodeA.x, nodeA.y);
      const [bx, by] = toScreen(nodeB.x, nodeB.y);

      const midX = (ax + bx) * 0.5 + (by - ay) * 0.08;
      const midY = (ay + by) * 0.5 - (bx - ax) * 0.08;

      const t = p.progress;
      const invT = 1 - t;
      const px = invT * invT * ax + 2 * invT * t * midX + t * t * bx;
      const py = invT * invT * ay + 2 * invT * t * midY + t * t * by;

      let dotColor = corridor.color || '#6B9E7A';
      if (corridor.from === 'chennai' && corridor.to === 'vellore') {
        if (excursionRatio > 0.4) {
          dotColor = '#E27373';
        }
      }

      if (corridor.from === 'chennai' && corridor.to === 'vellore' && excursionRatio > 0.4) {
        const ringSize = (pulseTimer * 12) % 24;
        ctx.beginPath();
        ctx.arc(px, py, ringSize, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(226, 115, 115, ${Math.max(0, 1 - ringSize / 24)})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.arc(px, py, 4.5, 0, Math.PI * 2);
      ctx.fillStyle = dotColor;
      ctx.shadowColor = dotColor;
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.shadowBlur = 0;

      if (currentZoom > 1.4 && corridor.code) {
        ctx.font = '10px "Plus Jakarta Sans", sans-serif';
        ctx.fillStyle = dotColor;
        ctx.fillText(corridor.code, px + 8, py - 4);
      }
    });

    // Draw Nodes
    Object.values(NODES).forEach(n => {
      const [nx, ny] = toScreen(n.x, n.y);

      let baseColor = n.type === 'primary' ? '#F4EFE6' : n.type === 'hub' ? '#6BBF89' : '#7A7A82';
      let nodeRadius = n.type === 'primary' ? 4 : n.type === 'hub' ? 3.5 : 3;

      if (n.id === 'VLR' && excursionRatio > 0.4) {
        baseColor = '#E27373';
      }
      if (n.id === 'KCH' && excursionRatio > 0.4) {
        baseColor = '#E5B869';
      }

      if (n.type === 'primary' || (n.id === 'VLR' && excursionRatio > 0.4)) {
        const pulseR = 6 + Math.sin(pulseTimer * 2 + n.x * 10) * 3;
        ctx.beginPath();
        ctx.arc(nx, ny, pulseR, 0, Math.PI * 2);
        ctx.strokeStyle = baseColor === '#E27373' ? 'rgba(226, 115, 115, 0.35)' : 'rgba(244, 239, 230, 0.2)';
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.arc(nx, ny, nodeRadius, 0, Math.PI * 2);
      ctx.fillStyle = baseColor;
      ctx.fill();

      if (currentZoom > 1.2 || n.type === 'primary') {
        ctx.font = '10px "Plus Jakarta Sans", sans-serif';
        ctx.fillStyle = 'rgba(200, 196, 188, 0.85)';
        ctx.fillText(n.name, nx + 7, ny + 3);
      }
    });

    ctx.restore();
    requestAnimationFrame(render);
  }

  requestAnimationFrame(render);
})();
