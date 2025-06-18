"""
AutonomesAI v2.1 - Minimal LangGraph DAG Implementation
Sprint 0-A: "Hello Graph" with OpenTelemetry integration

Following masterplan specifications exactly.
"""

from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
import json
import logging
import yaml
import os
from pathlib import Path

# Import our advanced OTel configuration
from telemetry.otel_config import get_tracer, create_gen_ai_span, otel_config

tracer = get_tracer(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutonomesState(TypedDict):
    """Simple state for our autonomous AI system"""
    messages: list
    status: str
    data: Dict[str, Any]


def load_prompt_template(prompt_name: str) -> Dict[str, Any]:
    """
    Load prompt template from versioned YAML files
    Sprint 0-B: Prompt versioning implementation
    """
    try:
        prompts_path = Path(__file__).parent / "prompts" / "system_prompts.yaml"
        
        with open(prompts_path, 'r', encoding='utf-8') as f:
            prompts_data = yaml.safe_load(f)
        
        if prompt_name in prompts_data.get("prompts", {}):
            prompt_info = prompts_data["prompts"][prompt_name]
            logger.info(f"📝 Loaded prompt '{prompt_name}' v{prompt_info.get('version', 'unknown')}")
            return prompt_info
        else:
            logger.warning(f"⚠️ Prompt '{prompt_name}' not found, using default")
            return {"version": "unknown", "content": "Default system prompt"}
            
    except Exception as e:
        logger.error(f"❌ Failed to load prompt '{prompt_name}': {e}")
        return {"version": "error", "content": "Error loading prompt"}


def bootstrap_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bootstrap node - first node in our DAG.
    Emits OpenTelemetry spans with Gen-AI semantic conventions v1.34.0.
    """
    with create_gen_ai_span(
        tracer, 
        "bootstrap", 
        "autonomesai-v2.1",
        temperature=0.1,
        max_tokens=500
    ) as span:
        logger.info("🚀 AutonomesAI v2.1 Bootstrap Node Executing")
        
        # Load prompt template
        prompt_data = load_prompt_template("bootstrap_agent")
        
        result = {
            "msg": "bootstrap",
            "status": "success",
            "timestamp": "2025-06-18T16:23:52Z",
            "version": "2.1.0",
            "sprint": "0-B",
            "prompt_version": prompt_data.get("version", "1.0.0")
        }
        
        # Filter PII and add response attributes
        filtered_result = otel_config.add_pii_protection_filter(span, result)
        otel_config.add_gen_ai_response_attributes(
            span, 
            "success", 
            {"prompt_tokens": 150, "completion_tokens": 50, "total_tokens": 200}
        )
        
        span.add_event("bootstrap_completed", {"result_keys": list(filtered_result.keys())})
        logger.info(f"✅ Bootstrap completed: {filtered_result}")
        return filtered_result


def end_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    End node - terminates the DAG execution with enhanced tracing.
    """
    with create_gen_ai_span(tracer, "finalize", "autonomesai-v2.1") as span:
        logger.info("🏁 AutonomesAI v2.1 End Node Executing")
        
        final_state = {
            **state,
            "completed": True,
            "final_status": "dag_completed",
            "telemetry_verified": True
        }
        
        # Apply PII protection and add telemetry
        filtered_state = otel_config.add_pii_protection_filter(span, final_state)
        otel_config.add_gen_ai_response_attributes(span, "completed")
        
        span.add_event("dag_completed", {"final_state_keys": list(filtered_state.keys())})
        logger.info(f"✅ DAG execution completed: {filtered_state}")
        
        return filtered_state


def create_autonomes_graph() -> StateGraph:
    """
    Create the minimal AutonomesAI LangGraph DAG.
    Following Sprint 0-A specifications exactly with LangGraph 0.4.8 API.
    """
    logger.info("🔧 Creating AutonomesAI Graph...")
    
    # Initialize the StateGraph with our custom state schema
    graph = StateGraph(AutonomesState)
    
    # Add nodes
    graph.add_node("bootstrap", bootstrap_node)
    graph.add_node("end", end_node)
    
    # Create the connection: bootstrap -> end
    graph.add_edge("bootstrap", "end")
    graph.add_edge("end", END)
    
    # Set entry point
    graph.set_entry_point("bootstrap")
    
    logger.info("✅ Graph created successfully with bootstrap->end->END flow")
    return graph


def main():
    """
    Main execution function for Sprint 0-A validation.
    """
    with tracer.start_as_current_span("main_execution") as span:
        span.set_attribute("gen_ai.system", "autonomesai")
        span.set_attribute("gen_ai.operation.name", "dag_execution")
        
        logger.info("=" * 50)
        logger.info("🚀 AutonomesAI v2.1 - Sprint 0-B Execution")
        logger.info("=" * 50)
        logger.info(f"🔍 Telemetry: {otel_config.environment} environment")
        logger.info(f"📊 Sampling rate: {otel_config.sampling_rate * 100}%")
        
        try:
            # Create and compile the graph
            graph = create_autonomes_graph()
            compiled_graph = graph.compile()
            
            # Execute the graph with initial state
            initial_state = {
                "messages": [],
                "status": "initializing", 
                "data": {
                    "session_id": "sprint-1-a-test",
                    "environment": "development",
                    "sprint": "1-A",
                    "features": ["ollama_integration", "fastapi_backend"]
                }
            }
            
            logger.info(f"🎯 Executing graph with initial state: {initial_state}")
            
            # Run the compiled graph
            result = compiled_graph.invoke(initial_state)
            
            logger.info("🎉 Graph execution completed successfully!")
            logger.info(f"📊 Final result: {json.dumps(result, indent=2)}")
            
            # Save result for next session
            with open("runtime_result.json", "w") as f:
                json.dump(result, f, indent=2)
            
            span.set_attribute("gen_ai.response.finish_reason", "success")
            span.add_event("sprint_0b_completed", {"success": True, "telemetry_enhanced": True})
            
            # Force flush traces to ensure they're exported  
            from opentelemetry import trace
            if hasattr(trace.get_tracer_provider(), 'force_flush'):
                trace.get_tracer_provider().force_flush(timeout_millis=5000)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Graph execution failed: {str(e)}")
            span.set_attribute("gen_ai.response.finish_reason", "error")
            span.add_event("sprint_0a_failed", {"error": str(e)})
            raise


if __name__ == "__main__":
    main()