#!/bin/bash
# Install Tap Python SDK AI development config into your project.
# Usage:
#   ./install-skills.sh              # Interactive menu (when run with a tty)
#   ./install-skills.sh cursor       # Cursor skill only
#   ./install-skills.sh claude       # Claude Code skill only
#   ./install-skills.sh agents       # AGENTS.md only
#   ./install-skills.sh all          # Cursor + Claude + AGENTS.md
#   curl -sL .../install-skills.sh | bash   # Defaults to "all" (no tty)
#
# Optional:
#   TAP_PYTHON_SDK_BRANCH=master   # GitHub branch/tag for remote install (default: master)

set -euo pipefail

REPO="TapWithUs/tap-python-sdk"
BRANCH="${TAP_PYTHON_SDK_BRANCH:-master}"
ARCHIVE_URL="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"
# GitHub replaces '/' in branch names with '-' in the extracted folder name.
EXTRACT_DIR="tap-python-sdk-${BRANCH//\//-}"
SKILL_NAME="tap-python-sdk"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
SOURCE_DIR=""
DOWNLOADED=0

safe_cleanup() {
  if [ "${DOWNLOADED}" -ne 1 ]; then
    return 0
  fi
  if [ -z "${EXTRACT_DIR:-}" ]; then
    echo "Warning: EXTRACT_DIR is empty, skipping cleanup." >&2
    return 0
  fi
  if [[ ! "$EXTRACT_DIR" =~ ^tap-python-sdk- ]]; then
    echo "Warning: EXTRACT_DIR does not match expected pattern, skipping cleanup." >&2
    return 0
  fi
  if [ -d "$EXTRACT_DIR" ]; then
    rm -rf "$EXTRACT_DIR"
  fi
}
trap safe_cleanup EXIT

resolve_source() {
  if [ -n "${SOURCE_DIR}" ]; then
    return 0
  fi
  # Prefer a local checkout when this script lives next to the skill files.
  if [ -n "${SCRIPT_DIR}" ] \
    && [ -f "${SCRIPT_DIR}/.cursor/skills/${SKILL_NAME}/SKILL.md" ] \
    && [ -f "${SCRIPT_DIR}/AGENTS.md" ]; then
    SOURCE_DIR="${SCRIPT_DIR}"
    echo "Using local skill files from ${SOURCE_DIR}"
    return 0
  fi
  echo "Downloading ${REPO}@${BRANCH}…"
  require_command curl
  require_command tar
  if [ -d "${EXTRACT_DIR}" ]; then
    rm -rf "${EXTRACT_DIR}"
  fi
  curl -fsSL "$ARCHIVE_URL" | tar xz
  DOWNLOADED=1
  if [ ! -d "${EXTRACT_DIR}" ]; then
    # Fallback: find the extracted top-level directory.
    EXTRACT_DIR="$(find . -maxdepth 1 -type d -name 'tap-python-sdk-*' | head -n 1)"
  fi
  if [ -z "${EXTRACT_DIR}" ] || [ ! -d "${EXTRACT_DIR}" ]; then
    echo "Error: Failed to download archive from ${ARCHIVE_URL}." >&2
    return 1
  fi
  SOURCE_DIR="${EXTRACT_DIR}"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: '$1' is not installed or not on PATH." >&2
    return 1
  fi
}

install_cursor() {
  echo "Installing Cursor skill (${SKILL_NAME})…"
  resolve_source
  local src="${SOURCE_DIR}/.cursor/skills/${SKILL_NAME}"
  if [ ! -f "${src}/SKILL.md" ]; then
    echo "Error: Missing ${src}/SKILL.md in source." >&2
    return 1
  fi
  mkdir -p ".cursor/skills/${SKILL_NAME}"
  cp "${src}/SKILL.md" ".cursor/skills/${SKILL_NAME}/SKILL.md"
  echo "Installed .cursor/skills/${SKILL_NAME}/SKILL.md"
}

install_claude() {
  echo "Installing Claude Code skill (${SKILL_NAME})…"
  resolve_source
  # Prefer the Cursor skill file (Claude twin is often a symlink to it).
  local src_skill="${SOURCE_DIR}/.cursor/skills/${SKILL_NAME}/SKILL.md"
  if [ ! -f "${src_skill}" ]; then
    src_skill="${SOURCE_DIR}/.claude/skills/${SKILL_NAME}/SKILL.md"
  fi
  if [ ! -f "${src_skill}" ]; then
    echo "Error: Missing Claude/Cursor SKILL.md in source." >&2
    return 1
  fi
  mkdir -p ".claude/skills/${SKILL_NAME}"
  cp "${src_skill}" ".claude/skills/${SKILL_NAME}/SKILL.md"
  echo "Installed .claude/skills/${SKILL_NAME}/SKILL.md"
}

install_agents() {
  echo "Installing AGENTS.md…"
  resolve_source
  if [ ! -f "${SOURCE_DIR}/AGENTS.md" ]; then
    echo "Error: Missing AGENTS.md in source." >&2
    return 1
  fi
  cp "${SOURCE_DIR}/AGENTS.md" AGENTS.md
  echo "Installed AGENTS.md"
}

install_all() {
  local failed=0
  install_cursor || failed=1
  install_claude || failed=1
  install_agents || failed=1
  if [ "$failed" -eq 1 ]; then
    return 1
  fi
}

show_menu() {
  echo ""
  echo "Tap Python SDK AI Config Installer"
  echo "=================================="
  echo ""
  echo "Which tool do you want to install config for?"
  echo ""
  echo "  1) Cursor         (.cursor/skills/${SKILL_NAME}/)"
  echo "  2) Claude Code    (.claude/skills/${SKILL_NAME}/)"
  echo "  3) AGENTS.md      (universal fallback)"
  echo "  4) All of the above"
  echo "  5) Cancel"
  echo ""
  read -rp "Enter choice [1-5]: " choice
  case "$choice" in
    1) install_cursor ;;
    2) install_claude ;;
    3) install_agents ;;
    4) install_all ;;
    5) echo "Cancelled." ; exit 0 ;;
    *) echo "Invalid choice." >&2 ; exit 1 ;;
  esac
}

# Main
TOOL="${1:-}"

if [ -n "$TOOL" ]; then
  case "$TOOL" in
    cursor)  install_cursor ;;
    claude)  install_claude ;;
    agents)  install_agents ;;
    all)     install_all ;;
    *)
      echo "Unknown tool: $TOOL. Use: cursor, claude, agents, or all." >&2
      exit 1
      ;;
  esac
elif [ -t 0 ]; then
  show_menu
else
  # Piped via curl — default to all (Meta install-skills.sh pattern)
  install_all
fi

echo ""
echo "Install complete. Restart your agent session (or reopen the project),"
echo "then ask it to use the ${SKILL_NAME} skill before writing BLE code."
