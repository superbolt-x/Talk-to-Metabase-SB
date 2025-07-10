# Installation Guide

## 📦 Download and Install

### Step 1: Download the Executable

Download the appropriate file for your platform from the [latest release](https://github.com/VincentGefflaut/Talk-to-Metabase/releases/latest):

| Platform | File | Architecture |
|----------|------|-------------|
| **macOS (Intel)** | `talk-to-metabase-macos-intel.tar.gz` | x86_64 |
| **macOS (Apple Silicon)** | `talk-to-metabase-macos-apple-silicon.tar.gz` | arm64 (M1/M2/M3/M4) |
| **Linux** | `talk-to-metabase-linux.tar.gz` | x86_64 |
| **Windows** | `talk-to-metabase-windows.exe` | x86_64 |

### Step 2: Extract and Authorize

#### macOS Installation
```bash
# Extract the archive (or double-click the .tar.gz file)
tar -xzf talk-to-metabase-macos-*.tar.gz

# Authorize the executable to run
# Right-click the extracted file > Open > Click "Open" in the popup
# Close the terminal that opens (click "Terminate" if prompted)
```

#### Linux Installation
```bash
# Extract with preserved permissions
tar -xzf talk-to-metabase-linux.tar.gz

# Run the executable
./talk-to-metabase-linux
```

#### Windows Installation
```cmd
# Just run the .exe file directly
talk-to-metabase-windows.exe
```

### Step 3: Optional - Add to PATH

For easier access from anywhere:

```bash
# macOS/Linux - Move to local bin directory
mkdir -p ~/.local/bin
mv talk-to-metabase-* ~/.local/bin/talk-to-metabase

# Add to PATH (add this line to ~/.zshrc or ~/.bash_profile)
export PATH="$HOME/.local/bin:$PATH"

# Reload your shell configuration
source ~/.zshrc  # or ~/.bash_profile
```

## 🔧 Configuration

### Claude Desktop Configuration

Add this configuration to your Claude Desktop settings file:

#### macOS Configuration Location
```bash
# Edit the configuration file
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### Windows Configuration Location
```cmd
# Edit the configuration file
notepad %APPDATA%\Claude\claude_desktop_config.json
```

### Configuration Template

```json
{
  "mcpServers": {
    "Talk to Metabase": {
      "command": "/path/to/talk-to-metabase",
      "args": [],
      "env": {
        "METABASE_URL": "https://your-metabase.company.com",
        "METABASE_USERNAME": "your-username",
        "METABASE_PASSWORD": "your-password",
        "METABASE_CONTEXT_AUTO_INJECT": "true",
        "RESPONSE_SIZE_LIMIT": "100000",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `METABASE_URL` | Your Metabase instance URL | ✅ Yes | - |
| `METABASE_USERNAME` | Metabase username | ✅ Yes | - |
| `METABASE_PASSWORD` | Metabase password | ✅ Yes | - |
| `METABASE_CONTEXT_AUTO_INJECT` | Load context guidelines | No | `true` |
| `RESPONSE_SIZE_LIMIT` | Max response size in characters | No | `100000` |
| `LOG_LEVEL` | Logging level | No | `INFO` |
| `MCP_TRANSPORT` | Transport protocol | No | `stdio` |

## 🚀 Alternative Installation Methods

### Option 1: Using pip (Development)

```bash
# Clone the repository
git clone https://github.com/VincentGefflaut/Talk-to-Metabase.git
cd Talk-to-Metabase

# Install in development mode
pip install -e .

# Run the server
python metabase_mcp.py
```

### Option 2: Using Docker (Advanced)

```bash
# Build the Docker image
docker build -t talk-to-metabase .

# Run with environment variables
docker run -e METABASE_URL=https://your-metabase.com \
           -e METABASE_USERNAME=your-username \
           -e METABASE_PASSWORD=your-password \
           talk-to-metabase
```

## 🔍 Verification

### Test the Installation

1. **Start Claude Desktop** with the new configuration
2. **Create a new conversation** in Claude
3. **Try a simple command**: "List the available databases in Metabase"
4. **Verify connection**: You should see your Metabase databases listed

### Expected First Interaction

```
You: "What databases are available in Metabase?"

Claude: "I'll check the available databases in your Metabase instance."
[Uses list_databases tool]

Response: "Here are the available databases in your Metabase instance:
- Database 1: Sample Database (H2)
- Database 2: Production Analytics (PostgreSQL)
- Database 3: Marketing Data (MySQL)"
```

## 🛠️ Troubleshooting

### Common Installation Issues

#### macOS: "Cannot be opened because the developer cannot be verified"
```bash
# Solution: Right-click the executable and select "Open"
# Then click "Open" in the security dialog
```

#### Linux: Permission denied
```bash
# Solution: Make the file executable
chmod +x talk-to-metabase-linux
```

#### Windows: Defender blocks the executable
```cmd
# Solution: Click "More info" then "Run anyway"
# Or add an exception in Windows Security
```

### Connection Issues

#### Cannot connect to Metabase
1. **Check URL**: Ensure your Metabase URL is correct and accessible
2. **Verify credentials**: Test login through Metabase web interface
3. **Check network**: Ensure no firewall blocks the connection
4. **API access**: Verify your Metabase instance allows API access

#### Authentication failures
1. **Username format**: Use email address if that's your login method
2. **Password special characters**: Ensure proper escaping in JSON
3. **2FA**: If enabled, you may need an API key instead of password

### Performance Issues

#### Large response errors
```json
{
  "env": {
    "RESPONSE_SIZE_LIMIT": "200000"
  }
}
```

#### Slow responses
```json
{
  "env": {
    "LOG_LEVEL": "DEBUG"
  }
}
```

### Configuration Validation

#### Test your configuration
```bash
# Check if the executable runs
./talk-to-metabase --help

# Test with environment variables
METABASE_URL=https://your-metabase.com \
METABASE_USERNAME=your-username \
METABASE_PASSWORD=your-password \
./talk-to-metabase
```

## 📋 Next Steps

After successful installation:

1. **Explore your data**: Try "Show me the structure of my main database"
2. **Create a simple chart**: "Create a bar chart showing sales by category"
3. **Build a dashboard**: "Create a dashboard with key metrics"
4. **Set up filters**: "Add interactive filters to this dashboard"

## 🔗 Additional Resources

- **Documentation**: Check the built-in documentation tools
- **Examples**: Use `GET_VISUALIZATION_DOCUMENT` for chart examples
- **Parameters**: Use `GET_CARD_PARAMETERS_DOCUMENTATION` for filter setup
- **Guidelines**: Use `GET_METABASE_GUIDELINES` for organization-specific help

## 💡 Pro Tips

### File Permissions
The tar.gz archives preserve Unix file permissions, so you don't need to run `chmod +x` manually.

### Path Configuration
Always use absolute paths in your Claude Desktop configuration to avoid issues with working directory changes.

### Environment Variables
Consider using a `.env` file for local development:

```bash
# Create .env file
METABASE_URL=https://your-metabase.com
METABASE_USERNAME=your-username
METABASE_PASSWORD=your-password
```

### Security
- Keep your credentials secure
- Use environment variables instead of hardcoding passwords
- Consider using API keys if your Metabase instance supports them

---

**Ready to start?** Follow the installation steps above and begin exploring your data with AI-powered insights!
