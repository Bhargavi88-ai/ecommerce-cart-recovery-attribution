# System Architecture & Development Specification Prompt

This file preserves the foundational specification and engineering requirements for the E-Commerce Abandoned Cart Recovery and Campaign Attribution System.

## Project Scope
Build a complete, production-grade project demonstrating:
1. Realistic synthetic data generation (50,000 carts, 20,000 abandoned, ~10,000 sends, seed: 20261022).
2. Relational database schema with 12 entities (Customer, Consent, Session, Cart, CartLine, Product, Campaign, MessageTemplate, SendAttempt, CommunicationEvent, Order, OrderLine, Attribution, AnomalyRecord).
3. Deterministic business logic engines:
   - Inactivity abandonment detection (60 min).
   - Independent Email/SMS point-in-time consent & suppression (`CONSENT_WITHDRAWN`).
   - Rolling 7-day frequency caps (max 3 messages per channel).
   - Simulated carrier telemetry (`SEND` -> `DELIVERED` -> `OPENED` -> `CLICKED` -> `BOUNCED`/`FAILED`).
   - Deterministic last-click attribution (7-day window, non-double-counted).
4. Labelled anomaly fixtures:
   - `MESSAGE_AFTER_OPTOUT`
   - `CART_ABANDONED_AFTER_PURCHASE`
   - `DUPLICATE_ATTRIBUTION`
   - `STALE_CART_TOTAL`
5. 16-point automated data quality validation suite.
6. Bitwise reproducible exports with source manifest and SHA-256 hashes.
7. Full-stack implementation: FastAPI backend + React 18 / Vite / TypeScript / Tailwind CSS / Recharts frontend.
