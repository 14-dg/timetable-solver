FROM ghcr.io/astral-sh/uv:alpine
COPY . /app
ENV UV_NO_DEV=1
WORKDIR /app
RUN uv sync --locked --no-editable
EXPOSE 7000
CMD ["uv", "run", "__main__.py"]