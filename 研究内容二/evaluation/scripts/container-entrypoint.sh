#!/bin/sh
set -eu
mkdir -p "$HOME" "$XDG_CONFIG_HOME/opencode/skills"
cp -R /opt/patch-port/skills/. "$XDG_CONFIG_HOME/opencode/skills/"
exec opencode "$@"
