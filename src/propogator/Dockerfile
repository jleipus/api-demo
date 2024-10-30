FROM python:3.12.2-bullseye as build

RUN pip install poetry==1.8.4

# Use a virtual enviroment to further isolate the build process from the host
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
# Create an empty README.md file,as Poetry will give errors if it doesn't exist
RUN touch README.md

# Install the dependencies, including the optional 'propogator' dependencies
RUN poetry install --with propogator --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.12.2-slim-bullseye as run

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# Copy the virtual environment from the previous image, negating the need to install Poetry,
# resulting in a smaller image
COPY --from=build ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY src /app

ENTRYPOINT ["python", "-m", "propogator.main"]