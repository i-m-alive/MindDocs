# syntax=docker/dockerfile:1          # keep BuildKit hint
###############################################################################
#  DocuSense-AI · FastAPI / LangChain backend       (Python 3.11 slim + OCR)
###############################################################################

######################## 1️⃣  BASE ################################################
FROM python:3.11-slim AS base
WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
ARG PIP_RETRIES=5
ARG PIP_TIMEOUT=1200


# --- OS libs:    ODBC driver  +  compiler chain  +  Poppler for EasyOCR/pdf2image ------
RUN set -eux; \
    apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg ca-certificates && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | \
        gpg --dearmor -o /usr/share/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] "\
         "https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        gcc g++ unixodbc-dev msodbcsql18 \
        poppler-utils           \
        && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Optional: tell pytesseract where the binary is (it’s /usr/bin/tesseract)
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV PYTHONUNBUFFERED=1

# Upgrade pip once (no BuildKit mounts needed here – keeps old Docker happy)
RUN python -m pip install --upgrade pip

######################## 2️⃣  PYTHON DEPENDENCIES ################################
FROM base AS deps
COPY requirements.txt .
RUN PIP_RETRIES=${PIP_RETRIES} \
    PIP_DEFAULT_TIMEOUT=${PIP_TIMEOUT} \
    python -m pip install --no-cache-dir -r requirements.txt

######################## 3️⃣  FINAL IMAGE ########################################
FROM base AS prod
COPY --from=deps /usr/local /usr/local
COPY . /app

# non-root user (nice to have)
RUN adduser --disabled-password --gecos "" docai && chown -R docai /app
USER docai

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
