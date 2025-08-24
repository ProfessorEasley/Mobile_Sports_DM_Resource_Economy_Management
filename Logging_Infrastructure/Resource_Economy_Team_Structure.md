# 🪙 Resource & Economy Management System - Team Structure Document

## 🎯 Core Goal
Design and implement the full economic simulation backbone for Monster Gridiron. The system must manage multi-currency flows, contract-triggered payouts, wallet UI, and analytics coverage.

---

## 👥 Revised Team Assignments

### **Systems Core Team** (2 interns)
**Harsh Zele** + **Dhruv Rajvansh** (50% time)

**Harsh Focus:**
- `WalletSystem` and DB schema
- API layer for coins, gems, and credits
- Transactional safety and mutex DB operations
- Salary Engine integration with external triggers

**Dhruv Focus (Systems 50%):**
- Unity-side MonoBehaviour for Wallet & Salary display
- Unity JSON output pipeline
- Salary bonus multiplier pipeline
- Sync triggers and performance profiling

---

### **UI & UX Implementation Team** (2 interns)
**Jamie Wei** + **Dhruv Rajvansh** (50% time)

**Jamie Focus:**
- Wallet HUD and Forecast Panel wireframes
- UX polish on Ledger and Bonus Views
- Accessibility and touch target pass
- Unity/Canvas prototyping of 4 screens

**Dhruv Focus (UI 50%):**
- Full Unity implementation of wireframes
- Transition logic and screen state memory
- Performance optimization for resource screens

---

### **Analytics and Balancing Team** (2 interns)
**Bhuvan Jayakumar** + **Dhruv Nadkar**

**Bhuvan Focus:**
- Logging hooks across all economic triggers
- Weekly delta and inflation dashboard pipeline
- Contract bonus inflation detection and mitigation

**Dhruv N. Focus:**
- Economy failure case modeling
- Forecast module behavior validation
- Alert thresholds and UX warning design

---

## 🔄 Dhruv’s Dual Role Workflow

### Daily Cycle
- **Morning (3–4 hrs)**: Systems integration, backend JSON/engine debugging
- **Afternoon (3–4 hrs)**: UI pipeline, animations, transitions
- **Friday**: Full system test day (cross-team handoff testing)

### Weekly Role Rotation
- Weeks 1–2: Systems-heavy (70%/30%)
- Weeks 3–4: Even balance (50%/50%)
- Weeks 5–6: UI-heavy (40%/60%)
- Weeks 7–8: Full polish cycle

### Handoff Protocols
**Jamie → Dhruv:** UI specs, Figma artifacts, responsive layout notes  
**Harsh → Dhruv:** REST API contract, schema migrations, test data  
**Bhuvan → Dhruv:** Metrics definitions, logging expectations, dashboard specs

---

## 📋 12-Week Schedule Highlights

### Weeks 1–2: Economic System Setup
- Harsh: DB schema, WalletSystem core
- Dhruv (Systems): JSON pipe, Unity shell setup
- Jamie: Forecast panel UX, ledger mockups
- Bhuvan: Metrics definitions, inflation model draft

### Weeks 3–4: Bonus & Salary Logic
- Harsh: Contract trigger logic, API safety tests
- Dhruv (UI): Wallet screen + Bonus panel
- Jamie: Interaction polish, mobile constraints pass
- Bhuvan + Dhruv N.: Initial alert logic + weekly delta graph

### Weeks 5–6: Forecast & Modifiers
- Harsh: Facilities + Acquisition modifier hooks
- Dhruv: Forecast + Modifier panel logic
- Jamie: Animation polish pass
- Analytics: End-to-end economic loop validation

### Weeks 7–8: Test, Polish, Handoff Prep
- All: Code freeze, UX testing, mobile profile
- Docs: Architecture, schema, test data
- Dhruv: Game simulation + save/load integration

### Weeks 9–12 (stretch):
- Additional dashboards, tuning tools, and monetization interfaces

---

## 📊 Success Metrics

### Technical
- Wallet update < 300ms  
- Forecast render < 1.5s  
- Log coverage > 95% of earn/spend events

### UX
- Forecast + Wallet understood in < 3 taps
- Bonus effects visible within 2 sessions

### Integration
- Unity JSON format conformant to schema v1.2
- Weekly ticks sync with Coaching + Acquisition modifiers

---

## ⚠️ Risk Management

### Dhruv Overload Risk
- Pre-scheduled role splits, weekly syncs
- Clear upstream/downstream docs from Jamie/Harsh

### Data Flow Errors
- Use static mocks for early prototyping
- Dashboard triggers via parity check and inflation threshold alerts

### Salary Inflation Edge Cases
- Daily simulation loop + inflation caps
- Contract stacking flag + warning system

---

## ✅ Final Validation
- Daily Slack checkpoints, Friday integration demos
- 3+ user testers evaluate Ledger + Forecast UI clarity
- Cross-team budget state parity after Week 6

This structure delivers a fully cross-validated, system-integrated economic simulation pipeline with player-facing UI, analytics coverage, and robust testing loops.
