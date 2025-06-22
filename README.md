# 📂 AutonomesAI v2.1 - Clean Project Structure

> Bulletproof autonomous AI coding system built on stable foundations

## 🎯 Project Overview
Building an enterprise-grade autonomous AI system that can code, plan, and execute tasks independently while maintaining 100% stability and session continuity.

## 📁 Project Structure
```
autonomesai/
├── README.md                   # This file
├── project/                    # Project management
│   ├── status.json            # Current project status
│   ├── NEXT_ACTIONS.md        # Session recovery instructions
│   ├── current-session.md     # Human-readable session status
│   └── rollback-points.json   # Backup points
├── docs/                      # Documentation
│   ├── strategy/              # Strategy documents
│   │   ├── bulletproof-strategy.md
│   │   ├── hybrid-strategy.md
│   │   ├── master-plan.md
│   │   └── dependency-strategy.md
│   ├── legacy/                # Historical documents
│   └── session-handoff.md
├── config/                    # Configuration files
│   ├── renovate.json          # Dependency update config
│   └── dependencies.lock      # Version locks
├── core/                      # Core autonomy code
│   ├── agents/                # Simple agent classes
│   ├── orchestrator/          # Orchestration logic
│   ├── session/               # Session management
│   └── utils/                 # Utilities
├── api/                       # Backend API
├── frontend/                  # Next.js frontend
├── integrations/              # External integrations
├── telemetry/                 # Observability
├── prompts/                   # LLM prompts
├── docker-compose.yml         # Container orchestration
└── requirements.txt           # Python dependencies
```

## 🚀 Current Status
- **Phase**: Agent Implementation Ready
- **Progress**: Foundation complete, ready for autonomy
- **Dependencies**: All locked to stable versions
- **Session Continuity**: Active (see project/NEXT_ACTIONS.md)

## 🛡️ Stability Guarantees
- ✅ **No dependency hell** - Exact version control
- ✅ **No broken builds** - Comprehensive fallbacks
- ✅ **No lost progress** - Continuous workspace file updates
- ✅ **No context loss** - Session recovery system

## 🎯 Next Steps
See `project/NEXT_ACTIONS.md` for exact implementation instructions.

## 📊 Key Features
- **Simple Agents**: PlannerAgent, CoderAgent, ReviewerAgent
- **Model Routing**: Ollama (local) + Claude (complex tasks)
- **Observability**: OpenTelemetry + Jaeger tracing
- **Session Recovery**: Token limit proof design

## 🔧 Quick Start
```bash
# Check current status
cat project/status.json

# See next actions
cat project/NEXT_ACTIONS.md

# Start development
cd core/agents
# Follow instructions in NEXT_ACTIONS.md
```

---
**Built for reliability, designed for autonomy** 🤖
