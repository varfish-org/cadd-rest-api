# syntax=docker/dockerfile:1.3

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

FROM python:3.10-bookworm AS base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

WORKDIR /usr/src/app

LABEL org.opencontainers.image.authors="Oliver Stolpe <oliver.stolpe@bih-charite.de>"
LABEL org.opencontainers.image.source="https://github.com/varfish-org/cadd-rest-api"

RUN apt-get update && apt-get install -y curl
RUN apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------

FROM base AS deps

RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends \
        apt-utils \
        gcc \
        make \
        wget \
        postgresql-client

# Install Python dependencies via pipenv.
COPY requirements requirements
RUN virtualenv .venv && \
    . .venv/bin/activate && \
    pip install --no-cache-dir -r requirements/production.txt

# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------

FROM base AS runtime

# Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /usr/local/bin/wait
RUN chmod +x /usr/local/bin/wait

# Install conda environment with varfish-server-worker if configured to do so.
RUN ["/bin/bash","-c", "cd /tmp && \
        wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh && \
        bash Mambaforge-Linux-x86_64.sh -b -p /opt/miniconda3 && \
        source /opt/miniconda3/bin/activate && \
        conda install -c conda-forge -y mamba && \
        mamba install -c conda-forge -c bioconda -y \
            cadd-scripts==1.6.post1 && \
        rm -f Mambaforge-Linux-x86_64.sh"]

COPY --from=deps /usr/src/app/.venv /usr/src/app/.venv

ENV PATH="/usr/src/app/.venv/bin:${PATH}"

# Temporarily setup environment variables for ``manage.py` commands below.
# We will clear them again later.
ENV DJANGO_SECRET_KEY=for-build-only \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    DATABASE_URL=postgres://cadd-rest-api:cadd-rest-api@fake/cadd-rest-api

# Copy source code
COPY . .

# Define entrypoint
COPY utils/docker/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["wsgi"]
EXPOSE 8080/tcp
