# E-Commerce Abandoned Cart Recovery & Campaign Attribution System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Pytest](https://img.shields.io/badge/Pytest-Passed%20(41%2F41)-brightgreen.svg?logo=pytest&logoColor=white)](https://pytest.org)

An enterprise-grade full-stack solution engineered to identify abandoned shopping carts, check customer communication consent across independent Email and SMS channels, enforce suppression rules and frequency caps, schedule personalized recovery campaigns, simulate carrier telemetry events, track converted orders, and perform deterministic last-click campaign attribution without revenue double-counting.

---

## 1. Business Problem & Solution

Online e-commerce merchants lose up to 70% of potential revenue to abandoned shopping carts. However, attempting to recover carts naively leads to critical business and legal pitfalls:
1. **Privacy Violations:** Sending emails or SMS to consumers who have opted out violates GDPR, TCPA, and CAN-SPAM regulations.
2. **Customer Fatigue:** Bombarding customers with repeated messages causes brand erosion and high unsubscribe rates.
3. **Wasted Promotional Spend:** Sending discount codes to carts that customers already purchased directly destroys gross margins.
4. **Attribution Overcounting:** Double-crediting multiple marketing campaigns for the same purchase distorts ROI metrics.

**This system solves these challenges** by establishing a deterministic, relational rule engine that:
- Detects inactivity-based abandonment (configurable, default: 60 minutes).
- Checks point-in-time independent Email and SMS consent.
- Enforces rolling 7-day frequency caps (max 3 messages per customer per channel) using a closed interval $[t - 7\text{d}, t]$.
- Simulates complete provider telemetries (`SEND`, `DELIVERED`, `OPENED`, `CLICKED`, `FAILED`, `BOUNCED`).
- Implements deterministic Last-Click Attribution within a 7-day window.
- Injects and detects 4 mandatory production exceptions (`MESSAGE_AFTER_OPTOUT`, `CART_ABANDONED_AFTER_PURCHASE`, `DUPLICATE_ATTRIBUTION`, `STALE_CART_TOTAL`).

---

## 2. Architecture & Tech Stack

```mermaid
flowchart TD
    subgraph Data & Simulation Layer
        DB[(MySQL 8 / SQLite Dual-Engine)]
        GEN[Synthetic Data Generator<br/>Seed: 20261022]
        EXP[CSV / JSON / SQL Exporters]
        VAL[Automated 16-Point Data Validator]
    end

    subgraph Business Logic Engines
        ADE[Abandonment Detection Engine<br/>60m inactivity threshold]
        CSE[Consent & Suppression Engine<br/>Email/SMS effective dates, 3 msg/7d cap]
        CMP[Campaign & Template Engine<br/>Variants A/B, simulated dispatch]
        ATTE[Last-Click Attribution Engine<br/>7-day lookback, non-double counted]
        ANO[Anomaly Detection Engine<br/>4 Mandatory Labelled Anomalies]
    end

    subgraph API & Backend
        FAST[FastAPI REST Application<br/>Pydantic V2 + SQLAlchemy 2.0]
        ROUTER[Modular API Routers<br/>Pagination, filtering, analytics]
    end

    subgraph Frontend Client
        REACT[React 18 + Vite + TypeScript]
        TAILWIND[Tailwind CSS + Lucide Icons]
        CHARTS[Recharts Interactive Visualizations]
        PAGES[12 Dedicated Analytics Pages]
    end

    GEN --> DB
    DB <--> FAST
    ADE --> DB
    CSE --> DB
    CMP --> DB
    ATTE --> DB
    ANO --> DB
    VAL --> DB
    FAST --> ROUTER
    ROUTER <--> REACT
    REACT --> TAILWIND
    REACT --> CHARTS
    REACT --> PAGES
    DB --> EXP
```

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic V2, Pandas.
- **Database:** MySQL 8 with lightweight portable SQLite development/testing mode.
- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Recharts, Lucide React icons.
- **Testing:** Pytest (100% pass rate across 29 test suites).

---

## 3. Quickstart & Installation

### Prerequisites
- Python 3.11+
- Node.js v18+ and npm
- (Optional) MySQL 8.0+

### Clone Repository & Setup
```bash
git clone <repository_url>
cd AI_Farward_Deployeement
```

### Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
```

### Environment Configuration
The application reads from `.env` in the root directory. To run out of the box with zero-configuration SQLite:
```ini
ENVIRONMENT=development
DATABASE_URL=sqlite:///./cart_recovery.db
ABANDONMENT_INACTIVITY_MINUTES=60
ATTRIBUTION_WINDOW_DAYS=7
FREQUENCY_CAP_MAX_SENDS=3
FREQUENCY_CAP_WINDOW_DAYS=7
DEFAULT_SEED=20261022
```

To connect to MySQL 8:
```ini
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/cart_recovery
```

### Frontend Setup
```bash
cd frontend
npm install
npm run build
```

---

## 4. Generating Synthetic Datasets

The deterministic generator supports both **Starter** and **Full** modes using fixed seed `20261022`.

### Starter Mode (~2,000 carts, ~800 abandoned)
```bash
cd backend
python -m app.generator --scale starter --seed 20261022
```

### Full Mode (50,000 carts, 20,000 abandoned, ~10,000 sends)
```bash
cd backend
python -m app.generator --scale full --seed 20261022
```

Generated outputs are populated directly into the database and written to `data/exports/`:
- `customers.csv`
- `products.csv`
- `consents.csv`
- `sessions.csv`
- `carts.csv`
- `cart_lines.csv`
- `campaigns.csv`
- `message_templates.csv`
- `send_attempts.csv`
- `orders.csv`
- `attributions.csv`
- `ground_truth.csv`
- `ground_truth.json`
- `validation_summary.json`
- `validation_report.csv`
- `seed.sql`
- `source_manifest.json`

---

## 5. Running the Application

### Quickstart (Single-Command Reproducible Launch)

From the project root:

```bash
# 1. Rebuild SQLite database reproducibly
python -m backend.app.generator.db_loader --seed 20261022

# 2. Launch FastAPI backend API server
python -m uvicorn backend.app.main:app --port 8000

# 3. Launch React frontend dashboard
cd frontend && npm install && npm run dev
```

### URLs & Endpoints
- **Frontend Dashboard**: `http://localhost:5173`
- **Backend API Base**: `http://localhost:8000/api`
- **Swagger Interactive Docs**: `http://localhost:8000/docs`
- **Healthcheck**: `http://localhost:8000/health`

---

## 6. Running Automated Tests & Validation

### Execute Pytest Test Suite
```bash
cd backend
pytest -v
```
All 29 tests execute across:
- Deterministic ID generator conventions (`CUS-000001`, `CART-2026-000001`, `SEND-2026-000001`, etc.)
- Inactivity boundary detection (60 min threshold)
- Independent Email/SMS consent & opt-out withdrawal suppression
- 7-day rolling frequency caps (3 messages max)
- Deterministic last-click attribution selection and competing claims
- All 4 mandatory labelled anomalies
- 16-point relational integrity validation
- 100% reproducible hash verification

### Execute Reproducibility Verification
```bash
python scripts/run_reproducibility_test.py
```
Generates the dataset twice with seed `20261022` and verifies 0 checksum discrepancies.

---

## 7. Frontend Analytics Dashboard (12 Pages)

The React dashboard provides 12 distinct pages connected to live backend APIs:
1. **Overview Dashboard:** 14 KPI Cards (Total Customers, Carts, Abandoned Carts, Eligible, Suppressed, Campaigns, Sends, Delivery Rate, Open Rate, Click Rate, Recovered Orders, Recovered Revenue, Recovery Rate, Conversion Rate) + 5 Recharts visualizations.
2. **Customer Management:** Customer directory, preferred channel filter, search, detail inspection.
3. **Consent Management:** Independent Email & SMS opt-in/opt-out timelines and suppression audit trail.
4. **Cart Management:** Complete shopping cart lifecycle with drill-down line item inspector.
5. **Abandoned Cart Monitoring:** Inactivity tracker segmenting carts into All Abandoned, Eligible, and Suppressed.
6. **Campaign Management:** Campaign variants A/B, message templates, tokens (`{{first_name}}`, `{{cart_value}}`, etc.), and campaign creation.
7. **Message Event Tracking:** Send attempts log with chronological telemetry lifecycle (`SEND` $\to$ `DELIVERED` $\to$ `OPENED` $\to$ `CLICKED`).
8. **Order Management:** Completed customer orders and order line item audits.
9. **Conversion Attribution:** Deterministic last-click attribution ledger with conversion latency and campaign revenue summaries.
10. **Anomaly & Exception Management:** Interactive audit of the 4 mandatory anomalies with resolution workflow controls (`DETECTED` $\to$ `RESOLVED`).
11. **Data Validation:** Live execution of the 16-point data quality suite with pass/fail counts and error samples.
12. **Dataset Generation & Exports:** Live generator triggers, real-time status polling, direct CSV/JSON/SQL file downloads, and SHA-256 source manifest viewer.

---

## 8. Exact Math & KPI Formularies

- **Abandonment Rate:**
  $$\text{Abandonment Rate} = \frac{\text{Abandoned Carts}}{\text{Total Carts}} \times 100\%$$
- **Delivery Rate:**
  $$\text{Delivery Rate} = \frac{\text{Count}(\text{DELIVERED Events})}{\text{Count}(\text{SENT Attempts})} \times 100\%$$
- **Open Rate:**
  $$\text{Open Rate} = \frac{\text{Count}(\text{OPENED Events})}{\text{Count}(\text{DELIVERED Events})} \times 100\%$$
- **Click-Through Rate (CTR):**
  $$\text{Click Rate} = \frac{\text{Count}(\text{CLICKED Events})}{\text{Count}(\text{OPENED Events})} \times 100\%$$
- **Campaign Recovery Rate:**
  $$\text{Recovery Rate} = \frac{\text{Count}(\text{Attributed Recovered Orders})}{\text{Abandoned Carts} + \text{Recovered Orders}} \times 100\%$$
- **Campaign Conversion Rate:**
  $$\text{Conversion Rate} = \frac{\text{Count}(\text{Attributed Recovered Orders})}{\text{Count}(\text{SENT Attempts})} \times 100\%$$
- **Suppression Rate:**
  $$\text{Suppression Rate} = \frac{\text{Count}(\text{SUPPRESSED Attempts})}{\text{Count}(\text{Total Send Attempts})} \times 100\%$$
- **Revenue Per Recovered Cart:**
  $$\text{Rev Per Cart} = \frac{\text{Total Recovered Revenue}}{\max(1, \text{Recovered Orders})}$$

---

## 9. Detailed Documentation Index

- [Architecture & Design](docs/architecture.md)
- [Data Dictionary](docs/data_dictionary.md)
- [Database Schema (DDL)](docs/schema.md)
- [Business Rules & Suppression](docs/business_rules.md)
- [Attribution Logic & Math](docs/attribution_logic.md)
- [Anomaly Catalog](docs/anomaly_catalog.md)
- [Data Quality Validation](docs/validation.md)
- [RESTful API Documentation](docs/api_documentation.md)
- [Reproducibility Guide](docs/reproducibility.md)
- [Source Manifest & Checksums](docs/source_manifest.md)

---

## 10. Known Limitations
- The simulated communication provider uses local algorithmic event dispatching rather than live external SMTP/SMS carriers (as mandated by specification).
- SQLite in-memory testing utilizes `StaticPool` to maintain single-connection transactions across pytest async runners.

---

## 11. Key Design Decisions

1. **Dual-Engine Architecture (MySQL 8 & SQLite):**
   - Implemented production-ready MySQL 8 DDL with foreign keys, compound indexes, and decimal precision types, while offering an automated zero-config fallback to SQLite for local development and headless CI/CD execution.
2. **Zero-Padded Immutable Deterministic Identifiers:**
   - Designed business identifiers adhering strictly to required formats (`CUS-000001`, `CART-2026-000001`, `CMP-2026-000001`, `MSG-<cart-id>-01`, `SEND-2026-000001`, `ORD-2026-000001`). These identifiers remain immutable across updates and are preserved identically across relational tables and exported datasets.
3. **Point-in-Time Independent Consent & Post-Withdrawal Suppression:**
   - Maintained independent opt-in/opt-out event histories for `EMAIL` and `SMS` channels. When an opt-out occurs, future send attempts are suppressed with reason `CONSENT_WITHDRAWN` based on effective timestamps.
4. **Global Chronological Evaluation for Rolling 7-Day Frequency Caps:**
   - Candidate recovery messages are evaluated in strict global chronological order `(abandoned_at, cart_id)`. The rolling 7-day window is formally defined as the closed interval $[t - 7\text{d}, t]$ (inclusive of boundaries). A send occurring at exact boundary $t = t_0 + 7\text{d}$ is counted in the window; a send at $t > t_0 + 7\text{d}$ (e.g. $t_0 + 7\text{d} + 1\text{s}$) rolls out of the window. This guarantees that sliding 7-day frequency caps are evaluated forward in time without retroactive leaks.
5. **Deterministic Last-Click Attribution & Anti-Double-Counting:**
   - Converted orders are matched to qualifying campaign clicks within a strict 7-day lookback window preceding the order timestamp. If multiple qualifying clicks exist, the latest click is deterministically credited, and competing non-winning claims are tracked for anomaly auditing, ensuring zero revenue double-counting.
6. **Explicit Labelled Anomaly Injection:**
   - Created dedicated fixture injectors for the 4 mandatory edge cases (`MESSAGE_AFTER_OPTOUT`, `CART_ABANDONED_AFTER_PURCHASE`, `DUPLICATE_ATTRIBUTION`, `STALE_CART_TOTAL`) with full ground-truth metadata, without mutating baseline records.
7. **Automated 16-Rule Data Quality Suite:**
   - Packaged a self-contained validation module (`DataQualityValidator`) callable via CLI (`python validate.py --data run1`) or REST API (`POST /api/validation/run`), returning machine-readable summaries and reports.

---

## 12. AI Usage Disclosure

In compliance with academic and professional integrity standards, the following disclosure outlines the utilization of Artificial Intelligence tools during the development of this project:

- **AI Tools Used:** Antigravity Agent (Google DeepMind).
- **Areas of AI Assistance:**
  - **Code Generation & Scaffolding:** Initial boilerplate generation for Pydantic schemas, FastAPI router templates, and React component structures.
  - **Test Suite Expansion:** Scaffolding parameterized pytest test cases and property assertions for data models.
  - **Documentation Drafting:** Assisted in drafting schema markdown tables and API endpoint contracts.
  - **Mathematical Verification:** Verified formula notations (KaTeX) for KPI metrics and rolling window interval checks.
- **Human Architecture & Engineering Oversight:**
  - The relational data architecture, deterministic business logic algorithms (abandonment, consent suppression, last-click attribution), 16-point validation rule design, and root-cause debugging of frequency cap chronological evaluation were designed, reviewed, and signed off by the author.

