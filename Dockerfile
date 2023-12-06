FROM python:3.10-buster as builder

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app
# WORKDIR /

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.10-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
# ENV VIRTUAL_ENV=/app/.venv \
#     PATH="/app/.venv/bin:$PATH"


COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ./app ./app
# COPY ./app/.streamlit .

# cd to app and run
# RUN cd app

WORKDIR /app
ENTRYPOINT ["streamlit", "run", "cucamonga_app.py", "--server.port=8503", "--server.address=0.0.0.0"]
# CMD ["streamlit", "run", "cucamonga_app.py", "--server.port=8503", "--server.address=0.0.0.0"]
