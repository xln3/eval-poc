#!/bin/bash
# Dynamic proxy config from environment variables (portable — no hardcoded addresses).
# If HTTP_PROXY/HTTPS_PROXY are set, generate Docker client config and git proxy.
# If not set, no proxy is configured — works on servers with direct internet access.

if [ -n "$HTTP_PROXY" ] || [ -n "$HTTPS_PROXY" ]; then
    # Docker BuildKit proxy injection: config.json tells Docker CLI to pass
    # proxy env vars into `docker compose build` RUN instructions.
    mkdir -p /root/.docker
    cat > /root/.docker/config.json <<EOJSON
{"proxies":{"default":{"httpProxy":"${HTTP_PROXY:-}","httpsProxy":"${HTTPS_PROXY:-}","noProxy":"${NO_PROXY:-localhost,127.0.0.1}"}}}
EOJSON

    # Git proxy for benchmarks that clone repos (e.g. osworld sparse checkout)
    git config --global http.proxy "${HTTP_PROXY:-}"
    git config --global https.proxy "${HTTPS_PROXY:-}"
fi

exec "$@"
