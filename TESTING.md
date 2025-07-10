# Manual Verification Guide

Instructions for manually verifying the Talk to Metabase MCP server functionality.

## 🔧 Setup and Configuration Verification

### Prerequisites

1. **Python 3.10+** installed
2. **Access to a Metabase instance**
3. **Valid Metabase credentials**
4. **Claude Desktop** installed

### Environment Setup

```bash
# Navigate to project directory
cd /Users/Pro/workspace/Talk\ to\ Metabase

# Create environment file for verification
cp .env.example .env

# Edit configuration with your credentials
vim .env
```

### Environment Configuration

```bash
# Metabase Configuration
METABASE_URL=https://your-metabase-instance.company.com
METABASE_USERNAME=your-username@example.com
METABASE_PASSWORD=your-password
MCP_TRANSPORT=stdio
LOG_LEVEL=INFO
RESPONSE_SIZE_LIMIT=100000
```

## 🚀 Installation Verification

### Option 1: Prebuilt Executable Verification

```bash
# Download and extract the appropriate executable
tar -xzf talk-to-metabase-*.tar.gz

# On macOS: Right-click and "Open" to authorize
# On Linux: Ensure executable permissions
chmod +x talk-to-metabase-*

# Verify the executable runs
./talk-to-metabase-* --help
```

### Option 2: Source Installation Verification

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .

# Verify installation
python -c "import talk_to_metabase; print('Installation successful')"
```

## 🔗 Claude Desktop Integration

### Configuration

Edit your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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
        "RESPONSE_SIZE_LIMIT": "100000",
        "METABASE_CONTEXT_AUTO_INJECT": "true"
      }
    }
  }
}
```

### Basic Connection Verification

1. **Restart Claude Desktop**
2. **Start a new conversation**
3. **Try the basic connection**:

```
You: "What databases are available in Metabase?"
Expected: List of databases from your Metabase instance
```

## 📊 Functionality Verification

### 1. Database Exploration

```
You: "Show me the structure of the main database"
Expected: Database schema with tables and fields

You: "What tables are available in database [ID]?"
Expected: List of tables with descriptions

You: "Get details about the fields in table [TABLE_NAME]"
Expected: Field metadata including types and descriptions
```

### 2. Query Execution

```
You: "Run this query: SELECT COUNT(*) FROM [TABLE_NAME] LIMIT 10"
Expected: Query results in a structured format

You: "Execute a query to show the top 5 records from [TABLE_NAME]"
Expected: Query results with data rows
```

### 3. Card Creation

```
You: "Create a simple table card showing all records from [TABLE_NAME]"
Expected: New card created with confirmation

You: "Create a bar chart showing [METRIC] by [DIMENSION]"
Expected: New card with bar chart visualization

You: "Get the documentation for line charts"
Expected: Comprehensive chart documentation with examples
```

### 4. Card with Parameters

```
You: "Create a card with a category parameter for status filtering"
Expected: Card created with interactive parameter

You: "Get the documentation for card parameters"
Expected: Complete parameter system documentation
```

### 5. Dashboard Operations

```
You: "Create a new dashboard called 'Sales Overview'"
Expected: New dashboard created

You: "Add the card [CARD_ID] to dashboard [DASHBOARD_ID]"
Expected: Card added to dashboard with positioning

You: "Add date range and category filters to the dashboard"
Expected: Dashboard updated with interactive parameters
```

### 6. Search and Discovery

```
You: "Search for all cards containing 'revenue'"
Expected: List of relevant cards

You: "Show me the contents of the 'Analytics' collection"
Expected: Collection contents with organized items

You: "Explore the collection hierarchy starting from root"
Expected: Collection tree structure
```

### 7. Visualization Settings

```
You: "Get documentation for pie chart settings"
Expected: Pie chart configuration options and examples

You: "Create a gauge chart with custom color segments"
Expected: Card with configured gauge visualization

You: "Update card [ID] to use a combo chart with custom colors"
Expected: Card updated with new visualization settings
```

## 🎯 Advanced Feature Verification

### Organization Context Guidelines

```
You: "Get the Metabase guidelines for our organization"
Expected: Custom guidelines if configured, or setup instructions

# If you haven't set up custom guidelines:
You: "How do I set up custom organizational guidelines?"
Expected: Step-by-step setup instructions
```

### Parameter Systems

```
You: "Get documentation for dashboard parameters"
Expected: Complete dashboard parameter documentation

You: "Create a dashboard with multi-select category filters"
Expected: Dashboard with properly configured multi-select parameters

You: "Link dashboard parameters to card parameters"
Expected: Parameter mappings created successfully
```

### MBQL Query Support

```
You: "Get the MBQL schema documentation"
Expected: Complete MBQL documentation and examples

You: "Create a card using MBQL instead of SQL"
Expected: Card created with MBQL query
```

## 🔍 Error Handling Verification

### Connection Issues

```
# Test with invalid credentials (temporarily)
You: "List databases"
Expected: Clear error message about authentication failure

# Test with invalid URL
Expected: Clear error message about connection failure
```

### Parameter Validation

```
You: "Create a card with invalid parameter configuration"
Expected: Validation error with specific guidance

You: "Create a dashboard parameter with unsupported multi-select"
Expected: Clear error about multi-select compatibility
```

### Response Size Limits

```
# Query a large table without limits
You: "SELECT * FROM [LARGE_TABLE]"
Expected: Response size warning or truncation notice
```

## 📋 Verification Checklist

### Basic Functionality
- [ ] Claude Desktop integration works
- [ ] Authentication with Metabase succeeds
- [ ] Database listing works
- [ ] Query execution returns results
- [ ] Error messages are clear and helpful

### Card Operations
- [ ] Card creation works with different chart types
- [ ] Card parameters can be configured
- [ ] Visualization settings apply correctly
- [ ] Card updates modify existing cards
- [ ] Card execution returns data

### Dashboard Operations
- [ ] Dashboard creation works
- [ ] Cards can be added to dashboards
- [ ] Dashboard parameters work correctly
- [ ] Multi-tab dashboards function properly
- [ ] Parameter mappings connect dashboard to cards

### Advanced Features
- [ ] Search functionality returns relevant results
- [ ] Collection navigation works properly
- [ ] Organization guidelines load correctly
- [ ] MBQL queries execute successfully
- [ ] Documentation tools provide helpful information

### Cross-Platform Verification
- [ ] macOS executable works correctly
- [ ] Linux executable works correctly  
- [ ] Windows executable works correctly
- [ ] Source installation works on all platforms

## 🐛 Common Issues and Solutions

### Authentication Problems

**Issue**: "Authentication failed"
**Solution**: 
- Verify Metabase URL is accessible
- Check username and password
- Ensure Metabase allows API access
- Try logging in through web interface

### Connection Issues

**Issue**: "Cannot connect to Metabase"
**Solution**:
- Check network connectivity
- Verify firewall settings
- Test URL in browser
- Check for proxy settings

### Parameter Validation Errors

**Issue**: "Invalid parameter configuration"
**Solution**:
- Review parameter documentation
- Check field references against database
- Verify parameter types are supported
- Use provided examples as templates

### Visualization Settings Issues

**Issue**: "Invalid visualization settings"
**Solution**:
- Get documentation for specific chart type
- Check field references in settings
- Verify color formats and values
- Use schema validation examples

## 📞 Getting Help

### Built-in Documentation

Use these commands for contextual help:
- `GET_VISUALIZATION_DOCUMENT` - Chart type documentation
- `GET_CARD_PARAMETERS_DOCUMENTATION` - Parameter system guide
- `GET_DASHBOARD_PARAMETERS_DOCUMENTATION` - Dashboard filter help
- `GET_METABASE_GUIDELINES` - Organization-specific guidance

### Debugging Information

Enable debug logging for detailed output:

```json
{
  "env": {
    "LOG_LEVEL": "DEBUG"
  }
}
```

### Manual API Verification

Use curl to test Metabase API directly:

```bash
# Test authentication
curl -X POST "https://your-metabase.com/api/session" \
  -H "Content-Type: application/json" \
  -d '{"username":"your-username","password":"your-password"}'

# Test database listing
curl -X GET "https://your-metabase.com/api/database" \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN"
```

## 💡 Best Practices for Verification

### Systematic Approach
1. Start with basic connectivity
2. Verify core functionality
3. Check advanced features
4. Validate error handling
5. Confirm cross-platform compatibility

### Documentation
- Keep notes of what works and what doesn't
- Document any configuration changes needed
- Record error messages for reference
- Note performance characteristics

### Security
- Use dedicated credentials for verification
- Don't commit credentials to version control
- Test with minimal required permissions
- Verify access controls are respected

---

This verification guide ensures the Talk to Metabase MCP server works correctly across all supported features and platforms through systematic manual verification.
