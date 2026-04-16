# O-RAN Interfaces

## A1
- Between: Non-RT RIC ↔ Near-RT RIC
- Purpose: Policy guidance and enrichment information transfer
- Type: Non-real-time (>1s)
- Notes:
  - Supports policy and enrichment information (EI)
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: A1: Interface between Non-RT RIC and Near-RT RIC to enable policy-driven guidance

---

## E2
- Between: Near-RT RIC ↔ E2 Nodes (O-CU-CP, O-CU-UP, O-DU)
- Purpose: Near-real-time monitoring and control
- Type: ~10 ms – 1 s
- Notes:
  - Uses E2 Service Models (E2SM)
  - Examples: KPM (monitoring), RC (control)
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: E2 interface supports interaction between Near-RT RIC and RAN nodes

---

## O1
- Between: SMO ↔ O-RAN Network Functions
- Purpose: Management, configuration, and telemetry
- Type: Management plane
- Notes:
  - Supports FCAPS
  - Provides aggregated telemetry
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O1: Interface for management of O-RAN network functions

---

## O2
- Between: SMO ↔ O-Cloud
- Purpose: Infrastructure and workload lifecycle management
- Type: Orchestration interface
- Notes:
  - O2dms → deployment management
  - O2ims → infrastructure management
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O2: Interface between SMO and O-Cloud

---

## Y1
- Between: Near-RT RIC ↔ external consumers
- Purpose: Exposure of RAN analytics
- Type: Data exposure interface
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: Y1 supports analytics exposure

---

## R1
- Between: rApps ↔ Non-RT RIC / SMO services
- Purpose: Service-based communication for rApps
- Type: Service interface
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: rApp interacts with Non-RT RIC services

---

## Open Fronthaul
- Between: O-DU ↔ O-RU
- Purpose: Transport of user data, control, and synchronization
- Type: Real-time fronthaul
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: Open Fronthaul supports communication between O-DU and O-RU