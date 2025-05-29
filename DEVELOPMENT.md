# Talk to Metabase Development Guide

This document outlines the development process and next steps for the Talk to Metabase MCP server project.

## Project Structure

The project is organized as follows:

```
Talk to Metabase/
├── LICENSE
├── .gitignore
├── .git/
├── pyproject.toml      # Project configuration and dependencies
├── README.md           # Project documentation
├── TESTING.md          # Testing instructions
├── .env.example        # Example environment file
├── metabase_mcp.py     # CLI entry point
├── install.sh          # Installation script (Unix)
├── install.bat         # Installation script (Windows)
├── test_import.py      # Basic import test
├── test_auth.py        # Authentication test
├── talk_to_metabase/      # Main package
│   ├── __init__.py     # Package initialization
│   ├── auth.py         # Metabase authentication
│   ├── client.py       # Metabase API client
│   ├── config.py       # Configuration management
│   ├── errors.py       # Error handling
│   ├── models.py       # Data models
│   ├── server.py       # MCP server implementation
│   └── tools/          # MCP tools for Metabase operations
│       ├── __init__.py # Tools registration
│       ├── common.py   # Shared utilities
│       ├── dashboard.py # Dashboard operations
│       ├── card.py     # Card operations
│       ├── collection.py # Collection operations
│       ├── database.py # Database operations
│       └── search.py   # Search operations
└── tests/              # Test suite
    ├── __init__.py
    ├── conftest.py     # Test fixtures
    ├── unit/           # Unit tests
    │   ├── __init__.py
    │   ├── test_auth.py # Auth module tests
    │   ├── test_config.py # Config module tests
    │   └── test_dashboard_tools.py # Dashboard tools tests
    └── integration/    # Integration tests
        └── __init__.py
```

## Core Features Implemented

1. **Authentication System**:
   - Session-based authentication with Metabase
   - Automatic re-authentication when tokens expire
   - Error handling for authentication failures

2. **Configuration Management**:
   - Environment variable-based configuration
   - Support for .env files
   - Validation of configuration parameters

3. **MCP Server Structure**:
   - FastMCP implementation with proper lifecycle management
   - Configurable transport (stdio, SSE, Streamable HTTP)
   - Context passing for sharing state between tools

4. **API Client**:
   - Complete Metabase API client with error handling
   - Resource abstraction for consistent operations
   - Support for all CRUD operations

5. **Tool Framework**:
   - Organized by resource type (dashboard, card, collection, etc.)
   - Structured error responses for Claude to understand
   - Clean separation of concerns

6. **Error Handling**:
   - Custom error types for different scenarios
   - Detailed error responses with context
   - Consistent error formatting

7. **Data Models**:
   - Pydantic models for type safety
   - Comprehensive representation of Metabase entities
   - Validation of input/output data

8. **Testing Infrastructure**:
   - Unit test setup with pytest
   - Mocking for external dependencies
   - Fixtures for common test scenarios

9. **Response Size Limitation**:
   - Configurable maximum response size
   - Graceful handling of oversized responses
   - Clear error messages when size limits are exceeded

## Next Steps

### 1. Implement Additional Tool Functions

Implement the remaining tools specified in the requirements:

- **Dashboard operations**:
  - `update_dashboard`
  - `add_card_to_dashboard`
  - `delete_dashboard`

- **Card operations**:
  - `create_card`
  - `update_card`
  - `execute_card_query`
  - `delete_card`

- **Collection operations**:
  - `get_collection`
  - `create_collection`
  - `update_collection`
  - `get_collection_items`

- **Database operations**:
  - `get_database_metadata`
  - `get_table`
  - `get_table_query_metadata`

- **Query operations**:
  - `run_dataset_query`

### 2. Add Integration Tests

Create integration tests that test the actual integration with a Metabase instance. These tests should:

- Verify that authentication works
- Test each tool with a real Metabase instance
- Handle test data creation and cleanup

### 3. Improve Error Handling

Enhance error handling based on real-world usage:

- Add more specific error types
- Improve error messages for Claude
- Add retry logic for transient errors

### 4. Add Caching

Implement caching for frequently accessed resources:

- Add a caching layer for API responses
- Implement cache invalidation strategies
- Configure cache timeouts based on resource types

### 5. Add Logging and Monitoring

Improve logging and add monitoring capabilities:

- Add structured logging
- Implement performance metrics
- Create health check endpoints

### 6. Security Enhancements

Improve security:

- Add support for environment variable encryption
- Implement secure token storage
- Add input validation for all tool parameters

### 7. Documentation

Improve documentation:

- Create API documentation
- Write user guides
- Add examples and tutorials

## Development Workflow

1. **Feature Development**:
   - Create a new branch for each feature
   - Write tests before implementing features
   - Ensure code follows project style and conventions

2. **Testing**:
   - Run unit tests with `pytest tests/unit`
   - Test authentication with `python test_auth.py`
   - Test with the MCP Inspector using `mcp dev metabase_mcp.py`
   - Run integration tests with a real Metabase instance

3. **Documentation**:
   - Update README.md with new features
   - Document new tools and their parameters
   - Add examples to the documentation

4. **Code Review**:
   - Review code changes
   - Ensure tests pass
   - Check for security issues
   - Verify documentation is up to date

## Conclusion

The Talk to Metabase MCP server provides a solid foundation for integrating Claude with Metabase. By implementing the remaining tools and features, you'll create a powerful tool that enables Claude to interact with Metabase data, providing users with AI-powered data analysis and visualization capabilities.
