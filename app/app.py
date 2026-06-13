import os
import time
import socket
import logging
import json
from typing import Dict, Any
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import psutil

# Configure structured JSON logging
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "filename": record.filename,
            "lineno": record.lineno,
        }
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        return json.dumps(log_data)

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

# Initialize FastAPI
app = FastAPI(
    title="Secure Cloud-Native API",
    description="Enterprise-grade FastAPI microservice deployed on AWS ECS Fargate",
    version="1.0.0"
)

# App start time to track uptime
START_TIME = time.time()

# Middleware to measure request duration and log request metadata
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Exclude health check from verbose logs to keep log storage clean/cost-optimized
    if request.url.path != "/health":
        extra_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        logger.info(f"HTTP Request: {request.method} {request.url.path} - {response.status_code}", extra={"extra_data": extra_data})
        
    return response

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint returning basic application information."""
    return {
        "status": "online",
        "service": "Secure Cloud-Native CI/CD Pipeline App",
        "environment": os.getenv("APP_ENV", "production"),
        "version": "1.0.0",
        "hostname": socket.gethostname(),
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint used by AWS ALB Target Group to monitor service status."""
    return {
        "status": "healthy",
        "timestamp": str(time.time()),
        "uptime_seconds": str(round(time.time() - START_TIME, 2))
    }

@app.get("/metrics")
async def system_metrics() -> Dict[str, Any]:
    """System metrics endpoint providing real-time CPU, memory, and disk usage details."""
    cpu_percent = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    return {
        "system": {
            "cpu_utilization_percent": cpu_percent,
            "memory": {
                "total_bytes": memory.total,
                "available_bytes": memory.available,
                "used_percent": memory.percent
            },
            "disk": {
                "total_bytes": disk.total,
                "free_bytes": disk.free,
                "used_percent": disk.percent
            }
        },
        "app": {
            "uptime_seconds": round(time.time() - START_TIME, 2),
            "process_memory_mb": round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2)
        }
    }

@app.get("/api/v1/secure-data")
async def get_secure_data() -> Dict[str, Any]:
    """Sample data endpoint that requires TLS and is monitored by DevSecOps security policies."""
    logger.info("Accessing secure data endpoint")
    return {
        "status": "success",
        "data": [
            {"id": 1, "name": "Secure Item A", "confidentiality": "restricted"},
            {"id": 2, "name": "Secure Item B", "confidentiality": "restricted"}
        ],
        "compliance": {
            "encryption_in_transit": "TLSv1.3",
            "data_classification": "Internal"
        }
    }

# Handle errors gracefully
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> Response:
    extra_data = {
        "path": request.url.path,
        "error_message": str(exc),
        "error_type": type(exc).__name__
    }
    logger.error("An unhandled exception occurred", extra={"extra_data": extra_data})
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred.", "code": "INTERNAL_SERVER_ERROR"}
    )
