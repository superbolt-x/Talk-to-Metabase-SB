# Installation Guide

## Download and Install

1. **Download** the appropriate file for your platform from the [latest release](https://github.com/VincentGefflaut/Talk-to-Metabase/releases/latest):
   - `talk-to-metabase-macos-intel.tar.gz` - Intel Mac (x86_64)
   - `talk-to-metabase-macos-apple-silicon.tar.gz` - Apple Silicon Mac (M1/M2/M3/M4)
   - `talk-to-metabase-linux.tar.gz` - Linux (x86_64)
   - `talk-to-metabase-windows.exe` - Windows (x86_64)

2. **Extract and run**:
    ```bash
    # macOS - Extract and authorize to run
    Click on the downloaded .tar.gz file - it should create an unzipped file
    On the newly extracted file, do right click>open and then click "open" on the popup
    Close the terminal that just poped-up (you can click on "Terminate" on the pop-up)

    ./talk-to-metabase-*

    # Linux - Extract with preserved permissions
    tar -xzf talk-to-metabase-*.tar.gz
    ./talk-to-metabase-*
    
    # Windows - Just run the .exe file
    talk-to-metabase-windows.exe
    ```
   
   ✅ **No chmod needed!** Executable permissions are preserved in the archive.

3. **Optional**: Move to a directory in your PATH:
   ```bash
   # macOS/Linux
   mkdir -p ~/.local/bin
   mv talk-to-metabase-* ~/.local/bin/talk-to-metabase
   
   # Add to PATH if not already there (add to ~/.zshrc or ~/.bash_profile)
   export PATH="$HOME/.local/bin:$PATH"
   ```

## Why tar.gz?

The **tar.gz archives preserve Unix file permissions**, including the executable bit, so users don't need to run `chmod +x`. This is the most reliable way to distribute executables via GitHub releases without requiring users to manually set permissions.

## Configuration

After installation, add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "Talk to Metabase": {
      "command": "/path/to/talk-to-metabase",
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

## Troubleshooting

If you still encounter permission issues after extracting:
```bash
chmod +x talk-to-metabase-*
```

But this should not be necessary with the tar.gz approach.
