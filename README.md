# VaxKavach

### Every degree, accounted for.

**VaxKavach is a cold-chain operations intelligence platform for vaccine logistics.**

It monitors simulated shipment telemetry, detects developing temperature problems, combines multiple operational signals to determine what is happening, calculates temperature impact using Mean Kinetic Temperature, recommends corrective action, and maintains a tamper-evident operational history.

> **Built for Smart India Hackathon 2026 — Problem Statement 5**
>
> VaxKavach is a working demonstration of an autonomous operations desk for vaccine cold-chain logistics.

---

## Table of Contents

* [What is VaxKavach?](#what-is-vaxkavach)
* [The Problem](#the-problem)
* [Why Cold Chain Matters](#why-cold-chain-matters)
* [The Core Idea](#the-core-idea)
* [What VaxKavach Actually Does](#what-vaxkavach-actually-does)
* [The Demo Story](#the-demo-story)
* [System Architecture](#system-architecture)
* [Data Flow](#data-flow)
* [Backend](#backend)
* [Frontend](#frontend)
* [Telemetry Simulation](#telemetry-simulation)
* [Problem Detection](#problem-detection)
* [Temperature Impact / MKT](#temperature-impact--mkt)
* [Rate of Temperature Change](#rate-of-temperature-change)
* [Signal Correlation](#signal-correlation)
* [Recommendation Engine](#recommendation-engine)
* [Nearest Depot / Rerouting](#nearest-depot--rerouting)
* [Audit Trail](#audit-trail)
* [Database](#database)
* [Live Map](#live-map)
* [Application Screens](#application-screens)
* [Why There Is No Machine Learning](#why-there-is-no-machine-learning)
* [What Is Simulated](#what-is-simulated)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [Running Locally](#running-locally)
* [Demo Walkthrough](#demo-walkthrough)
* [Design Philosophy](#design-philosophy)
* [Engineering Decisions](#engineering-decisions)
* [Limitations](#limitations)
* [Future Work](#future-work)
* [Compliance Position](#compliance-position)
* [Why This Project Matters](#why-this-project-matters)

---

# What is VaxKavach?

Vaccines are not ordinary cargo.

A shipment can physically reach its destination and still be compromised if its temperature history was unacceptable.

VaxKavach is designed around a simple question:

> **"Is this vaccine shipment okay right now, and if it isn't, what should the operator do?"**

Instead of showing operators a collection of disconnected sensor readings, VaxKavach attempts to turn those signals into an operational decision.

```text
LIVE DATA
   │
   ├── Temperature
   ├── Humidity
   ├── GPS
   ├── Door state
   ├── Ambient conditions
   └── Transit delay
          │
          ▼
   DETECTION ENGINE
          │
          ├── Threshold checks
          ├── Temperature change
          ├── Temperature impact
          └── Signal correlation
          │
          ▼
       PROBLEM
          │
          ▼
   RECOMMENDED ACTION
          │
          ▼
   OPERATOR DECISION
          │
          ▼
    AUDIT / HISTORY
```

The important part is the middle.

**VaxKavach does not merely display telemetry.**

It interprets telemetry.

---

# The Problem

A cold-chain operator may have access to:

* temperature sensors
* GPS
* door sensors
* humidity sensors
* vehicle information
* weather information
* transit status

But these signals are often viewed independently.

Imagine:

```text
Temperature:     rising
Door:            open
GPS:             stationary
Ambient:         hot
Transit:         delayed
```

Each signal by itself may not be enough to trigger a meaningful response.

Together, however, they tell a much clearer story:

> The shipment may be stationary, exposed to heat, and experiencing a developing refrigeration problem.

This is the problem VaxKavach addresses.

---

# Why Cold Chain Matters

Vaccines are temperature-sensitive biological products.

The important operational question is therefore not simply:

> "What is the temperature now?"

It is:

> **"What has this shipment experienced over time?"**

A short excursion may have very different consequences from prolonged exposure.

This is why VaxKavach considers both:

1. **instantaneous conditions**
2. **temperature history**

---

# The Core Idea

VaxKavach is built around three actions:

## WATCH

Continuously observe the operational signals associated with a shipment.

## SPOT

Detect when the signals indicate a developing or existing problem.

## ACT

Give the operator an evidence-backed recommended action.

```text
WATCH
  ↓
SPOT
  ↓
ACT
```

This becomes the central design principle of the system.

---

# What VaxKavach Actually Does

The system currently demonstrates:

### Shipment monitoring

Track simulated vaccine shipments across an Indian logistics network.

### Temperature monitoring

Observe temperature history and detect temperature problems.

### GPS monitoring

Track the simulated position of shipments.

### Door monitoring

Detect whether the shipment/container door is open.

### Transit monitoring

Represent delays or stationary periods during transit.

### Environmental context

Use ambient/weather conditions as an additional signal.

### Temperature Impact

Calculate Mean Kinetic Temperature from the temperature history.

### Problem detection

Use deterministic rules to identify developing problems.

### Signal correlation

Combine multiple signals into a single operational explanation.

### Recommendations

Suggest actions based on the detected state.

### Rerouting

Demonstrate rerouting toward an appropriate nearby depot.

### History

Maintain a chronological operational history.

### Tamper-evident audit

Use a hash chain so that each record depends on the previous record.

---

# The Demo Story

The primary demonstration shipment is:

```text
Shipment:    VK-1042
Origin:      Chennai
Destination: Vellore
```

The simulation begins normally.

```text
Chennai
   │
   │
   ▼
Vellore
```

The shipment starts inside an acceptable operating range.

Then the scenario develops.

```text
NORMAL
   ↓
Temperature begins rising
   ↓
Shipment is delayed
   ↓
Door/environmental signals become relevant
   ↓
Temperature problem develops
   ↓
Detection engine identifies the problem
   ↓
Temperature impact is evaluated
   ↓
Signals are correlated
   ↓
Recommended action is generated
   ↓
Operator can authorize a reroute
   ↓
New operational state is recorded
```

This is the main end-to-end demonstration.

---

# System Architecture

At a high level:

```text
                    ┌─────────────────────┐
                    │   Simulation Engine │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Telemetry / State  │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
          Detection        MKT Engine     Correlation
           Engine             │              Engine
                └──────────────┼──────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Recommendation      │
                    │ Engine               │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ FastAPI Backend     │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              REST API               WebSocket
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ VaxKavach Frontend  │
                    └─────────────────────┘
```

---

# Data Flow

A typical temperature update follows this path:

```text
Simulation
    ↓
New temperature sample
    ↓
Database/state
    ↓
Detection engine
    ↓
Problem state
    ↓
WebSocket
    ↓
Frontend
    ↓
Overview / Shipment / Map / Problem UI
```

When an operator takes an action:

```text
Operator
    ↓
Frontend
    ↓
REST API
    ↓
Backend validation
    ↓
Database/state mutation
    ↓
Audit event
    ↓
Updated frontend state
```

This is important because the frontend is **not the source of truth**.

The backend is.

---

# Backend

The backend is responsible for the operational intelligence.

The backend contains the logic for:

* shipment state
* telemetry
* simulation
* detection
* MKT
* temperature-change analysis
* recommendations
* depot selection
* rerouting
* audit history
* API responses
* real-time updates

The frontend primarily presents this state to the operator.

---

# Frontend

The frontend is designed as an operational control interface.

The major screens are:

```text
Landing
   ↓
Overview
   ↓
Shipments
   ↓
Shipment Details
   ↓
Live Map
   ↓
Problems
   ↓
Problem Details
   ↓
History
   ↓
Fleet
   ↓
Technical
   ↓
Settings
```

The interface uses a restrained:

```text
BLACK / GRAPHITE
+
WARM CREAM
+
MUTED SEMANTIC COLORS
```

visual language.

The goal is to feel like a serious logistics operations system rather than a generic dashboard.

---

# Telemetry Simulation

This project does not require physical vaccine hardware to demonstrate the operational model.

Instead, VaxKavach uses deterministic simulated telemetry.

The simulated streams include:

```text
Temperature
Humidity
GPS
Door
Ambient / Weather
Transit Delay
```

Each stream changes according to the demonstration timeline.

For example:

```text
Time 0
Temperature = normal
GPS = moving
Door = closed

        ↓

Time 1
Temperature = begins rising
GPS = slowing

        ↓

Time 2
Temperature = elevated
Transit = delayed

        ↓

Time 3
Problem detected
```

This makes the entire system reproducible.

A judge can observe the same scenario every time.

---

# Problem Detection

VaxKavach intentionally uses **deterministic decision logic**.

It does not require a machine-learning model to identify the demonstration scenario.

A simplified conceptual model is:

```text
temperature outside acceptable range
                OR
temperature changing abnormally
                OR
temperature impact becoming significant
                +
supporting operational signals
                ↓
             PROBLEM
```

The actual backend detection logic is authoritative.

This allows the system to explain:

> **Why did this become a problem?**

rather than simply saying:

> **AI says this is risky.**

---

# Temperature Impact / MKT

One of the technically important parts of the project is Mean Kinetic Temperature.

Temperature damage is not always adequately represented by looking at a single maximum temperature.

MKT attempts to represent the cumulative thermal effect of a temperature history.

The formula used is:

```text
                 -Ea / R
MKT = ─────────────────────────────────
      ln[(Σ exp(-Ea / (R·Ti))) / n]
```

Where:

```text
Ea = activation energy
R  = gas constant
Ti = absolute temperature of sample i
n  = number of samples
```

The implementation uses approximately:

```text
Ea = 83144 J/mol
R  = 8.314 J/(mol·K)
```

Temperature values must be converted from Celsius to Kelvin before being used in the exponential calculation.

```text
Kelvin = Celsius + 273.15
```

The backend performs this calculation.

The frontend displays the resulting operational value.

---

# Why MKT Matters

Consider two shipments:

### Shipment A

```text
2°C
3°C
4°C
3°C
2°C
```

### Shipment B

```text
2°C
3°C
8°C
3°C
2°C
```

Both may eventually return to normal.

But their thermal histories are different.

MKT provides an additional way of quantifying the cumulative thermal effect rather than only displaying the current reading.

---

# Rate of Temperature Change

VaxKavach also considers how quickly temperature is changing.

A shipment at:

```text
5.0°C
```

may not be alarming if it has been stable.

But:

```text
2.5°C
3.1°C
3.9°C
4.8°C
5.7°C
```

shows a different pattern.

The **direction and rate of change** can provide early warning before a severe threshold breach occurs.

This is a deterministic statistical/threshold-based approach rather than machine learning.

---

# Signal Correlation

This is one of the most important ideas in VaxKavach.

Instead of evaluating every signal independently:

```text
Temperature
GPS
Door
Weather
Transit
```

the system combines them.

For example:

```text
Temperature rising
        +
Door open
        +
Vehicle stationary
        +
High ambient temperature
        +
Transit delay
```

provides stronger operational evidence than any individual signal.

The purpose is not to produce an opaque "AI score."

The purpose is to explain:

> **These conditions occurring together are why the shipment requires attention.**

---

# Recommendation Engine

Once the system identifies a problem, it should answer:

> **What should the operator do next?**

A recommendation can be based on:

* severity
* shipment location
* temperature state
* thermal history
* transit status
* available cooling resources
* nearby certified/appropriate depot locations

For the main demonstration, the recommendation can involve redirecting the shipment toward a nearby suitable depot.

The important design principle is:

```text
DETECTION
    ↓
EVIDENCE
    ↓
RECOMMENDATION
```

rather than:

```text
DETECTION
    ↓
random action
```

---

# Nearest Depot / Rerouting

Depot selection is represented using geographic data.

The backend can determine which suitable depot is closest to the shipment.

Conceptually:

```text
Current Shipment Location
          │
          ▼
   Candidate Depots
          │
          ▼
 Geographic Distance
          │
          ▼
     Best Candidate
          │
          ▼
 Recommended Reroute
```

A spatial database can perform nearest-neighbour queries efficiently.

The project uses the Chennai → Vellore scenario as the primary demonstration of this concept.

---

# Audit Trail

Operational decisions need history.

VaxKavach therefore maintains an append-only style audit history using a hash chain.

Conceptually:

```text
Event 1
   │
   └── hash₁

Event 2
   │
   ├── previous_hash = hash₁
   └── hash₂

Event 3
   │
   ├── previous_hash = hash₂
   └── hash₃
```

Each record incorporates information from the previous record.

Therefore, modifying an earlier event would invalidate subsequent hashes.

This provides a **tamper-evident record structure**.

It does not make the system magically immutable or legally certified.

It provides cryptographic evidence of whether the recorded chain has been altered.

---

# Database

The backend uses a relational database for operational state.

Spatial functionality is useful for:

* shipment coordinates
* depot locations
* geographic queries
* nearest-depot selection
* route-related data

The project therefore uses PostgreSQL/PostGIS concepts where required.

The database contains the persistent state needed by the operational model rather than storing the entire demo solely in browser memory.

---

# Live Map

The Live Map visualizes the simulated logistics network.

The supplied India boundary geometry is used as the authoritative India geometry.

The map can display:

* shipment positions
* routes
* operational status
* problem state
* corridor overlays
* depot information
* shipment callouts

The primary demonstration follows:

```text
Chennai → Vellore
```

as the shipment state changes.

---

# Application Screens

## Landing

The cinematic introduction to VaxKavach.

Its purpose is to communicate:

```text
Vaccine
    ↓
Cold Chain
    ↓
Movement
    ↓
Temperature
    ↓
Problem
    ↓
Detection
    ↓
Action
```

The landing experience can use Three.js and GSAP for the cinematic presentation.

---

## Overview

Answers:

> **Are my shipments okay?**

Shows the operational state of the network.

---

## Shipments

Answers:

> **What shipments are currently moving?**

Provides the operational directory.

---

## Shipment Details

Answers:

> **What is happening to this shipment?**

Shows detailed shipment state, telemetry and history.

---

## Live Map

Answers:

> **Where is everything?**

Provides geographic context.

---

## Problems

Answers:

> **What needs attention?**

Acts as the operational triage queue.

---

## Problem Details

Answers:

> **Why is this a problem?**

Shows evidence, contributing signals, thermal impact and recommended action.

---

## History

Answers:

> **What happened?**

Shows chronological operational events and audit information.

---

## Fleet

Answers:

> **What does the wider network look like?**

Provides aggregate operational information from the available simulated dataset.

---

## Technical

Answers:

> **Why did the system make this decision?**

Exposes the technical reasoning behind:

* temperature analysis
* MKT
* temperature change
* thresholds
* signal correlation
* recommendations

This is particularly useful during technical evaluation.

---

## Settings / Demo Controls

Provides controls for the demonstration environment where supported.

For example:

* simulation start
* pause
* reset
* simulation speed

---

# Why There Is No Machine Learning

A deliberate engineering decision was made **not to use ML for the core demonstration**.

The reason is explainability.

For a safety-sensitive operational scenario, the system should be able to say:

```text
Temperature increased
+
Shipment was stationary
+
Door was open
+
Ambient conditions were unfavorable
=
Problem detected
```

rather than:

```text
Model confidence: 93.7%
```

Deterministic rules also make the SIH demonstration:

* reproducible
* debuggable
* explainable
* easier to validate
* easier to demonstrate offline

Machine learning could be added later for predictive maintenance, anomaly forecasting or demand optimization, but it is not required for the core operational intelligence loop.

---

# What Is Simulated?

This distinction is extremely important.

The current project is a **working simulation of the operational model**, not a deployment connected to physical vaccine trucks.

### Simulated

* temperature telemetry
* humidity
* GPS movement
* door state
* environmental conditions
* transit delay
* shipment progression
* incident development
* operational recommendations
* depot availability
* rerouting scenario

### Implemented as real software

* backend API
* database state
* detection logic
* MKT calculation
* temperature-change analysis
* correlation logic
* recommendation logic
* spatial lookup concepts
* audit hash chain
* frontend
* WebSocket communication
* operational UI

### Not currently claimed

* physical refrigeration control
* real truck actuation
* real sensor hardware integration
* real telephony
* real-world vaccine certification
* WHO/FDA certification
* production deployment

This distinction keeps the demonstration technically honest.

---

# Technology Stack

## Backend

```text
Python
FastAPI
PostgreSQL
PostGIS
SQLAlchemy
Alembic
WebSockets
```

## Frontend

The operational interface uses:

```text
HTML
CSS
JavaScript
```

with browser-side visualization and interaction.

The cinematic landing page can additionally use:

```text
Three.js
GSAP
ScrollTrigger
```

where appropriate.

## Geographic Data

```text
India boundary GeoJSON
Shipment coordinates
Depot coordinates
Route data
```

## Mathematical / Decision Layer

```text
MKT
Temperature Change
Threshold Detection
Signal Correlation
Deterministic Rules
```

---

# Project Structure

A representative structure is:

```text
VaxKavach/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   │   ├── detection/
│   │   │   ├── simulation/
│   │   │   └── audit/
│   │   └── ...
│   │
│   ├── migrations/
│   ├── seed.py
│   └── ...
│
├── frontend/
│   ├── landing.html
│   ├── overview.html
│   ├── shipments.html
│   ├── shipment.html
│   ├── map.html
│   ├── problems.html
│   ├── problem.html
│   ├── history.html
│   ├── fleet.html
│   ├── technical.html
│   ├── settings.html
│   │
│   ├── css/
│   ├── js/
│   └── assets/
│
├── data/
│   └── india/
│       └── india_boundaries.geojson
│
└── README.md
```

The exact structure may evolve as the implementation develops.

---

# Running Locally

## Prerequisites

You should have:

* Python 3.x
* Node.js
* npm
* Docker
* Docker Compose

---

## 1. Clone the repository

```bash
git clone <repository-url>
cd VaxKavach
```

---

## 2. Start the database

Start the project's PostgreSQL/PostGIS services using the provided Docker configuration.

```bash
docker compose up -d
```

Verify the database is running before continuing.

---

## 3. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## 4. Run migrations

Use the project's Alembic configuration:

```bash
alembic upgrade head
```

---

## 5. Seed the demonstration data

```bash
python seed.py
```

The primary deterministic scenario is:

```text
VK-1042
Chennai → Vellore
```

---

## 6. Start FastAPI

Run the backend using the project's configured entrypoint.

For example:

```bash
uvicorn app.main:app --reload --port 8001
```

The exact command should follow the current project configuration.

---

## 7. Start the frontend

Use the frontend's configured development server.

For example:

```bash
cd frontend
npm install
npm run dev
```

Then open the local landing page.

---

# Demo Walkthrough

The fastest way to understand VaxKavach is to run the VK-1042 scenario.

## Step 1 — Landing

Open the landing page.

Understand the basic idea:

> Every degree, accounted for.

---

## Step 2 — Launch the Operations Desk

Open the Overview.

You should see the operational network.

---

## Step 3 — Find VK-1042

Locate:

```text
VK-1042
Chennai → Vellore
```

---

## Step 4 — Observe the Simulation

Start the simulation.

Watch the shipment telemetry change.

---

## Step 5 — Temperature Changes

The simulated temperature begins moving away from its normal state.

The detection system evaluates the changing conditions.

---

## Step 6 — Problem Appears

The backend identifies the developing temperature problem.

The frontend reflects this across the relevant operational views.

---

## Step 7 — Investigate

Open Problem Details.

Look at:

```text
Temperature
Temperature Change
Temperature Impact / MKT
GPS
Door
Transit
Environmental context
```

The goal is to answer:

> **Why did this happen?**

---

## Step 8 — Recommendation

The system produces a recommended operational action.

The operator can inspect the evidence before acting.

---

## Step 9 — Reroute

Authorize the simulated reroute.

The action is sent to the backend.

The shipment's operational state changes.

---

## Step 10 — History

Open History.

The resulting operational event should appear in the chronological record.

The audit chain can be inspected there.

---

# Design Philosophy

VaxKavach intentionally avoids the visual language of typical "AI dashboards."

The operational interface uses:

```text
Graphite
Black
Warm Cream
Muted Green
Muted Amber
Muted Red
```

rather than:

```text
Neon Blue
Neon Purple
Cyberpunk Green
Glowing Gradients
```

The reason is simple:

> This is an operations system, not a gaming interface.

The UI should communicate:

**calm → evidence → decision → action.**

---

# Engineering Decisions

## 1. Backend as the source of truth

The frontend does not independently determine shipment health.

```text
Backend
   ↓
REST / WebSocket
   ↓
Frontend
```

This prevents the UI from drifting away from the actual operational state.

---

## 2. Deterministic simulation

The demonstration should be reproducible.

A judge should be able to see the same scenario without relying on unpredictable external sensor data.

---

## 3. Explainable detection

Every problem should have evidence.

The system should be able to answer:

```text
What happened?
Why did it happen?
How severe is it?
What should I do?
```

---

## 4. Mathematical temperature analysis

MKT provides a thermal-history metric instead of relying only on instantaneous temperature.

---

## 5. Spatial reasoning

Location is operationally meaningful.

Knowing that a shipment is in trouble is useful.

Knowing that it is:

```text
10 km from a suitable cooling facility
```

is much more actionable.

---

## 6. Auditability

Operational decisions should leave evidence.

The hash-chain mechanism provides a tamper-evident history structure.

---

# Limitations

This project is a demonstration.

It is not currently a production vaccine logistics deployment.

Important limitations include:

### Simulated telemetry

The current demonstration uses simulated data rather than physical IoT devices.

### Simulated actuation

Rerouting is a software demonstration.

It does not physically control a truck.

### Simulated external conditions

Weather/environmental signals are represented as part of the simulation.

### Limited deployment scope

The project currently focuses on demonstrating the operational intelligence loop rather than supporting an entire national vaccine distribution network.

### No ML prediction

The current system uses deterministic logic.

---

# Future Work

The architecture can be extended toward a production system.

Potential next steps include:

## Real IoT integration

Connect actual:

* temperature sensors
* GPS trackers
* door sensors
* humidity sensors

through an IoT gateway.

---

## Predictive failure detection

Use historical telemetry to predict:

* refrigeration failure
* compressor degradation
* battery problems
* prolonged thermal excursions

---

## Real weather integration

Use real weather APIs to enrich environmental context.

---

## Multi-shipment fleet optimization

Move from a single primary demonstration shipment to a larger operational fleet.

---

## Advanced route optimization

Consider:

* traffic
* weather
* depot capacity
* refrigeration availability
* delivery deadlines

---

## Automated compliance reports

Generate evidence packages containing:

* temperature history
* MKT
* excursions
* corrective actions
* audit history

---

## Role-based operations

Introduce:

* operator
* supervisor
* logistics manager
* compliance reviewer

roles.

---

## Hardware actuation

In a production system, validated integrations could allow recommendations to trigger approved operational systems.

This would require significantly stronger safety, validation and authorization controls than the current demonstration.

---

# Compliance Position

VaxKavach is designed around concepts relevant to regulated cold-chain operations.

The project may reference frameworks such as:

* WHO Good Distribution Practices
* FDA 21 CFR Part 11 concepts
* pharmaceutical cold-chain requirements

However:

> **VaxKavach is not claiming WHO, FDA, ISO, or other regulatory certification.**

The current project demonstrates technical concepts such as:

* traceability
* auditability
* temperature history
* evidence-based decisions
* tamper-evident records

Any production deployment would require formal validation, qualification, security controls, SOPs, regulatory review and appropriate certification.

---

# Why This Project Matters

The interesting problem is not:

> "Can we read a temperature sensor?"

That is relatively straightforward.

The harder problem is:

> **"Can we turn thousands of operational signals into a decision that a human operator can trust?"**

A cold-chain operator does not necessarily need another dashboard.

They need answers.

```text
What is happening?
        ↓
Where is it happening?
        ↓
Why is it happening?
        ↓
How serious is it?
        ↓
What should I do?
        ↓
Can I prove what happened later?
```

That is the problem VaxKavach is designed to solve.

---

# The Entire System in One Diagram

```text
                       VAXKAVACH
                           │
                           ▼
                ┌────────────────────┐
                │   LIVE SHIPMENT    │
                │      SIGNALS       │
                └─────────┬──────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
     Temperature        Location          Door
          │               │                │
          └───────────────┼────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ DETECTION ENGINE│
                 └────────┬────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
             MKT        TEMP Δ     CORRELATION
              │           │           │
              └───────────┼───────────┘
                          ▼
                  ┌───────────────┐
                  │    PROBLEM    │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ RECOMMENDATION│
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │    OPERATOR   │
                  │     ACTION    │
                  └───────┬───────┘
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
           ROUTE CHANGE          AUDIT
                │                   │
                └─────────┬─────────┘
                          ▼
                  ┌───────────────┐
                  │   VERIFIED    │
                  │    HISTORY    │
                  └───────────────┘
```

---

# The Short Version

If you only remember one thing about VaxKavach, remember this:

```text
WATCH
  ↓
SPOT
  ↓
EXPLAIN
  ↓
RECOMMEND
  ↓
ACT
  ↓
RECORD
```

VaxKavach turns cold-chain telemetry into an operational decision.

**Every degree, accounted for.**
