# O-RAN Interfaces

## A1
- Between: Non-RT RIC ↔ Near-RT RIC
- Purpose: Policy-based guidance, enrichment information, and model-related coordination
- Type: Non-real-time interface
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: A1: Interface between Non-RT RIC and Near-RT RIC to enable policy-driven guidance of Near-RT RIC
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: study potential impact and required enhancements to O-RAN interfaces E2, O1, A1, FH M-plane, FH CUS-Plane,
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: WG2 (Non-RT RIC, A1, R1) Impact

---

## E2
- Between: Near-RT RIC ↔ E2 Nodes (e.g., O-CU-CP, O-CU-UP, O-DU)
- Purpose: Near-real-time monitoring and control
- Type: Near-real-time interface
- Notes: Uses E2 Service Models (E2SM) for structured monitoring and control.
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: over E2 interface.
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O-eNB (O-RAN eNB): an eNB or ng-eNB that supports E2 interface.
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: E2: Interface connecting the Near-RT RIC and one or more O-CU-CPs, one or more O-CU-UPs, and one or more O-DUs.

---

## O1
- Between: SMO ↔ O-RAN Network Functions
- Purpose: Operations, administration, management, telemetry, and configuration
- Type: Management interface
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O1: Interface between orchestration & management entities (Orchestration/NMS) and O-RAN managed elements, for
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: study potential impact and required enhancements to O-RAN interfaces E2, O1, A1, FH M-plane, FH CUS-Plane,
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: over the relevant interface, e.g., O1, E2.

---

## O2
- Between: SMO ↔ O-Cloud
- Purpose: Cloud resource, infrastructure, and workload management
- Type: Orchestration interface
- Notes: Can include infrastructure management and deployment/lifecycle management roles.
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: Transfer the appropriate bMRO ML model to the Near-RT RIC over O1/O2.
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: for the purpose of training of relevant AI/ML models. Retrieve ML Models from the Non-RT RIC over O1/O2.
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: N modes (or simply to predict the best mode) and deploys the trained models in xApp to near-RT RIC (over O1 or O2 –

---

## Y1
- Between: Near-RT RIC ↔ Y1 consumers
- Purpose: Exposure of RAN analytics services
- Type: Analytics exposure interface
- Evidence:
  - O-RAN.WG1.TS.OAD-R005-v16.00.docx: O-RAN.WG3.TS.Y1GAP: "O-RAN Y1 interface: General Aspects and Principles" ("Y1GAP").
  - O-RAN.WG1.TS.OAD-R005-v16.00.docx: Near-RT RIC platform: Platform supporting A1, E2, Y1 and O1 interfaces and providing a set of services via Near-RT RIC APIs needed for xApp functionality.
  - O-RAN.WG1.TS.OAD-R005-v16.00.docx: Y1: An interface over which RAN analytics services are exposed by the Near-RT RIC to be consumed by Y1 consumers.

---

## R1
- Between: rApps ↔ Non-RT RIC framework / SMO services
- Purpose: Service-based interaction for rApps
- Type: Service-based interface
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: R1 and Near-RT RIC API,
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: SMO -> rAPP: <<R1>> Update Model Request
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: SMO -> rAPP: <<R1>> Data Retrieval

---

## Open Fronthaul
- Between: O-DU ↔ O-RU
- Purpose: Transport of fronthaul management, synchronization, control, and user-plane related functions
- Type: Fronthaul interface family
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: study potential impact and required enhancements to O-RAN interfaces E2, O1, A1, FH M-plane, FH CUS-Plane,
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: via Open FH M-Plane reading o-ran-beamforming YANG module.
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: via Open FH M-Plane transferring proprietary beamforming configuration file

---
