FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG NODE_VERSION=22.18.0
ARG OPENCODE_VERSION=1.18.4

LABEL org.opencontainers.image.title="Patch Analysis Agents for OpenCode" \
      org.opencontainers.image.description="OpenCode environment with patch intent and relation analysis skills installed" \
      org.opencontainers.image.version="1.0"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        python3 \
        xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    architecture="$(dpkg --print-architecture)"; \
    case "${architecture}" in \
        amd64) node_arch="x64" ;; \
        arm64) node_arch="arm64" ;; \
        *) echo "Unsupported architecture: ${architecture}" >&2; exit 1 ;; \
    esac; \
    node_archive="node-v${NODE_VERSION}-linux-${node_arch}.tar.xz"; \
    curl -fsSLO "https://nodejs.org/dist/v${NODE_VERSION}/${node_archive}"; \
    curl -fsSLO "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt"; \
    grep " ${node_archive}$" SHASUMS256.txt | sha256sum -c -; \
    tar -xJf "${node_archive}" -C /usr/local --strip-components=1 --no-same-owner; \
    rm -f "${node_archive}" SHASUMS256.txt; \
    npm install --global "opencode-ai@${OPENCODE_VERSION}"; \
    npm cache clean --force; \
    node --version; \
    npm --version; \
    opencode --version

RUN groupadd --gid 1000 node \
    && useradd --uid 1000 --gid node --create-home --shell /bin/bash node \
    && mkdir -p \
        /home/node/.cache \
        /home/node/.config/opencode \
        /home/node/.opencode/skills \
        /workspace \
    && chown -R node:node \
        /home/node/.cache \
        /home/node/.config \
        /home/node/.opencode \
        /workspace

COPY --chown=node:node patch-intent-analysis/ \
    /home/node/.opencode/skills/patch-intent-analysis/

COPY --chown=node:node patch-relation-analysis/ \
    /home/node/.opencode/skills/patch-relation-analysis/

USER node
ENV HOME=/home/node
ENV XDG_CACHE_HOME=/home/node/.cache
WORKDIR /workspace

RUN test -f /home/node/.opencode/skills/patch-intent-analysis/SKILL.md \
    && test -f /home/node/.opencode/skills/patch-relation-analysis/SKILL.md \
    && python3 -m py_compile \
        /home/node/.opencode/skills/patch-relation-analysis/scripts/analyze_relation.py \
        /home/node/.opencode/skills/patch-relation-analysis/scripts/relation_core.py \
    && python3 /home/node/.opencode/skills/patch-intent-analysis/scripts/install_ctags.py \
    && python3 /home/node/.opencode/skills/patch-intent-analysis/scripts/check_dependencies.py

CMD ["opencode"]
