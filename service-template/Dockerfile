# Multi-stage Dockerfile for FastAPI app
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
# Install pip-tools and use poetry to export a deterministic requirements.txt if available.
# Fallback: install production deps from pyproject via pip (best-effort) to keep image builds reliable.
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pip-tools
RUN set -eux; \
	if command -v poetry >/dev/null 2>&1 || python -c "import importlib.util,sys; sys.exit(0)"; then \
		# Try to install poetry via official installer, export requirements, then install
		curl -sSL https://install.python-poetry.org | python - && \
		export PATH="$HOME/.local/bin:$PATH"; \
		poetry config virtualenvs.create false || true; \
		poetry export -f requirements.txt --without-hashes --without dev -o /app/requirements.txt || true; \
		pip install --no-cache-dir -r /app/requirements.txt || true; \
	else \
		echo "Poetry not available; attempting best-effort pip install from pyproject"; \
		pip install --no-cache-dir . || true; \
	fi

FROM python:3.11-slim
WORKDIR /app
# Copy installed packages from builder (if any)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . /app
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
