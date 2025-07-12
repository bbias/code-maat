"""
MCP utility tools for Code Maat operations.
"""

from typing import Any, Dict, List
from mcp.types import Tool, TextContent
import os
import tempfile
import json

from ..code_maat_wrapper import CodeMaatWrapper, CodeMaatError


class UtilityTools:
    """MCP utility tools for Code Maat operations."""
    
    def __init__(self):
        self.wrapper = CodeMaatWrapper()
    
    def get_tools(self) -> List[Tool]:
        """Return list of MCP utility tools."""
        return [
            Tool(
                name="generate_git_log",
                description="Generate a git log file suitable for Code Maat analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_path": {
                            "type": "string",
                            "description": "Path to the git repository"
                        },
                        "output_file": {
                            "type": "string",
                            "description": "Output log file path (optional, will create temp file if not provided)"
                        },
                        "format_type": {
                            "type": "string",
                            "enum": ["git", "git2"],
                            "description": "Git log format type (git2 is recommended)",
                            "default": "git2"
                        },
                        "after_date": {
                            "type": "string",
                            "description": "Only include commits after this date (YYYY-MM-DD format)"
                        },
                        "exclude_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Paths to exclude from analysis (e.g., vendor/, test/)"
                        }
                    },
                    "required": ["repo_path"]
                }
            ),
            Tool(
                name="list_available_analyses",
                description="List all available Code Maat analysis types with descriptions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_details": {
                            "type": "boolean",
                            "description": "Include detailed descriptions and use cases",
                            "default": True
                        }
                    }
                }
            ),
            Tool(
                name="validate_log_file",
                description="Validate if a log file is suitable for Code Maat analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_file": {
                            "type": "string",
                            "description": "Path to the log file to validate"
                        },
                        "vcs": {
                            "type": "string",
                            "enum": ["git", "git2", "svn", "hg", "p4", "tfs"],
                            "description": "Expected VCS type"
                        }
                    },
                    "required": ["log_file", "vcs"]
                }
            ),
            Tool(
                name="get_analysis_info",
                description="Get detailed information about a specific analysis type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "analysis": {
                            "type": "string",
                            "description": "Analysis type to get information about"
                        }
                    },
                    "required": ["analysis"]
                }
            ),
            Tool(
                name="check_code_maat_status",
                description="Check if Code Maat is properly configured and accessible",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    async def generate_git_log(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Generate a git log file for Code Maat analysis."""
        try:
            repo_path = arguments["repo_path"]
            output_file = arguments.get("output_file")
            
            # Create temp file if no output file specified
            if not output_file:
                temp_fd, output_file = tempfile.mkstemp(suffix=".log", prefix="code_maat_")
                os.close(temp_fd)  # Close file descriptor, we just need the path
            
            result_file = self.wrapper.generate_git_log(
                repo_path=repo_path,
                output_file=output_file,
                format_type=arguments.get("format_type", "git2"),
                after_date=arguments.get("after_date"),
                exclude_paths=arguments.get("exclude_paths")
            )
            
            # Get basic stats about the generated log
            with open(result_file, 'r') as f:
                lines = f.readlines()
            
            commit_count = 0
            if arguments.get("format_type", "git2") == "git2":
                commit_count = sum(1 for line in lines if line.startswith("--"))
            else:
                commit_count = sum(1 for line in lines if line.startswith("["))
            
            return [TextContent(
                type="text",
                text=f"""# Git Log Generated Successfully

**Output file**: {result_file}
**Total lines**: {len(lines)}
**Estimated commits**: {commit_count}
**Format**: {arguments.get("format_type", "git2")}

The log file is ready for Code Maat analysis. Use this file with any of the analysis tools.

Example usage:
```
run_summary_analysis(log_file="{result_file}", vcs="{arguments.get("format_type", "git2")}")
```"""
            )]
            
        except CodeMaatError as e:
            return [TextContent(
                type="text",
                text=f"Error generating git log: {str(e)}"
            )]
    
    async def list_available_analyses(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """List all available Code Maat analysis types."""
        include_details = arguments.get("include_details", True)
        
        analyses = {
            "authors": {
                "description": "Number of authors per module and revision count",
                "use_case": "Identify modules with high communication overhead due to many developers"
            },
            "revisions": {
                "description": "Number of revisions per module",
                "use_case": "Find the most frequently changed modules"
            },
            "coupling": {
                "description": "Logical coupling between modules that tend to change together",
                "use_case": "Discover hidden dependencies and refactoring candidates"
            },
            "soc": {
                "description": "Sum of coupling for modules",
                "use_case": "Identify modules with the highest overall coupling"
            },
            "summary": {
                "description": "Overview statistics of the repository",
                "use_case": "Get high-level metrics about commits, entities, and authors"
            },
            "identity": {
                "description": "Raw parsed data (debugging purpose)",
                "use_case": "Debug parser issues or export raw data"
            },
            "abs-churn": {
                "description": "Absolute code churn over time",
                "use_case": "Track development activity trends over time"
            },
            "author-churn": {
                "description": "Code churn by author",
                "use_case": "Understand individual developer contributions"
            },
            "entity-churn": {
                "description": "Code churn by module/entity",
                "use_case": "Identify unstable or heavily modified modules"
            },
            "entity-ownership": {
                "description": "Ownership distribution per module",
                "use_case": "Find modules with clear vs distributed ownership"
            },
            "main-dev": {
                "description": "Main developer per module by lines changed",
                "use_case": "Identify module experts for knowledge transfer"
            },
            "refactoring-main-dev": {
                "description": "Main developer excluding initial commit",
                "use_case": "Find who maintains modules after initial development"
            },
            "entity-effort": {
                "description": "Effort distribution among developers per entity",
                "use_case": "Understand collaboration patterns within modules"
            },
            "main-dev-by-revs": {
                "description": "Main developer by number of revisions",
                "use_case": "Alternative view of module ownership by activity"
            },
            "fragmentation": {
                "description": "How fragmented the development effort is",
                "use_case": "Assess development coordination challenges"
            },
            "communication": {
                "description": "Communication patterns between developers",
                "use_case": "Identify collaboration needs and team structure"
            },
            "messages": {
                "description": "Commit message word frequency analysis",
                "use_case": "Understand development themes and focus areas"
            },
            "age": {
                "description": "Age of modules (time since last change)",
                "use_case": "Find stable vs actively changing code areas"
            }
        }
        
        if include_details:
            output = ["# Available Code Maat Analyses\n"]
            for analysis, info in analyses.items():
                output.append(f"## {analysis}")
                output.append(f"**Description**: {info['description']}")
                output.append(f"**Use case**: {info['use_case']}")
                output.append("")
        else:
            output = ["# Available Analyses\n"]
            output.extend([f"- `{analysis}`: {info['description']}" for analysis, info in analyses.items()])
        
        return [TextContent(
            type="text",
            text="\n".join(output)
        )]
    
    async def validate_log_file(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Validate a log file for Code Maat analysis."""
        try:
            log_file = arguments["log_file"]
            vcs = arguments["vcs"]
            
            # Basic file existence check
            if not os.path.exists(log_file):
                return [TextContent(
                    type="text",
                    text=f"❌ Log file not found: {log_file}"
                )]
            
            # Check file size
            file_size = os.path.getsize(log_file)
            if file_size == 0:
                return [TextContent(
                    type="text",
                    text=f"❌ Log file is empty: {log_file}"
                )]
            
            # Read first few lines to check format
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = [f.readline().strip() for _ in range(10)]
            
            # Basic format validation
            validation_result = self._validate_log_format(first_lines, vcs)
            
            # Try to run a quick identity analysis to verify parsing
            try:
                results = self.wrapper.run_analysis(log_file, vcs, "identity")
                if not results:
                    parsing_status = "⚠️  Log file parsed but no data extracted"
                else:
                    parsing_status = f"✅ Log file parsed successfully ({len(results)} entries)"
            except CodeMaatError as e:
                parsing_status = f"❌ Parsing failed: {str(e)}"
            
            return [TextContent(
                type="text",
                text=f"""# Log File Validation Results

**File**: {log_file}
**VCS Type**: {vcs}
**File Size**: {file_size:,} bytes

## Format Validation
{validation_result}

## Parsing Test
{parsing_status}

## Recommendations
- For git repositories, prefer 'git2' format over 'git'
- Ensure log includes file change statistics (--numstat for git)
- Consider filtering by date range for large repositories
- Exclude vendor/third-party directories if present"""
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error validating log file: {str(e)}"
            )]
    
    def _validate_log_format(self, lines: List[str], vcs: str) -> str:
        """Validate log format against expected VCS format."""
        if not lines or all(not line for line in lines):
            return "❌ File appears to be empty or unreadable"
        
        if vcs == "git2":
            # Look for git2 format: --hash--date--author
            git2_pattern_found = any(line.startswith("--") and line.count("--") >= 3 for line in lines)
            if git2_pattern_found:
                return "✅ Git2 format detected"
            else:
                return "⚠️  Git2 format not detected. Expected lines starting with '--hash--date--author'"
        
        elif vcs == "git":
            # Look for git format: [hash] author date message
            git_pattern_found = any(line.startswith("[") and "]" in line for line in lines)
            if git_pattern_found:
                return "✅ Git format detected"
            else:
                return "⚠️  Git format not detected. Expected lines starting with '[hash] author date'"
        
        elif vcs == "svn":
            # SVN XML format
            xml_found = any("<?xml" in line or "<log>" in line for line in lines)
            if xml_found:
                return "✅ SVN XML format detected"
            else:
                return "⚠️  SVN XML format not detected. Expected XML structure"
        
        else:
            return f"ℹ️  Basic validation passed for {vcs} format"
    
    async def get_analysis_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get detailed information about a specific analysis."""
        analysis = arguments["analysis"]
        info = self.wrapper.get_analysis_info(analysis)
        
        if not info:
            return [TextContent(
                type="text",
                text=f"Analysis type '{analysis}' not found. Use list_available_analyses to see all options."
            )]
        
        output = [f"# {analysis.title()} Analysis\n"]
        output.append(f"**Description**: {info.get('description', 'No description available')}")
        output.append(f"**Use case**: {info.get('use_case', 'No use case defined')}")
        
        if 'output_columns' in info:
            output.append(f"**Output columns**: {', '.join(info['output_columns'])}")
        
        output.append("\n## Example Usage")
        output.append(f"```")
        output.append(f"run_{analysis.replace('-', '_')}_analysis(")
        output.append(f"    log_file=\"path/to/logfile.log\",")
        output.append(f"    vcs=\"git2\"")
        output.append(f")")
        output.append(f"```")
        
        return [TextContent(
            type="text",
            text="\n".join(output)
        )]
    
    async def check_code_maat_status(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Check Code Maat configuration and status."""
        try:
            # Test wrapper initialization
            wrapper = CodeMaatWrapper()
            
            status_info = []
            status_info.append("# Code Maat Status Check\n")
            
            # Check JAR file
            jar_path = wrapper.config.jar_path
            if os.path.exists(jar_path):
                jar_size = os.path.getsize(jar_path)
                status_info.append(f"✅ **JAR File**: Found at {jar_path} ({jar_size:,} bytes)")
            else:
                status_info.append(f"❌ **JAR File**: Not found at {jar_path}")
            
            # Check Java
            try:
                import subprocess
                result = subprocess.run([wrapper.config.java_executable, "-version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    java_version = result.stderr.split('\n')[0] if result.stderr else "Unknown version"
                    status_info.append(f"✅ **Java**: {java_version}")
                else:
                    status_info.append(f"❌ **Java**: Not accessible at {wrapper.config.java_executable}")
            except Exception:
                status_info.append(f"❌ **Java**: Not accessible at {wrapper.config.java_executable}")
            
            # Check configuration
            status_info.append(f"**Java Options**: {' '.join(wrapper.config.java_opts)}")
            
            # Test basic functionality if JAR exists
            if os.path.exists(jar_path):
                status_info.append("\n## Quick Test")
                try:
                    # Create a minimal test to verify Code Maat runs
                    cmd = [
                        wrapper.config.java_executable,
                        *wrapper.config.java_opts,
                        "-jar", jar_path,
                        "-h"
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if "Code Maat" in result.stdout:
                        status_info.append("✅ Code Maat responds correctly to help command")
                    else:
                        status_info.append("⚠️  Code Maat runs but unexpected output")
                except Exception as e:
                    status_info.append(f"❌ Code Maat test failed: {str(e)}")
            
            return [TextContent(
                type="text",
                text="\n".join(status_info)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error checking Code Maat status: {str(e)}"
            )]