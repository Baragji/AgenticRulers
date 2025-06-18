# AutonomesAI v2.1 — Master Plan  (Single Source of Truth, June 2025)

> **Scope & purpose** – This canvas is the canonical recipe for taking the project from **zero → MVP → enterprise‑grade** with the least necessary complexity. It merges:
>
> * v2 blueprint from ChatGPT
> * Optimisations from R9‑ZentoGPT (architecture map, test pyramid, scaling matrix, UI design system)
> * Steering committee decisions (upgrade triggers & backlog deferrals)
>
> **Governance rule**: any change to this document must be approved in chat and committed here – no other docs override this one.

---

## 0  Executive summary

LangGraph + OpenTelemetry is the minimal runtime. Local Llama‑3 via **Ollama** keeps cost low. **CrewAI** (roles) and **AutoGen 0.6** (self‑debug) are bolt‑ons activated only when metrics warrant it. OTel Gen‑AI spans give one trace for every LLM/tool call, flowing to Grafana Tempo + Langfuse.

---

## 1  Architecture snapshot

*(see `/docs/diagrams/runtime‑v2.1.svg` for the visual map added by R9)*

| Layer             | Stack                                                                            | Reason                              |
| ----------------- | -------------------------------------------------------------------------------- | ----------------------------------- |
| **Orchestrator**  | LangGraph 0.3 + Swarm add‑on                                                     | Deterministic DAGs, visual debugger |
| **Observability** | OpenTelemetry Gen‑AI ➜ Grafana Tempo & Langfuse                                  | Vendor‑neutral tracing              |
| **Local LLM**     | Ollama 0.3.5 – `llama3:8b` (dev), `llama3:70b` (GPU)                             | 50‑80 % cheaper drafting            |
| **Prompt roles**  | LangGraph `RoleBasedAgent` → *upgrade* CrewAI YAML when role‑churn or >10 agents | Keeps deps light until needed       |
| **Self‑debug**    | Autogen `CodeExecutionAgent` (lazy‑load)                                         | Cuts defective commits by ≈22 %     |
| **Data & RAG**    | Postgres 15 + pgvector IVFFlat                                                   | Cheap vector search                 |
| **Routing**       | OSRM docker service                                                              | Geo routing per tech plan           |
| **Guardrails**    | Upstash Redis RateLimit + budget alert                                           | Token spend under \$10/day          |

---

## 2  Phase roadmap & sprint grid

| Phase  | Days  | Goal                         | Deliverables                                              | Key tools               |
| ------ | ----- | ---------------------------- | --------------------------------------------------------- | ----------------------- |
| **0**  |  1‑3  | Bootstrap runtime            | DevContainer, minimal DAG, OTel console export, CI        | LangGraph, OTel SDK     |
| **1A** | 4‑5   | Local LLM + Next.js skeleton | Ollama service, modelRouter, `apps/web` scaffold          | Node 18, Tailwind       |
| **1B** | 6‑7   | Data & routing slice         | Prisma + pgvector schema, OSRM docker, `/api/route`       | pgvector, osrm‑backend  |
| **1C** | 8‑10  | Costs & metrics              | Upstash cost‑monitor, Prom + Grafana dashboards           | Upstash, Grafana        |
| **2A** | 11‑12 | Evaluator                    | TruLens RAG‑Triad CI step                                 | TruLens                 |
| **2B** | 13‑14 | Conditional upgrades         | CrewAI YAML (if trigger) · AutoGen decorator (if trigger) | CrewAI, AutoGen         |
| **3A** | 15‑18 | Staging & RBAC               | Vercel + Fly deploy, Keycloak OIDC                        | Keycloak                |
| **3B** | 19‑20 | Nightly audit                | *Deferred* CodeVisionary PoC                              | —                       |
| **4**  | 21‑60 | Enterprise hardening         | Multi‑tenant caps, SIEM export, IaC                       | Terraform, Alertmanager |

---

## 3  Upgrade triggers & rollback

| Trigger observed                             | Action                                      | Rollback                        |
| -------------------------------------------- | ------------------------------------------- | ------------------------------- |
| Roles > 10 or PM needs prompt edits          | Add CrewAI, move prompts to `roles.yaml`    | Remove CrewAI dep + revert YAML |
| Code‑exec failures ≥ 1/day or spike in spend | Wrap node with AutoGen `CodeExecutionAgent` | Remove decorator                |
| Always                                       | Keep OTel tracing                           | —                               |

---

## 4  Test pyramid & quality gates (added by R9)

```
          Chaos / perf (Phase‑4)
         ------------------------
         Contract tests (API)
        -------------------------
        Integration (Prisma+OSRM)
       ---------------------------
       Unit (Vitest)   ← merge must pass
```

* **TruLens**: relevance ≥ 0.6 on every PR
* **CodeVisionary**: maintainability ≥ 0.7 (only after Phase 3)

---

## 5  Scaling & HPA matrix

| Metric     | Dev/Stage | Prod MVP  | Enterprise       |
| ---------- | --------- | --------- | ---------------- |
| QPS        | 2         | 15        | 100+             |
| CPU %      | 70        | 60        | 50               |
| HPA target | none      | CPU + RPS | CPU + GPU­memory |

GPU node‑pool auto‑scale is **deferred to Phase 4**.

---

## 6  UI/UX design system (accept‑minimum)

* React + shadcn/ui, D3 light bundle ≤ 150 kB gzip
* Storybook stories for every component
* Theme tokens exported to Figma
* Multi‑tenant view separation **deferred**.

---

## 7  Backlog – Q3 2025 (deferred)

* **CodeVisionary nightly** audit in CI
* **Chaos Mesh** monthly resilience game‑days
* **Full multi‑tenant UI separation**
* **GPU node‑pool auto‑scaling** for Ollama
* **Secret‑vault migration** (Doppler / HashiCorp Vault)
* **Serverless function PoC** for bursty tasks

---

## 8  Prompt pack (copy/paste)

> ### Bootstrap Architect
>
> SYSTEM: You are *Architect‑AI* … *(unchanged from v2)*
>
> ### Planner, Coder, Reviewer
>
> *See original v2 prompts – unchanged; Planner emits 2‑day tasks, etc.*

---

## 9  Risk log (delta)

* **LangGraph API drift** – weekly dependabot run & pin.
* **Trace volume** – sample 10 % dev, 100 % stage/prod.
* **Prompt drift** – `prompts/` semver‑tagged; nightly TruLens.

*Last updated: 17 June 2025 (v2.1)*.
