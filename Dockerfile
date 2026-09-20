FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DATAREADY_HOST=0.0.0.0 \
    DATAREADY_PORT=8080 \
    DATAREADY_SHOW=0 \
    DATAREADY_RELOAD=0

WORKDIR /app

# libgomp1 is needed by phonenumbers' optional C extension; the rest of the
# stack is pure Python.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first so the dependency layer caches across code changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app_files ./app_files
COPY configs ./configs
COPY site ./site
COPY main.py ./

# Batch output and downloads land here; mounted in docker-compose so they
# survive restarts.
RUN mkdir -p /app/output

EXPOSE 8080

# Probe the port actually bound, resolved the same way main.py does, so a
# platform-injected PORT (Render, Heroku) does not leave the check probing a
# dead 8080 while the app is healthy elsewhere.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request,sys; p=os.getenv('PORT') or os.getenv('DATAREADY_PORT') or '8080'; urllib.request.urlopen(f'http://localhost:{p}/'); sys.exit(0)" || exit 1

ENTRYPOINT ["python", "main.py"]