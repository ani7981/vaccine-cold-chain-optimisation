# VaxKavach API / Action Matrix

| UI action | Server operation | UI result |
| --- | --- | --- |
| Load operational screens | `GET /api/shipments/`, `GET /api/fleet/`, `GET /api/problems/` | Render server records and live values. |
| Open shipment / telemetry | `GET /api/shipments/{id}`, `/telemetry`, `/problems` | Bind the selected shipment rather than a fixed VK-1042 fixture. |
| Open problem | `GET /api/problems/{id}` | Bind the problem and its recommendation. |
| Start live source | `POST /api/simulation/start`, `WS /api/ws` | Existing simulator is authoritative for telemetry updates. |
| Acknowledge problem | `POST /api/problems/{id}/acknowledge` | Persist status and append audit event. |
| Authorize reroute | `POST /api/shipments/{id}/reroute` | Validate active recommendation/depot, update shipment/problem/recommendation/transit state, append audit event. |
| Override problem | `POST /api/problems/{id}/override` | Persist override and append audit event. |
| History integrity | `GET /api/audit/`, `POST /api/audit/verify` | Display actual ledger and verification result. |
| Export incident log | `GET /api/problems/` then client CSV | Export loaded server problem records only. |

Driver communications and probe diagnostics remain clearly demo-only: the backend has no telephony or hardware diagnostic capability, so neither action claims a physical operation.
