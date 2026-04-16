# O-RAN Glossary

## E2 Node
- Definition: Logical node connected to Near-RT RIC via E2 interface
- Notes:
  - Includes O-CU-CP, O-CU-UP, O-DU
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: E2 interface supports interaction between Near-RT RIC and RAN nodes

---

## Control Loop
- Definition: Feedback loop used for network optimization
- Notes:
  - Non-RT loop (>1s)
  - Near-RT loop (~10ms–1s)
  - Real-time loop (<10ms)
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: control loop concepts described across RIC layers

---

## A1 Policy
- Definition: Policy sent from Non-RT RIC to Near-RT RIC via A1 interface
- Notes:
  - Guides behavior of xApps
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: A1 enables policy-driven guidance

---

## Enrichment Information
- Definition: Contextual data sent via A1 interface
- Notes:
  - Used to enhance decision-making in Near-RT RIC
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: enrichment information concept referenced in A1 context

---

## E2 Service Model (E2SM)
- Definition: Data model used over E2 interface
- Notes:
  - Defines structure of measurements and control messages
  - Examples: KPM, RC
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: E2-related data structures referenced

---

## O-RAN NF
- Definition: O-RAN Network Function
- Notes:
  - Includes O-CU, O-DU, Near-RT RIC, etc.
- Evidence:
  - O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf: references to O-RAN network functions

---

## Intent
- Definition: High-level objective for network behavior
- Notes:
  - Used in intent-based management
  - Handled by intent owner / handler
- Evidence:
  - O-RAN.WG1 specifications: intent-based management concepts referenced