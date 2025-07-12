# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code Maat is a command-line tool written in Clojure for mining and analyzing version control system (VCS) data. It performs various analyses on git, Mercurial, SVN, Perforce, and TFS logs to identify patterns like logical coupling, code churn, organizational metrics, and temporal dependencies.

## Build and Development Commands

### Building the project
```bash
# Build standalone JAR
lein uberjar

# Run directly via leiningen  
lein run -l logfile.log -c <vcs>

# Build Docker image
docker build -t code-maat-app .
```

### Running tests
```bash
# Run all tests
lein test

# Run specific test namespace
lein test code-maat.analysis.authors-test
```

### Development workflow
```bash
# Start REPL for interactive development
lein repl

# Check dependencies
lein deps

# Clean build artifacts
lein clean
```

## Architecture

### Core Structure
- **Entry point**: `src/code_maat/cmd_line.clj` - Command line interface and main entry
- **Parsers**: `src/code_maat/parsers/` - VCS log parsers for different systems (git, svn, hg, p4, tfs)
- **Analysis**: `src/code_maat/analysis/` - Core analysis algorithms for coupling, churn, authors, etc.
- **Output**: `src/code_maat/output/` - CSV formatting and filtering
- **Application**: `src/code_maat/app/` - Application logic, grouping, and team mapping

### Key Analysis Types
- **Logical coupling**: Modules that change together (coupling_algos.clj)
- **Code churn**: Change frequency metrics (churn.clj) 
- **Author patterns**: Developer contributions and ownership (authors.clj)
- **Entity metrics**: Module-level statistics (entities.clj)
- **Communication patterns**: Team interaction analysis (communication.clj)

### VCS Parser Support
Each parser in `/parsers/` handles different VCS log formats:
- `git.clj` - Legacy git format
- `git2.clj` - Improved git format (preferred)
- `svn.clj`, `mercurial.clj`, `perforce.clj`, `tfs.clj` - Other VCS systems

### Memory Configuration
The project requires significant memory for large datasets:
- JVM heap: `-Xmx4g` (configured in project.clj)
- Stack size: `-Xss512M`
- Headless mode: `-Djava.awt.headless=true`

## Testing Strategy
- Unit tests located in `test/` directory mirroring `src/` structure
- End-to-end tests in `test/code_maat/end_to_end/` with sample log files
- Data-driven tests using sample VCS logs for different scenarios

## Development Notes
- Uses Leiningen for dependency management and build automation
- Clojure 1.8.0 with Incanter for data analysis
- Output format is CSV for compatibility with visualization tools
- Supports architectural-level analysis via regex-based grouping files

## MCP Server Integration

### MCP Server for Claude Desktop
This repository includes a Model Context Protocol (MCP) server in `mcp-server/` that exposes Code Maat's analysis capabilities to LLMs like Claude:

```bash
# Build Code Maat JAR first
lein uberjar

# Set up MCP server
cd mcp-server
pip install -r requirements.txt
python3 verify_fastmcp.py
```

### MCP Server Commands
The MCP server provides 11 tools for VCS analysis:

**Analysis Tools** (7):
- `run_coupling_analysis` - Logical coupling between modules
- `run_summary_analysis` - Repository overview statistics  
- `run_authors_analysis` - Developer contribution patterns
- `run_churn_analysis` - Code change frequency analysis
- `run_age_analysis` - Code stability metrics
- `run_entity_effort_analysis` - Developer effort per module
- `run_communication_analysis` - Team collaboration patterns

**Utility Tools** (4):
- `generate_git_log` - Create properly formatted git logs
- `validate_log_file` - Check log file compatibility
- `check_code_maat_status` - Verify server configuration
- `list_available_analyses` - Show all available analyses

### Claude Desktop Configuration
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-maat": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/path/to/code-maat/mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/code-maat/mcp-server"
      }
    }
  }
}
```

### MCP Server Architecture
- **FastMCP Framework**: Uses modern MCP Python SDK with decorators
- **Analysis Wrapper**: Python wrapper around Code Maat JAR execution
- **Error Handling**: Comprehensive validation and error reporting
- **Testing**: 90% test coverage with unit and integration tests