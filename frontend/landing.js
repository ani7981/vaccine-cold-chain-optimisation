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
  scene.background = new THREE.Color('#0D0E11');
  scene.fog = new THREE.Fog('#0D0E11', 40, 240);

  const camera = new THREE.PerspectiveCamera(35, innerWidth / innerHeight, 0.1, 500);
  camera.position.set(0, 1.1, 7);
  const lookTarget = new THREE.Vector3(0, 0.1, 0);

  const key = new THREE.SpotLight('#f0ece4', 160, 45, 0.58, 0.7, 1);
  key.position.set(4, 7, 5);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);

  const hemi = new THREE.HemisphereLight('#64777b', '#08090a', 1.6);
  const ambient = new THREE.AmbientLight('#2A2D38', 0.8);
  const alertDir = new THREE.DirectionalLight('#F0ECE4', 1.2);
  alertDir.position.set(15, 35, 15);

  scene.add(key, hemi, ambient, alertDir);

  const rim = new THREE.PointLight('#d5d0c7', 26, 18);
  rim.position.set(-4, 2, -4);
  scene.add(rim);

  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(400, 400),
    new THREE.MeshStandardMaterial({ color: '#131210', roughness: 0.84, metalness: 0.03 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  floor.position.y = -1.65;
  scene.add(floor);

  const root = new THREE.Group();
  scene.add(root);

  const syringe = syringeModel();
  const shipper = shipperModel();
  const truck = truckModel();
  const road = roadModel();

  const cKeyBase = new THREE.Color('#f0ece4');
  const cKeyAlert = new THREE.Color('#ff4d42');
  const cRimBase = new THREE.Color('#d5d0c7');
  const cRimAlert = new THREE.Color('#c0382e');
  const cHemiSkyBase = new THREE.Color('#64777b');
  const cHemiSkyAlert = new THREE.Color('#e03e3e');
  const cHemiGndBase = new THREE.Color('#08090a');
  const cHemiGndAlert = new THREE.Color('#38090c');
  const cAmbBase = new THREE.Color('#2A2D38');
  const cAmbAlert = new THREE.Color('#66191c');
  const cDirBase = new THREE.Color('#F0ECE4');
  const cDirAlert = new THREE.Color('#ff3830');
  const cFogBase = new THREE.Color('#0D0E11');
  const cFogAlert = new THREE.Color('#280c0f');
  const redTint = { val: 0.0 };

  function updateLightingTint(t) {
    key.color.copy(cKeyBase).lerp(cKeyAlert, t);
    rim.color.copy(cRimBase).lerp(cRimAlert, t);
    hemi.color.copy(cHemiSkyBase).lerp(cHemiSkyAlert, t);
    hemi.groundColor.copy(cHemiGndBase).lerp(cHemiGndAlert, t);
    ambient.color.copy(cAmbBase).lerp(cAmbAlert, t);
    alertDir.color.copy(cDirBase).lerp(cDirAlert, t);
    alertDir.intensity = THREE.MathUtils.lerp(1.2, 2.4, t);
    scene.fog.color.copy(cFogBase).lerp(cFogAlert, t);
    scene.background.copy(cFogBase).lerp(cFogAlert, t);
    if (truck.userData && truck.userData.setWarning) truck.userData.setWarning(t);
  }

  root.add(syringe, shipper, truck, road);

  shipper.position.set(25, -0.45, 0); // Way offscreen right
  shipper.visible = false; // Strictly hidden on starting hero screen
  
  // Do NOT hide them immediately, GSAP handles their positions smoothly
  shipper.visible = false;
  truck.visible = false;
  truck.position.set(16, -0.55, 0); // Offscreen right until loading
  road.visible = false;
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
    // 3D Model Stage Transitions:
    // Syringe active in scenes 0-2
    // Shipper active from scene 1 onwards (never hidden prematurely while inside truck)
    // Truck & Road active from scene 2 onwards
    syringe.visible = n < 3;
    shipper.visible = n >= 1;
    truck.visible = n >= 2;
    road.visible = n >= 2;
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
        hudBarFill.style.backgroundColor = 'var(--vk-healthy, #6BBF89)';
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
        hudBarFill.style.backgroundColor = 'var(--vk-healthy, #6BBF89)';
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
        hudBarFill.style.backgroundColor = 'var(--vk-healthy, #6BBF89)';
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
        hudBarFill.style.backgroundColor = 'var(--vk-healthy, #6BBF89)';
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
    // --- SCENE 0: Initial Screen (Hero Syringe Inspection) ---
    .to(camera.position, { x: 1.1, y: 0.8, z: 4.1, duration: 1.0 }, 0)
    .to(syringe.rotation, { y: 0.65, duration: 1.0 }, 0)
    
    // --- SCENE 1: Box Enters & Syringe Packs into Box ---
    // 1) Shipper box becomes visible & slides in from far right
    .set(shipper, { visible: true }, 0.75)
    .fromTo(shipper.position,
      { x: 22, y: -0.45, z: 0 },
      { x: 0, y: -0.45, z: 0, duration: 0.50, ease: 'power2.out' },
      0.75
    )
    .to(camera.position, { x: -0.4, y: 1.9, z: 7.8, duration: 1.0 }, 1.0)
    
    // 2) Syringe becomes smaller, lifts up, and aligns flat directly above the hollow opening
    .to(syringe.scale, { x: 0.20, y: 0.20, z: 0.20, duration: 0.35, ease: 'power2.inOut' }, 0.95)
    .to(syringe.position, { x: 0.1, y: 1.85, z: 0, duration: 0.35, ease: 'power2.out' }, 0.95)
    .to(syringe.rotation, { x: 0, y: 0, z: Math.PI / 2, duration: 0.35, ease: 'power2.inOut' }, 0.95)
    
    // 3) Syringe smoothly settles down into the box through the top opening
    .to(syringe.position, { x: 0.1, y: -0.55, z: 0, duration: 0.40, ease: 'power2.inOut' }, 1.30)
    
    // 4) Hinged lid closes shut over the top opening
    .to(shipper.userData.lid.rotation, { x: 0, duration: 0.35, ease: 'power2.in' }, 1.70)
    .to(shipper.rotation, { y: -0.28, duration: 0.35 }, 1.85)

    // --- SCENE 2: Box flies in wide arc around truck & enters through open rear latch ---
    // 5) Grey truck enters into loading position with dark grey rear doors folded open in front of wheels
    .set(road, { visible: true }, 2.05)
    .set(truck, { visible: true }, 2.05)
    .fromTo(truck.position,
      { x: 14, y: -0.55, z: 0 },
      { x: 0.5, y: -0.55, z: 0, duration: 0.45, ease: 'power2.out' },
      2.05
    )

    // 6a) Box shrinks down and takes off, swooping high into the foreground (Z=2.4) to clear all walls
    .to(shipper.scale, { x: 0.20, y: 0.20, z: 0.20, duration: 0.30, ease: 'power2.inOut' }, 2.25)
    .to(shipper.position, { x: 0.8, y: 1.40, z: 2.40, duration: 0.30, ease: 'power2.out' }, 2.25)
    .to(shipper.rotation, { x: -0.15, y: 0.30, z: 0.10, duration: 0.30, ease: 'power2.out' }, 2.25)

    // 6b) Box sweeps wide past the rear corner, staying well out in the foreground (Z=2.2, X=3.8)
    .to(shipper.position, { x: 3.80, y: 0.80, z: 2.20, duration: 0.30, ease: 'power1.inOut' }, 2.55)
    .to(shipper.rotation, { x: -0.05, y: 0.10, z: 0.05, duration: 0.30 }, 2.55)

    // CAMERA MOVES TO LOOK DIRECTLY INTO THE REAR OPEN DOORS (No side-wall occlusion!)
    .to(camera.position, { x: 3.6, y: 0.9, z: 4.8, duration: 0.45, ease: 'power2.out' }, 2.55)
    .to(lookTarget, { x: 2.0, y: -0.2, z: 0.1, duration: 0.45, ease: 'power2.out' }, 2.55)

    // 6c) Box lines up right outside the open rear doorway in plain, unobstructed view
    .to(shipper.position, { x: 3.50, y: -0.35, z: 0.35, duration: 0.30, ease: 'power1.inOut' }, 2.85)
    .to(shipper.rotation, { x: 0, y: -0.20, z: 0, duration: 0.30 }, 2.85)

    // Red warning tint fades in as box reaches the open doors & payload loading begins
    .to(redTint, {
      val: 1.0,
      duration: 0.50,
      ease: 'power2.out',
      onUpdate: () => updateLightingTint(redTint.val)
    }, 2.90)

    // 6d) Box glides straight through the open doorway right onto the hollow cargo container deck!
    .to(shipper.position, { x: 1.65, y: -0.60, z: 0.15, duration: 0.35, ease: 'power2.inOut' }, 3.15)

    // 7) Dark grey rear doors swing shut:
    // Right door (towards us) swings out towards us (+Z) and closes FIRST:
    .to(truck.userData.doorR.rotation, { y: 0, duration: 0.30, ease: 'power2.in' }, 3.45)
    // Left door then swings shut over the rear opening:
    .to(truck.userData.doorL.rotation, { y: 0, duration: 0.26, ease: 'power2.in' }, 3.65)

    // --- SCENE 3: Truck moves forward while camera flies to the back of it ---
    // 8a) Truck aligns straight down the highway and starts rolling forward (-X)
    .to(truck.rotation, { y: 0, duration: 0.20, ease: 'power2.inOut' }, 3.80)
    .to(shipper.rotation, { y: 0, duration: 0.20, ease: 'power2.inOut' }, 3.80)
    .to(shipper.position, { z: 0.0, duration: 0.20, ease: 'power2.inOut' }, 3.80)

    // RED FADES OUT ONCE THE TRUCK STARTS MOVING ON THE ROAD:
    .to(redTint, {
      val: 0.0,
      duration: 0.35,
      ease: 'power2.inOut',
      onUpdate: () => updateLightingTint(redTint.val)
    }, 3.80)
    
    // 8b) Camera gets into position directly behind the truck on the road (pointed straight at rear doors!)
    .to(camera.position, { x: 4.2, y: 0.10, z: 0.0, duration: 0.25, ease: 'power2.inOut' }, 3.80)
    .to(lookTarget, { x: -8.0, y: -0.2, z: 0.0, duration: 0.25, ease: 'power2.inOut' }, 3.80)

    // --- SCENE 4: Truck speeds down the road to the end; camera stays pointed to the back of the truck ---
    .to(truck.position, { x: -85.0, duration: 0.55, ease: 'power2.in' }, 3.90)
    .to(shipper.position, { x: -83.7, duration: 0.55, ease: 'power2.in' }, 3.90)
    // Camera stays positioned behind the truck and continuously tracks the retreating rear doors:
    .to(lookTarget, { x: -85.0, y: -0.4, z: 0.0, duration: 0.55, ease: 'power2.in' }, 3.90)
    .to(camera.position, { x: 4.2, y: 0.25, z: 0.0, duration: 0.55, ease: 'linear' }, 3.90)

    // --- SCENE 5: As truck reaches the end of the road, TILT CAMERA ALL THE WAY TILL ONLY ROAD IS VISIBLE ---
    .to(truck.position, { x: -160.0, duration: 0.40, ease: 'power1.in' }, 4.45)
    .to(shipper.position, { x: -158.7, duration: 0.40, ease: 'power1.in' }, 4.45)
    .to(camera.position, { x: -15.0, y: 2.2, z: 0.0, duration: 0.45, ease: 'power2.inOut' }, 4.45)
    .to(lookTarget, { x: -15.01, y: -1.54, z: 0.0, duration: 0.45, ease: 'power2.inOut' }, 4.45)

    // --- FINALE: AND PAN OUT BY MOVING PERPENDICULARLY UP ABOVE THE ROAD (ZOOM OUT INTO VOID) ---
    .to(camera.position, { x: -15.0, y: 105.0, z: 0.0, duration: 1.15, ease: 'power2.inOut' }, 4.90)
    .to(lookTarget, { x: -15.01, y: -1.54, z: 0.0, duration: 1.15, ease: 'power2.inOut' }, 4.90);

  let active = true;
  document.addEventListener('visibilitychange', () => (active = !document.hidden));

  let raf;
  function render() {
    raf = requestAnimationFrame(render);
    if (!active) return;
    camera.lookAt(lookTarget);
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

function syringeModel() {
  const g = new THREE.Group();

  const barrelLength = 3.2;
  const barrelRadius = 0.44;

  const barrelGlassMat = new THREE.MeshStandardMaterial({
    color: 0x9EA2B0, metalness: 0.12, roughness: 0.18,
    transparent: true, opacity: 0.48, depthWrite: false, side: THREE.DoubleSide
  });

  const liquidMat = new THREE.MeshStandardMaterial({
    color: 0x767988, metalness: 0.25, roughness: 0.35,
    transparent: true, opacity: 0.70
  });

  const surgicalSteelMat = new THREE.MeshStandardMaterial({
    color: 0xD2D5DE, metalness: 0.95, roughness: 0.15
  });

  const rubberPistonMat = new THREE.MeshStandardMaterial({
    color: 0x2A2C33, metalness: 0.05, roughness: 0.92
  });

  const plungerShaftMat = new THREE.MeshStandardMaterial({
    color: 0x7E818E, metalness: 0.45, roughness: 0.35
  });

  const flangePlasticMat = new THREE.MeshStandardMaterial({
    color: 0x616470, metalness: 0.30, roughness: 0.40
  });

  const markMat = new THREE.MeshBasicMaterial({ color: 0x181920 });

  const barrelMesh = new THREE.Mesh(new THREE.CylinderGeometry(barrelRadius, barrelRadius, barrelLength, 48, 1, true), barrelGlassMat);
  g.add(barrelMesh);

  const nozzleTaper = new THREE.Mesh(new THREE.CylinderGeometry(0.18, barrelRadius, 0.40, 48), barrelGlassMat);
  nozzleTaper.position.y = barrelLength / 2 + 0.20;
  g.add(nozzleTaper);

  const nozzleTip = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.35, 36), barrelGlassMat);
  nozzleTip.position.y = barrelLength / 2 + 0.40 + 0.175;
  g.add(nozzleTip);

  const hubMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.15, 0.30, 32), surgicalSteelMat);
  hubMesh.position.y = barrelLength / 2 + 0.75;
  g.add(hubMesh);

  const needleLength = 1.6;
  const needleMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.020, needleLength, 24), surgicalSteelMat);
  needleMesh.position.y = barrelLength / 2 + 0.90 + needleLength / 2;
  g.add(needleMesh);

  const tipMesh = new THREE.Mesh(new THREE.ConeGeometry(0.018, 0.15, 24), surgicalSteelMat);
  tipMesh.position.y = barrelLength / 2 + 0.90 + needleLength + 0.07;
  g.add(tipMesh);

  const flangeMesh = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.08, 0.55), flangePlasticMat);
  flangeMesh.position.y = -barrelLength / 2;
  g.add(flangeMesh);

  const flangeLip = new THREE.Mesh(new THREE.TorusGeometry(barrelRadius + 0.03, 0.03, 16, 48), flangePlasticMat);
  flangeLip.rotation.x = Math.PI / 2;
  flangeLip.position.y = -barrelLength / 2;
  g.add(flangeLip);

  const marksCount = 18;
  const startY = -barrelLength / 2 + 0.45;
  const endY = barrelLength / 2 - 0.25;
  const stepY = (endY - startY) / (marksCount - 1);

  for (let i = 0; i < marksCount; i++) {
    const isMajor = (i % 4 === 0);
    const markMesh = new THREE.Mesh(new THREE.PlaneGeometry(isMajor ? 0.32 : 0.18, isMajor ? 0.022 : 0.014), markMat);
    markMesh.position.set(0, startY + i * stepY, barrelRadius + 0.002);
    g.add(markMesh);
  }

  const plungerAssembly = new THREE.Group();
  g.add(plungerAssembly);

  const stopperRib1 = new THREE.Mesh(new THREE.CylinderGeometry(barrelRadius * 0.96, barrelRadius * 0.96, 0.12, 36), rubberPistonMat);
  const stopperRib2 = new THREE.Mesh(new THREE.CylinderGeometry(barrelRadius * 0.96, barrelRadius * 0.96, 0.12, 36), rubberPistonMat);
  stopperRib1.position.y = 0.09;
  stopperRib2.position.y = -0.09;
  plungerAssembly.add(stopperRib1, stopperRib2);

  const rodLength = barrelLength + 0.6;
  const rod1 = new THREE.Mesh(new THREE.BoxGeometry(0.06, rodLength, 0.32), plungerShaftMat);
  const rod2 = new THREE.Mesh(new THREE.BoxGeometry(0.32, rodLength, 0.06), plungerShaftMat);
  rod1.position.y = -rodLength / 2;
  rod2.position.y = -rodLength / 2;
  plungerAssembly.add(rod1, rod2);

  const thumbDisc = new THREE.Mesh(new THREE.CylinderGeometry(0.48, 0.48, 0.08, 40), flangePlasticMat);
  thumbDisc.position.y = -rodLength;
  plungerAssembly.add(thumbDisc);

  const liquidMesh = new THREE.Mesh(new THREE.CylinderGeometry(barrelRadius * 0.94, barrelRadius * 0.94, 1, 36), liquidMat);
  g.add(liquidMesh);

  // set plunger to a specific %
  const percent = 65;
  const minPos = barrelLength / 2 - 0.25;
  const maxPos = -barrelLength / 2 + 0.35;
  const currentY = minPos + (maxPos - minPos) * (percent / 100);
  plungerAssembly.position.y = currentY;

  const liquidTop = barrelLength / 2;
  const currentLiquidHeight = Math.max(0.01, liquidTop - currentY);
  liquidMesh.scale.set(1, currentLiquidHeight, 1);
  liquidMesh.position.y = liquidTop - currentLiquidHeight / 2;

  // Make it match roughly the size/rotation of the original vial
  // Original vial scaled to 1.25. The syringe is quite tall (~3.2 unit barrel)
  // Let's scale the syringe down by 0.35 so it's not massive
  g.scale.setScalar(0.45);
  // Default tilt angle so it looks nice when floating
  g.rotation.z = Math.PI / 4;
  g.rotation.x = 0.25;

  return g;
}

function shipperModel() {
  const g = new THREE.Group();
  
  const outerMat = material('#5A5D66', 0.80, 0.15);     // Exterior surgical grey
  const innerWallMat = material('#3F424A', 0.88, 0.05); // Dark insulated cavity wall
  const foamBaseMat = material('#7E828C', 0.92, 0.02);  // High-density base foam
  const cradleMat = material('#202228', 0.95, 0.0);     // Recessed dark cradle bed
  const gasketMat = material('#25272F', 0.50, 0.40);    // Top rim silicone seal

  const boxW = 3.6;
  const boxH = 2.1;
  const boxD = 2.6;
  const wallT = 0.14;
  const wallH = boxH - wallT; // 1.96

  // 1. Bottom Floor Plate
  const bottom = new THREE.Mesh(new THREE.BoxGeometry(boxW, wallT, boxD), outerMat);
  bottom.position.y = -boxH / 2 + wallT / 2; // -0.98
  bottom.castShadow = true;
  bottom.receiveShadow = true;
  g.add(bottom);

  // 2. Front Wall
  const frontWall = new THREE.Mesh(new THREE.BoxGeometry(boxW, wallH, wallT), outerMat);
  frontWall.position.set(0, 0.07, boxD / 2 - wallT / 2); // z = 1.23
  frontWall.castShadow = true;
  frontWall.receiveShadow = true;
  g.add(frontWall);

  // 3. Back Wall
  const backWall = new THREE.Mesh(new THREE.BoxGeometry(boxW, wallH, wallT), outerMat);
  backWall.position.set(0, 0.07, -boxD / 2 + wallT / 2); // z = -1.23
  backWall.castShadow = true;
  backWall.receiveShadow = true;
  g.add(backWall);

  // 4. Left Wall
  const leftWall = new THREE.Mesh(new THREE.BoxGeometry(wallT, wallH, boxD - 2 * wallT), outerMat);
  leftWall.position.set(-boxW / 2 + wallT / 2, 0.07, 0); // x = -1.73
  leftWall.castShadow = true;
  leftWall.receiveShadow = true;
  g.add(leftWall);

  // 5. Right Wall
  const rightWall = new THREE.Mesh(new THREE.BoxGeometry(wallT, wallH, boxD - 2 * wallT), outerMat);
  rightWall.position.set(boxW / 2 - wallT / 2, 0.07, 0); // x = 1.73
  rightWall.castShadow = true;
  rightWall.receiveShadow = true;
  g.add(rightWall);

  // 6. Inner Foam Base Cushion (Inside the hollow chamber)
  const foamCushion = new THREE.Mesh(new THREE.BoxGeometry(3.28, 0.32, 2.28), foamBaseMat);
  foamCushion.position.set(0, -0.75, 0);
  foamCushion.receiveShadow = true;
  g.add(foamCushion);

  // 7. Recessed Syringe Cradle Slot (where the syringe settles)
  const cradleSlot = new THREE.Mesh(new THREE.BoxGeometry(2.3, 0.06, 0.48), cradleMat);
  cradleSlot.position.set(0.1, -0.58, 0);
  cradleSlot.receiveShadow = true;
  g.add(cradleSlot);

  // 8. Top Opening Rim Sealing Gaskets (defines the hollow aperture)
  const topY = 1.05;
  const rimFront = new THREE.Mesh(new THREE.BoxGeometry(boxW, 0.04, wallT), gasketMat);
  rimFront.position.set(0, topY, boxD / 2 - wallT / 2);
  const rimBack = new THREE.Mesh(new THREE.BoxGeometry(boxW, 0.04, wallT), gasketMat);
  rimBack.position.set(0, topY, -boxD / 2 + wallT / 2);
  const rimLeft = new THREE.Mesh(new THREE.BoxGeometry(wallT, 0.04, boxD - 2 * wallT), gasketMat);
  rimLeft.position.set(-boxW / 2 + wallT / 2, topY, 0);
  const rimRight = new THREE.Mesh(new THREE.BoxGeometry(wallT, 0.04, boxD - 2 * wallT), gasketMat);
  rimRight.position.set(boxW / 2 - wallT / 2, topY, 0);
  g.add(rimFront, rimBack, rimLeft, rimRight);

  // 9. Front Brand / Telemetry Label
  const label = new THREE.Mesh(
    new THREE.PlaneGeometry(1.4, 0.38),
    new THREE.MeshStandardMaterial({ color: '#25272F', roughness: 0.75 })
  );
  label.position.set(0, 0.20, boxD / 2 + 0.005);
  g.add(label);

  // 10. Hinged Lid Assembly (Hinges at the top-back edge)
  const lidGroup = new THREE.Group();
  lidGroup.position.set(0, topY, -boxD / 2); // Hinge pivot at back rim

  const lidMesh = new THREE.Mesh(new THREE.BoxGeometry(boxW + 0.04, 0.16, boxD + 0.04), outerMat);
  lidMesh.position.set(0, 0.08, boxD / 2); // Offset so pivot is along back edge
  lidMesh.castShadow = true;
  lidMesh.receiveShadow = true;
  lidGroup.add(lidMesh);

  // Underside Insulated Plug of the Lid
  const lidSeal = new THREE.Mesh(new THREE.BoxGeometry(3.26, 0.08, 2.26), foamBaseMat);
  lidSeal.position.set(0, -0.04, boxD / 2);
  lidGroup.add(lidSeal);

  // Lid starts wide open tilted back (~117 degrees)
  lidGroup.rotation.x = -Math.PI * 0.65;
  g.add(lidGroup);

  g.userData.lid = lidGroup;
  return g;
}

function roadModel() {
  const g = new THREE.Group();
  
  const asphaltMat = material('#15161A', 0.95, 0.05);
  const markWhiteMat = material('#9AA0B0', 0.60, 0.20);
  const markYellowMat = material('#C8A852', 0.50, 0.10);
  const shoulderMat = material('#1F2128', 0.90, 0.05);

  const roadLen = 160;
  const roadWidth = 5.6;

  // 1. Asphalt Road Surface
  const asphalt = new THREE.Mesh(new THREE.PlaneGeometry(roadLen, roadWidth), asphaltMat);
  asphalt.rotation.x = -Math.PI / 2;
  asphalt.receiveShadow = true;
  g.add(asphalt);

  // 2. Road Shoulders / Curbs
  const shoulderL = new THREE.Mesh(new THREE.PlaneGeometry(roadLen, 0.7), shoulderMat);
  shoulderL.rotation.x = -Math.PI / 2;
  shoulderL.position.set(0, 0.002, -roadWidth/2 - 0.35);
  const shoulderR = new THREE.Mesh(new THREE.PlaneGeometry(roadLen, 0.7), shoulderMat);
  shoulderR.rotation.x = -Math.PI / 2;
  shoulderR.position.set(0, 0.002, roadWidth/2 + 0.35);
  g.add(shoulderL, shoulderR);

  // 3. Edge White Solid Lines
  const edgeLineL = new THREE.Mesh(new THREE.PlaneGeometry(roadLen, 0.12), markWhiteMat);
  edgeLineL.rotation.x = -Math.PI / 2;
  edgeLineL.position.set(0, 0.004, -roadWidth/2 + 0.25);
  const edgeLineR = new THREE.Mesh(new THREE.PlaneGeometry(roadLen, 0.12), markWhiteMat);
  edgeLineR.rotation.x = -Math.PI / 2;
  edgeLineR.position.set(0, 0.004, roadWidth/2 - 0.25);
  g.add(edgeLineL, edgeLineR);

  // 4. Center Dashed Highway Dividers
  const dashCount = 36;
  const dashLen = 2.2;
  const dashSpacing = 4.4;
  const startX = -roadLen/2 + dashLen;
  for (let i = 0; i < dashCount; i++) {
    const dash = new THREE.Mesh(new THREE.PlaneGeometry(dashLen, 0.14), markYellowMat);
    dash.rotation.x = -Math.PI / 2;
    dash.position.set(startX + i * dashSpacing, 0.004, 0);
    g.add(dash);
  }

  g.position.set(-15, -1.54, 0); // Positioned flush below wheels
  return g;
}

function truckModel() {
  const g = new THREE.Group();

  const cargoMat = material('#2E3037', 0.50, 0.25);       // Durable reefer body grey
  const cargoInnerMat = material('#1C1D22', 0.65, 0.15);  // Solid interior liner & floor
  const cabMat = material('#3B3D45', 0.40, 0.45);        // Sleek cab grey
  const doorMat = material('#202227', 0.60, 0.25);       // Deep charcoal truck doors
  const doorSealMat = material('#111215', 0.90, 0.05);   // Matte black rubber astragal seal gasket
  const doorHardwareMat = material('#D0D4E0', 0.20, 0.90); // Shiny chrome/stainless locking rods & cams
  const handleGripMat = material('#141518', 0.85, 0.05);  // Black textured rubber handle grip
  const chassisMat = material('#181A1F', 0.70, 0.30);    // Heavy steel frame rails & subframe
  const bumperMat = material('#1A1B20', 0.60, 0.30);     // Dark bumper
  const glassMat = material('#121316', 0.10, 0.90);      // High-gloss tinted glass
  const tyreMat = material('#0A0A0C', 0.95, 0.05);       // Jet-black rubber tyres
  const rimMat = material('#22242D', 0.40, 0.70);        // Metallic dark rim
  const hubCapMat = material('#808492', 0.25, 0.85);     // Chrome hub cap
  const reeferMat = material('#34363E', 0.50, 0.30);     // Rooftop condenser
  const headLightMat = material('#EEF2FC', 0.10, 0.90);  // Xenon headlights
  const tailLightMat = material('#8B2424', 0.20, 0.50);  // Ruby tail lights

  // Active Telemetry Indicator LED
  const warnLedMat = new THREE.MeshBasicMaterial({ color: '#4CD964' }); // Starts nominal green
  const cLedNominal = new THREE.Color('#4CD964');
  const cLedBreach = new THREE.Color('#FF3B30');

  // 1. Heavy-Duty Steel Chassis Rails & Subframe (Runs completely under cab & cargo box)
  const chassisRailL = new THREE.Mesh(new THREE.BoxGeometry(6.6, 0.18, 0.12), chassisMat);
  chassisRailL.position.set(0.0, -0.68, -0.52);
  const chassisRailR = new THREE.Mesh(new THREE.BoxGeometry(6.6, 0.18, 0.12), chassisMat);
  chassisRailR.position.set(0.0, -0.68, 0.52);
  g.add(chassisRailL, chassisRailR);

  // Crossmembers connecting chassis rails
  for (let cx = -2.8; cx <= 2.8; cx += 1.4) {
    const crossMem = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 0.96), chassisMat);
    crossMem.position.set(cx, -0.68, 0);
    g.add(crossMem);
  }

  // 2. Cargo Box Shell (Mounted directly on top of chassis subframe, well above all wheels)
  const cargoW = 5.30;
  const cargoH = 2.45;
  const cargoD = 2.22;
  const cargoX = 0.55;
  const cargoFloorY = -0.46; // Solid bottom of cargo container
  const cargoY = cargoFloorY + cargoH / 2; // 0.765
  const wallT = 0.10;

  // Solid Cargo Outer Floor (Hermetically seals the container bottom from the wheels)
  const cFloor = new THREE.Mesh(new THREE.BoxGeometry(cargoW, wallT, cargoD), cargoMat);
  cFloor.position.set(cargoX, cargoFloorY + wallT/2, 0); // y = -0.41
  cFloor.castShadow = true;
  cFloor.receiveShadow = true;
  g.add(cFloor);

  // Solid Seamless Interior Floor Plate (Covers 100% of the interior floor - zero gap, zero wheel view!)
  const cInnerFloor = new THREE.Mesh(new THREE.BoxGeometry(cargoW - 2*wallT, 0.04, cargoD - 2*wallT), cargoInnerMat);
  cInnerFloor.position.set(cargoX, cargoFloorY + wallT + 0.02, 0); // y = -0.34
  cInnerFloor.receiveShadow = true;
  g.add(cInnerFloor);

  // Cargo Roof
  const cRoof = new THREE.Mesh(new THREE.BoxGeometry(cargoW, wallT, cargoD), cargoMat);
  cRoof.position.set(cargoX, cargoY + cargoH/2 - wallT/2, 0);
  cRoof.castShadow = true;
  g.add(cRoof);

  // Front Bulkhead
  const cFront = new THREE.Mesh(new THREE.BoxGeometry(wallT, cargoH - 2*wallT, cargoD), cargoMat);
  cFront.position.set(cargoX - cargoW/2 + wallT/2, cargoY, 0);
  g.add(cFront);

  // Left & Right Outer Walls (Solid, insulated panels)
  const cLeft = new THREE.Mesh(new THREE.BoxGeometry(cargoW, cargoH - 2*wallT, wallT), cargoMat);
  cLeft.position.set(cargoX, cargoY, -cargoD/2 + wallT/2);
  cLeft.castShadow = true;
  const cRight = new THREE.Mesh(new THREE.BoxGeometry(cargoW, cargoH - 2*wallT, wallT), cargoMat);
  cRight.position.set(cargoX, cargoY, cargoD/2 - wallT/2);
  cRight.castShadow = true;
  g.add(cLeft, cRight);

  // Rooftop Refrigeration Unit
  const reefer = new THREE.Mesh(new THREE.BoxGeometry(1.25, 0.70, 1.60), reeferMat);
  reefer.position.set(cargoX - cargoW/2 + 0.68, cargoY + cargoH/2 + 0.32, 0);
  reefer.castShadow = true;
  g.add(reefer);

  // Telemetry Status Indicator LED on Reefer Unit
  const reeferLed = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 12), warnLedMat);
  reeferLed.position.set(cargoX - cargoW/2 + 0.68, cargoY + cargoH/2 + 0.70, 0.82);
  g.add(reeferLed);

  // 3. Hinged Rear Cargo Doors with ZERO GAP and FULL LOCKING HARDWARE ON BOTH DOORS
  const rearX = cargoX + cargoW/2; // 3.20
  const doorH = cargoH - 2*wallT;  // 2.25
  const halfDoorSpan = 1.05;       // Hinge pivot distance from centerline
  const doorW = 1.07;              // Each door width (slight overlap in center)

  // Function to build industrial locking cam rod & lever handle on a door
  function buildDoorHardware(doorGroup, rodZ, handleDirection) {
    // Chrome vertical locking cam rod
    const rod = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, doorH * 0.92, 16), doorHardwareMat);
    rod.position.set(0.048, 0, rodZ);
    doorGroup.add(rod);

    // Top & Bottom Cam Keeper Brackets
    const topCam = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.08, 0.06), doorHardwareMat);
    topCam.position.set(0.045, doorH * 0.46, rodZ);
    const btmCam = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.08, 0.06), doorHardwareMat);
    btmCam.position.set(0.045, -doorH * 0.46, rodZ);
    doorGroup.add(topCam, btmCam);

    // Mid Rod Guide Collars
    const guide1 = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.04, 0.05), doorHardwareMat);
    guide1.position.set(0.045, 0.35, rodZ);
    const guide2 = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.04, 0.05), doorHardwareMat);
    guide2.position.set(0.045, -0.35, rodZ);
    doorGroup.add(guide1, guide2);

    // Cam Lock Latch Lever Handle (extending horizontally with rubber grip)
    const handleArm = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.035, 0.20), doorHardwareMat);
    handleArm.position.set(0.065, -0.05, rodZ + handleDirection * 0.09);
    doorGroup.add(handleArm);

    const grip = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.045, 0.11), handleGripMat);
    grip.position.set(0.066, -0.05, rodZ + handleDirection * 0.14);
    doorGroup.add(grip);
  }

  // --- Left Rear Door (far side) ---
  const doorLGroup = new THREE.Group();
  doorLGroup.position.set(rearX, cargoY, -halfDoorSpan); // Hinge pivot at z = -1.05
  const doorLMesh = new THREE.Mesh(new THREE.BoxGeometry(0.07, doorH, doorW), doorMat);
  doorLMesh.position.set(0, 0, doorW/2); // Centers panel from hinge z=0 to inner edge z=+1.07
  doorLMesh.castShadow = true;
  doorLGroup.add(doorLMesh);
  // Add hardware to Left Door (locking rod near inner edge)
  buildDoorHardware(doorLGroup, doorW * 0.82, -1);
  // Starts open: pointing backwards into loading bay (clear of any wheels!)
  doorLGroup.rotation.y = Math.PI * 0.58;
  g.add(doorLGroup);

  // --- Right Rear Door (camera side - swings toward viewer when closing) ---
  const doorRGroup = new THREE.Group();
  doorRGroup.position.set(rearX, cargoY, halfDoorSpan); // Hinge pivot at z = +1.05
  const doorRMesh = new THREE.Mesh(new THREE.BoxGeometry(0.07, doorH, doorW), doorMat);
  doorRMesh.position.set(0, 0, -doorW/2); // Centers panel from hinge z=0 to inner edge z=-1.07
  doorRMesh.castShadow = true;
  doorRGroup.add(doorRMesh);

  // Overlapping Rubber Weatherstrip Astragal Seal (completely seals the center crack - ZERO GAP!)
  const astragalSeal = new THREE.Mesh(new THREE.BoxGeometry(0.03, doorH + 0.02, 0.07), doorSealMat);
  astragalSeal.position.set(0.036, 0, -doorW); // Fastened along the inner edge of the right door
  doorRGroup.add(astragalSeal);

  // Add hardware to Right Door (locking rod near inner edge)
  buildDoorHardware(doorRGroup, -doorW * 0.82, 1);

  // Security Padlock / Telemetry Seal Hasp fixture on Right Door
  const sealHasp = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.08, 0.04), doorHardwareMat);
  sealHasp.position.set(0.05, 0.08, -doorW * 0.90);
  doorRGroup.add(sealHasp);

  // Starts open: pointing outwards & backwards (clear of rear wheels!)
  doorRGroup.rotation.y = -Math.PI * 0.58;
  g.add(doorRGroup);

  g.userData.doorL = doorLGroup;
  g.userData.doorR = doorRGroup;

  // 4. Driver Cab
  const cabW = 1.65;
  const cabH = 2.10;
  const cabD = 2.12;
  const cabX = -2.75;
  const cabY = 0.28;

  const cab = new THREE.Mesh(new THREE.BoxGeometry(cabW, cabH, cabD, 4, 2, 3), cabMat);
  cab.position.set(cabX, cabY, 0);
  cab.castShadow = true;
  g.add(cab);

  // Windshield
  const windshield = new THREE.Mesh(new THREE.PlaneGeometry(1.88, 0.88), glassMat);
  windshield.rotation.y = -Math.PI / 2;
  windshield.rotation.z = 0.15;
  windshield.position.set(cabX - cabW/2 - 0.01, cabY + 0.38, 0);
  g.add(windshield);

  // Side Windows
  const winL = new THREE.Mesh(new THREE.PlaneGeometry(0.70, 0.55), glassMat);
  winL.position.set(cabX - 0.15, cabY + 0.38, -cabD/2 - 0.005);
  const winR = new THREE.Mesh(new THREE.PlaneGeometry(0.70, 0.55), glassMat);
  winR.position.set(cabX - 0.15, cabY + 0.38, cabD/2 + 0.005);
  g.add(winL, winR);

  // Front Bumper & Headlights
  const bumper = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.45, 2.22), bumperMat);
  bumper.position.set(cabX - cabW/2 - 0.10, -0.72, 0);
  bumper.castShadow = true;
  g.add(bumper);

  const hlL = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.16, 0.30), headLightMat);
  hlL.position.set(cabX - cabW/2 - 0.12, -0.65, -0.75);
  const hlR = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.16, 0.30), headLightMat);
  hlR.position.set(cabX - cabW/2 - 0.12, -0.65, 0.75);
  g.add(hlL, hlR);

  // 5. Black Wheels Tucked Under Chassis (Completely below cargo floor & well clear of rear doors)
  const wheelRadius = 0.44;
  const wheelWidth = 0.28;
  const wy = -0.935; // Calibrated so wheel bottom in world space matches road surface at y=-1.54!
  const wz = 0.86;   // Tucked under body (outer edge at 0.86 + 0.14 = 1.00, well inside cargoD/2 = 1.11)

  const wheelPositions = [
    [-2.75, wy, -wz], // Front Left
    [-2.75, wy,  wz], // Front Right
    [ 0.65, wy, -wz], // Mid Left
    [ 0.65, wy,  wz], // Mid Right
    [ 1.70, wy, -wz], // Rear Left  (Clearance to rear of truck rearX=3.20 is 1.06 units!)
    [ 1.70, wy,  wz]  // Rear Right
  ];

  g.userData.wheels = [];

  wheelPositions.forEach(([wx, yPos, zPos]) => {
    const wheelGroup = new THREE.Group();
    wheelGroup.position.set(wx, yPos, zPos);

    // Deep Jet-Black Tyre
    const tyreGeo = new THREE.CylinderGeometry(wheelRadius, wheelRadius, wheelWidth, 28);
    const tyre = new THREE.Mesh(tyreGeo, tyreMat);
    tyre.rotation.x = Math.PI / 2;
    tyre.castShadow = true;
    wheelGroup.add(tyre);

    // Dark Metallic Rim
    const rimGeo = new THREE.CylinderGeometry(wheelRadius * 0.64, wheelRadius * 0.64, wheelWidth + 0.01, 24);
    const rim = new THREE.Mesh(rimGeo, rimMat);
    rim.rotation.x = Math.PI / 2;
    wheelGroup.add(rim);

    // Chrome Center Hub Cap
    const capGeo = new THREE.CylinderGeometry(wheelRadius * 0.28, wheelRadius * 0.28, wheelWidth + 0.02, 16);
    const cap = new THREE.Mesh(capGeo, hubCapMat);
    cap.rotation.x = Math.PI / 2;
    wheelGroup.add(cap);

    g.add(wheelGroup);
    g.userData.wheels.push(wheelGroup);
  });

  // Rear Mudguards / Wheel Arch Skirts (Protects container underside)
  const fenderL = new THREE.Mesh(new THREE.BoxGeometry(2.35, 0.08, 0.32), chassisMat);
  fenderL.position.set(1.18, -0.48, -wz);
  const fenderR = new THREE.Mesh(new THREE.BoxGeometry(2.35, 0.08, 0.32), chassisMat);
  fenderR.position.set(1.18, -0.48, wz);
  g.add(fenderL, fenderR);

  // Rear Underrun Bumper & Tail Lights
  const rearBumper = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.22, 2.22), bumperMat);
  rearBumper.position.set(rearX + 0.08, -0.85, 0);
  g.add(rearBumper);

  const tlL = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.14, 0.26), tailLightMat);
  tlL.position.set(rearX + 0.15, -0.80, -0.82);
  const tlR = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.14, 0.26), tailLightMat);
  tlR.position.set(rearX + 0.15, -0.80, 0.82);
  g.add(tlL, tlR);

  // Grey Logistics Stripe
  const stripeMat = material('#727682', 0.40, 0.40);
  const stripeL = new THREE.Mesh(new THREE.PlaneGeometry(4.8, 0.16), stripeMat);
  stripeL.position.set(cargoX, cargoY + 0.10, -cargoD/2 - 0.005);
  const stripeR = new THREE.Mesh(new THREE.PlaneGeometry(4.8, 0.16), stripeMat);
  stripeR.position.set(cargoX, cargoY + 0.10, cargoD/2 + 0.005);
  g.add(stripeL, stripeR);

  // Telemetry status callback (linked to red warning tint)
  g.userData.setWarning = (t) => {
    warnLedMat.color.copy(cLedNominal).lerp(cLedBreach, t);
  };

  g.scale.setScalar(0.72);
  g.position.set(16, -0.55, 0);
  g.rotation.y = -0.20; // 3/4 perspective: open rear latch faces the viewer
  return g;
}

