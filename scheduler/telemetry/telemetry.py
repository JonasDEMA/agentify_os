"""Telemetry Service - Manages tracing, metrics, and logging using OpenTelemetry."""
import logging
import structlog
from typing import Optional, Any, Dict

logger = structlog.get_logger()

class TelemetryService:
    """Service for system observability."""

    def __init__(self):
        self._setup_logging()
        self._setup_tracing()
        self._setup_metrics()

    def _setup_logging(self):
        """Configure structured logging."""
        # Already configured in main.py, but we can add OTel handler here
        pass

    def _setup_tracing(self):
        """Configure OpenTelemetry tracing."""
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
            
            provider = TracerProvider()
            processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)
            self.tracer = trace.get_tracer(__name__)
            logger.info("telemetry_tracing_initialized")
        except ImportError:
            logger.warning("opentelemetry_tracing_missing")
            self.tracer = None

    def _setup_metrics(self):
        """Configure OpenTelemetry metrics."""
        try:
            from opentelemetry import metrics
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
            
            reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
            provider = MeterProvider(metric_readers=[reader])
            metrics.set_meter_provider(provider)
            self.meter = metrics.get_meter(__name__)
            
            # Define common counters
            self.jobs_counter = self.meter.create_counter(
                "jobs_total", 
                description="Total number of jobs processed"
            )
            logger.info("telemetry_metrics_initialized")
        except ImportError:
            logger.warning("opentelemetry_metrics_missing")
            self.meter = None

    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Start a new tracing span."""
        if self.tracer:
            return self.tracer.start_as_current_span(name, attributes=attributes)
        # Fallback context manager
        class MockSpan:
            def __enter__(self): return self
            def __exit__(self, *args): pass
        return MockSpan()

    def record_job(self, status: str = "success"):
        """Record a job processed metric."""
        if self.meter:
            self.jobs_counter.add(1, {"status": status})
