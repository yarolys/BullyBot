FROM python:3.12
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean
RUN pip install --no-cache-dir poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root
COPY . .

# CMD ["celery", "-A", "src.handlers.audio.celery_cfg.app", "worker", "--loglevel=info"]
