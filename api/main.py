"""
AutonomesAI v2.1 - FastAPI Backend
Sprint 1-A: Ollama integration with LangGraph orchestration

Production-ready API with OpenTelemetry tracing.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import asyncio
import logging
import json
from datetime import datetime

# Our custom modules
from telemetry.otel_config import get_tracer, create_gen_ai_span, otel_config
from graph import create_autonomes_graph
from integrations.ollama_client import OllamaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get tracer for this module
tracer = get_tracer(__name__)

# FastAPI app instance
app = FastAPI(
    title="AutonomesAI v2.1 API",
    description="Advanced AI orchestration with LangGraph + Ollama",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    model: str = Field(default="llama3.3:8b", description="Ollama model to use")
    stream: bool = Field(default=False, description="Enable streaming response")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=4000)

class ChatResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: Optional[int] = None
    processing_time_ms: int
    trace_id: str

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    services: Dict[str, str]

# Global Ollama client instance
ollama_client = OllamaClient()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    with tracer.start_as_current_span("api_startup") as span:
        logger.info("🚀 AutonomesAI v2.1 API starting up...")
        
        # Initialize Ollama client
        await ollama_client.initialize()
        
        # Test LangGraph compilation
        graph = create_autonomes_graph()
        compiled_graph = graph.compile()
        
        span.add_event("services_initialized", {
            "ollama_ready": ollama_client.is_ready(),
            "langgraph_compiled": True
        })
        
        logger.info("✅ All services initialized successfully")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    with tracer.start_as_current_span("health_check") as span:
        
        # Check Ollama connection
        ollama_status = "healthy" if await ollama_client.health_check() else "unhealthy"
        
        health_data = HealthResponse(
            status="healthy" if ollama_status == "healthy" else "degraded",
            version="2.1.0",
            timestamp=datetime.now().isoformat(),
            services={
                "ollama": ollama_status,
                "langgraph": "healthy",
                "telemetry": "healthy"
            }
        )
        
        span.set_attribute("health.status", health_data.status)
        span.add_event("health_check_completed", {
            "services_checked": len(health_data.services)
        })
        
        return health_data

@app.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Main chat completion endpoint using Ollama + LangGraph orchestration
    """
    start_time = datetime.now()
    
    with create_gen_ai_span(
        tracer,
        "chat_completion",
        request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    ) as span:
        
        try:
            logger.info(f"💬 Processing chat request with model: {request.model}")
            
            # Create and run LangGraph with Ollama integration
            graph = create_autonomes_graph()
            compiled_graph = graph.compile()
            
            # Prepare initial state with chat request
            initial_state = {
                "messages": [{"role": "user", "content": request.message}],
                "status": "processing",
                "data": {
                    "model": request.model,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "stream": request.stream
                }
            }
            
            # Execute the graph
            result = await compiled_graph.ainvoke(initial_state)
            
            # Generate response using Ollama
            ollama_response = await ollama_client.generate(
                model=request.model,
                prompt=request.message,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Add telemetry attributes
            otel_config.add_gen_ai_response_attributes(
                span, 
                "success",
                {
                    "prompt_tokens": len(request.message.split()),
                    "completion_tokens": len(ollama_response["response"].split()),
                    "total_tokens": len(request.message.split()) + len(ollama_response["response"].split())
                }
            )
            
            span.add_event("chat_completed", {
                "model_used": request.model,
                "processing_time_ms": processing_time,
                "response_length": len(ollama_response["response"])
            })
            
            response = ChatResponse(
                response=ollama_response["response"],
                model_used=request.model,
                tokens_used=ollama_response.get("tokens_used"),
                processing_time_ms=int(processing_time),
                trace_id=format(span.get_span_context().trace_id, '032x')
            )
            
            logger.info(f"✅ Chat completion successful in {processing_time:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"❌ Chat completion failed: {str(e)}")
            
            span.set_attribute("gen_ai.response.finish_reason", "error")
            span.add_event("error_occurred", {"error": str(e)})
            
            raise HTTPException(
                status_code=500,
                detail=f"Chat completion failed: {str(e)}"
            )

@app.get("/models")
async def list_models():
    """List available Ollama models"""
    with tracer.start_as_current_span("list_models") as span:
        try:
            models = await ollama_client.list_models()
            
            span.add_event("models_listed", {"count": len(models)})
            
            return {"models": models}
        except Exception as e:
            logger.error(f"❌ Failed to list models: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/{model_name}/pull")
async def pull_model(model_name: str, background_tasks: BackgroundTasks):
    """Pull a new model from Ollama registry"""
    with tracer.start_as_current_span("pull_model") as span:
        span.set_attribute("model.name", model_name)
        
        try:
            # Add to background tasks for async processing
            background_tasks.add_task(ollama_client.pull_model, model_name)
            
            span.add_event("model_pull_initiated", {"model": model_name})
            
            return {"message": f"Model {model_name} pull initiated", "status": "processing"}
        except Exception as e:
            logger.error(f"❌ Failed to initiate model pull: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_system_status():
    """Get detailed system status and metrics"""
    with tracer.start_as_current_span("system_status") as span:
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "version": "2.1.0",
            "environment": otel_config.environment,
            "telemetry": {
                "sampling_rate": otel_config.sampling_rate,
                "traces_enabled": True,
                "metrics_enabled": True
            },
            "ollama": {
                "connected": await ollama_client.health_check(),
                "models_count": len(await ollama_client.list_models()) if await ollama_client.health_check() else 0
            }
        }
        
        span.add_event("status_collected", status)
        
        return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )