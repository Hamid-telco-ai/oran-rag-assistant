# O-RAN Components

## SMO
- Role: Central management, orchestration, and automation layer
- Key interfaces: O1, O2
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: SMO: Service Management and Orchestration system.
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: SMO
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: Service Management and Orchestration

---

## Non-RT RIC
- Role: Non-real-time optimization and policy layer
- Key interfaces: A1, R1
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: Non-RT RIC (O-RAN non-real-time RAN Intelligent Controller): a logical function that enables non-real-time control
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: A1: Interface between Non-RT RIC and Near-RT RIC to enable policy-driven guidance of Near-RT RIC
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: rApp: An application designed to run on the Non-RT RIC. Such modular application leverages the functionality exposed

---

## Near-RT RIC
- Role: Near-real-time control and optimization layer
- Key interfaces: E2, A1, O1, Y1
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: based guidance of applications/features in Near-RT RIC.
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: Near-RT RIC (O-RAN near-real-time RAN Intelligent Controller): a logical function that enables near-real-time control
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: A1: Interface between Non-RT RIC and Near-RT RIC to enable policy-driven guidance of Near-RT RIC

---

## O-CU-CP
- Role: Control-plane central unit
- Key interfaces: E2, O1
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O-CU-CP: O-RAN Central Unit – Control Plane: a logical node hosting the RRC and the control plane part of the PDCP
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: for NR access: O-CU-CP, O-CU-UP, O-DU or any combination
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: RAN requirements to host the relevant O-RAN functions (such as Near-RT RIC, O-CU-CP, O-CU-UP, and O-DU), the

---

## O-CU-UP
- Role: User-plane central unit
- Key interfaces: E2, O1
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O-CU-UP: O-RAN Central Unit – User Plane: a logical node hosting the user plane part of the PDCP protocol and the
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: for NR access: O-CU-CP, O-CU-UP, O-DU or any combination
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: RAN requirements to host the relevant O-RAN functions (such as Near-RT RIC, O-CU-CP, O-CU-UP, and O-DU), the

---

## O-DU
- Role: Distributed unit hosting RLC, MAC, and High-PHY functions
- Key interfaces: E2, O1, Open Fronthaul
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O-DU: O-RAN Distributed Unit: a logical node hosting RLC/MAC/High-PHY layers based on a lower layer functional
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: for NR access: O-CU-CP, O-CU-UP, O-DU or any combination
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: RAN requirements to host the relevant O-RAN functions (such as Near-RT RIC, O-CU-CP, O-CU-UP, and O-DU), the

---

## O-RU
- Role: Radio unit hosting Low-PHY and RF functions
- Key interfaces: Open Fronthaul
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O-RU: O-RAN Radio Unit: a logical node hosting Low-PHY layer and RF processing based on a lower layer functional
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: beam failure statistics. The rApp knows O-RU specifics such as antenna array parameters, O-RU capabilities, beam file
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: Towards O-RU

---

## O-Cloud
- Role: Cloud platform hosting O-RAN functions and workloads
- Key interfaces: O2
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: O-Cloud: O-Cloud is a cloud computing platform comprising a collection of physical infrastructure nodes that meet O-
  - O-RAN.WG1.Network-Energy-Savings-Technical-Report-R003-v02.00.pdf: O-Cloud Resource Energy Saving Mode
  - O-RAN.WG1.Network-Energy-Savings-Technical-Report-R003-v02.00.pdf: O-CU/O-DU Hardware & Software / O-Cloud Software & Platform KPIs

---

## xApp
- Role: Application running on Near-RT RIC for near-real-time optimization and control
- Key interfaces: E2
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: xApp: An application designed to run on the Near-RT RIC. Such an application is likely to consist of one or more
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: between the xApp and the RAN functionality.
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: The Near-RT RIC may host an xApp to optimize inter-cell beam mobility such as bMRO. In this case the Near-RT RIC

---

## rApp
- Role: Application running on Non-RT RIC for non-real-time optimization and policy generation
- Key interfaces: R1, A1
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: rApp: An application designed to run on the Non-RT RIC. Such modular application leverages the functionality exposed
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: The Non-RT RIC hosts an rApp application whose task is to determine the suitable GoB configuration for a cell or a
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: beam failure statistics. The rApp knows O-RU specifics such as antenna array parameters, O-RU capabilities, beam file

---
