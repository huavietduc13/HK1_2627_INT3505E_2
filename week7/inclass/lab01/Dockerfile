# build
FROM python:3.12-slim AS builder
WORKDIR /build

COPY requirements.txt ./
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# runtime
FROM python:3.12-slim
WORKDIR /app

RUN groupadd -r app && useradd -r -g app -d /app app

COPY --from=builder --chown=app:app /opt/venv /opt/venv

COPY --chown=app:app . /app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER app
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:create_app()"]
