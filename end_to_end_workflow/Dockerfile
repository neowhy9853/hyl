FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG NODE_VERSION=22.18.0
ARG OPENCODE_VERSION=1.18.4

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    set -eu; \
    rm -f /etc/apt/apt.conf.d/docker-clean; \
    apt-get -o Acquire::Retries=3 update; \
    for attempt in 1 2 3; do \
    if apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
    ca-certificates curl git python3 python3-pip ripgrep universal-ctags xz-utils \
    build-essential pkg-config autoconf automake libtool bison flex patch \
    cmake ninja-build gettext perl zip unzip rsync gperf texinfo \
    libssl-dev zlib1g-dev libncurses-dev libelf-dev python3-dev \
    libxml2-dev libxslt1-dev libpcre2-dev libcurl4-openssl-dev libexpat1-dev \
    libreadline-dev libsqlite3-dev libffi-dev golang-go; then break; fi; \
    if [ "$attempt" -eq 3 ]; then exit 1; fi; \
    sleep 3; \
    done; \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir PyYAML==6.0.3 tree-sitter==0.26.0 tree-sitter-c==0.24.2

RUN set -eux; \
    architecture="$(dpkg --print-architecture)"; \
    case "$architecture" in \
        amd64) node_arch=x64 ;; \
        arm64) node_arch=arm64 ;; \
        *) echo "Unsupported architecture: $architecture" >&2; exit 1 ;; \
    esac; \
    archive="node-v${NODE_VERSION}-linux-${node_arch}.tar.xz"; \
    curl --retry 3 --retry-delay 2 -fsSLO "https://nodejs.org/dist/v${NODE_VERSION}/${archive}"; \
    curl --retry 3 --retry-delay 2 -fsSLO "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt"; \
    grep " ${archive}$" SHASUMS256.txt | sha256sum -c -; \
    tar -xJf "$archive" -C /usr/local --strip-components=1 --no-same-owner; \
    rm "$archive" SHASUMS256.txt; \
    npm install --global "opencode-ai@${OPENCODE_VERSION}"; \
    npm cache clean --force

RUN groupadd --gid 1000 node \
    && useradd --uid 1000 --gid node --create-home --shell /bin/bash node

USER node
WORKDIR /home/node
CMD ["python3", "--version"]
