"""
Model Context Protocol server for Code Maat VCS analysis tool.
"""

import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from .tools.analysis_tools import AnalysisTools
from .tools.utility_tools import UtilityTools


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create the FastMCP server
mcp = FastMCP("code-maat-mcp-server")

# Initialize analysis and utility tools
analysis_tools = AnalysisTools()
utility_tools = UtilityTools()

# Add all analysis tools
@mcp.tool()
async def run_coupling_analysis(
    log_file: str,
    vcs: str,
    min_coupling: int = 30,
    max_coupling: int = 100,
    min_revs: int = 5,
    max_changeset_size: int = 30
) -> str:
    """Analyze logical coupling between modules that tend to change together."""
    arguments = {
        "log_file": log_file,
        "vcs": vcs,
        "min_coupling": min_coupling,
        "max_coupling": max_coupling,
        "min_revs": min_revs,
        "max_changeset_size": max_changeset_size
    }
    result = await analysis_tools.run_coupling_analysis(arguments)
    return result[0].text

@mcp.tool()
async def run_summary_analysis(log_file: str, vcs: str) -> str:
    """Generate overview statistics of the repository."""
    arguments = {"log_file": log_file, "vcs": vcs}
    result = await analysis_tools.run_summary_analysis(arguments)
    return result[0].text

@mcp.tool()
async def run_authors_analysis(log_file: str, vcs: str, min_revs: int = 5, rows: int = None) -> str:
    """Analyze developer contribution metrics per module."""
    arguments = {"log_file": log_file, "vcs": vcs, "min_revs": min_revs}
    if rows:
        arguments["rows"] = rows
    result = await analysis_tools.run_authors_analysis(arguments)
    return result[0].text

@mcp.tool()
async def run_churn_analysis(
    log_file: str, 
    vcs: str, 
    churn_type: str = "entity-churn",
    min_revs: int = 5,
    rows: int = None
) -> str:
    """Analyze code churn patterns (entity-churn, author-churn, or abs-churn)."""
    arguments = {
        "log_file": log_file,
        "vcs": vcs,
        "churn_type": churn_type,
        "min_revs": min_revs
    }
    if rows:
        arguments["rows"] = rows
    result = await analysis_tools.run_churn_analysis(arguments)
    return result[0].text

@mcp.tool()
async def run_age_analysis(log_file: str, vcs: str, age_time_now: str = None, rows: int = None) -> str:
    """Analyze code age and stability metrics."""
    arguments = {"log_file": log_file, "vcs": vcs}
    if age_time_now:
        arguments["age_time_now"] = age_time_now
    if rows:
        arguments["rows"] = rows
    result = await analysis_tools.run_age_analysis(arguments)
    return result[0].text

@mcp.tool()
async def run_entity_effort_analysis(log_file: str, vcs: str, min_revs: int = 5, rows: int = None) -> str:
    """Analyze effort distribution among developers per entity."""
    arguments = {"log_file": log_file, "vcs": vcs, "min_revs": min_revs}
    if rows:
        arguments["rows"] = rows
    result = await analysis_tools.run_entity_effort_analysis(arguments)
    return result[0].text

@mcp.tool()
async def run_communication_analysis(log_file: str, vcs: str, min_shared_revs: int = 5, rows: int = None) -> str:
    """Analyze communication patterns between developers."""
    arguments = {"log_file": log_file, "vcs": vcs, "min_shared_revs": min_shared_revs}
    if rows:
        arguments["rows"] = rows
    result = await analysis_tools.run_communication_analysis(arguments)
    return result[0].text

# Add utility tools
@mcp.tool()
async def generate_git_log(
    repo_path: str,
    output_file: str = None,
    format_type: str = "git2",
    after_date: str = None,
    exclude_paths: list[str] = None
) -> str:
    """Generate a git log file suitable for Code Maat analysis."""
    arguments = {
        "repo_path": repo_path,
        "format_type": format_type
    }
    if output_file:
        arguments["output_file"] = output_file
    if after_date:
        arguments["after_date"] = after_date
    if exclude_paths:
        arguments["exclude_paths"] = exclude_paths
    result = await utility_tools.generate_git_log(arguments)
    return result[0].text

@mcp.tool()
async def list_available_analyses(include_details: bool = True) -> str:
    """List all available Code Maat analysis types with descriptions."""
    arguments = {"include_details": include_details}
    result = await utility_tools.list_available_analyses(arguments)
    return result[0].text

@mcp.tool()
async def validate_log_file(log_file: str, vcs: str) -> str:
    """Validate if a log file is suitable for Code Maat analysis."""
    arguments = {"log_file": log_file, "vcs": vcs}
    result = await utility_tools.validate_log_file(arguments)
    return result[0].text

@mcp.tool()
async def get_analysis_info(analysis: str) -> str:
    """Get detailed information about a specific analysis type."""
    arguments = {"analysis": analysis}
    result = await utility_tools.get_analysis_info(arguments)
    return result[0].text

@mcp.tool()
async def check_code_maat_status() -> str:
    """Check if Code Maat is properly configured and accessible."""
    arguments = {}
    result = await utility_tools.check_code_maat_status(arguments)
    return result[0].text

# Add resources
@mcp.resource("code-maat://config")
async def get_config() -> str:
    """Get the current Code Maat server configuration."""
    config_info = {
        "server_name": "code-maat-mcp-server",
        "version": "0.1.0",
        "code_maat_jar": analysis_tools.wrapper.config.jar_path,
        "java_executable": analysis_tools.wrapper.config.java_executable,
        "java_opts": analysis_tools.wrapper.config.java_opts,
        "supported_vcs": list(analysis_tools.wrapper.SUPPORTED_VCS),
        "supported_analyses": list(analysis_tools.wrapper.SUPPORTED_ANALYSES)
    }
    return json.dumps(config_info, indent=2)

@mcp.resource("code-maat://help")
async def get_help() -> str:
    """Get the getting started guide."""
    return """# Code Maat MCP Server

This server provides Code Maat VCS analysis capabilities through MCP.

## Quick Start
1. Generate git log: `generate_git_log(repo_path="/path/to/repo")`
2. Run summary: `run_summary_analysis(log_file="logfile.log", vcs="git2")`
3. Find coupling: `run_coupling_analysis(log_file="logfile.log", vcs="git2")`

## Available Tools
- Analysis: coupling, summary, authors, churn, age, effort, communication
- Utilities: generate_git_log, validate_log_file, check_code_maat_status

Use `list_available_analyses()` for more details.
"""


def main():
    """Main entry point."""
    logger.info("Starting Code Maat MCP Server...")
    
    # Verify Code Maat is accessible
    try:
        import os
        if not os.path.exists(analysis_tools.wrapper.config.jar_path):
            logger.warning(f"Code Maat JAR not found at: {analysis_tools.wrapper.config.jar_path}")
        else:
            logger.info(f"Code Maat JAR found at: {analysis_tools.wrapper.config.jar_path}")
    except Exception as e:
        logger.error(f"Error checking Code Maat: {e}")
    
    # Run the FastMCP server with stdio transport
    mcp.run()


if __name__ == "__main__":
    main()