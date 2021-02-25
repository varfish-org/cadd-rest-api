FROM python:3.6-buster

ARG app_git_url=https://github.com/bihealth/cadd-rest-api.git
ARG app_git_tag

ENV DEBIAN_FRONTEND noninteractive

# Copy source code into Docker image.
RUN mkdir -p /usr/src
RUN git clone --depth 1 --branch $app_git_tag $app_git_url /usr/src/app

# Install system dependencies.
RUN apt-get update && \
    apt-get install -y \
        apt-utils
RUN apt-get install -y \
        gcc \
        make \
        postgresql-client

# Install miniconda3
RUN cd /tmp && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3 &&
    rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH="/opt/miniconda3/bin:${PATH}"
RUN conda install -y mamba && \
    mamba install -y python=3.6

# Install Python dependencies.
RUN cd /usr/src/app && \
    pip install --no-cache-dir -r requirements/production.txt && \
    pip install --no-cache-dir -r requirements/local.txt

# Prepare static files
RUN cd /usr/src/app && \
    DJANGO_SECRET_KEY=for-build-only \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    python manage.py collectstatic --no-input

# Define the entry point.
COPY docker-entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && \
    ln -s /usr/local/bin/docker-entrypoint.sh / # backwards compat
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["wsgi"]
EXPOSE 8080/tcp
