#!/bin/bash
# Dynamic proxy config from environment variables (portable — no hardcoded addresses).
# If HTTP_PROXY/HTTPS_PROXY are set, generate Docker client config and git proxy.
# If not set, no proxy is configured — works on servers with direct internet access.

if [ -n "$HTTP_PROXY" ] || [ -n "$HTTPS_PROXY" ]; then
    # Docker BuildKit proxy injection: config.json tells Docker CLI to pass
    # proxy env vars into `docker compose build` RUN instructions.
    #
    # IMPORTANT (Bug #122/#123): Use the Docker bridge gateway IP (10.0.0.1)
    # instead of host.docker.internal, because host.docker.internal does NOT
    # resolve inside Docker build containers on Linux Docker Engine.
    # The config.json proxy is injected into BUILD containers, so it must use
    # an address reachable from those containers.
    DOCKER_BRIDGE_PROXY="http://10.0.0.1:7890"
    mkdir -p /root/.docker
    cat > /root/.docker/config.json <<EOJSON
{"proxies":{"default":{"httpProxy":"${DOCKER_BRIDGE_PROXY}","httpsProxy":"${DOCKER_BRIDGE_PROXY}","noProxy":"${NO_PROXY:-localhost,127.0.0.1}"}}}
EOJSON

    # Git proxy for benchmarks that clone repos (e.g. osworld sparse checkout)
    git config --global http.proxy "${HTTP_PROXY:-}"
    git config --global https.proxy "${HTTPS_PROXY:-}"
fi

# Bug #118: Allow git operations on repos owned by different UIDs.
# The host cache (/home/xln/.cache) is mounted into the container (/root/.cache),
# causing UID mismatch (host UID 1000 vs container root UID 0).
# Without this, osworld/osworld_small fail with "dubious ownership" errors.
git config --global --add safe.directory '*'

exec "$@"
