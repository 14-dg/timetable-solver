# uv-Image mit vorinstalliertem Python auf Debian (glibc).
# Alpine (musl) geht nicht, weil ortools nur manylinux-Wheels anbietet.
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

# bytecode beim installieren erzeugen -> schnellerer start
# copy statt hardlinks, weil der uv-cache ein gemountetes volume ist
# das python aus dem image nutzen statt eins herunterzuladen
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PYTHON=/usr/local/bin/python3

WORKDIR /app

# zuerst nur die abhängigkeiten installieren.
# dieser layer wird nur neu gebaut, wenn sich uv.lock oder pyproject.toml ändern
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# venv auf den PATH, damit python, uvicorn und rq direkt aufrufbar sind (ohne "uv run").
# src auf den PYTHONPATH, damit "core" und "features" importierbar sind (wie pythonpath = src in pytest.ini)
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1

# nicht als root laufen
RUN useradd --create-home --uid 1000 app
USER app

EXPOSE 7000

CMD ["python", "src/__main__.py"]
