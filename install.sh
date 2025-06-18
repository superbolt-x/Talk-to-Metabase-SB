#!/bin/bash

# install.sh - Easy installer for Talk to Metabase MCP Server
# Usage: curl -sSL https://raw.githubusercontent.com/yourusername/talk-to-metabase/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO="vincentgefflaut/talk-to-metabase"  # Update this with your actual GitHub repo
INSTALL_DIR="$HOME/.talk-to-metabase"
BINARY_NAME="talk-to-metabase"

echo -e "${GREEN}Talk to Metabase MCP Server Installer${NC}"
echo -e "${BLUE}====================================${NC}\n"

# Detect platform and architecture
detect_platform() {
    local os=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch=$(uname -m)
    
    case "$os" in
        darwin)
            case "$arch" in
                x86_64) echo "macos-intel" ;;
                arm64) echo "macos-apple-silicon" ;;
                *) echo "unsupported" ;;
            esac
            ;;
        linux)
            case "$arch" in
                x86_64) echo "linux" ;;
                *) echo "unsupported" ;;
            esac
            ;;
        mingw*|cygwin*|msys*)
            echo "windows"
            ;;
        *)
            echo "unsupported"
            ;;
    esac
}

# Get latest release info from GitHub API
get_latest_release() {
    local api_url="https://api.github.com/repos/${REPO}/releases/latest"
    
    if command -v curl >/dev/null 2>&1; then
        curl -s "$api_url"
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- "$api_url"
    else
        echo -e "${RED}❌ Neither curl nor wget found. Please install one of them.${NC}"
        exit 1
    fi
}

# Download and install
install_talk_to_metabase() {
    echo -e "${BLUE}🚀 Installing Talk to Metabase MCP Server...${NC}"
    
    # Detect platform
    local platform=$(detect_platform)
    if [ "$platform" = "unsupported" ]; then
        echo -e "${RED}❌ Unsupported platform: $(uname -s)-$(uname -m)${NC}"
        echo -e "${YELLOW}💡 Supported platforms: macOS (Intel & Apple Silicon), Linux (x86_64), Windows${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}📍 Detected platform: $platform${NC}"
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    
    # Get latest release information
    echo -e "${YELLOW}🔍 Fetching latest release information...${NC}"
    local release_info=$(get_latest_release)
    
    if [ -z "$release_info" ]; then
        echo -e "${RED}❌ Could not fetch release information${NC}"
        exit 1
    fi
    
    # Extract download URL for our platform
    local binary_suffix=""
    local search_name="${BINARY_NAME}-${platform}"
    
    if [ "$platform" = "windows" ]; then
        binary_suffix=".exe"
        search_name="${search_name}.exe"
    fi
    
    local download_url=$(echo "$release_info" | grep -o "https://github.com/${REPO}/releases/download/[^\"]*${search_name}" | head -1)
    
    if [ -z "$download_url" ]; then
        echo -e "${RED}❌ Could not find download URL for platform: $platform${NC}"
        echo -e "${YELLOW}💡 Available assets:${NC}"
        echo "$release_info" | grep -o "https://github.com/${REPO}/releases/download/[^\"]*${BINARY_NAME}[^\"]*" || echo "No assets found"
        exit 1
    fi
    
    echo -e "${YELLOW}📥 Downloading from: $download_url${NC}"
    
    # Download binary
    local binary_path="$INSTALL_DIR/${BINARY_NAME}${binary_suffix}"
    
    if command -v curl >/dev/null 2>&1; then
        curl -L -o "$binary_path" "$download_url"
    elif command -v wget >/dev/null 2>&1; then
        wget -O "$binary_path" "$download_url"
    fi
    
    # Make executable on Unix systems
    if [ "$platform" != "windows" ]; then
        chmod +x "$binary_path"
    fi
    
    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo -e "${BLUE}📁 Installed to: $binary_path${NC}"
    
    # Test the installation
    echo -e "${YELLOW}🧪 Testing installation...${NC}"
    if timeout 5s "$binary_path" --help >/dev/null 2>&1 || [ $? -eq 124 ]; then
        echo -e "${GREEN}✅ Installation test passed!${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not test installation, but file was downloaded${NC}"
    fi
    
    # Generate Claude Desktop configuration
    generate_claude_config "$binary_path"
}

# Generate Claude Desktop configuration
generate_claude_config() {
    local binary_path="$1"
    local config_file="$INSTALL_DIR/claude-config-template.json"
    
    cat > "$config_file" << EOF
{
  "mcpServers": {
    "Talk to Metabase": {
      "command": "$binary_path",
      "args": [],
      "env": {
        "METABASE_URL": "https://your-metabase.com",
        "METABASE_USERNAME": "your-username",
        "METABASE_PASSWORD": "your-password",
        "METABASE_CONTEXT_AUTO_INJECT": "true"
      }
    }
  }
}
EOF
    
    echo -e "\n${BLUE}📋 Claude Desktop Configuration:${NC}"
    echo -e "${YELLOW}Add this to your Claude Desktop config (update the environment variables):${NC}\n"
    cat "$config_file"
    echo -e "\n${GREEN}💾 Config template saved to: $config_file${NC}"
    
    echo -e "\n${BLUE}🔧 Next Steps:${NC}"
    echo -e "1. Update the environment variables in the config with your actual Metabase credentials"
    echo -e "2. Add the configuration to your Claude Desktop settings"
    echo -e "3. Restart Claude Desktop"
    echo -e "4. Start chatting with your Metabase data!"
    
    echo -e "\n${GREEN}🎉 Installation successful!${NC}"
}

# Main execution
main() {
    install_talk_to_metabase
}

# Run installer
main "$@"
