FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG NODE_VERSION=22.18.0
ARG OPENCODE_VERSION=1.18.4

LABEL org.opencontainers.image.title="Security Patch Port Agents for OpenCode" \
      org.opencontainers.image.description="OpenCode environment with history and cross-repository patch porting, dependency discovery, and independent validation" \
      org.opencontainers.image.version="2.1"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        python3 \
        ripgrep \
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

COPY --chown=node:node skills/ /home/node/.opencode/skills/

USER node
ENV HOME=/home/node
ENV XDG_CACHE_HOME=/home/node/.cache
WORKDIR /workspace

RUN test -f /home/node/.opencode/skills/security-patch-port/SKILL.md \
    && test -f /home/node/.opencode/skills/patch-dependency-discovery/SKILL.md \
    && test -f /home/node/.opencode/skills/patch-dependency-discovery/references/discovery-contract.md \
    && test -f /home/node/.opencode/skills/patch-port-analysis/references/history-tracing.md \
    && test -f /home/node/.opencode/skills/patch-port-analysis/references/analysis-evidence.md \
    && test -f /home/node/.opencode/skills/patch-port-analysis/references/cross-repo-semantic.md \
    && test -f /home/node/.opencode/skills/patch-port-analysis/scripts/search_code.py \
    && test -f /home/node/.opencode/skills/patch-port-analysis/SKILL.md \
    && test -f /home/node/.opencode/skills/patch-port-analysis/references/analysis-contract.md \
    && test -f /home/node/.opencode/skills/patch-port-apply/SKILL.md \
    && test -f /home/node/.opencode/skills/patch-port-apply/scripts/candidate_workspace.py \
    && test -f /home/node/.opencode/skills/patch-port-validation/SKILL.md \
    && test -f /home/node/.opencode/skills/patch-port-validation/scripts/validate_candidate.py \
    && test -f /home/node/.opencode/skills/patch-port-validation/references/validation-matrix.md

RUN python3 -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ required'" \
    && python3 -m compileall -q /home/node/.opencode/skills \
    && python3 /home/node/.opencode/skills/patch-port-analysis/scripts/search_code.py --help > /dev/null \
    && python3 /home/node/.opencode/skills/patch-port-apply/scripts/candidate_workspace.py --help > /dev/null \
    && python3 /home/node/.opencode/skills/patch-port-validation/scripts/validate_candidate.py --help > /dev/null

CMD ["opencode"]
