"""
AutonomesAI v2.1 - Ollama Integration Client
Sprint 1-A: Async Ollama client with comprehensive error handling

Production-ready client for Ollama local LLM operations.
"""

import aiohttp
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, AsyncGenerator
from urllib.parse import urljoin
import os

from telemetry.otel_config import get_tracer, create_gen_ai_span, otel_config

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


class OllamaClient:
    """
    Async client for Ollama local LLM operations
    Includes comprehensive error handling and telemetry
    """
    
    def __init__(
        self,
        base_url: str = None,
        timeout: int = 300,  # 5 minutes for model operations
        max_retries: int = 3
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
        
        logger.info(f"🦙 Ollama client initialized with base URL: {self.base_url}")
    
    async def initialize(self) -> None:
        """Initialize the HTTP session"""
        if not self._initialized:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            self._initialized = True
            logger.info("✅ Ollama HTTP session initialized")
    
    async def close(self) -> None:
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self._initialized = False
            logger.info("🔒 Ollama HTTP session closed")
    
    def is_ready(self) -> bool:
        """Check if client is ready for operations"""
        return self._initialized and self.session is not None
    
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy"""
        with tracer.start_as_current_span("ollama_health_check") as span:
            try:
                if not self.is_ready():
                    await self.initialize()
                
                url = urljoin(self.base_url, "/api/tags")
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        models_count = len(data.get("models", []))
                        
                        span.set_attribute("ollama.health.status", "healthy")
                        span.set_attribute("ollama.models.count", models_count)
                        
                        logger.info(f"✅ Ollama is healthy with {models_count} models available")
                        return True
                    else:
                        span.set_attribute("ollama.health.status", "unhealthy")
                        span.set_attribute("ollama.health.status_code", response.status)
                        logger.warning(f"⚠️ Ollama health check failed with status {response.status}")
                        return False
                        
            except Exception as e:
                span.set_attribute("ollama.health.status", "error")
                span.add_event("health_check_error", {"error": str(e)})
                logger.error(f"❌ Ollama health check error: {str(e)}")
                return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available models"""
        with tracer.start_as_current_span("ollama_list_models") as span:
            try:
                if not await self.health_check():
                    raise ConnectionError("Ollama service is not available")
                
                url = urljoin(self.base_url, "/api/tags")
                
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    models = data.get("models", [])
                    
                    span.set_attribute("ollama.models.count", len(models))
                    span.add_event("models_listed", {"count": len(models)})
                    
                    logger.info(f"📦 Found {len(models)} available models")
                    return models
                    
            except Exception as e:
                span.add_event("list_models_error", {"error": str(e)})
                logger.error(f"❌ Failed to list models: {str(e)}")
                raise
    
    async def pull_model(self, model_name: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Pull a model from Ollama registry with streaming progress"""
        with tracer.start_as_current_span("ollama_pull_model") as span:
            span.set_attribute("ollama.model.name", model_name)
            
            try:
                if not self.is_ready():
                    await self.initialize()
                
                url = urljoin(self.base_url, "/api/pull")
                payload = {"name": model_name}
                
                logger.info(f"📥 Starting to pull model: {model_name}")
                
                async with self.session.post(url, json=payload) as response:
                    response.raise_for_status()
                    
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                
                                # Log progress
                                if "status" in data:
                                    logger.info(f"📥 {model_name}: {data['status']}")
                                
                                span.add_event("pull_progress", data)
                                yield data
                                
                                # Check if completed
                                if data.get("status") == "success":
                                    span.set_attribute("ollama.pull.status", "completed")
                                    logger.info(f"✅ Model {model_name} pulled successfully")
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                                
            except Exception as e:
                span.set_attribute("ollama.pull.status", "failed")
                span.add_event("pull_error", {"error": str(e)})
                logger.error(f"❌ Failed to pull model {model_name}: {str(e)}")
                raise
    
    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate completion using specified model"""
        
        with create_gen_ai_span(
            tracer,
            "ollama_generate",
            model,
            temperature=temperature,
            max_tokens=max_tokens
        ) as span:
            
            try:
                if not await self.health_check():
                    raise ConnectionError("Ollama service is not available")
                
                url = urljoin(self.base_url, "/api/generate")
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": stream,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                
                span.set_attribute("ollama.request.prompt_length", len(prompt))
                
                logger.info(f"🤖 Generating completion with {model}")
                
                async with self.session.post(url, json=payload) as response:
                    response.raise_for_status()
                    
                    if stream:
                        # Handle streaming response
                        full_response = ""
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    if "response" in data:
                                        full_response += data["response"]
                                    if data.get("done", False):
                                        break
                                except json.JSONDecodeError:
                                    continue
                        
                        result = {
                            "response": full_response,
                            "model": model,
                            "done": True
                        }
                    else:
                        # Handle non-streaming response
                        result = await response.json()
                    
                    # Add telemetry data
                    response_length = len(result.get("response", ""))
                    estimated_tokens = len(result.get("response", "").split())
                    
                    otel_config.add_gen_ai_response_attributes(
                        span,
                        "success",
                        {
                            "prompt_tokens": len(prompt.split()),
                            "completion_tokens": estimated_tokens,
                            "total_tokens": len(prompt.split()) + estimated_tokens
                        }
                    )
                    
                    span.set_attribute("ollama.response.length", response_length)
                    span.add_event("generation_completed", {
                        "model": model,
                        "response_length": response_length,
                        "estimated_tokens": estimated_tokens
                    })
                    
                    logger.info(f"✅ Generation completed with {estimated_tokens} tokens")
                    return result
                    
            except Exception as e:
                span.set_attribute("gen_ai.response.finish_reason", "error")
                span.add_event("generation_error", {"error": str(e)})
                logger.error(f"❌ Generation failed: {str(e)}")
                raise
    
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Chat completion using conversation format"""
        
        with create_gen_ai_span(
            tracer,
            "ollama_chat",
            model,
            temperature=temperature,
            max_tokens=max_tokens
        ) as span:
            
            try:
                if not await self.health_check():
                    raise ConnectionError("Ollama service is not available")
                
                url = urljoin(self.base_url, "/api/chat")
                payload = {
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                
                span.set_attribute("ollama.chat.messages_count", len(messages))
                
                logger.info(f"💬 Starting chat with {model} ({len(messages)} messages)")
                
                async with self.session.post(url, json=payload) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    # Extract response message
                    response_message = result.get("message", {})
                    response_content = response_message.get("content", "")
                    
                    # Add telemetry
                    estimated_tokens = len(response_content.split())
                    total_input_tokens = sum(len(msg.get("content", "").split()) for msg in messages)
                    
                    otel_config.add_gen_ai_response_attributes(
                        span,
                        "success",
                        {
                            "prompt_tokens": total_input_tokens,
                            "completion_tokens": estimated_tokens,
                            "total_tokens": total_input_tokens + estimated_tokens
                        }
                    )
                    
                    span.add_event("chat_completed", {
                        "model": model,
                        "response_length": len(response_content),
                        "estimated_tokens": estimated_tokens
                    })
                    
                    logger.info(f"✅ Chat completed with {estimated_tokens} tokens")
                    return result
                    
            except Exception as e:
                span.set_attribute("gen_ai.response.finish_reason", "error")
                span.add_event("chat_error", {"error": str(e)})
                logger.error(f"❌ Chat failed: {str(e)}")
                raise
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()