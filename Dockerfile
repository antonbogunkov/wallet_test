FROM python:3.12-slim

WORKDIR /opt/project

RUN useradd wallet

RUN chown wallet:wallet /opt/project

EXPOSE 8000

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONPATH="${WORKDIR}:${PYTHONPATH}" \
  PORT=8000 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry'

RUN apt-get update --yes --quiet \
  && apt-get install --yes --quiet --no-install-recommends \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
  && apt-get autoremove --yes && apt-get clean --yes && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir --upgrade pip \
  && pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --with test --no-root

COPY --chown=wallet:wallet . .

USER wallet

RUN chmod +x entrypoint.sh

CMD ./entrypoint.sh
