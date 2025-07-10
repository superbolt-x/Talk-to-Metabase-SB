# Development Guide

A comprehensive guide for developers working on the Talk to Metabase MCP server project.

## 🏗️ Project Overview

Talk to Metabase is a sophisticated MCP (Model Context Protocol) server that bridges Claude with Metabase, enabling AI-powered data analysis and visualization. The server follows the MCP specification to expose Metabase functionality as tools that Claude can use.

## 📁 Project Structure

```
Talk to Metabase/
├── talk_to_metabase/           # Main package
│   ├── __init__.py             # Package initialization
│   ├── auth.py                 # Metabase authentication
│   ├── client.py               # Metabase API client
│   ├── config.py               # Configuration management
│   ├── errors.py               # Error handling
│   ├── models.py               # Data models
│   ├── resources.py            # Resource loading utilities
│   ├── server.py               # MCP server implementation
│   ├── schemas/                # JSON schemas and documentation
│   │   ├── *.json              # Validation schemas
│   │   └── *_docs.md           # Documentation files
│   └── tools/                  # MCP tools implementation
│       ├── __init__.py         # Tools registration
│       ├── common.py           # Shared utilities
│       ├── card.py             # Card/question operations
│       ├── card_parameters/    # Advanced parameter system
│       ├── collection.py       # Collection operations
│       ├── context.py          # Context guidelines
│       ├── dashboard.py        # Dashboard operations
│       ├── dashboard_parameters.py # Dashboard filters
│       ├── dashcards.py        # Dashboard card management
│       ├── database.py         # Database operations
│       ├── dataset.py          # Query execution
│       ├── mbql.py             # MBQL support
│       ├── parameters/         # Parameter utilities
│       ├── search.py           # Search operations
│       └── visualization.py    # Chart settings
├── docs/                       # Additional documentation
├── scripts-backup/             # Utility scripts
├── build*/                     # Build artifacts
├── dist/                       # Distribution packages
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
├── metabase_mcp.py            # CLI entry point
└── *.md                       # Documentation files
```

## 🔧 Core Components

### 1. Authentication System (`auth.py`)

Handles session-based authentication with Metabase:

```python
class MetabaseAuth:
    def __init__(self, base_url: str, username: str, password: str)
    async def authenticate(self) -> str  # Returns session token
    async def refresh_token(self) -> str  # Re-authenticates when needed
    async def get_current_user(self) -> dict  # Gets user info
```

**Key Features:**
- Automatic session management
- Token refresh on expiry
- Secure credential handling
- Error recovery

### 2. API Client (`client.py`)

Comprehensive Metabase API client:

```python
class MetabaseClient:
    def __init__(self, auth: MetabaseAuth)
    async def get(self, endpoint: str, params: dict = None) -> dict
    async def post(self, endpoint: str, data: dict = None) -> dict
    async def put(self, endpoint: str, data: dict = None) -> dict
    async def delete(self, endpoint: str) -> dict
```

**Key Features:**
- Async HTTP operations
- Automatic authentication
- Error handling and retries
- Request/response logging

### 3. Configuration Management (`config.py`)

Environment-based configuration:

```python
class Config:
    metabase_url: str
    metabase_username: str
    metabase_password: str
    response_size_limit: int = 100000
    log_level: str = "INFO"
    mcp_transport: str = "stdio"
```

**Key Features:**
- Environment variable support
- `.env` file integration
- Validation and defaults
- Type safety with Pydantic

### 4. Data Models (`models.py`)

Pydantic models for type safety:

```python
class Database(BaseModel):
    id: int
    name: str
    engine: str
    
class Card(BaseModel):
    id: int
    name: str
    display: str
    dataset_query: dict
    visualization_settings: dict
```

**Key Features:**
- Type validation
- Serialization/deserialization
- Documentation generation
- IDE support

### 5. MCP Server (`server.py`)

Main server implementation:

```python
async def main():
    # Initialize configuration
    config = Config()
    
    # Setup authentication
    auth = MetabaseAuth(config.metabase_url, config.metabase_username, config.metabase_password)
    
    # Create client
    client = MetabaseClient(auth)
    
    # Initialize MCP server
    server = mcp.Server("talk-to-metabase")
    
    # Register tools
    register_tools(server, client)
    
    # Run server
    await server.run()
```

## 🛠️ Tools Architecture

### Tool Categories

#### Database Tools (`database.py`)
- `list_databases` - List available databases
- `get_database_metadata` - Get schema information
- `get_table_query_metadata` - Get field details for queries

#### Card Tools (`card.py`)
- `get_card_definition` - Get card metadata with MBQL→SQL translation
- `create_card` - Create new cards with validation
- `update_card` - Update existing cards
- `execute_card_query` - Execute card queries

#### Dashboard Tools (`dashboard.py`)
- `get_dashboard` - Get dashboard structure
- `create_dashboard` - Create new dashboards
- `update_dashboard` - Update dashboard with cards and parameters
- `get_dashboard_tab` - Get tab contents

#### Search Tools (`search.py`)
- `search_resources` - Search across all Metabase resources

#### Query Tools (`dataset.py`)
- `run_dataset_query` - Execute SQL/MBQL queries directly

### Tool Implementation Pattern

```python
@mcp.tool(name="tool_name")
async def tool_function(
    param1: int,
    param2: str,
    ctx: Context,
    optional_param: Optional[str] = None
) -> str:
    """
    Tool description for Claude.
    
    Args:
        param1: Description of parameter
        param2: Description of parameter
        ctx: MCP context (automatically provided)
        optional_param: Optional parameter description
    
    Returns:
        JSON string with results or error information
    """
    try:
        # Get client from context
        client = ctx.get_client()
        
        # Perform operation
        result = await client.get(f"/api/endpoint/{param1}")
        
        # Return structured response
        return json.dumps({
            "success": True,
            "data": result,
            "message": "Operation completed successfully"
        })
        
    except Exception as e:
        # Return error response
        return json.dumps({
            "success": False,
            "error": str(e),
            "help": "Suggestion for fixing the issue"
        })
```

## 🎯 Advanced Features

### 1. Parameter System (`card_parameters/`)

Comprehensive parameter support for interactive cards:

```python
# Parameter types supported
PARAMETER_TYPES = {
    # Simple variables
    "category": "text",
    "number/=": "number", 
    "date/single": "date",
    
    # Field filters
    "string/=": "field_filter",
    "number/between": "field_filter",
    "date/range": "field_filter",
    # ... more types
}

# Processing pipeline
async def process_card_parameters(
    client: MetabaseClient,
    parameters: List[Dict[str, Any]]
) -> Tuple[List[Dict], Dict, List[str]]:
    """
    Process card parameters with validation.
    
    Returns:
        - Processed parameters for API
        - Template tags for SQL
        - Validation errors
    """
```

**Key Features:**
- JSON Schema validation
- Field reference validation
- UI widget compatibility
- Automatic UUID generation
- Template tag creation

### 2. Dashboard Parameters (`dashboard_parameters.py`)

Multi-select dashboard filters:

```python
# Multi-select support matrix
MULTI_SELECT_SUPPORTED = {
    "string/=", "string/!=", "string/contains",
    "number/=", "number/!=", "id"
}

# Default multi-select behavior
def get_default_multi_select(param_type: str) -> bool:
    return param_type in MULTI_SELECT_SUPPORTED
```

**Key Features:**
- 18 parameter types
- Automatic multi-select defaults
- Value source management
- Location parameter support

### 3. Visualization Settings (`visualization.py`)

17 chart types with comprehensive customization:

```python
# Chart type mappings
UI_TO_API_MAPPING = {
    "detail": "object",
    "number": "scalar", 
    "trend": "smartscalar"
}

# Validation function
def validate_visualization_settings(
    chart_type: str, 
    settings: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """Validate settings against JSON schema."""
```

**Key Features:**
- JSON Schema validation
- UI/API name mapping
- Complete documentation
- Error handling

### 4. MBQL Support (`mbql.py`)

Database-agnostic query language:

```python
# MBQL query structure
{
    "source-table": 1,
    "aggregation": [["sum", ["field", 123, null]]],
    "breakout": [["field", 456, {"temporal-unit": "month"}]],
    "filter": ["=", ["field", 789, null], "active"]
}
```

**Key Features:**
- Complete MBQL schema
- Validation without execution
- Cross-database compatibility
- Structured query building

## 🔬 Development Workflow

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/vincentgefflaut/talk-to-metabase.git
cd talk-to-metabase

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running the Server for Development

When developing and testing with Claude Desktop, you should run the server from source rather than using prebuilt executables. This allows you to:

- See real-time code changes without rebuilding
- Access debug output and logging
- Use debugging tools and breakpoints
- Modify code and test immediately

#### Configure Claude Desktop for Development

Update your Claude Desktop configuration to use the development environment:

```json
{
  "mcpServers": {
    "Talk to Metabase Dev": {
      "command": "/absolute/path/to/talk-to-metabase/venv/bin/python",
      "args": ["/absolute/path/to/talk-to-metabase/metabase_mcp.py"],
      "env": {
        "METABASE_URL": "https://your-metabase-instance.company.com",
        "METABASE_USERNAME": "your-username@example.com",
        "METABASE_PASSWORD": "your-password",
        "RESPONSE_SIZE_LIMIT": "100000",
        "METABASE_CONTEXT_AUTO_INJECT": "true",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**Important Notes:**
- Use **absolute paths** for both the Python executable and the script
- Use the Python executable from your virtual environment (`venv/bin/python`)
- Set `LOG_LEVEL` to `DEBUG` for detailed development output
- Restart Claude Desktop after configuration changes

#### Development Workflow

1. **Make code changes** in your editor
2. **Save the files** (no restart needed for most changes)
3. **Test in Claude Desktop** - the server will use the updated code
4. **Check logs** for debug information and errors
5. **Iterate** - repeat the process for development

This approach gives you the fastest development cycle and full visibility into the server's operation during development.

### Code Quality Tools

```bash
# Format code
black talk_to_metabase/
isort talk_to_metabase/

# Lint code
ruff talk_to_metabase/

# Type checking
mypy talk_to_metabase/
```

### Adding New Tools

1. **Create tool function** in appropriate module:
```python
@mcp.tool(name="new_tool")
async def new_tool_function(param: str, ctx: Context) -> str:
    """Tool description."""
    # Implementation
```

2. **Add to tool registry** in `tools/__init__.py`:
```python
from .module import new_tool_function
# Register in tool list
```

3. **Update documentation** as needed

### Adding New Parameter Types

1. **Update schema** in `schemas/card_parameters.json`:
```json
{
  "enum": ["existing_types", "new_type"]
}
```

2. **Add validation logic** in `card_parameters/core.py`:
```python
def validate_new_type(param_config: Dict) -> List[str]:
    # Validation logic
```

3. **Update documentation** in `schemas/card_parameters_docs.md`

### Adding New Chart Types

1. **Create schema** in `schemas/new_chart_visualization.json`
2. **Create documentation** in `schemas/new_chart_visualization_docs.md`
3. **Update chart type mappings** in `visualization.py`
4. **Add validation support**

## 📊 Performance Considerations

### Response Size Management

```python
# Check response size
def check_response_size(data: str, limit: int = 100000) -> bool:
    return len(data) <= limit

# Truncate large responses
def truncate_response(data: dict, limit: int) -> dict:
    # Implementation to reduce response size
```

### Async Operations

```python
# Use async/await for I/O operations
async def fetch_multiple_resources(ids: List[int]) -> List[dict]:
    tasks = [client.get(f"/api/resource/{id}") for id in ids]
    return await asyncio.gather(*tasks)
```

### Caching Strategy

```python
# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def get_database_schema(database_id: int) -> dict:
    # Expensive operation
```

## 🔐 Security Considerations

### Credential Management

```python
# Use environment variables
import os
from pydantic import SecretStr

class Config:
    metabase_password: SecretStr = os.getenv("METABASE_PASSWORD")
    
    def get_password(self) -> str:
        return self.metabase_password.get_secret_value()
```

### Input Validation

```python
# Validate all inputs
def validate_database_id(db_id: int) -> None:
    if not isinstance(db_id, int) or db_id <= 0:
        raise ValueError("Database ID must be positive integer")
```

### Error Handling

```python
# Don't expose sensitive information
try:
    result = await client.get("/api/sensitive")
except Exception as e:
    # Log the full error
    logger.error(f"API call failed: {e}")
    # Return generic error to user
    return {"error": "Operation failed"}
```

## 🚀 Build and Deployment

### Building Executables

```bash
# Install PyInstaller
pip install pyinstaller

# Build for current platform
pyinstaller talk-to-metabase.spec

# Build for specific platform
pyinstaller talk-to-metabase-macos-apple-silicon.spec
```

### Creating Releases

```bash
# Tag version
git tag v1.0.0
git push origin v1.0.0

# Build distributions
python -m build

# Upload to PyPI
twine upload dist/*
```

### Docker Build

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY talk_to_metabase/ talk_to_metabase/
COPY metabase_mcp.py .

CMD ["python", "metabase_mcp.py"]
```

## 📝 Documentation Standards

### Code Documentation

```python
def complex_function(param1: str, param2: int) -> dict:
    """
    Brief description of function.
    
    Longer description explaining the purpose and behavior.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
    
    Returns:
        Dictionary containing the result with keys:
        - success: Boolean indicating success
        - data: The actual result data
        - message: Human-readable message
    
    Raises:
        ValueError: When parameters are invalid
        ConnectionError: When Metabase is unreachable
    
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result["success"])
        True
    """
```

### Tool Documentation

```python
@mcp.tool(name="tool_name")
async def tool_function(param: str, ctx: Context) -> str:
    """
    One-line description for Claude.
    
    Longer description explaining what the tool does,
    when to use it, and any important considerations.
    
    Args:
        param: Description of parameter with examples
        ctx: MCP context (automatically provided)
    
    Returns:
        JSON string with structured response
    """
```

### Schema Documentation

Include comprehensive examples in schema files:

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Parameter name used in SQL queries",
      "example": "order_status"
    }
  },
  "examples": [
    {
      "name": "category_filter",
      "type": "string/=",
      "default": "electronics"
    }
  ]
}
```

## 🤝 Contributing Guidelines

### Code Style

- Follow PEP 8 style guide
- Use type hints for all functions
- Write comprehensive docstrings
- Keep functions focused and small
- Use meaningful variable names

### Commit Messages

```
feat: add new visualization type support
fix: resolve parameter validation issue
docs: update installation instructions
refactor: simplify error handling logic
```

### Pull Request Process

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes** with documentation
4. **Run quality checks**: `black`, `isort`, `ruff`
5. **Commit changes**: Follow commit message format
6. **Push to fork**: `git push origin feature/new-feature`
7. **Create pull request** with description

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Breaking changes are documented
- [ ] Security considerations are addressed

## 🔍 Debugging

### Logging Configuration

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Common Issues

**Authentication failures:**
- Check credentials
- Verify Metabase URL
- Verify with curl/postman

**Parameter validation errors:**
- Review JSON schema
- Check field references
- Validate against examples

**Performance issues:**
- Check response sizes
- Review query complexity
- Monitor database load

### Development Tools

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python metabase_mcp.py

# Use MCP inspector
mcp dev metabase_mcp.py

# Profile performance
python -m cProfile metabase_mcp.py
```

## 📋 Roadmap

### Short-term Goals
- [ ] Add model support
- [ ] Implement safe mode
- [ ] Add more chart types
- [ ] Improve error messages

### Medium-term Goals
- [ ] Add caching layer
- [ ] Implement query optimization
- [ ] Add more parameter types
- [ ] Improve performance

### Long-term Goals
- [ ] Multi-instance support
- [ ] Plugin architecture
- [ ] Advanced analytics
- [ ] Machine learning integration

---

This development guide provides a comprehensive overview of the Talk to Metabase project architecture and development practices. For specific implementation details, refer to the code comments and inline documentation.
