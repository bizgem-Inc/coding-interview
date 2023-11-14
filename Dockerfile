# syntax=docker/dockerfile:1


###############################################
# set code
###############################################
FROM python:3.11-slim as build_base

ENV PIP_VER="23.3.1" \
    PIPENV_VER="2023.10.24"

WORKDIR /tmp

COPY ./api ./api \
    ./config ./config \
    ./Pipfile ./ \
    ./Pipfile.lock ./


###############################################
# install modules for development
###############################################
FROM build_base as build_development

RUN pip install --upgrade --no-cache-dir pip=="${PIP_VER}" && \
    pip install --no-cache-dir pipenv=="${PIPENV_VER}" && \
    pipenv sync --system --dev && \
    pip uninstall -y pipenv


###############################################
# install modules for development
###############################################
FROM build_base as build_production

RUN pip install --upgrade --no-cache-dir pip=="${PIP_VER}" && \
    pip install --no-cache-dir pipenv=="${PIPENV_VER}" && \
    pipenv sync --system && \
    pip uninstall -y pipenv


###############################################
# set environment base
###############################################
FROM python:3.11-slim  as environment_base

ENV PYTHONUNBUFFERED=1 \
    USER=django \
    WORKDIR=/app

# for security
RUN rm -rf /tmp && \
    chmod u-s /usr/bin/passwd && \
    chmod g-s /usr/bin/wall && \
    chmod u-s /usr/bin/chfn && \
    chmod u-s /usr/bin/gpasswd && \
    chmod u-s /usr/bin/chsh && \
    chmod u-s /bin/mount && \
    chmod u-s /bin/su && \
    chmod u-s /usr/bin/newgrp && \
    chmod g-s /usr/bin/expiry && \
    chmod g-s /usr/bin/chage && \
    chmod g-s /sbin/unix_chkpwd && \
    chmod u-s /bin/umount


RUN useradd -d /home/${USER} -m -s /bin/bash ${USER}
USER ${USER}

WORKDIR ${WORKDIR}

COPY --from=build_base /tmp/ ./


###############################################
# set environment for development
###############################################
FROM environment_base as development
COPY --from=build_development /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages


###############################################
# set environment for production
###############################################
FROM environment_base as production
COPY --from=build_production /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages