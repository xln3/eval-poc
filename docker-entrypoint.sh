#!/bin/bash
# Dynamic proxy config from environment variables (portable — no hardcoded addresses).
# If HTTP_PROXY/HTTPS_PROXY are set, generate Docker client config and git proxy.
# If not set, no proxy is configured — works on servers with direct internet access.

if [ -n "$HTTP_PROXY" ] || [ -n "$HTTPS_PROXY" ]; then
    # Docker BuildKit proxy injection: config.json tells Docker CLI to pass
    # proxy env vars into `docker compose build` RUN instructions.
    #
    # IMPORTANT (Bug #122/#123): host.docker.internal does NOT resolve inside
    # Docker build containers on Linux Docker Engine. We must replace the
    # hostname with an IP reachable from build containers.
    #
    # Strategy: detect the container's default gateway (= Docker bridge gateway),
    # then replace the proxy hostname with that IP. This gateway is reachable
    # from both the running container and any build containers on the same host.
    _PROXY_SRC="${HTTP_PROXY:-$HTTPS_PROXY}"
    _BRIDGE_GW=$(ip route 2>/dev/null | awk '/default/{print $3}' | head -1)
    if [ -z "$_BRIDGE_GW" ]; then
        # Fallback: parse gateway from /proc if ip command unavailable
        _BRIDGE_GW=$(awk '$2 == "00000000" {printf "%d.%d.%d.%d", "0x"substr($3,7,2), "0x"substr($3,5,2), "0x"substr($3,3,2), "0x"substr($3,1,2)}' /proc/net/route 2>/dev/null | head -1)
    fi
    # Extract port from proxy URL (e.g. http://host.docker.internal:7890 → 7890)
    _PROXY_PORT=$(echo "$_PROXY_SRC" | grep -oE '[0-9]+$')
    if [ -n "$_BRIDGE_GW" ] && [ -n "$_PROXY_PORT" ]; then
        DOCKER_BRIDGE_PROXY="http://${_BRIDGE_GW}:${_PROXY_PORT}"
    else
        # Cannot derive bridge proxy — use the original proxy URL as-is
        DOCKER_BRIDGE_PROXY="$_PROXY_SRC"
    fi
    mkdir -p /root/.docker
    cat > /root/.docker/config.json <<EOJSON
{"proxies":{"default":{"httpProxy":"${DOCKER_BRIDGE_PROXY}","httpsProxy":"${DOCKER_BRIDGE_PROXY}","noProxy":"${NO_PROXY:-localhost,127.0.0.1}"}}}
EOJSON

    # Git proxy for benchmarks that clone repos (e.g. osworld sparse checkout)
    git config --global http.proxy "${HTTP_PROXY:-}"
    git config --global https.proxy "${HTTPS_PROXY:-}"
fi

# Bug #118: Allow git operations on repos owned by different UIDs.
# The host cache is mounted into the container (/root/.cache),
# causing UID mismatch (host UID vs container root UID 0).
# Without this, osworld/osworld_small fail with "dubious ownership" errors.
git config --global --add safe.directory '*'

exec "$@"
