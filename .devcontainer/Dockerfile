FROM python:3.11-slim

# Install system dependencies
RUN apt-get update \
	&& apt-get install -y --no-install-recommends curl git sqlite3 \
	&& rm -rf /var/lib/apt/lists/*

# Install uv (The fast Python package installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables for uv to install packages into the system python environment
ENV UV_SYSTEM_PYTHON=1

WORKDIR /workspace

# Copy dependency file and install
COPY pyproject.toml .
RUN uv pip install -r pyproject.toml

# The rest of the workspace will be mounted dynamically by Dev Containers or standard Docker volume mounts.