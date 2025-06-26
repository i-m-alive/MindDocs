# syntax=docker/dockerfile:1.7
###############################################################################
#  DocuSense AI – FastAPI / LangChain backend (Python 3.11, slim)             #
###############################################################################

######################## 1️⃣ BASE ─────────────────────────────────────────────
FROM python:3.11-slim AS base
WORKDIR /app

# ----- build-time tuning flags (override with --build-arg) -------------------
ARG DEBIAN_FRONTEND=noninteractive
ARG PIP_RETRIES=5
ARG PIP_TIMEOUT=1200

# ----- OS libs (Microsoft ODBC + tool-chain) --------------------------------
RUN set -eux; \
    # core utils first
    apt-get update && apt-get install -y --no-install-recommends \
        curl gnupg ca-certificates && \
    \
    # Microsoft GPG key
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | \
        gpg --dearmor -o /usr/share/keyrings/microsoft.gpg && \
    \
    # SQL Server repo for Debian 12 (bookworm).  Change 12→11 & bookworm→bullseye
    # if you ever switch to a Debian 11 base image.
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] \
        https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/mssql-release.list && \
    \
    # final install (accept EULA automatically)
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        gcc g++ unixodbc-dev msodbcsql18 && \
    \
    # slim the layer
    apt-get clean && rm -rf /var/lib/apt/lists/*

# upgrade pip once (cached)
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip

######################## 2️⃣ DEPS ─────────────────────────────────────────────
FROM base AS deps
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    PIP_RETRIES=${PIP_RETRIES} \
    PIP_DEFAULT_TIMEOUT=${PIP_TIMEOUT} \
    python -m pip install --no-cache-dir -r requirements.txt

######################## 3️⃣ PROD ─────────────────────────────────────────────
FROM base AS prod
COPY --from=deps /usr/local /usr/local
COPY . /app
RUN adduser --disabled-password --gecos "" docai && chown -R docai /app
USER docai

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
