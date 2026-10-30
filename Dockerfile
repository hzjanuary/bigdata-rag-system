FROM ghcr.io/astral-sh/uv:0.9.7@sha256:ba4857bf2a068e9bc0e64eed8563b065908a4cd6bfb66b531a9c424c8e25e142 AS uv
FROM python:3.12-slim@sha256:aa943ce411423c7582288f18707ff66eddcbaeb510502d747a72aeb34f30d159 AS builder
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /build
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv
COPY pyproject.toml uv.lock LICENSE NOTICE ./
COPY rag_core ./rag_core
RUN uv sync --frozen --no-dev --no-editable --no-cache && rm -rf /opt/venv/lib/python3.12/site-packages/onnxruntime/datasets

FROM python:3.12-slim@sha256:aa943ce411423c7582288f18707ff66eddcbaeb510502d747a72aeb34f30d159
ARG SOURCE_REVISION=unverified
LABEL org.opencontainers.image.revision=$SOURCE_REVISION
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PATH=/opt/venv/bin:$PATH RAG_CONFIG=/private/config/config.json HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
RUN python -m pip uninstall -y pip && rm -rf /usr/local/lib/python3.12/ensurepip && groupadd --gid 10001 rag && useradd --uid 10001 --gid 10001 --no-create-home rag && mkdir /private && chown rag:rag /private
COPY --from=builder /opt/venv /opt/venv
COPY LICENSE NOTICE /usr/share/doc/rag-core/
USER 10001:10001
WORKDIR /private
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=6s CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=5)"]
ENTRYPOINT ["rag"]
CMD ["serve", "--host", "0.0.0.0"]
