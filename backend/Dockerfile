FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry==1.8.0 && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --only main --no-root

COPY . .
RUN poetry install --no-interaction --no-ansi --only main

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
