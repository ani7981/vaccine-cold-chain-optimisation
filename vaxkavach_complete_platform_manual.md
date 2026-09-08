# VaxKavach — Full Platform Component Audit & AI Architecture Manual

**Project**: VaxKavach Autonomous Vaccine Cold-Chain Logistics Platform  
**Scope**: All 11 Frontend Pages & Complete AI/ML Machine Learning Integration  
**Status**: Production Verified · All Endpoints Active (`127.0.0.1:8001`) · UI Active (`localhost:5173`)

---

## Executive Summary & Incident Resolution

### Resolution: "Resolve Incident not properly shown" on `overview.html`

The reported defect where the **"Resolve Incident"** component on `frontend/overview.html` was not properly shown was diagnosed through an exhaustive multi-subagent audit. Four root causes were identified and definitively resolved:

1. **Missing Google Material Symbols Font**:
   - `<head>` in `overview.html` only imported *Plus Jakarta Sans*, omitting `Material Symbols Outlined`.
   - When the diversion cockpit modal opened, the browser displayed the raw text words **`verified`** and **`close`** rather than icons, making the modal and action toasts appear visually broken and unstyled.
   - **Fix**: Added `<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />` to `<head>`.

2. **Action Ambiguity & Click Hijacking**:
   - The original button contained an inline `onclick="location.href='/problem.html?id=VK-1042'"` with a navigation chevron `→`. However, `app.js` line 488 intercepted the button via regex `/Resolve Incident/i` and hijacked it into `openDiversionApprovalModal('ship_1')`.
   - Furthermore, `overview.html` had no element with `id="rescue-btn"`, meaning that upon authorizing a reroute, the card remained stuck in its warning state.
   - **Fix**: Redesigned the Excursion Panel into a dual-action Operations Cockpit:
     - **Primary Action (`id="rescue-btn"`)**: *"Resolve Incident & Divert Route"* with dynamic status transformation to *"Reroute Confirmed & Transmitted ✓"* upon modal authorization.
     - **Secondary Action**: *"Investigate Incident & Audit Log →"* which cleanly navigates to the complete Root Cause Diagnostic Console (`/problem.html?id=VK-1042`).
     - **Tertiary Action**: *"Digital Twin & Telemetry"* (`/shipment.html?id=VK-1042`).

3. **Light Mode Contrast Collapse & Lost Alert Border**:
   - In light mode (`html.light`), generic rules in `vaxkavach.css` forced `background-color: #FFFFFF !important` and `border-color: #DCD6CA !important` on all `<section>` elements, wiping out the 4px red alert stripe (`#E27373`) and reducing button contrast to 1.08:1 (WCAG AA failure).
   - **Fix**: Added explicit scoped classes `.excursion-alert-banner` and `.btn-resolve-incident` with high-contrast light-mode styles (`#FFF5F5` background, `#DC2626` 4px left border, `#111215` solid high-contrast button).

4. **Backend Route Parameter Lookup (404 on `?id=VK-1042`)**:
   - Navigating to `/problem.html?id=VK-1042` previously failed with `404 Problem not found` because the API only matched on `Problem.id` (`prob_1`) rather than `Shipment.shipment_code` (`VK-1042`).
   - **Fix**: Implemented a database join in `backend/app/api/endpoints/problems.py` resolving both problem codes and shipment codes.

---

## The AI / ML Architecture Across the Whole Platform

VaxKavach is architected around a **6-Tier Hybrid Decision Engine** that fuses deterministic clinical standards with production machine learning models:

```
                                  IOT TELEMETRY INGESTION (Every 30s)
               [Chamber Temp, Ambient Temp, Door State, Compressor RPM, GPS, Vibration]
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         ▼                                        ▼                                        ▼
┌──────────────────┐                     ┌──────────────────┐                     ┌──────────────────┐
│     TIER 1       │                     │      TIER 2      │                     │      TIER 3      │
│ Clinical Rules   │                     │ Chemical Kinetics│                     │  Predictive ML   │
│ (WHO-PQS 2°C-8°C)│                     │  (Haynes MKT)    │                     │   (XGBoost 4h)   │
├──────────────────┤                     ├──────────────────┤                     ├──────────────────┤
│ Instant Hard     │                     │ Activation Energy│                     │ Spoilage Risk %  │
│ Excursion Breach │                     │ ΔH = 83.14 kJ/mol│                     │ (99.85% Acc,     │
│ Thresholds       │                     │ Thermal Memory   │                     │  100% Precision) │
└────────┬─────────┘                     └────────┬─────────┘                     └────────┬─────────┘
         │                                        │                                        │
         └────────────────────────────────────────┼────────────────────────────────────────┘
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         ▼                                        ▼                                        ▼
┌──────────────────┐                     ┌──────────────────┐                     ┌──────────────────┐
│     TIER 4       │                     │      TIER 5      │                     │      TIER 6      │
│ Multi-Horizon    │                     │ Explainable AI   │                     │ Spatial Kinetic  │
│  Forecasting     │                     │  (TreeSHAP)      │                     │     PostGIS      │
├──────────────────┤                     ├──────────────────┤                     ├──────────────────┤
│ +1h, +2h, +4h    │                     │ Physical Feature │                     │ Geodetic Buffer  │
│ Future Chamber   │                     │ Attribution      │                     │ Road ETA vs      │
│ Temperatures     │                     │ (Why is it hot?) │                     │ Time-to-Breach   │
└──────────────────┘                     └──────────────────┘                     └──────────────────┘
```

### Prominent AI Model Breakdown:

1. **XGBoost 4-Hour Lookahead Spoilage Classifier (`xgb_spoilage_classifier.joblib`)**:
   - **Purpose**: Evaluates an 11-dimensional IoT physical feature vector and calculates the forward probability ($P$) that vaccine potency will be permanently degraded within 4 hours.
   - **Trained Performance**: 99.85% Accuracy, 100% Precision (zero false positives to eliminate unnecessary rerouting costs), 98.84% Recall, 0.9997 ROC-AUC.
   - **Thresholds**:
     - `P ≥ 0.70`: **CRITICAL** (Red indicator, audio alert, auto-generates rescue diversion candidates).
     - `P ≥ 0.45`: **HIGH** (Amber indicator, pre-chill depot alerts).
     - `P ≥ 0.20`: **MEDIUM** (Operator advisory).
     - `P < 0.20`: **LOW / NOMINAL** (Green safe corridor).

2. **Multi-Horizon Temperature Regressors (`xgb_temp_forecaster.joblib`)**:
   - **Horizons**: Three discrete XGBoost regressors predicting internal chamber temperature at **+1 hour**, **+2 hours**, and **+4 hours**.
   - **Validation Error**: MAE of $1.006^\circ\text{C}$ (+1h), $1.130^\circ\text{C}$ (+2h), and $1.454^\circ\text{C}$ (+4h).
   - **Surfacing**: Displayed as forward trend pill tiles on `overview.html`, `shipment.html`, `map.html`, and `problem.html`.

3. **SHAP TreeExplainer Local Attribution (`shap_explainer.joblib`)**:
   - **Purpose**: Solves the "black-box ML" problem for clinical regulators (WHO, CDSCO, US FDA 21 CFR Part 11).
   - **Mechanism**: Computes exact Shapley values across the 11 telemetry features, quantifying how much each sensor contributed to the risk score.
   - **Surfacing**: Rendered as dynamic risk chips, e.g.:
     - `▲ Thermal Gradient (+0.412)` (Ambient heat bleeding through insulation)
     - `▲ Temp Delta 1H (+0.285)` (Rapid upward temperature acceleration)
     - `▼ Chiller Secondary Loop (-0.092)` (Compressor compensating)

4. **Haynes Mean Kinetic Temperature (MKT) Engine**:
   - Implements the Arrhenius equation:
     $$T_{\text{MKT}} = \frac{\frac{\Delta H}{R}}{-\ln\left(\frac{1}{n}\sum_{i=1}^n e^{-\frac{\Delta H}{R \cdot T_i}}\right)}$$
   - Uses activation energy $\Delta H = 83.144\text{ kJ/mol}$ (standard for pharmaceutical proteins and mRNA lipid nanoparticles) to ensure transient temperature spikes are chemically weighted.

5. **PostGIS Geodetic & Road Reachability Engine**:
   - Executes spatial spherical distance calculations (`ST_DistanceSphere`) against the verified national cold-chain depot network.
   - Calculates **Kinetic Reserve**:
     $$\text{Kinetic Reserve Margin} = \text{Time to Critical Thermal Breach} - (\text{Road ETA} + \text{15 min Docking Buffer})$$
   - If Kinetic Reserve is positive ($> 0$), the reroute is certified safe. If negative ($< 0$), the route is rejected as non-viable.

---

## Component-by-Component Breakdown of All 11 Frontend Pages

---

### Page 1: `frontend/overview.html` — Operations Overview Dashboard

- **Primary Role**: The high-level command center providing national cold-chain situational awareness, live health statistics, active interstate corridors, and immediate incident triage.
- **Components & Working**:
  1. **Top Control Bar** (`lines 140–158`):
     - Identity cluster with system status pill "Operations Core".
     - Header Theme Toggle (`#btn-theme-toggle`): Triggers `toggleTheme()` switching between dark mode (`#0D0E11`) and light mode (`#F8F6F0`).
     - Walkthrough Tour Button (`#btn-walkthrough-tour`): Launches interactive 7-step guided tour powered by `driver.js`.
     - AI Inference Engine Badge: Displays live pulsating cyan indicator confirming active XGBoost inference.
     - Live Telemetry Stream pill: Shows active timestamp with green pulse.
  2. **Network Health State Section** (`lines 161–193`):
     - Displays aggregate vehicle metrics across the national network:
       - 12 Shipments moving (dynamic counter).
       - Healthy (9): shipments within $2^\circ\text{C}\text{--}8^\circ\text{C}$ with $P < 0.20$.
       - Attention (2): shipments in warning zone ($7^\circ\text{C}\text{--}8^\circ\text{C}$ or $+0.1^\circ\text{C/min}$ drift).
       - Problem (1): shipments with active thermal breach or $P \ge 0.70$.
     - Dynamically updated in real-time by `initOverview()` via `fetchShipments()`.
  3. **Critical Excursion & AI Decision Cockpit** (`lines 195–264`):
     - Active Excursion Badge + **AI Spoilage Risk Badge** (`#ai-risk-badge`): Evaluates real-time risk percentage (e.g. `CRITICAL 89.2%`).
     - Telemetry grid: Current status, Chamber temp (`9.4°C`), Safe range (`2°C — 8°C`), and Excursion duration (`11 min`).
     - **XGBoost Multi-Horizon Forecaster Pills** (`#ai-forecast-pills`): Live predictions for $+1\text{h}$ (`10.8°C`), $+2\text{h}$ (`12.1°C`), $+4\text{h}$ (`14.5°C`).
     - **SHAP Feature Attribution Container** (`#ai-shap-factors`): Surfaces top root cause drivers (`▲ Thermal Gradient`, `▲ Ambient Heat`).
     - Action Cluster:
       - Primary: `id="rescue-btn"` (*Resolve Incident & Divert Route*) — opens `openDiversionApprovalModal('ship_1')`.
       - Secondary: *Investigate Incident & Audit Log →* — navigates to `/problem.html?id=VK-1042`.
       - Tertiary: *Digital Twin & Telemetry* — navigates to `/shipment.html?id=VK-1042`.
  4. **Active Corridors List** (`lines 267–363`, 7-column span):
     - Live directory of top 5 interstate transits (VK-1042, VK-1039, VK-1045, VK-1047, VK-1051) with carrier model, route, current temp, status chip, and timestamp.
     - Every row is click-bound to open the shipment's Digital Twin (`/shipment.html?id=...`).
  5. **Network Topology Mini-Map SVG** (`lines 366–420`, 5-column span):
     - Coordinate-grid vector map rendering India interstate transit vectors.
     - Chennai-to-Vellore problem corridor rendered in dashed red with concentric pulsating pulse rings.
     - "Open Live Map →" button navigates to `/map.html`.
  6. **What Changed Activity Log** (`lines 423–459`):
     - Chronological timeline of operational milestones within the last 30 minutes.
- **AI Integration Prominence**:
  - The Overview dashboard is now directly connected to `fetchAiInsights('VK-1042')`, displaying live XGBoost spoilage probability, multi-horizon temperature forecasting, and SHAP root-cause feature attribution directly on the main screen.

---

### Page 2: `frontend/shipments.html` — Shipments Directory & Inspector

- **Primary Role**: The tactical registry of all vaccine consignments with deep-filter search, batch tracking, and a slide-over Inspector Drawer.
- **Components & Working**:
  1. **Directory Header & ⌘K Search**:
     - Full-text search across shipment codes, vaccine batches, driver names, and transit routes.
     - Filter Chips: `All`, `Critical`, `Attention`, `Optimal` with live count badges.
  2. **Consignments Data Table**:
     - Columns: Shipment Code, Consignment Payload (Vaccine type, dose count, cold-chain tier), Vehicle & Driver, Current Temp & RoC velocity, MKT, Status badge, and Action launcher.
     - Dynamic row highlighting: problem shipments pulse subtly with red borders.
  3. **Interactive Inspector Drawer (`openShipmentDrawer(id)`)**:
     - Slides out from right edge (480px width) on row selection without leaving the directory.
     - Live SVG Temperature Sparkline: Plots trailing 2-hour sensor readings with $2^\circ\text{C}\text{--}8^\circ\text{C}$ clinical ceiling boundaries.
     - Payload Metadata: Batch Number, Expiry Date, Manufacturer (Serum Institute, Bharat Biotech), Regulatory Dossier link.
     - Live Telemetry Tiles: Dual PT100 probe divergence, ambient temperature, compressor RPM, door cycle count.
     - Quick Action Footer:
       - "Direct Driver Link" (triggers `driverCommsModal`).
       - "Evaluate Reroute" (triggers `openDiversionApprovalModal`).
       - "Open Full Digital Twin" (navigates to `/shipment.html?id=...`).
- **AI Integration Prominence**:
  - Each shipment row displays an **AI Spoilage Risk Gauge** with predicted Time-to-Ceiling Breach (`T-minus 22m`). The Inspector Drawer surfaces the XGBoost + SHAP prediction summary and forecasted temperature trend line.

---

### Page 3: `frontend/shipment.html` — Shipment Digital Twin & Diagnostic Console

- **Primary Role**: The deep-dive telemetry workbench for a single vaccine consignment, displaying high-fidelity multi-sensor physics and explainable AI.
- **Components & Working**:
  1. **Consignment Identity & Digital Twin Ribbon**:
     - Route origin and destination, vehicle model, license plate, GPS lat/long, and cryptographic batch seal hash.
  2. **Multi-Probe Temperature & MKT Telemetry**:
     - High-frequency dual-probe line chart: Probe A (front cargo) vs Probe B (rear door).
     - Calculated Arrhenius Mean Kinetic Temperature (MKT) over 24-hour and trailing trip windows.
  3. **Refrigeration & Environmental Telematics**:
     - Ambient temperature gauge vs internal chamber delta.
     - Compressor load %, RPM velocity, vibration RMS, door magnetic reed switch state.
  4. **AI Spoilage Prognostics Card**:
     - XGBoost Spoilage Probability meter ($0\%\text{--}100\%$) with clinical risk classification.
     - Multi-Horizon Regressor forecasts (+1h, +2h, +4h) plotted as projected dotted extensions on the primary temperature chart.
     - TreeExplainer SHAP Waterfall Plot: Explains exactly why the risk is elevated (e.g. ambient heat, door breach duration).
  5. **Operator Intervention Actions**:
     - Secondary Chiller Loop Override: Remotely commands the reefer unit to auxiliary max cooling.
     - Driver Telephony Bridge: Direct modal link to driver with GPS corridor coordinates.
     - Emergency Diversion Trigger: Launches the PostGIS reroute solver.
- **AI Integration Prominence**:
  - Centralized showcase of the XGBoost multi-model suite: probability classification, multi-horizon forward regression, and SHAP interpretability.

---

### Page 4: `frontend/map.html` — Live Geospatial Tactical Map

- **Primary Role**: Full-screen interactive GIS command center displaying the national cold-chain spatial network, live vehicle locations, and emergency reroute paths.
- **Components & Working**:
  1. **Leaflet.js Map Engine**:
     - Tactical dark-mode basemap tiles with custom CSS inversion filters.
     - Corridors layer: Interstate highway trajectories (NH-48, Agra Expressway, etc.) color-coded by corridor health.
     - Depot markers: WHO-PQS certified cold storage hubs with storage capacities, ILR buffer counts, and backup power facilities.
     - Vehicle markers: Custom SVG truck icons with rotating heading indicators and animated status halos (green, amber, red).
  2. **Corridor Metrics Drawer**:
     - Floating left overlay showing live vehicle roster, current temperature, and geodetic distance to destination.
  3. **Reroute Preview & Path Simulation**:
     - When an excursion occurs, the map dynamically renders:
       - Dashed amber/red line along original planned trajectory showing projected failure zone.
       - Solid green polyline to the optimal backup depot with distance, ETA, and kinetic thermal reserve badge.
- **AI Integration Prominence**:
  - PostGIS spatial AI engine (`ST_DistanceSphere`) evaluates geodetic distance and combines it with road graph routing and thermal breach velocity to determine reachable safe depots.

---

### Page 5: `frontend/problems.html` — Problems Operational Queue

- **Primary Role**: The high-urgency triage queue prioritizing all active excursions and supply chain anomalies across the entire fleet.
- **Components & Working**:
  1. **Severity Filters & Search**:
     - Filter tabs: `Critical (1)`, `Warning (2)`, `All Active (3)`, `Resolved (18)`.
  2. **Active Problem Triage Cards**:
     - Card Header: Problem Code (`PR-1042`), Shipment Code, Detected Timestamp, Severity indicator.
     - Evidence Matrix: Multi-sensor physical correlation:
       - Temperature Limit: `BREACHED (9.4°C > 8.0°C)`
       - Rate of Change: `ELEVATED (+0.22°C/min)`
       - Door Events: `NORMAL`
       - Ambient Heat: `CRITICAL (38.5°C)`
       - Refrigeration: `SUB-OPTIMAL`
  3. **Automated Recommendation Banner**:
     - Rule ID: `WHO_MKT_RULE_04B` / `AI_DIVERSION_REC_01`.
     - Recommended action: "Divert immediately to Vellore Sub-District Depot (14 km · 18 min ETA)".
     - Target facility accredited services: Walk-in Cold Room, Solar-Direct Drive ILR.
  4. **Triage Actions**:
     - "Acknowledge" (claims incident, updates status to IN_PROGRESS).
     - "Execute Recommendation" (opens route diversion confirmation).
     - "Manual Override" (allows operator to sign off with clinical justification).
- **AI Integration Prominence**:
  - Incidents are prioritized by AI Spoilage Probability and Kinetic Thermal Breach Velocity. The triage cards display real-time SHAP evidence metrics directly within the problem card.

---

### Page 6: `frontend/problem.html` — Incident Resolution Cockpit

- **Primary Role**: The single-incident resolution cockpit where operators investigate root causes, simulate counterfactual routes, authorize diversions, and commit cryptographic resolution blocks.
- **Components & Working**:
  1. **Incident Diagnosis Card & Timeline**:
     - Problem metadata, detected time, duration above ceiling, and visual rule chain progression (`WHO_MKT_RULE_04B`).
  2. **Emergency Cold-Chain Diversion Cockpit**:
     - **Counterfactual Simulation**:
       - *Plan A (Maintain Route)*: Distance 68 km, ETA 1h 14m, Projected arrival temp +11.4°C (SPOILED), Deficit: -48 min. Disposition: `QUARANTINE_FOR_DESTRUCTION`.
       - *Plan B (Authorized Reroute)*: Distance 14 km, ETA 18m, Projected arrival temp +5.2°C (OPTIMAL), Kinetic Reserve: +24m. Disposition: `RELEASE_FOR_ADMINISTRATION`.
  3. **Candidate Backup Depots Table**:
     - Ranked list of reachable cold stores with road distance, ETA, available ILR capacity, and thermal feasibility margin.
  4. **Cryptographic Seal & Resolution**:
     - "Authorize Route Diversion" commits the reroute, triggers the audio chime, and appends a SHA-256 Merkle audit block with operator digital signature.
- **AI Integration Prominence**:
  - The counterfactual simulation directly runs the XGBoost multi-horizon forecast to compare Plan A vs Plan B future temperatures, proving why diversion is clinically necessary.

---

### Page 7: `frontend/history.html` — Cryptographic Audit History & Regulatory Dossier

- **Primary Role**: Regulatory compliance ledger and tamper-evident audit history proving the cold chain was maintained end-to-end.
- **Components & Working**:
  1. **RFC 6962 Binary Merkle Tree Root Banner**:
     - Displays the current top SHA-256 Merkle Root hash (e.g. `e3b0c442...`).
     - "Verify Merkle Tree" button runs client-side hash verification against backend audit blocks.
  2. **Audit Timeline**:
     - Chronological feed of immutable events: `TELEMETRY_INGEST`, `EXCURSION_DETECTED`, `AI_PREDICTION_LOGGED`, `DIVERSION_AUTHORIZED`, `CONSIGNMENT_RELEASED`.
     - Each entry shows leaf hash, previous block hash, actor ID, and cryptographic timestamp.
  3. **Tamper Simulation & Detection Test**:
     - Interactive security test: Operator can click "Simulate Tamper on Block #3".
     - The engine alters 1 bit in a historical temperature record, recalculates the Merkle proof, and immediately flags `TAMPER DETECTED: Root Hash Mismatch!`.
  4. **CDSCO / WHO Batch Release Certificate Generator**:
     - Generates an official, printable regulatory release certificate containing shipment summary, MKT calculation, excursion log, and cryptographic integrity proof for batch release sign-off.
- **AI Integration Prominence**:
  - Every AI prediction (XGBoost risk score, multi-horizon forecast, and top SHAP feature factors) is permanently hashed into the Merkle tree to satisfy regulatory explainability requirements under 21 CFR Part 11.

---

### Page 8: `frontend/fleet.html` — Reefer Fleet Diagnostics & Asset Health

- **Primary Role**: Fleet management console monitoring vehicle chassis, refrigeration units, compressor health, and predictive maintenance.
- **Components & Working**:
  1. **National Reefer Vehicle Grid**:
     - 12 commercial refrigerated trucks (Tata Ultra, Eicher Pro, BharatBenz, Ashok Leyland).
     - Status taxonomy: `IN_TRANSIT (5)`, `AVAILABLE (4)`, `MAINTENANCE (2)`, `CRITICAL (1)`.
  2. **Vehicle Telemetry Card**:
     - Chiller Type: Chilled ($+2^\circ\text{C}\text{--}+8^\circ\text{C}$) vs Deep-Frozen ($-20^\circ\text{C}$).
     - Compressor RPM velocity, coolant pressure, evaporator coil temperature, and auxiliary battery voltage.
  3. **Interactive Digital Twin Topology Modal**:
     - 6-tier interactive vehicle schematic showing cab, chassis, reefer compressor, evaporator, cargo chamber, and door seals.
  4. **Incident Resolution Protocol Modal**:
     - Provides 7 standard corrective protocols: compressor restart, backup generator engagement, refrigerant recharge, thermal blanket deployment, etc.
- **AI Integration Prominence**:
  - Features predictive maintenance models that detect compressor wear, cooling decay, and thermal seal degradation before catastrophic refrigeration failure occurs.

---

### Page 9: `frontend/technical.html` — Technical Diagnostics & Chaos Testing Console

- **Primary Role**: Hardware engineering, sensor telemetry diagnostics, and simulation chaos console.
- **Components & Working**:
  1. **Hardware & Sensor Health Panel**:
     - Dual PT100 probe divergence monitoring (flags warning if discrepancy $> 1.5^\circ\text{C}$).
     - Telemetry packet loss rate, RSSI cellular signal strength, ADC freeze lockup detection, and Kalman filter noise reduction status.
  2. **Synthetic Incident Injection Console (Chaos Engine)**:
     - Live testing triggers:
       - `Compressor Failure` (cuts cooling loop, initiates chamber temperature rise).
       - `+46°C Heatwave Surge` (spikes ambient external temperature).
       - `Door Ajar Breach` (simulates unsealed cargo doors).
       - `Highway Gridlock` (halts vehicle velocity, increases transit time).
     - "Clear All Incidents" button restores nominal simulation conditions.
  3. **Feature Engineering Pipeline Monitor**:
     - Displays the live 11-dimensional feature vector fed into the XGBoost model: `temp_mean`, `probe_discrepancy`, `ambient_temp`, `humidity`, `thermal_gradient`, `temp_delta_1h`, `temp_delta_3h`, `temp_accel`, `rolling_mean_3h`, `rolling_std_3h`, `is_frozen`.
- **AI Integration Prominence**:
  - Transparently displays the exact mathematics and transformation pipeline that converts raw IoT sensor readings into normalized tensors for model inference.

---

### Page 10: `frontend/settings.html` — Settings & System Governance

- **Primary Role**: Regulatory compliance parameters, thermal boundary definitions, AI model governance, and operator preferences.
- **Components & Working**:
  1. **WHO-PQS Thermal Envelope Configuration**:
     - Standard Refrigerated ($+2.0^\circ\text{C}$ to $+8.0^\circ\text{C}$).
     - Deep Frozen ($-25.0^\circ\text{C}$ to $-15.0^\circ\text{C}$).
     - Continuous Excursion Buffer (minutes before auto-incident escalation).
  2. **Haynes Arrhenius MKT Parameters**:
     - Activation energy slider ($\Delta H = 83.144\text{ kJ/mol}$).
     - Trailing calculation window (12h, 24h, 48h, Entire Transit).
  3. **Audio & Theme Preferences**:
     - Clinical alert chime volume with Web Audio API synthesizer (880 Hz $\rightarrow$ 587 Hz dual-tone).
     - Light / Dark theme selector.
  4. **AI Model Governance & Thresholds**:
     - Spoilage Probability Threshold ($P_{\text{crit}} = 0.70$).
     - AI Auto-Diversion Permission toggle (requires dual sign-off vs automated dispatch).
     - Model Versioning & Drift Monitor (`v2.0.0-leakage-free-production`).
- **AI Integration Prominence**:
  - Operators can tune the sensitivity of the XGBoost classifier and configure false-positive rate controls to meet specific clinical and economic mandates.

---

### Page 11: `frontend/landing.html` — Public Showcase & 3D Interactive Experience

- **Primary Role**: The public-facing product showcase and architectural overview demonstrating VaxKavach's capabilities to health ministries and logistics partners.
- **Components & Working**:
  1. **Interactive Three.js 3D Reefer Truck Model**:
     - Fully interactive 3D truck with working refrigeration unit, rotating tires, and interactive camera controls.
  2. **Interactive 3D Syringe & Vaccine Vial (`syringe.html`, `syringe-3d.html`)**:
     - High-detail Three.js model of a vaccine vial with volumetric fluid rendering and thermal degradation color transition.
  3. **India Geospatial Point Cloud**:
     - 3D particle map of India rendered from `india_points.json` visualizing nationwide cold-chain arterial routes.
  4. **Hero & Architecture Narrative**:
     - Explains the 4-tier autonomous defense: Edge IoT Sensors $\rightarrow$ Cloud AI Predictive Engine $\rightarrow$ Dynamic Rerouting $\rightarrow$ Immutable Merkle Audit Trail.
     - Direct CTA: "Launch Operations Core" (navigates to `/overview.html`).
- **AI Integration Prominence**:
  - Highlights the core value proposition: preventing vaccine wastage through predictive AI lookahead rather than reactive post-spoilage disposal.

---

## Verification & System State Summary

- **PostGIS Spatial Database**: Running and healthy in WSL Fedora (`vaxkavach_db`).
- **FastAPI Backend (`http://127.0.0.1:8001`)**:
  - Auto-reloading active.
  - `/api/analytics/ai-insights/VK-1042`: Returns HTTP 200 with complete XGBoost probability, multi-horizon forecast, and SHAP factors.
  - `/api/problems/VK-1042`: Returns HTTP 200 with problem code `PR-1042` and PostGIS candidate depot.
- **Vite Dev Server (`http://localhost:5173`)**:
  - Serving all 11 pages cleanly.
  - `overview.html` now includes Google Material Symbols, responsive high-contrast excursion banner, dynamic AI prognostics, and dual-action buttons.
  - Theme toggle and walkthrough tour work seamlessly.
