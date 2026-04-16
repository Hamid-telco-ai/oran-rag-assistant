# O-RAN Components

## SMO
- Role: Central management, orchestration, and automation layer
- Functions:
  - lifecycle management
  - network management via O1
  - cloud orchestration via O2
- Hosts: Non-RT RIC
- Key interfaces: O1, O2
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: SMO: Service Management and Orchestration system.

---

## Non-RT RIC
- Role: Non-real-time intelligence and policy layer
- Hosts: rApps
- Functions:
  - policy generation
  - ML training
  - long-timescale optimization
- Key interfaces: A1, R1
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: Non-RT RIC (O-RAN non-real-time RAN Intelligent Controller): a logical function that enables non-real-time control

---

## Near-RT RIC
- Role: Near-real-time control and optimization layer
- Hosts: xApps
- Functions:
  - control decisions
  - KPI processing
  - near-real-time optimization
- Key interfaces: E2, A1, O1, Y1
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: Near-RT RIC (O-RAN near-real-time RAN Intelligent Controller): a logical function that enables near-real-time control

---

## O-CU-CP
- Role: Control plane central unit
- Functions:
  - hosts RRC
  - hosts control-plane PDCP
- Key interfaces: E2, O1
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O-CU-CP: O-RAN Central Unit – Control Plane: a logical node hosting the RRC and the control plane part of the PDCP

---

## O-CU-UP
- Role: User plane central unit
- Functions:
  - hosts user-plane PDCP
  - hosts SDAP
- Key interfaces: E2, O1
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O-CU-UP: O-RAN Central Unit – User Plane: a logical node hosting the user plane part of the PDCP protocol and the SDAP protocol

---

## O-DU
- Role: Distributed unit
- Functions:
  - hosts RLC
  - hosts MAC
  - hosts High-PHY
- Key interfaces: E2, O1, Open Fronthaul
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O-DU: O-RAN Distributed Unit: a logical node hosting RLC/MAC/High-PHY layers based on a lower layer functional split.

---

## O-RU
- Role: Radio unit
- Functions:
  - hosts Low-PHY
  - performs RF processing
- Key interfaces: Open Fronthaul
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O-RU: O-RAN Radio Unit: a logical node hosting Low-PHY layer and RF processing based on a lower layer functional split.

---

## O-Cloud
- Role: Infrastructure platform hosting O-RAN functions and workloads
- Functions:
  - provides compute resources
  - supports workload hosting
  - supports lifecycle management
- Key interfaces: O2
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O-Cloud: O-Cloud is a cloud computing platform comprising a collection of physical infrastructure nodes that meet O-RAN requirements to host the relevant O-RAN functions

---

## xApp
- Runs on: Near-RT RIC
- Role: Near-real-time optimization and control application
- Key interfaces: E2
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: xApp: An application designed to run on the Near-RT RIC.

---

## rApp
- Runs on: Non-RT RIC
- Role: Non-real-time optimization, policy, and ML application
- Key interfaces: R1, A1
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: rApp: An application designed to run on the Non-RT RIC.