#!/bin/bash
# Install Tap Python SDK skills into the current project.
# Add -g to install for your user (every project) instead.
#
#   ./install-skills.sh                 # menu, this folder
#   ./install-skills.sh claude          # .claude/skills/
#   ./install-skills.sh codex           # .agents/skills/
#   ./install-skills.sh cursor          # .cursor/skills/ + .cursor/rules/
#   ./install-skills.sh agents          # ./AGENTS.md
#   ./install-skills.sh all             # all four, this folder
#   ./install-skills.sh -g claude       # Claude Code plugin for your user
#   ./install-skills.sh -g codex        # Codex plugin for your user
#   ./install-skills.sh -g cursor       # ~/.cursor/skills/ + ~/.cursor/rules/
#   ./install-skills.sh -g agents       # ~/.codex/AGENTS.md
#   ./install-skills.sh -g all
#   curl -sL .../install-skills.sh | bash          # all, this folder
#   curl -sL .../install-skills.sh | bash -s -- -g # all, for your user

set -euo pipefail

REPO="TapWithUs/tap-python-sdk"
BRANCH="master"
ARCHIVE_URL="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"
EXTRACT_DIR="tap-python-sdk-${BRANCH}"
PLUGIN="tap-python-sdk"
MARKETPLACE="tap-python-sdk-marketplace"
INSTALL_GLOBAL=0

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

skills_dir() {
  echo "${EXTRACT_DIR}/plugins/${PLUGIN}/skills"
}

rule_file() {
  echo "${EXTRACT_DIR}/.cursor/rules/tap-sdk.mdc"
}

stage_skills() {
  download_archive
  if [ ! -d "$(skills_dir)" ]; then
    echo "Error: Failed to download skills." >&2
    return 1
  fi
}

copy_skills_to() {
  local dest="$1"
  stage_skills
  mkdir -p "$dest"
  cp -R "$(skills_dir)/." "$dest/"
  find "$dest" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
  find "$dest" -name '*.pyc' -delete 2>/dev/null || true
  echo "Installed $(ls "$(skills_dir)" | wc -l | tr -d ' ') skills in ${dest}/."
}

copy_cursor_rule_to() {
  local dest_dir="$1"
  stage_skills
  if [ ! -f "$(rule_file)" ]; then
    echo "Error: Failed to download Cursor rule." >&2
    return 1
  fi
  mkdir -p "$dest_dir"
  cp "$(rule_file)" "${dest_dir}/tap-sdk.mdc"
  echo "Installed ${dest_dir}/tap-sdk.mdc."
}

write_agents_file() {
  local dest="$1"
  download_archive
  if [ ! -f "${EXTRACT_DIR}/AGENTS.md" ]; then
    echo "Error: Failed to download AGENTS.md." >&2
    return 1
  fi
  if [ -e "$dest" ] && ! head -n 1 "$dest" | grep -q '^# Tap Python SDK$'; then
    echo "Error: ${dest} already exists and is not the Tap guide. Remove it or pick another folder." >&2
    return 1
  fi
  mkdir -p "$(dirname "$dest")"
  # The contributor section is for the SDK repository only.
  sed '/^## Contributing to this repository/,$d' "${EXTRACT_DIR}/AGENTS.md" > "$dest"
  echo "Installed ${dest}."
}

install_claude() {
  if [ "$INSTALL_GLOBAL" -eq 1 ]; then
    echo "Installing Claude Code plugin for your user..."
    require_command claude
    claude plugin marketplace add "${REPO}" || return 1
    claude plugin install "${PLUGIN}@${MARKETPLACE}" --scope user || return 1
    echo "Installed Claude Code plugin ${PLUGIN} for your user."
    return 0
  fi
  echo "Installing Claude Code skills in this folder..."
  copy_skills_to ".claude/skills"
}

install_codex() {
  if [ "$INSTALL_GLOBAL" -eq 1 ]; then
    echo "Installing Codex plugin for your user..."
    require_command codex
    codex plugin marketplace add "${REPO}" || return 1
    codex plugin add "${PLUGIN}@${MARKETPLACE}" || return 1
    echo "Installed Codex plugin ${PLUGIN} for your user."
    return 0
  fi
  echo "Installing Codex skills in this folder..."
  copy_skills_to ".agents/skills"
}

install_cursor() {
  if [ "$INSTALL_GLOBAL" -eq 1 ]; then
    echo "Installing Cursor skills for your user..."
    copy_skills_to "${HOME}/.cursor/skills"
    copy_cursor_rule_to "${HOME}/.cursor/rules"
    return 0
  fi
  echo "Installing Cursor skills in this folder..."
  copy_skills_to ".cursor/skills"
  copy_cursor_rule_to ".cursor/rules"
}

install_agents() {
  if [ "$INSTALL_GLOBAL" -eq 1 ]; then
    echo "Installing AGENTS.md for your user..."
    write_agents_file "${HOME}/.codex/AGENTS.md"
    return 0
  fi
  echo "Installing AGENTS.md in this folder..."
  write_agents_file "AGENTS.md"
}

install_all() {
  local failed=0
  if [ "$INSTALL_GLOBAL" -eq 1 ]; then
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
  else
    install_claude || failed=1
    install_codex || failed=1
  fi
  install_cursor || failed=1
  install_agents || failed=1
  return "$failed"
}

show_menu() {
  echo ""
  echo "Tap Python SDK - AI assistant config installer"
  if [ "$INSTALL_GLOBAL" -eq 1 ]; then
    echo "Scope: your user (every project)"
  else
    echo "Scope: this folder"
  fi
  echo "=============================================="
  echo ""
  echo "  1) Claude Code"
  echo "  2) Codex"
  echo "  3) Cursor"
  echo "  4) AGENTS.md"
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

usage() {
  echo "Usage: $0 [-g] [claude|codex|cursor|agents|all]" >&2
  echo "  default  install into the current folder" >&2
  echo "  -g       install for your user, in every project" >&2
}

TOOL=""
while [ $# -gt 0 ]; do
  case "$1" in
    -g|--global) INSTALL_GLOBAL=1 ;;
    -h|--help) usage; exit 0 ;;
    claude|codex|cursor|agents|all)
      if [ -n "$TOOL" ]; then
        echo "Error: only one target is allowed." >&2
        usage
        exit 1
      fi
      TOOL="$1"
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

if [ -n "$TOOL" ]; then
  "install_${TOOL}"
elif [ -t 0 ]; then
  show_menu
else
  install_all
fi

echo ""
if [ "$INSTALL_GLOBAL" -eq 1 ]; then
  echo "Install complete. The Tap skills are available in every project you open."
else
  echo "Install complete. Open your coding agent in this folder and ask it to build something with your Tap."
fi
