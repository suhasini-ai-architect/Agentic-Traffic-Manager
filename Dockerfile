# ==========================================
# STAGE 1: Dependency Compiler / Builder
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ==========================================
# STAGE 2: Hardened Runtime Target
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /workspace

# Create a non-privileged system user for zero-trust compliance
RUN groupadd -g 10001 gatewayuser && \
    useradd -u 10001 -g gatewayuser -m -s /sbin/nologin gatewayuser

COPY --from=builder /root/.local /home/gatewayuser/.local
COPY --from=builder /usr/lib /usr/lib

ENV PATH=/home/gatewayuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Copy the exact layout folders securely
COPY ./app ./app
COPY ./dashboard ./dashboard

RUN chown -R gatewayuser:gatewayuser /workspace

USER gatewayuser

EXPOSE 8000
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8000/v1/proxy || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]