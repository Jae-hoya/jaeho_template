# Build stage
FROM python:3.13-alpine AS uv

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Configure uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_FROZEN=1 \
    UV_PYTHON_PREFERENCE=only-system

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo

# Install Python dependencies
COPY uv-requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /app/.venv && \
    uv pip install -r uv-requirements.txt

# Copy the lockfile and sync packages
COPY uv.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Copy the project
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --no-deps .

# Runtime stage
FROM python:3.13-alpine

# Set PATH to include venv
ENV PATH="/app/.venv/bin:$PATH"

# Install runtime dependencies
RUN apk add --no-cache ca-certificates

# Create non-root user
RUN adduser -D -u 1000 app

# Copy the virtual environment from the build stage
COPY --from=uv --chown=app:app /app/.venv /app/.venv

# Copy healthcheck script
COPY --chown=app:app docker-healthcheck.sh /app/docker-healthcheck.sh
RUN chmod +x /app/docker-healthcheck.sh

# Run as non-root user
USER app

# Add healthcheck
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 \
    CMD ["/app/docker-healthcheck.sh"]

# Run the server
ENTRYPOINT ["/app/.venv/bin/awslabs.{{ cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') }}"]
