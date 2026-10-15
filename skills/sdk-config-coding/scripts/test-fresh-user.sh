#!/usr/bin/env bash
#
# Simulates a brand-new user on a brand-new machine loading the
# sdk-config-assistant plugin (which carries sdk-config-coding): no
# project artifacts, no dedicated Chrome profile, no setup marker, nothing.
#
# Runs `claude --plugin-dir` under a throwaway $HOME and a throwaway project
# directory, so every path the plugin (or Claude Code itself) resolves off the
# machine — ~/.chrome-acoustic-profile, ~/.zshrc, ~/.claude/sdk-config-coding/,
# the user-scoped MCP registration in ~/.claude.json —
# points at scratch space instead of your real ones. Nothing real is read or
# written; cleanup on exit removes only the scratch space this script created.
#
# Usage: skills/sdk-config-coding/scripts/test-fresh-user.sh [--handoff] [--legacy]
#
#   --handoff  Seed the throwaway project with a synthetic site handed off from
#              sdk-config-assistant (scripts/fixtures/handoff/shop.example.com),
#              to exercise the "First open of a handed-off site" flow.
#   --legacy   With --handoff: seed it as sites/shop.example.com (the old layout)
#              instead of sdk-config-coding/, to exercise Step 0b's offer to move it.
#
# This covers the dedicated-profile first run. To test default-profile mode, or
# switching between modes, re-run /sdk-config-assistant:sdk-config-coding setup
# in a normal session instead — default mode attaches to your real everyday
# Chrome, which a sandboxed $HOME can't fake.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# The whole plugin is loaded, so the other sdk-config-assistant skills are
# present too — the same coexistence a real user gets.
PLUGIN_ROOT="$(cd "$SKILL_DIR/../.." && pwd)"

HANDOFF=0
LEGACY=0
for arg in "$@"; do
  case "$arg" in
    --handoff) HANDOFF=1 ;;
    --legacy) LEGACY=1 ;;
    *) echo "Unknown option: $arg" >&2; echo "Usage: $0 [--handoff] [--legacy]" >&2; exit 1 ;;
  esac
done

PORT_PID="$(lsof -nP -iTCP:9222 -sTCP:LISTEN -t 2>/dev/null | head -n 1 || true)"
if [ -n "$PORT_PID" ]; then
  PORT_CMD="$(ps -ww -p "$PORT_PID" -o command= 2>/dev/null || true)"
  echo "Port 9222 is already in use (the fresh-user session needs it for its own Chrome)." >&2
  case "$PORT_CMD" in
    *.chrome-acoustic-profile*)
      echo "It's your real dedicated Chrome profile — quit that Chrome window, then re-run this script." >&2 ;;
    *"Google Chrome"*--remote-debugging-port*)
      echo "It's a Chrome started with --remote-debugging-port — quit it, then re-run this script:" >&2
      echo "  $PORT_CMD" >&2 ;;
    *"Google Chrome"*)
      echo "It's your everyday Chrome with remote debugging on (the plugin's default-profile mode)." >&2
      echo "Turn it off at chrome://inspect/#remote-debugging, then re-run this script." >&2 ;;
    *)
      echo "Owner: ${PORT_CMD:-unknown} — quit it, then re-run this script." >&2 ;;
  esac
  exit 1
fi

FAKE_HOME="$(mktemp -d /tmp/sdk-test-home.XXXXXX)"
FAKE_PROJECT="$(mktemp -d /tmp/sdk-test-project.XXXXXX)"

cleanup() {
  echo
  echo "Cleaning up fresh-user test sandbox..."
  pkill -f "$FAKE_HOME/.chrome-acoustic-profile" 2>/dev/null || true
  rm -rf "$FAKE_HOME" "$FAKE_PROJECT"
}
trap cleanup EXIT

if [ "$HANDOFF" -eq 1 ]; then
  SITES_DIR="sdk-config-coding"
  [ "$LEGACY" -eq 1 ] && SITES_DIR="sites"
  mkdir -p "$FAKE_PROJECT/$SITES_DIR"
  cp -R "$SKILL_DIR/scripts/fixtures/handoff/shop.example.com" "$FAKE_PROJECT/$SITES_DIR/"
fi

echo "Fresh-user test sandbox:"
echo "  fake \$HOME = $FAKE_HOME"
echo "  fake project dir = $FAKE_PROJECT"
echo "  plugin loaded from = $PLUGIN_ROOT"
if [ "$HANDOFF" -eq 1 ]; then
  echo "  seeded handoff site = $SITES_DIR/shop.example.com (try: \"let's work on shop.example.com\")"
fi
echo
echo "Expect a login/trust prompt once — this session has no config yet, same as a real new machine."
echo

cd "$FAKE_PROJECT"
HOME="$FAKE_HOME" claude --plugin-dir "$PLUGIN_ROOT"
