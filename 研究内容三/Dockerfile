FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG NODE_VERSION=22.18.0
ARG OPENCODE_VERSION=1.18.4
ARG TARGETARCH

LABEL org.opencontainers.image.title="PCAT Agent for OpenCode" \
      org.opencontainers.image.description="OpenCode environment with patch-compatibility-utils installed" \
      org.opencontainers.image.version="1.0"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        build-essential \
        ca-certificates \
        clang \
        cmake \
        curl \
        file \
        git \
        jq \
        lcov \
        libtool \
        llvm \
        ninja-build \
        nodejs \
        npm \
        openssh-client \
        patch \
        pkg-config \
        python3 \
        python3-pip \
        python3-venv \
        rsync \
        strace \
        unzip \
        zip \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    case "${TARGETARCH:-amd64}" in \
        amd64) node_arch="x64" ;; \
        arm64) node_arch="arm64" ;; \
        *) echo "Unsupported architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    node_archive="node-v${NODE_VERSION}-linux-${node_arch}.tar.xz"; \
    curl -fsSLO "https://nodejs.org/dist/v${NODE_VERSION}/${node_archive}"; \
    curl -fsSLO "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt"; \
    grep " ${node_archive}$" SHASUMS256.txt | sha256sum -c -; \
    tar -xJf "${node_archive}" -C /usr/local --strip-components=1 --no-same-owner; \
    rm -f "${node_archive}" SHASUMS256.txt; \
    node --version; \
    npm --version

RUN python3 -m venv /opt/pcat-venv \
    && /opt/pcat-venv/bin/pip install --no-cache-dir \
        tree-sitter \
        tree-sitter-language-pack \
    && npm install --global "opencode-ai@${OPENCODE_VERSION}" \
    && npm cache clean --force \
    && opencode --version

RUN groupadd --gid 1000 node \
    && useradd --uid 1000 --gid node --create-home --shell /bin/bash node \
    && mkdir -p /home/node/.opencode/skills /workspace \
    && chown -R node:node /home/node/.opencode /workspace

COPY --chown=node:node patch-compatibility-utils/ \
    /home/node/.opencode/skills/patch-compatibility-utils/

USER node
ENV HOME=/home/node
ENV PATH="/opt/pcat-venv/bin:${PATH}"
WORKDIR /workspace

RUN test -f /home/node/.opencode/skills/patch-compatibility-utils/SKILL.md \
    && python3 /home/node/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/check_dependencies.py \
        --include-callgraph \
        --languages c,go,ruby,python \
        --json

CMD ["opencode"]
