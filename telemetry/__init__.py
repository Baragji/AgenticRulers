"""
AutonomesAI v2.1 - Telemetry Package
Advanced OpenTelemetry configuration for AI operations
"""

from .otel_config import (
    AutonomesOTelConfig,
    get_tracer,
    get_meter,
    create_gen_ai_span,
    otel_config
)

__version__ = "2.1.0"
__all__ = [
    "AutonomesOTelConfig",
    "get_tracer", 
    "get_meter",
    "create_gen_ai_span",
    "otel_config"
]