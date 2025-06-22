# 🚨 NEXT ACTIONS - Session Recovery
**Last Updated**: 2025-06-22 10:55:00
**Status**: Project cleanup completed, ready for autonomy implementation

## 🎯 IF NEW CHAT SESSION NEEDED

### Quick Context Recovery
1. **READ THIS FILE FIRST** - Contains everything you need
2. **Current Status**: Just completed major project reorganization
3. **Next Phase**: Implement simple autonomous agents

### Current Project Structure
```
✅ COMPLETED: Clean project structure
├── project/           # Project management files
├── docs/strategy/     # All strategy documents  
├── config/           # Configuration files
├── core/             # NEW - For autonomy code
│   ├── agents/       # NEW - Simple agent classes
│   ├── orchestrator/ # NEW - Orchestration logic
│   ├── session/      # NEW - Session management
│   └── utils/        # NEW - Utilities
├── api/              # Existing backend
├── frontend/         # Existing UI
└── [other existing directories]
```

### EXACT NEXT STEPS (Start Here in New Session)

#### 1. Create Simple Agent Classes (30 minutes)
**File to create**: `core/agents/simple_agents.py`
**Code to add**:
```python
"""
Simple, stable agents - no complex dependencies
Built for reliability and session continuity
"""

class PlannerAgent:
    """Breaks down tasks into manageable steps"""
    def __init__(self, ollama_client):
        self.client = ollama_client
        self.prompt = "You are a software architect. Break complex tasks into clear, actionable steps."
    
    def plan(self, task: str) -> list:
        response = self.client.generate(f"{self.prompt}\n\nTask: {task}")
        return self.parse_steps(response)
    
    def parse_steps(self, response: str) -> list:
        # Simple parsing - extract numbered steps
        lines = response.split('\n')
        steps = [line.strip() for line in lines if line.strip() and ('.' in line or '-' in line)]
        return steps[:10]  # Max 10 steps for simplicity

class CoderAgent:
    """Writes code based on specifications"""
    def __init__(self, ollama_client):
        self.client = ollama_client
        self.prompt = "You are an expert programmer. Write clean, working code."
    
    def code(self, specification: str) -> str:
        response = self.client.generate(f"{self.prompt}\n\nImplement: {specification}")
        return self.extract_code(response)
    
    def extract_code(self, response: str) -> str:
        # Extract code blocks
        if "```" in response:
            parts = response.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Odd indices are code blocks
                    return part.strip()
        return response  # Return as-is if no code blocks

class ReviewerAgent:
    """Reviews code for quality and correctness"""
    def __init__(self, ollama_client):
        self.client = ollama_client
        self.prompt = "You are a code reviewer. Check for errors, suggest improvements."
    
    def review(self, code: str) -> dict:
        response = self.client.generate(f"{self.prompt}\n\nReview this code:\n{code}")
        
        # Simple approval logic
        approval_keywords = ["good", "lgtm", "looks good", "approved", "correct"]
        approved = any(keyword in response.lower() for keyword in approval_keywords)
        
        return {
            "approved": approved,
            "feedback": response,
            "confidence": 0.8 if approved else 0.3
        }
```

#### 2. Test the Agents (15 minutes)
**File to create**: `core/agents/test_agents.py`
**Code to add**:
```python
"""
Test the simple agents to ensure they work
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.ollama_client import OllamaClient
from simple_agents import PlannerAgent, CoderAgent, ReviewerAgent

async def test_agents():
    # Initialize Ollama client
    client = OllamaClient()
    await client.initialize()
    
    # Create agents
    planner = PlannerAgent(client)
    coder = CoderAgent(client)
    reviewer = ReviewerAgent(client)
    
    # Test simple task
    task = "Create a Python function that adds two numbers"
    
    print("🎯 Testing Agents with:", task)
    
    # Test planner
    plan = planner.plan(task)
    print("📋 Plan:", plan)
    
    # Test coder
    if plan:
        code = coder.code(plan[0] if plan else task)
        print("💻 Code:", code)
        
        # Test reviewer
        review = reviewer.review(code)
        print("✅ Review:", review)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agents())
```

#### 3. Run Test Command
```bash
cd core/agents
python test_agents.py
```

### What NOT to Touch
- ❌ Don't modify existing LangGraph code yet
- ❌ Don't change requirements.txt versions  
- ❌ Don't add complex frameworks
- ❌ Don't touch Docker setup

### Dependencies Status
- ✅ All versions locked and stable
- ✅ LangGraph 0.4.8 pinned
- ✅ Ollama integration working
- ✅ OpenTelemetry configured

### Expected Results
- Simple agents should create/run without errors
- Basic autonomy functionality (plan → code → review)
- Foundation for more advanced orchestration

### If Issues Occur
1. Check Ollama is running: `docker-compose ps`
2. Verify Python environment: `python --version`
3. Test basic connectivity: `curl http://localhost:11434/api/tags`

### Next Session After This
- Create orchestrator to wire agents together
- Add model routing (Ollama → Claude for complex tasks)
- Implement basic evaluation metrics

**CONFIDENCE**: This approach is bulletproof - simple, stable, no dependency risks!
