# Code Maat MCP Server Changelog

## [0.2.0] - 2025-01-12

### Major Changes
- **BREAKING**: Migrated from legacy MCP Server API to FastMCP framework
- Updated to use modern `@mcp.tool()` and `@mcp.resource()` decorators
- Simplified server architecture and startup process

### Added
- FastMCP-based server implementation with automatic stdio transport
- Installation verification script (`verify_fastmcp.py`)
- Enhanced error handling and logging
- Improved Claude Desktop integration documentation
- Updated configuration examples with full Python paths and PYTHONPATH

### Fixed
- Resolved `stdio_server` AttributeError by migrating to FastMCP
- Fixed import path issues in Claude Desktop environment
- Improved Python path resolution for different execution contexts
- Updated all documentation to reflect current API

### Technical Improvements
- 11 MCP tools properly registered (7 analysis + 4 utility)
- 2 MCP resources for configuration and help
- 90% test coverage maintained
- Compatible with MCP Python SDK 1.0+

### Documentation Updates
- Updated README.md with current installation and usage instructions
- Enhanced EXAMPLES.md with FastMCP context
- Updated CLAUDE.md with MCP server integration details
- Added troubleshooting section for MCP server issues

## [0.1.0] - 2025-01-12

### Initial Release
- Initial MCP server implementation for Code Maat
- 7 analysis tools covering all major Code Maat analyses
- 4 utility tools for log generation and validation
- Comprehensive test suite with unit and integration tests
- Complete documentation and examples
- Claude Desktop integration support

### Analysis Tools
- Logical coupling analysis
- Summary statistics
- Author contribution analysis
- Code churn patterns
- Code age metrics
- Entity effort distribution
- Communication patterns

### Utility Tools
- Git log generation with multiple formats
- Log file validation
- Analysis information and help
- Server status checking