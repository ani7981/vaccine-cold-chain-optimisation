import * as THREE from 'three';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const canvas = document.querySelector('#cinema');
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

// Dialog handling with accessibility
const dialog = document.querySelector('#how-dialog');
const howBtn = document.querySelector('#how');
const closeBtn = dialog ? dialog.querySelector('.close') : null;

if (howBtn && dialog) {
  howBtn.onclick = () => dialog.showModal();
}
if (closeBtn && dialog) {
  closeBtn.onclick = () => dialog.close();
}
if (dialog) {
  dialog.addEventListener('click', (e) => {
    const rect = dialog.getBoundingClientRect();
    const isInDialog = (
      rect.top <= e.clientY && e.clientY <= rect.top + rect.height &&
      rect.left <= e.clientX && e.clientX <= rect.left + rect.width
    );
    if (!isInDialog) dialog.close();
  });
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && dialog.open) dialog.close();
  });
}

try {
  run();
} catch (error) {
  if (canvas) canvas.style.display = 'none';
  console.warn('Cinematic fallback enabled', error);
}

function run() {
  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: false,
    powerPreference: 'high-performance'
  });
  renderer.setPixelRatio(Math.min(devicePixelRatio, innerWidth < 720 ? 1.25 : 1.75));
  renderer.setSize(innerWidth, innerHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#171614');
  scene.fog = new THREE.Fog('#171614', 11, 34);

  const camera = new THREE.PerspectiveCamera(35, innerWidth / innerHeight, 0.1, 100);
  camera.position.set(0, 1.1, 7);

  const key = new THREE.SpotLight('#f0ece4', 160, 30, 0.58, 0.7, 1);
  key.position.set(4, 7, 5);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  scene.add(key, new THREE.HemisphereLight('#64777b', '#08090a', 1.4));

  const rim = new THREE.PointLight('#d5d0c7', 26, 13);
  rim.position.set(-4, 2, -4);
  scene.add(rim);

  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(60, 60),
    new THREE.MeshStandardMaterial({ color: '#131210', roughness: 0.84, metalness: 0.03 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  floor.position.y = -1.65;
  scene.add(floor);

  const root = new THREE.Group();
  scene.add(root);

  const vial = vialModel();
  const shipper = shipperModel(vial.clone());
  const truck = truckModel();
  const india = new THREE.Group();
  root.add(vial, shipper, truck, india);

  shipper.visible = false;
  truck.visible = false;
  india.visible = false;

  // DOM Elements for continuous floating HUD & in-scene probe
  const hud = document.querySelector('#live-telemetry-hud');
  const hudBadge = document.querySelector('#hud-badge');
  const hudTemp = document.querySelector('#hud-temp');
  const hudDelta = document.querySelector('#hud-delta');
  const hudBarFill = document.querySelector('#hud-bar-fill');
  const hudStatus = document.querySelector('#hud-status');
  const hudMkt = document.querySelector('#hud-mkt');
  const thermalReadout = document.querySelector('#thermal-readout');

  function phase(n) {
    // 3D Model Stage Transitions
    vial.visible = n < 2;
    shipper.visible = n >= 1 && n < 3;
    truck.visible = n >= 3 && n < 5;
    india.visible = n >= 5;

    // Studio Lighting Color State
    if (n === 4) {
      key.color.set('#d09488');
      rim.color.set('#8f4e48');
    } else {
      key.color.set('#f0ece4');
      rim.color.set('#d5d0c7');
    }

    // Update in-scene instrument probe
    if (thermalReadout) {
      thermalReadout.textContent = n >= 4 ? '8.9°C' : (n === 3 ? '5.6°C' : '4.2°C');
    }

    // Continuous Telemetry HUD Updates
    if (!hud) return;

    if (n < 2) {
      // Scene 0 & 1: Baseline Vial
      hud.classList.remove('hud-warning');
      if (hudBadge) {
        hudBadge.textContent = 'Nominal';
        hudBadge.className = 'hud-badge';
      }
      if (hudTemp) hudTemp.textContent = '4.2°C';
      if (hudDelta) hudDelta.textContent = 'Safe Buffer';
      if (hudBarFill) {
        hudBarFill.style.transform = 'scaleX(0.36)';
        hudBarFill.style.backgroundColor = 'var(--vk-healthy, #71816F)';
      }
      if (hudStatus) hudStatus.textContent = 'Safe Range (2.0°C – 8.0°C)';
      if (hudMkt) hudMkt.textContent = 'MKT: 4.1°C';
    } else if (n === 2) {
      // Scene 2: Insulated Shipper Box
      hud.classList.remove('hud-warning');
      if (hudBadge) {
        hudBadge.textContent = 'Enclosed';
        hudBadge.className = 'hud-badge';
      }
      if (hudTemp) hudTemp.textContent = '4.4°C';
      if (hudDelta) hudDelta.textContent = 'PCM Phase Active';
      if (hudBarFill) {
        hudBarFill.style.transform = 'scaleX(0.40)';
        hudBarFill.style.backgroundColor = 'var(--vk-healthy, #71816F)';
      }
      if (hudStatus) hudStatus.textContent = 'VIP Vacuum Insulation';
      if (hudMkt) hudMkt.textContent = 'MKT: 4.2°C';
    } else if (n === 3) {
      // Scene 3: In-Transit Highway Corridor
      hud.classList.remove('hud-warning');
      if (hudBadge) {
        hudBadge.textContent = 'In Transit · NH48';
        hudBadge.className = 'hud-badge';
      }
      if (hudTemp) hudTemp.textContent = '5.6°C';
      if (hudDelta) hudDelta.textContent = '+1.4° road drift';
      if (hudBarFill) {
        hudBarFill.style.transform = 'scaleX(0.60)';
        hudBarFill.style.backgroundColor = 'var(--vk-healthy, #71816F)';
      }
      if (hudStatus) hudStatus.textContent = 'Reefer Compressor: 1850 RPM';
      if (hudMkt) hudMkt.textContent = 'MKT: 4.8°C';
    } else if (n === 4) {
      // Scene 4: Anomaly / Thermal Excursion
      hud.classList.add('hud-warning');
      if (hudBadge) {
        hudBadge.textContent = 'Breach Active';
        hudBadge.className = 'hud-badge breach';
      }
      if (hudTemp) hudTemp.textContent = '8.9°C';
      if (hudDelta) hudDelta.textContent = '+0.9° Above Limit';
      if (hudBarFill) {
        hudBarFill.style.transform = 'scaleX(0.92)';
        hudBarFill.style.backgroundColor = '#d88980';
      }
      if (hudStatus) hudStatus.textContent = 'Critical Thermal Excursion';
      if (hudMkt) hudMkt.textContent = 'MKT: 6.9°C (Elevated)';
    } else {
      // Scene 5 & Finale: Automated Diversion & Safe Preservation
      hud.classList.remove('hud-warning');
      if (hudBadge) {
        hudBadge.textContent = 'Diverted';
        hudBadge.className = 'hud-badge';
      }
      if (hudTemp) hudTemp.textContent = '4.8°C';
      if (hudDelta) hudDelta.textContent = 'Kanchipuram Depot';
      if (hudBarFill) {
        hudBarFill.style.transform = 'scaleX(0.46)';
        hudBarFill.style.backgroundColor = 'var(--vk-healthy, #71816F)';
      }
      if (hudStatus) hudStatus.textContent = 'Safe Preservation Bay';
      if (hudMkt) hudMkt.textContent = 'MKT: 5.1°C (Preserved)';
    }
  }

  phase(0);

  const sections = [...document.querySelectorAll('.scene')];
  sections.forEach((section, i) => {
    ScrollTrigger.create({
      trigger: section,
      start: 'top center',
      end: 'bottom center',
      onEnter: () => phase(i),
      onEnterBack: () => phase(i)
    });

    const copy = section.querySelector('.copy');
    if (copy && !reduced) {
      gsap.fromTo(
        copy,
        { autoAlpha: 0.35, y: 28 },
        {
          autoAlpha: 1,
          y: 0,
          duration: 0.8,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 72%',
            toggleActions: 'play none none reverse'
          }
        }
      );
    }
  });

  const choreography = gsap.timeline({
    scrollTrigger: {
      trigger: '#story',
      start: 'top top',
      end: 'bottom bottom',
      scrub: reduced ? false : 1.25
    }
  });

  choreography
    .to(camera.position, { x: 1.1, y: 0.8, z: 4.1, duration: 1 })
    .to(vial.rotation, { y: 0.65, duration: 1 }, 0)
    .to(camera.position, { x: -0.4, y: 1.8, z: 7.7, duration: 1 })
    .to(shipper.rotation, { y: -0.28, duration: 1 }, 1)
    .to(camera.position, { x: 3.3, y: 1.3, z: 10, duration: 1 })
    .to(truck.position, { x: -0.6, duration: 1 }, 2)
    .to(camera.position, { x: 0.3, y: 6.5, z: 14.5, duration: 2 })
    .to(india.rotation, { x: -0.25, y: 0.08, duration: 2 }, 4);

  if (!reduced) {
    gsap.to(root.rotation, { y: 0.12, duration: 1.4, yoyo: true, repeat: -1, ease: 'sine.inOut' });
    if (thermalReadout) {
      gsap.to(thermalReadout, { opacity: 0.62, duration: 1.4, yoyo: true, repeat: -1, ease: 'sine.inOut' });
    }
    const routeCard = document.querySelector('.route-card');
    if (routeCard) {
      gsap.to(routeCard, { borderColor: '#71816f', duration: 2, yoyo: true, repeat: -1, ease: 'sine.inOut' });
    }
  }

  buildIndia(india);

  let active = true;
  document.addEventListener('visibilitychange', () => (active = !document.hidden));

  let raf;
  function render() {
    raf = requestAnimationFrame(render);
    if (!active) return;
    camera.lookAt(0, 0.1, 0);
    renderer.render(scene, camera);
  }
  render();

  addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setPixelRatio(Math.min(devicePixelRatio, innerWidth < 720 ? 1.25 : 1.75));
    renderer.setSize(innerWidth, innerHeight);
  });
}

function material(color, rough = 0.5, metal = 0) {
  return new THREE.MeshPhysicalMaterial({
    color,
    roughness: rough,
    metalness: metal,
    clearcoat: metal ? 0.3 : 0,
    clearcoatRoughness: 0.25
  });
}

function vialModel() {
  const g = new THREE.Group();
  const glass = new THREE.MeshPhysicalMaterial({
    color: '#d9e1db',
    roughness: 0.08,
    metalness: 0,
    transmission: 0.55,
    transparent: true,
    opacity: 0.83,
    thickness: 0.2
  });

  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.56, 1.45, 48), glass);
  body.position.y = -0.25;
  body.castShadow = true;

  const liquid = new THREE.Mesh(
    new THREE.CylinderGeometry(0.47, 0.5, 0.63, 40),
    new THREE.MeshPhysicalMaterial({
      color: '#d1d9c7',
      roughness: 0.28,
      transmission: 0.15,
      transparent: true,
      opacity: 0.7
    })
  );
  liquid.position.y = -0.58;

  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.29, 0.35, 32), glass);
  neck.position.y = 0.65;

  const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.17, 32), material('#b7b8b5', 0.25, 0.85));
  cap.position.y = 0.91;

  const stopper = new THREE.Mesh(new THREE.CylinderGeometry(0.23, 0.23, 0.12, 32), material('#303233', 0.6));
  stopper.position.y = 1.01;

  const label = new THREE.Mesh(
    new THREE.CylinderGeometry(0.565, 0.565, 0.5, 48, 1, true),
    new THREE.MeshStandardMaterial({ color: '#e7e2d7', roughness: 0.75 })
  );
  label.position.y = -0.18;

  const line = new THREE.Mesh(new THREE.BoxGeometry(0.005, 0.015, 0.52), material('#17191b'));
  line.position.set(0.567, -0.18, 0);

  g.add(body, liquid, neck, cap, stopper, label, line);
  g.scale.setScalar(1.25);
  return g;
}

function shipperModel(vial) {
  const g = new THREE.Group();
  vial.position.set(0, 0.05, 0);
  vial.scale.setScalar(0.75);

  const box = new THREE.Mesh(new THREE.BoxGeometry(3.6, 2.3, 2.7, 4, 2, 4), material('#c8c4bb', 0.82));
  box.castShadow = true;
  box.receiveShadow = true;

  const foam = new THREE.Mesh(new THREE.BoxGeometry(2.9, 1.65, 2.05), material('#e7e4dc', 0.94));
  foam.position.y = 0.05;

  const seam = new THREE.Mesh(new THREE.BoxGeometry(3.66, 0.035, 2.73), material('#6d6b66', 0.8));
  seam.position.y = 0.95;

  const mark = new THREE.Mesh(
    new THREE.PlaneGeometry(1.45, 0.42),
    new THREE.MeshStandardMaterial({ color: '#252627', roughness: 0.8 })
  );
  mark.position.set(0, 0.2, 1.36);

  g.add(box, foam, seam, mark, vial);
  g.position.set(0, -0.45, 0);
  return g;
}

function truckModel() {
  const g = new THREE.Group();
  const white = material('#c8c9c6', 0.4, 0.15);

  const cargo = new THREE.Mesh(new THREE.BoxGeometry(5.3, 2.55, 2.25, 5, 2, 3), white);
  cargo.position.set(0.55, 0.2, 0);
  cargo.castShadow = true;

  const cab = new THREE.Mesh(new THREE.BoxGeometry(1.55, 1.95, 2.15, 4, 2, 3), material('#747878', 0.38, 0.5));
  cab.position.set(-2.75, -0.08, 0);
  cab.castShadow = true;
  g.add(cargo, cab);

  for (const x of [-2.75, 1.75]) {
    for (const z of [-1.08, 1.08]) {
      const tyre = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.52, 0.35, 24), material('#121314', 0.75));
      tyre.rotation.x = Math.PI / 2;
      tyre.position.set(x, -1.03, z);
      tyre.castShadow = true;
      g.add(tyre);
    }
  }

  const stripe = new THREE.Mesh(new THREE.PlaneGeometry(4.6, 0.18), material('#71816f', 0.55));
  stripe.position.set(0.8, 0.12, 1.14);
  g.add(stripe);

  g.scale.setScalar(0.72);
  g.position.set(0, -0.55, 0);
  return g;
}

async function buildIndia(g) {
  // Calibrated Tamil Nadu transit corridor: Chennai -> Sriperumbudur -> Kanchipuram -> Ranipet -> Vellore
  // Projection formula: x = (lon - 79) * 0.12, y = (lat - 22) * 0.12
  const routePts = [
    [0.152, -1.070],  // Chennai State Depot (80.27°E, 13.08°N)
    [0.113, -1.085],  // Sriperumbudur NH48 Toll
    [0.084, -1.100],  // Kanchipuram Sub-Depot (Divert Point)
    [0.040, -1.088],  // Ranipet Industrial Bypass
    [0.016, -1.090]   // Vellore Medical College (79.13°E, 12.92°N)
  ];

  const routeGeo = new THREE.BufferGeometry().setFromPoints(
    routePts.map(([x, y]) => new THREE.Vector3(x, y, 0))
  );
  const route = new THREE.Line(
    routeGeo,
    new THREE.LineDashedMaterial({ color: '#f0ece4', dashSize: 0.04, gapSize: 0.02 })
  );
  route.computeLineDistances();
  route.scale.setScalar(4.7);
  g.add(route);

  // Corridor Waypoint Spheres
  for (let idx = 0; idx < routePts.length; idx++) {
    const [x, y] = routePts[idx];
    const isDiversion = (idx === 2); // Kanchipuram
    const p = new THREE.Mesh(
      new THREE.SphereGeometry(isDiversion ? 0.065 : 0.045, 12, 12),
      material(isDiversion ? '#d88980' : '#f0ece4', 0.3, 0.2)
    );
    p.position.set(x * 4.7, y * 4.7, 0.05);
    g.add(p);
  }

  // Load GeoJSON boundary points
  try {
    const data = await fetch('/india_boundaries.geojson').then((r) => r.json());
    const positions = [];
    data.features.forEach((f) => {
      const polys = f.geometry.type === 'MultiPolygon' ? f.geometry.coordinates : [f.geometry.coordinates];
      polys.forEach((poly) =>
        poly.forEach((ring) =>
          ring.forEach(([lon, lat]) => {
            positions.push((lon - 79) * 0.12, (lat - 22) * 0.12, 0.01);
          })
        )
      );
    });

    if (positions.length) {
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      g.add(
        new THREE.Points(
          geometry,
          new THREE.PointsMaterial({
            color: '#9e9b95',
            size: 0.012,
            sizeAttenuation: true,
            transparent: true,
            opacity: 0.52
          })
        )
      );
    }
  } catch (e) {
    console.warn('India geometry unavailable', e);
  }

  g.position.y = -0.55;
  g.scale.setScalar(1.05);
}

