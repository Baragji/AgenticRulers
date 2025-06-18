"""
AutonomesAI v2.1 - Advanced OpenTelemetry Configuration
Sprint 0-B: Enhanced tracing with Gen-AI semantic conventions v1.34.0

Production-ready observability setup following 2025 best practices.
"""

import os
from typing import Dict, Any, Optional
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
import logging

logger = logging.getLogger(__name__)


class AutonomesOTelConfig:
    """
    Centralized OpenTelemetry configuration for AutonomesAI v2.1
    Implements Gen-AI semantic conventions v1.34.0
    """
    
    def __init__(
        self,
        service_name: str = "autonomesai",
        service_version: str = "2.1.0",
        environment: str = "development",
        sampling_rate: float = 0.1,  # 10% sampling in dev, 100% in prod
        enable_console_export: bool = True
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.sampling_rate = sampling_rate if environment != "production" else 1.0
        self.enable_console_export = enable_console_export
        
        # Initialize telemetry
        self._setup_tracing()
        self._setup_metrics()
        
    def _setup_tracing(self) -> None:
        """Setup distributed tracing with Gen-AI semantic conventions"""
        
        # Create resource with proper attributes
        resource = Resource.create({
            SERVICE_NAME: self.service_name,
            SERVICE_VERSION: self.service_version,
            DEPLOYMENT_ENVIRONMENT: self.environment,
            "service.namespace": "autonomesai",
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "ai.system.type": "agent_framework",
            "ai.system.name": "langgraph"
        })
        
        # Setup sampling - respect PII and performance
        if self.environment == "development":
            sampler = TraceIdRatioBased(self.sampling_rate)
            logger.info(f"🔍 Tracing: {self.sampling_rate*100:.1f}% sampling rate for development")
        else:
            sampler = TraceIdRatioBased(1.0)  # 100% in production
            logger.info("🔍 Tracing: 100% sampling rate for production")
        
        # Create tracer provider
        trace_provider = TracerProvider(
            resource=resource,
            sampler=sampler
        )
        
        # Add span processors
        if self.enable_console_export:
            console_processor = BatchSpanProcessor(
                ConsoleSpanExporter(),
                max_export_batch_size=10,
                export_timeout_millis=30000
            )
            trace_provider.add_span_processor(console_processor)
        
        # Set global tracer provider
        trace.set_tracer_provider(trace_provider)
        
        logger.info(f"✅ OpenTelemetry tracing initialized for {self.service_name} v{self.service_version}")
    
    def _setup_metrics(self) -> None:
        """Setup metrics collection for AI operations"""
        
        # Create metrics resource
        resource = Resource.create({
            SERVICE_NAME: self.service_name,
            SERVICE_VERSION: self.service_version,
            DEPLOYMENT_ENVIRONMENT: self.environment
        })
        
        # Setup metric readers
        readers = []
        if self.enable_console_export:
            readers.append(
                PeriodicExportingMetricReader(
                    ConsoleMetricExporter(),
                    export_interval_millis=60000  # Export every minute
                )
            )
        
        # Create meter provider
        metrics.set_meter_provider(
            MeterProvider(
                resource=resource,
                metric_readers=readers
            )
        )
        
        logger.info("✅ OpenTelemetry metrics initialized")
    
    def get_tracer(self, name: str) -> trace.Tracer:
        """Get tracer instance with proper naming"""
        return trace.get_tracer(name)
    
    def get_meter(self, name: str):
        """Get meter instance for custom metrics"""
        return metrics.get_meter(name)
    
    def create_gen_ai_span(
        self,
        tracer: trace.Tracer,
        operation_name: str,
        model_name: str,
        system_name: str = "langgraph",
        **kwargs
    ) -> trace.Span:
        """
        Create a span with Gen-AI semantic conventions v1.34.0
        
        Following: https://opentelemetry.io/docs/specs/semconv/gen-ai/
        """
        span = tracer.start_span(f"gen_ai.{operation_name}")
        
        # Required Gen-AI attributes
        span.set_attribute("gen_ai.system", system_name)
        span.set_attribute("gen_ai.operation.name", operation_name)
        span.set_attribute("gen_ai.request.model", model_name)
        
        # Optional but recommended attributes
        if "temperature" in kwargs:
            span.set_attribute("gen_ai.request.temperature", kwargs["temperature"])
        if "max_tokens" in kwargs:
            span.set_attribute("gen_ai.request.max_tokens", kwargs["max_tokens"])
        if "top_p" in kwargs:
            span.set_attribute("gen_ai.request.top_p", kwargs["top_p"])
        
        return span
    
    def add_gen_ai_response_attributes(
        self,
        span: trace.Span,
        finish_reason: str,
        usage_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add Gen-AI response attributes to span"""
        
        span.set_attribute("gen_ai.response.finish_reason", finish_reason)
        
        if usage_data:
            if "prompt_tokens" in usage_data:
                span.set_attribute("gen_ai.usage.input_tokens", usage_data["prompt_tokens"])
            if "completion_tokens" in usage_data:
                span.set_attribute("gen_ai.usage.output_tokens", usage_data["completion_tokens"])
            if "total_tokens" in usage_data:
                span.set_attribute("gen_ai.usage.total_tokens", usage_data["total_tokens"])
    
    def add_pii_protection_filter(self, span: trace.Span, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out PII from trace data
        Sprint 0-B requirement: Protect PII in traces
        """
        
        # List of potential PII fields to mask
        pii_fields = ["email", "phone", "ssn", "credit_card", "password", "token", "api_key"]
        
        filtered_data = {}
        for key, value in data.items():
            if any(pii_field in key.lower() for pii_field in pii_fields):
                filtered_data[key] = "[REDACTED]"
                span.add_event("pii_filtered", {"field": key})
            else:
                filtered_data[key] = value
        
        return filtered_data


# Global configuration instance
otel_config = AutonomesOTelConfig(
    environment=os.getenv("DEPLOYMENT_ENVIRONMENT", "development"),
    sampling_rate=float(os.getenv("OTEL_SAMPLING_RATE", "0.1"))
)

# Convenience functions for easy access
def get_tracer(name: str) -> trace.Tracer:
    """Get configured tracer instance"""
    return otel_config.get_tracer(name)

def get_meter(name: str):
    """Get configured meter instance"""
    return otel_config.get_meter(name)

def create_gen_ai_span(tracer: trace.Tracer, operation_name: str, model_name: str, **kwargs) -> trace.Span:
    """Create Gen-AI semantic convention compliant span"""
    return otel_config.create_gen_ai_span(tracer, operation_name, model_name, **kwargs)