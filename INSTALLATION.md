# Easy Installation Guide

## Quick Install (Recommended)

### One-liner Installation
```bash
curl -sSL https://raw.githubusercontent.com/vincentgefflaut/talk-to-metabase/main/install.sh | bash
```

This will:
1. Detect your platform (macOS Intel, macOS Apple Silicon, Linux, Windows)
2. Download the appropriate executable from the latest GitHub release
3. Install it to `~/.talk-to-metabase/`
4. Generate a Claude Desktop configuration template

### Manual Installation

1. **Download the executable** for your platform from the [latest release](https://github.com/vincentgefflaut/talk-to-metabase/releases/latest):
   - `talk-to-metabase-macos-intel` - Intel Mac (x86_64)
   - `talk-to-metabase-macos-apple-silicon` - Apple Silicon Mac (M1/M2/M3)
   - `talk-to-metabase-linux` - Linux (x86_64)
   - `talk-to-metabase-windows.exe` - Windows (x86_64)

2. **Make it executable** (macOS/Linux only):
   ```bash
   chmod +x talk-to-metabase-*
   ```

3. **Configure Claude Desktop** by adding this to your configuration:
   ```json
   {
     "mcpServers": {
       "Talk to Metabase": {
         "command": "/path/to/talk-to-metabase-[your-platform]",
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
   ```

4. **Restart Claude Desktop** and start chatting with your Metabase data!

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `METABASE_URL` | Your Metabase instance URL | ✅ Yes |
| `METABASE_USERNAME` | Your Metabase username | ✅ Yes |
| `METABASE_PASSWORD` | Your Metabase password | ✅ Yes |
| `METABASE_CONTEXT_AUTO_INJECT` | Auto-load context guidelines | No (default: true) |

## Troubleshooting

### macOS Security Warning
If you get a security warning on macOS:
1. Right-click the executable and select "Open"
2. Or run: `xattr -d com.apple.quarantine talk-to-metabase-*`

### Windows Security Warning
If Windows Defender blocks the executable:
1. Click "More info" then "Run anyway"
2. Or add an exception in Windows Security

### Connection Issues
- Verify your Metabase URL is accessible
- Check your username and password
- Ensure your Metabase instance allows API access

## Advanced Configuration

For advanced users, you can also set these optional environment variables:
- `RESPONSE_SIZE_LIMIT` - Maximum response size in characters (default: 100000)
- `LOG_LEVEL` - Logging level (default: INFO)
- `MCP_TRANSPORT` - Transport method (default: stdio)

## Development

If you want to run from source instead of using the prebuilt executables, see [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.
