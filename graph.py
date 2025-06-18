"""
AutonomesAI v2.1 - Minimal LangGraph DAG Implementation
Sprint 0-A: "Hello Graph" with OpenTelemetry integration

Following masterplan specifications exactly.
"""

from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
import json
import logging

# Setup OpenTelemetry tracing (Gen-AI semantic conventions ready)
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({
            SERVICE_NAME: "autonomesai",
            "service.version": "2.1.0",
            "deployment.environment": "development"
        })
    )
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

tracer = trace.get_tracer(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutonomesState(TypedDict):
    """Simple state for our autonomous AI system"""
    messages: list
    status: str
    data: Dict[str, Any]


def bootstrap_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bootstrap node - first node in our DAG.
    Emits OpenTelemetry spans with Gen-AI attributes.
    """
    with tracer.start_as_current_span("bootstrap_node") as span:
        # Add Gen-AI semantic convention attributes
        span.set_attribute("gen_ai.system", "langgraph")
        span.set_attribute("gen_ai.operation.name", "bootstrap")
        span.set_attribute("gen_ai.request.model", "autonomesai-v2.1")
        
        logger.info("🚀 AutonomesAI v2.1 Bootstrap Node Executing")
        
        result = {
            "msg": "bootstrap",
            "status": "success",
            "timestamp": "2025-06-18T12:00:00Z",
            "version": "2.1.0",
            "sprint": "0-A"
        }
        
        # Log the result for observability
        span.set_attribute("gen_ai.response.finish_reason", "success")
        span.add_event("bootstrap_completed", {"result_keys": list(result.keys())})
        
        logger.info(f"✅ Bootstrap completed: {result}")
        return result


def end_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    End node - terminates the DAG execution.
    """
    with tracer.start_as_current_span("end_node") as span:
        span.set_attribute("gen_ai.system", "langgraph") 
        span.set_attribute("gen_ai.operation.name", "end")
        
        logger.info("🏁 AutonomesAI v2.1 End Node Executing")
        
        final_state = {
            **state,
            "completed": True,
            "final_status": "dag_completed"
        }
        
        span.add_event("dag_completed", {"final_state_keys": list(final_state.keys())})
        logger.info(f"✅ DAG execution completed: {final_state}")
        
        return final_state


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
        logger.info("🚀 AutonomesAI v2.1 - Sprint 0-A Execution")
        logger.info("=" * 50)
        
        try:
            # Create and compile the graph
            graph = create_autonomes_graph()
            compiled_graph = graph.compile()
            
            # Execute the graph with initial state
            initial_state = {
                "messages": [],
                "status": "initializing", 
                "data": {
                    "session_id": "sprint-0-a-test",
                    "environment": "development"
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
            span.add_event("sprint_0a_completed", {"success": True})
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Graph execution failed: {str(e)}")
            span.set_attribute("gen_ai.response.finish_reason", "error")
            span.add_event("sprint_0a_failed", {"error": str(e)})
            raise


if __name__ == "__main__":
    main()