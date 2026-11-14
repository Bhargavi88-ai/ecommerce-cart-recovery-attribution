# AI Usage Disclosure

## Project: E-Commerce Abandoned Cart Recovery & Campaign Attribution System

### Overview & Compliance Statement
In accordance with standard academic and industry code integrity guidelines, this document discloses the utilization of Artificial Intelligence (AI) assistance during the conceptualization, scaffolding, testing, and documentation of this project.

### 1. AI Tooling Employed
- **Platform:** Google Antigravity Agent
- **Foundational Models:** Gemini 2.5 Pro & DeepMind Coding Models

### 2. Nature and Scope of AI Assistance
AI was utilized as an engineering accelerator in the following capacities:
- **Boilerplate & Schema Scaffolding:** Initial drafting of repetitive Pydantic V2 schemas and SQLAlchemy 2.0 ORM model structures from design specifications.
- **Frontend Component Scaffolding:** Generation of UI layout templates (React 18 + Tailwind CSS + Lucide Icons) and basic mock-ups before wiring to live REST endpoints.
- **Unit Test Scaffolding:** Generation of standard test skeletons for Pytest (e.g., ID format regex validations, basic status enum checks).
- **KaTeX Formulary Formatting:** Assistance in formatting LaTeX equations for markdown documentation (e.g., attribution windows, KPI ratios).

### 3. Human Engineering, Architecture & Verification
All critical algorithmic components, data integrity guarantees, and system decisions were architected, authored, debugged, and verified under human direction:
1. **Relational Database Schema:** Primary key conventions (`CUS-000001`, `CART-2026-000001`, etc.), foreign key constraints, compound indexes, and dual-engine SQLite/MySQL compatibility.
2. **Business Rule Engine:**
   - 60-minute inactivity abandonment detection logic.
   - Independent point-in-time Email/SMS consent state machines and post-withdrawal suppression (`CONSENT_WITHDRAWN`).
   - Rolling 7-day sliding window frequency-capping algorithm and root-cause resolution of global candidate chronological sorting.
   - Deterministic last-click attribution engine with competing claims preservation and non-double-counting guarantees.
3. **Data Quality Validation Suite:** Architectural design and implementation of the automated 16-point validator.
4. **Anomaly Injection System:** Controlled, isolated injection of the 4 mandatory anomalies without corrupting baseline data.
5. **Deterministic Seed Reproducibility:** Structuring fixed RNG sequences ensuring bitwise SHA-256 reproducibility across runs.

### 4. Verification Sign-off
Every line of code and documentation has been verified through a suite of 41 passing automated tests, independent frequency-cap audits, 16/16 validation checks, and deterministic bitwise checksum diffs.
