#!/bin/sh
set -eu
mkdir -p "$HOME/.opencode"
if [ ! -e "$HOME/.opencode/skills" ]; then
    ln -s /opt/patch-analysis/skills "$HOME/.opencode/skills"
fi
exec opencode "$@"
