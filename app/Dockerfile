# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install basic build tools if any compilation is needed, and copy requirements
COPY requirements.txt .

# Install dependencies into a wheels directory to avoid installing compiler tools in the final image
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# STAGE 2: Final Runtime Image (Distroless-like security posture)
# ==========================================
FROM python:3.11-slim AS runner

# Set environment variables for security and Python performance
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    PORT=8000

WORKDIR /app

# Create a non-privileged system group and user
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/false -m appuser

# Copy installed dependencies from the builder stage
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application source code
COPY --chown=appuser:appgroup app.py .
COPY --chown=appuser:appgroup tests/ ./tests/

# Set ownership of the application directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Built-in health check using python (reduces vulnerability footprint by not requiring curl/wget)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run the API server with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
