#!/usr/bin/env bash
# ==============================================================================
# 👶 Baby LLM: Frictionless One-Line Installer (macOS & Linux)
# https://github.com/webdev-hemant/baby-llm
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/webdev-hemant/baby-llm/main/install.sh | bash
#
# Uninstall:
#   curl -fsSL https://raw.githubusercontent.com/webdev-hemant/baby-llm/main/install.sh | bash -s -- --uninstall
# ==============================================================================

set -euo pipefail

# ANSI color codes
BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
MAGENTA="\033[0;35m"
NC="\033[0m"

INSTALL_DIR="${HOME}/.local/share/baby-llm"
BIN_DIR="${HOME}/.local/bin"
EXECUTABLE="${BIN_DIR}/baby-llm"
REPO_URL="git+https://github.com/webdev-hemant/baby-llm.git"

print_banner() {
    echo -e "${MAGENTA}${BOLD}"
    cat << 'EOF'
  ____        _             _     _     __  __ 
 |  _ \      | |           | |   | |   |  \/  |
 | |_) | __ _| |__  _   _  | |   | |   | \  / |
 |  _ < / _` | '_ \| | | | | |   | |   | |\/| |
 | |_) | (_| | |_) | |_| | | |___| |___| |  | |
 |____/ \__,_|_.__/ \__, | |______|______|_|  |_|
                     __/ |                      
                    |___/                       
EOF
    echo -e "${NC}${BOLD}The Privacy-First, Self-Evolving Local Memory Engine${NC}"
    echo -e "─────────────────────────────────────────────────────────────"
}

info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✔${NC} $1"
}

warn() {
    echo -e "${YELLOW}▲${NC} $1"
}

error() {
    echo -e "${RED}✖${NC} $1" >&2
}

# Handle uninstall flag
if [[ "${1:-}" == "--uninstall" ]]; then
    echo -e "${YELLOW}${BOLD}Uninstalling Baby LLM...${NC}"
    rm -rf "${INSTALL_DIR}"
    rm -f "${EXECUTABLE}"
    success "Baby LLM has been completely removed from ${INSTALL_DIR} and ${EXECUTABLE}."
    echo -e "Note: Personal memories in ~/.baby_llm were preserved. Delete manually if desired:"
    echo -e "  rm -rf ~/.baby_llm"
    exit 0
fi

print_banner

# Step 1: Detect Operating System & Architecture
OS="$(uname -s)"
ARCH="$(uname -m)"

if [[ "${OS}" != "Darwin" && "${OS}" != "Linux" ]]; then
    error "Baby LLM installer currently supports macOS and Linux. Detected: ${OS}"
    exit 1
fi

info "Detected Platform: ${BOLD}${OS} (${ARCH})${NC}"
if [[ "${OS}" == "Darwin" && "${ARCH}" == "arm64" ]]; then
    info "Apple Silicon Metal GPU acceleration will be utilized."
fi

# Step 2: Ensure uv package manager is available
if command -v uv >/dev/null 2>&1; then
    UV_BIN="$(command -v uv)"
    success "Found uv package manager: ${UV_BIN}"
else
    info "uv not found. Installing standalone uv (Astral) in ~/.local/bin..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="${BIN_DIR}:${PATH}"
    if command -v uv >/dev/null 2>&1; then
        UV_BIN="$(command -v uv)"
        success "uv installed successfully: ${UV_BIN}"
    else
        error "Failed to install uv. Please install uv manually: https://docs.astral.sh/uv/"
        exit 1
    fi
fi

# Step 3: Create isolated installation environment
mkdir -p "${INSTALL_DIR}"
mkdir -p "${BIN_DIR}"

info "Provisioning isolated Python 3.12 environment in ${INSTALL_DIR}/venv..."
"${UV_BIN}" venv --python 3.12 "${INSTALL_DIR}/venv" --quiet
success "Python 3.12 isolated environment created."

# Step 4: Install baby-llm
TARGET_SOURCE="${REPO_URL}"
# If running inside a cloned repository root, install local editable version
if [[ -f "./pyproject.toml" ]] && grep -q 'name = "baby-llm"' "./pyproject.toml" 2>/dev/null; then
    TARGET_SOURCE="."
    info "Detected local repository clone. Installing local source..."
else
    info "Installing Baby LLM from GitHub repository (${REPO_URL})..."
fi

"${UV_BIN}" pip install --python "${INSTALL_DIR}/venv" "${TARGET_SOURCE}" --quiet
success "Baby LLM package and embedded dependencies installed successfully."

# Step 5: Create launcher script in ~/.local/bin
info "Creating launcher executable in ${EXECUTABLE}..."
cat << 'EOF' > "${EXECUTABLE}"
#!/usr/bin/env bash
exec "${HOME}/.local/share/baby-llm/venv/bin/baby-llm" "$@"
EOF
chmod +x "${EXECUTABLE}"
success "Launcher script created: ${EXECUTABLE}"

# Step 6: Verify PATH setup
PATH_CONFIGURED=false
if echo ":${PATH}:" | grep -q ":${BIN_DIR}:"; then
    PATH_CONFIGURED=true
fi

if [[ "${PATH_CONFIGURED}" == "false" ]]; then
    SHELL_NAME="$(basename "${SHELL:-/bin/zsh}")"
    RC_FILE=""
    if [[ "${SHELL_NAME}" == "zsh" ]]; then
        RC_FILE="${HOME}/.zshrc"
    elif [[ "${SHELL_NAME}" == "bash" ]]; then
        if [[ "${OS}" == "Darwin" ]]; then
            RC_FILE="${HOME}/.bash_profile"
        else
            RC_FILE="${HOME}/.bashrc"
        fi
    fi

    if [[ -n "${RC_FILE}" ]]; then
        if ! grep -q '\.local/bin' "${RC_FILE}" 2>/dev/null; then
            echo '' >> "${RC_FILE}"
            echo '# Added by Baby LLM installer' >> "${RC_FILE}"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "${RC_FILE}"
            success "Added ~/.local/bin to ${RC_FILE}"
        fi
        warn "Please run: ${BOLD}source ${RC_FILE}${NC} or restart your terminal to update PATH."
    fi
fi

# Step 7: Verification Check
if "${EXECUTABLE}" --help >/dev/null 2>&1; then
    success "Self-verification test passed."
fi

echo ""
echo -e "${GREEN}${BOLD}🎉 Baby LLM is installed and ready!${NC}"
echo -e "─────────────────────────────────────────────────────────────"
echo -e "${BOLD}Quickstart Commands:${NC}"
echo -e "  ${CYAN}baby-llm chat${NC}       Start interactive offline chat"
echo -e "  ${CYAN}baby-llm ui${NC}         Launch local Glass-Box Web Dashboard (Port 21225)"
echo -e "  ${CYAN}baby-llm serve${NC}      Run local REST API server"
echo -e "  ${CYAN}baby-llm dream${NC}      Run one-shot REM memory consolidation"
echo -e "  ${CYAN}baby-llm --help${NC}     View full command-line options"
echo -e "─────────────────────────────────────────────────────────────"
