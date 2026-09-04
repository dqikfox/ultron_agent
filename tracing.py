"""
OpenTelemetry Tracing Setup for ULTRON Agent
Visualizes agent operations at http://localhost:4319
"""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import functools

# Configure tracing
resource = Resource.create({"service.name": "ultron-agent"})
trace.set_tracer_provider(TracerProvider(resource=resource))

# OTLP exporter to localhost:4319
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4319/v1/traces")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Get tracer
tracer = trace.get_tracer(__name__)

# Auto-instrument HTTP requests and Flask
RequestsInstrumentor().instrument()
FlaskInstrumentor().instrument()

def trace_function(name=None):
    """Decorator to trace function calls"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__name__}"
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.result", str(type(result)))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
        return wrapper
    return decorator

def trace_agent_operation(operation_type, details=None):
    """Create a span for agent operations"""
    span = tracer.start_span(f"agent.{operation_type}")
    if details:
        for key, value in details.items():
            span.set_attribute(f"agent.{key}", str(value))
    return span