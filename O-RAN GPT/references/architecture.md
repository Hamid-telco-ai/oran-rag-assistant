# O-RAN Architecture

## Overview

O-RAN architecture is a layered, service-oriented system that separates:

- Management and orchestration
- Non-real-time intelligence
- Near-real-time control
- Real-time radio execution

---

## Layered Architecture

```text
SMO
 ├── Non-RT RIC (rApps)
 │       ↓ A1
 ├── Near-RT RIC (xApps)
 │       ↓ E2
 ├── O-CU / O-DU (E2 Nodes)
 │       ↓ Open Fronthaul
 └── O-RU