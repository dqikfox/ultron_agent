#!/bin/bash
echo "Installing OpenTelemetry tracing dependencies..."

. venv/bin/activate

pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-exporter-otlp-proto-http \
            opentelemetry-instrumentation-requests \
            opentelemetry-instrumentation-flask

echo "✅ OpenTelemetry dependencies installed"
echo "Start ULTRON Agent to see traces at http://localhost:4319"