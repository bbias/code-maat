# Code Maat MCP Server

A Model Context Protocol (MCP) server that exposes [Code Maat](https://github.com/adamtornhill/code-maat)'s powerful VCS analysis capabilities to Large Language Models like Claude.

## Overview

Code Maat is a command-line tool for mining and analyzing data from version control systems. This MCP server makes Code Maat's analyses accessible through the standardized MCP protocol, enabling LLMs to analyze code evolution, detect coupling patterns, and understand development trends.

## Features

### Analysis Tools
- **Logical Coupling**: Find modules that tend to change together
- **Summary Statistics**: Get repository overview metrics  
- **Author Analysis**: Analyze developer contribution patterns
- **Code Churn**: Track change frequency and patterns
- **Code Age**: Measure stability and maintenance needs
- **Entity Effort**: Understand developer effort distribution
- **Communication**: Analyze team collaboration patterns

### Utility Tools
- **Git Log Generation**: Create properly formatted log files
- **Log Validation**: Verify log file compatibility
- **Analysis Information**: Get detailed descriptions of analyses
- **Status Checking**: Verify Code Maat configuration

## Prerequisites

1. **Java 8+**: Required to run Code Maat
2. **Code Maat JAR**: The standalone JAR file (built from main project)
3. **Python 3.8+**: For the MCP server
4. **Git Repository**: To analyze (for git-based analyses)

## Installation

1. **Build Code Maat** (if not already done):
   ```bash
   cd .. # Go to main code-maat directory
   lein uberjar
   ```

2. **Install Python dependencies**:
   ```bash
   cd mcp-server
   pip install -r requirements.txt
   # Or install in development mode
   pip install -e .
   ```

3. **Verify installation**:
   ```bash
   python3 verify_fastmcp.py
   ```

4. **Configure the server** (optional):
   Edit `mcp_config.json` to point to your Code Maat JAR:
   ```json
   {
     "code_maat": {
       "jar_path": "../target/code-maat-1.0.5-SNAPSHOT-standalone.jar",
       "java_executable": "java",
       "java_opts": ["-Xmx4g", "-Djava.awt.headless=true", "-Xss512M"]
     }
   }
   ```

## Usage

### Running the Server

```bash
# From the mcp-server directory
python3 -m src.mcp_server
```

### Using with Claude Desktop

Add to your Claude Desktop MCP configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "code-maat": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/Users/your-username/path/to/code-maat/mcp-server",
      "env": {
        "PYTHONPATH": "/Users/your-username/path/to/code-maat/mcp-server"
      }
    }
  }
}
```

**Note**: Replace `/Users/your-username/path/to/code-maat/mcp-server` with your actual path.

### Quick Start Example

1. **Generate a git log** (for git repositories):
   ```python
   generate_git_log(
       repo_path="/path/to/your/repo",
       format_type="git2",
       after_date="2023-01-01"
   )
   ```

2. **Get repository overview**:
   ```python
   run_summary_analysis(
       log_file="logfile.log",
       vcs="git2"
   )
   ```

3. **Find coupled modules**:
   ```python
   run_coupling_analysis(
       log_file="logfile.log", 
       vcs="git2",
       min_coupling=50
   )
   ```

## Available Analyses

| Analysis | Description | Use Case |
|----------|-------------|----------|
| `coupling` | Logical coupling between modules | Find hidden dependencies |
| `summary` | Repository overview statistics | Understand codebase metrics |
| `authors` | Developer contribution patterns | Identify communication overhead |
| `entity-churn` | Code change frequency by module | Find unstable areas |
| `author-churn` | Code changes by developer | Understand individual contributions |
| `age` | Time since last module change | Assess code stability |
| `entity-effort` | Developer effort per module | Understand collaboration patterns |
| `communication` | Team collaboration analysis | Optimize team structure |

## Supported VCS Systems

- **Git** (recommended: use `git2` format)
- **Subversion (SVN)**
- **Mercurial (Hg)**
- **Perforce (P4)**
- **Team Foundation Server (TFS)**

## Configuration

### Memory Settings

Code Maat analyses can be memory-intensive. Default settings:
- Heap size: 4GB (`-Xmx4g`)
- Stack size: 512MB (`-Xss512M`)
- Headless mode: enabled

### Log File Formats

**Git2 Format** (recommended):
```bash
git log --all --numstat --date=short --pretty=format:'--%h--%ad--%aN' --no-renames --after=2023-01-01 > logfile.log
```

**Git Format** (legacy):
```bash
git log --pretty=format:'[%h] %aN %ad %s' --date=short --numstat --after=2023-01-01 > logfile.log
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

### Project Structure

```
mcp-server/
├── src/
│   ├── mcp_server.py          # Main FastMCP server (updated)
│   ├── code_maat_wrapper.py   # Code Maat execution wrapper
│   └── tools/
│       ├── analysis_tools.py  # Analysis MCP tools
│       └── utility_tools.py   # Utility MCP tools
├── tests/
│   ├── unit/                  # Unit tests (90% pass rate)
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test fixtures
├── mcp_config.json           # Configuration
├── verify_fastmcp.py         # Installation verification
├── test_installation.py      # Full installation test
├── start_server.py           # Alternative startup script
└── README.md                 # This file
```

## Troubleshooting

### Common Issues

1. **JAR file not found**:
   - Ensure Code Maat is built: `lein uberjar`
   - Check `jar_path` in `mcp_config.json`

2. **Java not found**:
   - Verify Java 8+ is installed
   - Check `java_executable` in config

3. **Memory errors**:
   - Increase heap size in `java_opts`
   - Filter log files by date range

4. **Log parsing errors**:
   - Use `validate_log_file()` to check format
   - Ensure log includes file statistics (`--numstat` for git)

### Diagnostic Tools

```python
# Check server status and configuration
check_code_maat_status()

# Validate log file format
validate_log_file(log_file="logfile.log", vcs="git2")

# List all available analyses
list_available_analyses(include_details=True)

# Get information about specific analysis
get_analysis_info(analysis="coupling")
```

### MCP Server Issues

5. **Server won't start**:
   - Check Claude Desktop logs for errors
   - Verify Python path in configuration
   - Run `python3 verify_fastmcp.py` to test setup
   - Ensure PYTHONPATH is set correctly

6. **Import errors**:
   - Make sure you're using the correct Python version (`/usr/local/bin/python3`)
   - Verify MCP package is installed: `python3 -c "import mcp; print('OK')"`
   - Check that working directory is set to mcp-server folder

## Performance Tips

1. **Filter by date**: Limit analysis to recent commits
2. **Exclude vendor directories**: Use git pathspecs to exclude noise
3. **Use git2 format**: Faster parsing than legacy git format
4. **Cache results**: MCP server caches analysis results
5. **Adequate memory**: Ensure sufficient heap size for large repositories

## Examples

### Analyzing a Repository

```python
# 1. Generate log file
generate_git_log(
    repo_path="/path/to/repo",
    format_type="git2", 
    after_date="2023-06-01",
    exclude_paths=["vendor/", "node_modules/"]
)

# 2. Get overview
run_summary_analysis(log_file="logfile.log", vcs="git2")

# 3. Find hotspots (high author count)
run_authors_analysis(log_file="logfile.log", vcs="git2", rows=20)

# 4. Detect coupling
run_coupling_analysis(
    log_file="logfile.log",
    vcs="git2", 
    min_coupling=60,
    max_changeset_size=20
)

# 5. Check code age
run_age_analysis(log_file="logfile.log", vcs="git2")
```

## License

This MCP server follows the same license as Code Maat: GNU General Public License v3.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Resources

- [Code Maat Documentation](https://github.com/adamtornhill/code-maat)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Your Code as a Crime Scene](https://pragprog.com/book/atcrime/your-code-as-a-crime-scene) (Book)
- [Software Design X-Rays](https://pragprog.com/book/atevol/software-design-x-rays) (Book)