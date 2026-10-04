#!/bin/bash
# Install Tap Python SDK AI-assistant config (skills, rules, AGENTS.md) for your project.
# Usage:
#   ./install-skills.sh              # Interactive menu (when run with a tty)
#   ./install-skills.sh claude       # Claude Code plugin
#   ./install-skills.sh codex        # Codex plugin
#   ./install-skills.sh cursor       # .cursor/skills + .cursor/rules in the current folder
#   ./install-skills.sh agents       # AGENTS.md in the current folder
#   ./install-skills.sh all          # All of the above (CLI plugins only when the CLI is installed)
#   curl -sL https://raw.githubusercontent.com/TapWithUs/tap-python-sdk/master/install-skills.sh | bash
#                                    # Defaults to "all" (no tty)

set -euo pipefail

REPO="TapWithUs/tap-python-sdk"
BRANCH="master"
ARCHIVE_URL="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"
EXTRACT_DIR="tap-python-sdk-${BRANCH}"
PLUGIN="tap-python-sdk"
MARKETPLACE="tap-python-sdk-marketplace"

safe_cleanup() {
  if [[ "${EXTRACT_DIR:-}" =~ ^tap-python-sdk- ]] && [ -d "$EXTRACT_DIR" ]; then
    rm -rf "$EXTRACT_DIR"
  fi
}
trap safe_cleanup EXIT

download_archive() {
  if [ ! -d "${EXTRACT_DIR}" ]; then
    curl -sL "$ARCHIVE_URL" | tar xz 2>/dev/null
  fi
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: '$1' is not installed or not on PATH." >&2
    return 1
  fi
}

install_claude() {
  echo "Installing Claude Code plugin..."
  require_command claude
  claude plugin marketplace add "${REPO}" || return 1
  claude plugin install "${PLUGIN}@${MARKETPLACE}" || return 1
  echo "Installed Claude Code plugin ${PLUGIN}."
}

install_codex() {
  echo "Installing Codex plugin..."
  require_command codex
  codex plugin marketplace add "${REPO}" || return 1
  codex plugin add "${PLUGIN}@${MARKETPLACE}" || return 1
  echo "Installed Codex plugin ${PLUGIN}."
}

install_cursor() {
  echo "Installing Cursor skills and rule..."
  download_archive
  local skills="${EXTRACT_DIR}/plugins/${PLUGIN}/skills"
  local rule="${EXTRACT_DIR}/.cursor/rules/tap-sdk.mdc"
  if [ ! -d "$skills" ] || [ ! -f "$rule" ]; then
    echo "Error: Failed to download Cursor config." >&2
    return 1
  fi
  mkdir -p .cursor/skills .cursor/rules
  cp -R "$skills/." .cursor/skills/
  cp "$rule" .cursor/rules/
  echo "Installed $(ls "$skills" | wc -l | tr -d ' ') skills in .cursor/skills/ and .cursor/rules/tap-sdk.mdc."
}

install_agents() {
  echo "Installing AGENTS.md..."
  download_archive
  if [ ! -f "${EXTRACT_DIR}/AGENTS.md" ]; then
    echo "Error: Failed to download AGENTS.md." >&2
    return 1
  fi
  # The contributor section is for the SDK repository only.
  sed '/^## Contributing to this repository/,$d' "${EXTRACT_DIR}/AGENTS.md" > AGENTS.md
  echo "Installed AGENTS.md."
}

install_all() {
  local failed=0
  if command -v claude >/dev/null 2>&1; then
    install_claude || failed=1
  else
    echo "Skipping Claude Code plugin because 'claude' is not on PATH."
  fi
  if command -v codex >/dev/null 2>&1; then
    install_codex || failed=1
  else
    echo "Skipping Codex plugin because 'codex' is not on PATH."
  fi
  install_cursor || failed=1
  install_agents || failed=1
  return "$failed"
}

show_menu() {
  echo ""
  echo "Tap Python SDK - AI assistant config installer"
  echo "=============================================="
  echo ""
  echo "  1) Claude Code plugin"
  echo "  2) Codex plugin"
  echo "  3) Cursor          (.cursor/skills + .cursor/rules)"
  echo "  4) AGENTS.md       (any agent)"
  echo "  5) All"
  echo "  6) Cancel"
  echo ""
  read -rp "Enter choice [1-6]: " choice
  case "$choice" in
    1) install_claude ;;
    2) install_codex ;;
    3) install_cursor ;;
    4) install_agents ;;
    5) install_all ;;
    6) echo "Cancelled."; exit 0 ;;
    *) echo "Invalid choice." >&2; exit 1 ;;
  esac
}

TOOL="${1:-}"
if [ -n "$TOOL" ]; then
  case "$TOOL" in
    claude) install_claude ;;
    codex)  install_codex ;;
    cursor) install_cursor ;;
    agents) install_agents ;;
    all)    install_all ;;
    *)      echo "Unknown tool: $TOOL. Use: claude, codex, cursor, agents, or all." >&2; exit 1 ;;
  esac
elif [ -t 0 ]; then
  show_menu
else
  install_all
fi

echo ""
echo "Install complete. Open your coding agent in this folder and ask it to build something with your Tap."
