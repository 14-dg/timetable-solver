FROM ghcr.io/astral-sh/uv:alpine
COPY . /app
ENV UV_NO_DEV=1
WORKDIR /app
RUN uv sync --locked
EXPOSE 
CMD ["uv", "run", ""]