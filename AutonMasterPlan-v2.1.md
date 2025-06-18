# AutonomesAI v2.1 – Masterplan (June 2025)

> This document is the single source of truth for building, scaling and governing your autonomous coding framework. It compresses the conclusions reached in the ChatGPT × Claude debate, integrates your assistant's (R9‑ZentoGPT) feedback, and maps every step from **zero → MVP → enterprise‑grade**. Follow it verbatim unless a newer revision is explicitly approved.

---

## 0  High‑level summary

* **Runtime core:** start with **LangGraph + OpenTelemetry** (OTel Gen‑AI semantic conventions). LangGraph Swarm (May 2025) gives deterministic DAGs and a visual debugger. ([changelog.langchain.com](https://changelog.langchain.com/?date=2025-05-01&page=3&utm_source=chatgpt.com)) ([changelog.langchain.com](https://changelog.langchain.com/?categories=cat_5UBL6DD8PcXXL&utm_source=chatgpt.com))
* **Local model first:** spin up **Ollama** with Llama‑3‑8B/70B; route only "high‑stakes" calls to Claude‑Sonnet‑4 or GPT‑4o. ([reddit.com](https://www.reddit.com/r/LocalLLaMA/comments/1h8qsal/llama_33_on_a_4090_quick_feedback/?utm_source=chatgpt.com))
* **Quality & costs:** instrument every LLM/tool call with OTel Gen‑AI spans; nightly **TruLens RAG Triad** evaluation for new commits. ([trulens.org](https://www.trulens.org/blog/otel_for_the_agentic_world?utm_source=chatgpt.com))
* **Upgrade triggers:**

  * add **CrewAI** YAML crews when roles > 10 **or** PMs must edit prompts. ([docs.crewai.com](https://docs.crewai.com/concepts/crews?utm_source=chatgpt.com)) ([docs.crewai.com](https://docs.crewai.com/quickstart?utm_source=chatgpt.com))
  * add **AutoGen 0.6** CodeExecutionAgent when code‑exec failures ≥ 1 per day or token burn spikes. ([github.com](https://github.com/microsoft/autogen/issues/6207?utm_source=chatgpt.com)) ([github.com](https://github.com/microsoft/autogen/releases?utm_source=chatgpt.com))
* **Enterprise hardening:** pgvector IVFFlat, OSRM routing, Upstash Redis rate‑limit, Prom+Grafana, Alertmanager. ([upstash.com](https://upstash.com/docs/redis/sdks/ratelimit-ts/overview?utm_source=chatgpt.com)) ([trulens.org](https://www.trulens.org/blog/otel_for_the_agentic_world?utm_source=chatgpt.com)) ([d1rdz15x9x7c4f.cloudfront.net](https://d1rdz15x9x7c4f.cloudfront.net/assets/images/llama3.3-installation-guide.pdf?utm_source=chatgpt.com))

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AutonomesAI v2 Architecture                    │
├─────────────────┬─────────────────────────────────────────┬─────────────┤
│                 │                                         │             │
│  ┌─────────┐    │            ┌─────────────┐              │  ┌────────┐ │
│  │ Next.js │    │            │ LangGraph   │              │  │ Ollama │ │
│  │ 14 UI   │◄───┼───REST────►│ Runtime     │◄─Model Call──┼─►│ Local  │ │
│  └─────────┘    │            └─────┬───────┘              │  │ Models │ │
│                 │                  │                      │  └────────┘ │
│                 │                  │                      │             │
│  ┌─────────┐    │                  │                      │  ┌────────┐ │
│  │ API     │    │                  │                      │  │ Cloud  │ │
│  │ Gateway │◄───┼───────────┐      │                      │  │ Models │ │
│  └─────────┘    │           │      │                      │  └────────┘ │
│                 │           │      │                      │             │
│  ┌─────────┐    │           │      ▼                      │             │
│  │ Keycloak│    │     ┌─────┴──────────┐                  │             │
│  │ OIDC    │◄───┼────►│ Agent Services │                  │             │
│  └─────────┘    │     └────────────────┘                  │             │
│                 │            │    │                       │             │
│                 │            │    │                       │             │
│  ┌─────────┐    │            │    │                       │  ┌────────┐ │
│  │ Postgres│    │            │    │                       │  │ Redis  │ │
│  │ pgvector│◄───┼────────────┘    └───────────────────────┼─►│ Cache  │ │
│  └─────────┘    │                                         │  └────────┘ │
│                 │                                         │             │
├─────────────────┼─────────────────────────────────────────┼─────────────┤
│                 │         Observability Layer             │             │
│  ┌─────────┐    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  │  ┌────────┐ │
│  │ TruLens │    │  │ OpenTel │  │ Grafana │  │ Prom    │  │  │ Alert  │ │
│  │ Eval    │◄───┼─►│ Collect │◄─►│ Dash   │◄─►│ Metrics │◄─┼─►│ Manager│ │
│  └─────────┘    │  └─────────┘  └─────────┘  └─────────┘  │  └────────┘ │
│                 │                                         │             │
└─────────────────┴─────────────────────────────────────────┴─────────────┘
```

---

## 1  Phase roadmap

| Phase | Days  | Goal              | Key outputs                                                                                               | Tooling                                                |
| ----- | ----- | ----------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| **0** | 1‑3   | Runtime bootstrap | DevContainer, minimal LangGraph DAG (`Start→End`), OTel console export, CI workflow                       | LangGraph, OTel SDK                                    |
| **1** | 4‑10  | Vertical slices   | Next.js 14 skeleton, Prisma + pgvector schema, OSRM service, Upstash cost monitor, Prom+Grafana dashboard | Ollama (local model), Docker compose                   |
| **2** | 11‑14 | Guardrails & eval | TruLens evaluator; optional CrewAI + AutoGen if triggers met; budget alert via Alertmanager               | TruLens, (CrewAI, AutoGen)                             |
| **3** | 15‑30 | MVP hardening     | Role‑based tests, staging env on Vercel/K8s, basic RBAC, secret management                                | LangGraph Studio, Keycloak/OIDC, Doppler/HashiCorp     |
| **4** | 31‑60 | Enterprise grade  | Multi‑tenant auth, per‑customer cost caps, OTel → SIEM, disaster‑recovery playbooks                       | CrewAI full rollout, AutoGen everywhere, Terraform IaC |

---

## 2  Sprint detail (atomic, two‑day mini‑sprints)

### Sprint 0‑A   "Hello Graph" (Day 1‑2)

1. **Init repo**

   ```bash
   git init autonomesai && cd autonomesai
   echo "python, node" > .devcontainer
   ```
2. **Install core deps**

   ```bash
   pip install "langgraph==0.3.*" "opentelemetry-sdk==1.27.0"
   ```
3. **Seed DAG** `graph.py`

   ```python
   from langgraph import Graph
   def hello(_: dict):
       return {"msg": "bootstrap"}
   g = Graph()
   g.add_node("Start", hello)
   g.link("Start", "End")
   g.compile("runtime.json")
   ```
4. **CI** – `.github/workflows/ci.yml` runs `python graph.py` and fails on exception.
5. **Dependency health** - Add Renovate bot config for npm and pip.

### Sprint 0‑B   "Trace everything" (Day 3)

1. Configure OTel exporter:

   ```python
   from opentelemetry import trace
   from opentelemetry.sdk.resources import SERVICE_NAME, Resource
   from opentelemetry.sdk.trace import TracerProvider
   from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
   trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "autonomesai"})))
   trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
   ```
2. Verify `gen_ai.*` attributes after a dummy LLM call.
3. Set up prompt versioning with Git tags in `prompts/` directory.

### Sprint 1‑A   "Local model + web app" (Day 4‑5)

1. Add **Ollama** service to `docker-compose.yml`:

   ```yaml
   services:
     ollama:
       image: ollama/ollama:0.3.5
       volumes:
         - ollama:/root/.ollama
       ports: [11434:11434]
   volumes: {ollama: {}}
   ```
2. Pull model: `docker exec ollama ollama pull llama3:8b-Q4_2025`.
3. Scaffold Next.js 14 app (`apps/web`).
4. Implement `lib/modelRouter.ts` – chooses Ollama unless `{importance:"high"}`.

### Sprint 1‑B   "Data & routing" (Day 6‑7)

1. Add Postgres + pgvector + Prisma models.
2. Add OSRM Docker service (`osrm/osrm-backend`, port 5000). ([trulens.org](https://www.trulens.org/blog/otel_for_the_agentic_world?utm_source=chatgpt.com))
3. Write `/api/route` proxy endpoint.

### Sprint 1‑C   "Costs & metrics" (Day 8‑10)

1. Upstash Redis Ratelimit SDK guard in `lib/ai/cost-monitor.ts`. ([upstash.com](https://upstash.com/docs/redis/sdks/ratelimit-ts/overview?utm_source=chatgpt.com))
2. Prometheus Node exporter + Grafana dashboards.
3. Hook OTel traces into Grafana Tempo.
4. Create UI proof-of-concept for React Flow visualization (≤150kB gzip).

### Sprint 2‑A   "Evaluator" (Day 11‑12)

1. Install TruLens; register RAG Triad feedback functions. ([trulens.org](https://www.trulens.org/blog/otel_for_the_agentic_world?utm_source=chatgpt.com))
2. CI step `trulens-eval` blocks merge if relevance < 0.6.
3. Set up OTel sampling filter to protect PII in traces (10% in dev, 100% in prod).

### Sprint 2‑B   "Optional upgrades" (Day 13‑14)

* **CrewAI**: `pip install crewai` and create `roles.yaml` if role‑churn or >10 agents.
* **AutoGen 0.6**: decorate `CodeWrite` node; `max_retries_on_error=2`. ([github.com](https://github.com/microsoft/autogen/issues/6207?utm_source=chatgpt.com))
* Weekly CVE scan for dependencies in CI pipeline.

### Sprint 3‑A   "Staging & RBAC" (Day 15‑18)

1. Deploy staging to Vercel (web) + Fly.io (backend).
2. Add Keycloak OIDC gateway; map GitHub org teams.
3. Implement basic tenant labels in API layer.

### Sprint 3‑B   "Secret Management" (Day 19‑20)

1. Integrate Doppler/HashiCorp Vault for secret management.
2. Replace plain env vars in docker-compose with secrets.
3. Set up load testing with k6 for critical API endpoints.

### Sprint 4 (30‑60) – Enterprise

* Multi‑tenant cost caps -> per‑tenant OTel attributes.
* Disaster recovery scripts.
* Terraform modules for AWS EKS, RDS, S3 backups.
* CodeVisionary evaluator integration.
* Chaos Mesh testing in staging environment.
* Full multi-tenant UI separation.
* GPU auto-scaling for Ollama in production.

---

## 3  Prompt pack (copy/paste)

### Bootstrap agent

```
SYSTEM: You are *Architect-AI*. Goal: bootstrap runtime.
1. Create a minimal LangGraph DAG with a Start and End node.
2. Ensure every node emits OpenTelemetry Gen-AI spans.
3. Ask for approval before committing.
```

### Planner agent (RoleBasedAgent or CrewAI)

```
SYSTEM: You are *Planner*. Input is a feature request. Output is a YAML task list with atomic 2‑day sprints.
Constraints: no task > 2 dev‑days; include acceptance tests.
```

### Coder agent

```
SYSTEM: You are *Coder*. Implement tasks using Next.js 14, Prisma, pgvector, Docker, and follow repository standards.
TOOLS: shell, git, node, prisma, docker.
STOP when all unit tests pass.
```

### Reviewer agent

```
SYSTEM: You are *Reviewer*. For every PR, run `npm test`, TruLens eval, and verify test coverage doesn't decrease. If any fail, request changes.
```

---

## 4  Governance & observability

* **Trace schema**: adopt OTel Gen‑AI semconv §§ events, spans. ([opentelemetry.io](https://opentelemetry.io/docs/specs/semconv/gen-ai/?utm_source=chatgpt.com)) ([opentelemetry.io](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-events/?utm_source=chatgpt.com))
* **Dashboards**: Grafana boards for latency, token spend, failure rate.
* **Alerting**: Alertmanager route `severity=budget` to Slack `#ai-ops` when daily token cost > \$10.
* **Prompt versioning**: Store prompts in version-controlled directory with semver tags.

---

## 5  Risk log & mitigations

| Risk                        | Likelihood | Impact | Action                                                       |
| --------------------------- | ---------- | ------ | ------------------------------------------------------------ |
| LangGraph API change        | M          | M      | Pin `langgraph==0.3.*`; run weekly dependabot tests          |
| Local model memory pressure | H          | M      | Use 8B for dev, 70B only on GPU nodes                        |
| Prompt drift                | M          | H      | Version prompts with semver tags, nightly TruLens evaluation |
| Trace volume overload       | M          | L      | Sample 10% in dev, 100% in staging/prod                      |
| Data privacy concerns       | M          | H      | Implement OTel sampling filters to protect PII in traces     |

---

## 6  Glossary

* **Agent** – LLM‑powered component with a role and tools.
* **Crew** – A collection of agents orchestrated to complete a goal (CrewAI term).
* **DAG** – Directed Acyclic Graph; LangGraph's execution structure.
* **OTel** – OpenTelemetry, open standard for traces/metrics/logs.
* **Gen‑AI semconv** – OTel's semantic conventions for generative AI spans.
* **LOC** – Lines of Code (physical SLOC count).
* **PII** – Personally Identifiable Information.

---

## 7  Testing Strategy

### Test Pyramid

| Test Type        | Coverage Target | Tools                  | Execution                    |
| ---------------- | --------------- | ---------------------- | ---------------------------- |
| **Unit Tests**   | 90%             | Jest, Pytest           | Every commit, <2 min runtime |
| **Integration**  | 80%             | Playwright, Supertest  | Every PR, <5 min runtime     |
| **E2E**          | Critical paths  | Cypress                | Nightly, <15 min runtime     |
| **LLM Eval**     | All agents      | TruLens RAG Triad      | Every PR affecting agents    |
| **Load Tests**   | API endpoints   | k6, Artillery          | Weekly + pre-release         |

### Test Implementation Plan

1. **Sprint 0**: Basic unit tests for LangGraph nodes
2. **Sprint 1**: Integration tests for API endpoints
3. **Sprint 2**: E2E tests for critical user journeys
4. **Sprint 3**: Automated TruLens evaluation pipeline
5. **Sprint 4**: Load testing infrastructure

### Test Guardrails

* No PR merges if unit/integration test coverage decreases
* TruLens relevance score ≥0.6 required for agent-related changes
* Performance regression testing: latency increase >10% blocks release

---

## 8  Scaling Strategy

### Horizontal Scaling

| Component        | Scaling Mechanism           | Metrics-Based Triggers                     |
| ---------------- | --------------------------- | ------------------------------------------ |
| **Web Frontend** | Vercel Edge Network         | Response time >200ms, CPU >70%             |
| **API Layer**    | K8s HPA                     | CPU >60%, memory >70%, requests >100/sec   |
| **LangGraph**    | K8s StatefulSet             | Queue depth >50, processing time >2sec     |
| **Ollama**       | Single GPU nodes (MVP)      | GPU utilization >80%, inference time >1sec |
| **Database**     | PgBouncer + Read replicas   | Connection count >80%, query time >100ms   |
| **Redis Cache**  | Redis Cluster               | Memory >70%, eviction rate >0              |

### Performance Optimizations

1. **Response Caching**
   * Implement Redis caching for identical LLM requests
   * TTL-based invalidation (24h default)
   * Cache hit target: >40% in production

2. **Database Optimizations**
   * pgvector IVFFlat indexes for all vector columns
   * Materialized views for common analytics queries
   * Connection pooling with PgBouncer

3. **Load Shedding**
   * Circuit breaker pattern for all external services
   * Graceful degradation when cloud models unavailable
   * Priority-based request queuing

---

## 9  UI/UX Design System

### Design Principles

1. **Progressive Disclosure**
   * Show basic options by default
   * Reveal advanced features as users need them
   * Maintain consistent information hierarchy

2. **Transparent AI**
   * Visualize agent reasoning process
   * Show confidence scores for all AI outputs
   * Provide edit/override options for all AI decisions

3. **Responsive Feedback**
   * Streaming responses for all LLM interactions
   * Progress indicators for long-running operations
   * Clear error states with actionable recovery paths

### Component Library

| Component            | Purpose                                | Implementation                 |
| -------------------- | -------------------------------------- | ------------------------------ |
| **Agent Chat**       | Interactive agent conversations        | React + Tailwind + Framer Motion |
| **Process Graph**    | Visualize LangGraph execution          | React Flow (PoC in Sprint 1-C) |
| **Token Monitor**    | Real-time token usage tracking         | Recharts + Tailwind            |
| **Prompt Editor**    | YAML-based prompt editing for PMs      | Monaco Editor + YAML schema    |
| **Evaluation Board** | TruLens results                        | Tailwind + Headless UI         |

### Implementation Timeline

1. **Sprint 1**: Basic UI components and layouts
   * Responsive dashboard shell
   * Agent chat interface
   * Simple metrics display

2. **Sprint 2**: Interactive visualizations
   * Process graph visualization (PoC)
   * Token usage charts
   * Basic prompt editor

3. **Sprint 3**: Advanced UI features
   * Full-featured prompt editor with validation
   * Evaluation results dashboard
   * User preference management

4. **Sprint 4**: Enterprise UI features
   * Role-based access controls in UI
   * Basic tenant labels in UI

---

## 10  Deferred Backlog (Q3 2025)

The following features are intentionally deferred to maintain the 14-day MVP timeline:

1. **Advanced Evaluation**
   * CodeVisionary integration for code quality assessment
   * Automated nightly audits with CodeVisionary

2. **Chaos Testing**
   * Chaos Mesh integration for infrastructure resilience testing
   * Monthly chaos experiments in staging environment

3. **Advanced Scaling**
   * GPU auto-scaling for Ollama in production
   * Advanced K8s HPA configurations with custom metrics

4. **Full Multi-Tenant UI**
   * Complete UI separation between tenants
   * White-labeling capabilities
   * Tenant-specific dashboards and analytics

5. **Advanced Security Features**
   * SIEM integration for security monitoring
   * Advanced threat detection for LLM interactions

These features will be prioritized for implementation after the MVP is successfully deployed and validated.

---

*Last updated: 18 June 2025*