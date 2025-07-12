"""
MCP tools for Code Maat analysis functions.
"""

from typing import Any, Dict, List
from mcp.types import Tool, TextContent
import json
import os

from ..code_maat_wrapper import CodeMaatWrapper, CodeMaatError


class AnalysisTools:
    """MCP tools for running Code Maat analyses."""
    
    def __init__(self):
        self.wrapper = CodeMaatWrapper()
    
    def get_tools(self) -> List[Tool]:
        """Return list of MCP tools for analysis functions."""
        return [
            Tool(
                name="run_coupling_analysis",
                description="Analyze logical coupling between modules that tend to change together",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_file": {
                            "type": "string",
                            "description": "Path to the VCS log file"
                        },
                        "vcs": {
                            "type": "string",
                            "enum": ["git", "git2", "svn", "hg", "p4", "tfs"],
                            "description": "Version control system type"
                        },
                        "min_coupling": {
                            "type": "integer",
                            "description": "Minimum coupling percentage to include (default: 30)",
                            "default": 30
                        },
                        "max_coupling": {
                            "type": "integer", 
                            "description": "Maximum coupling percentage to include (default: 100)",
                            "default": 100
                        },
                        "min_revs": {
                            "type": "integer",
                            "description": "Minimum revisions to include entity (default: 5)",
                            "default": 5
                        },
                        "max_changeset_size": {
                            "type": "integer",
                            "description": "Maximum changeset size to consider (default: 30)",
                            "default": 30
                        }
                    },
                    "required": ["log_file", "vcs"]
                }
            ),
            Tool(
                name="run_summary_analysis", 
                description="Generate overview statistics of the repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_file": {
                            "type": "string",
                            "description": "Path to the VCS log file"
                        },
                        "vcs": {
                            "type": "string",
                            "enum": ["git", "git2", "svn", "hg", "p4", "tfs"],
                            "description": "Version control system type"
                        }
                    },
                    "required": ["log_file", "vcs"]
                }
            ),
            Tool(
                name="run_authors_analysis",
                description="Analyze developer contribution metrics per module",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_file": {
                            "type": "string",
                            "description": "Path to the VCS log file"
                        },
                        "vcs": {
                            "type": "string",
                            "enum": ["git", "git2", "svn", "hg", "p4", "tfs"],
                            "description": "Version control system type"
                        },
                        "min_revs": {
                            "type": "integer",
                            "description": "Minimum revisions to include entity (default: 5)",
                            "default": 5
                        },
                        "rows": {
                            "type": "integer",
                            "description": "Maximum number of results to return"
                        }
                    },
                    "required": ["log_file", "vcs"]
                }
            ),
            Tool(
                name="run_churn_analysis",
                description="Analyze code churn patterns (entity-churn, author-churn, or abs-churn)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_file": {
                            "type": "string",
                            "description": "Path to the VCS log file"
                        },
                        "vcs": {
                            "type": "string",
                            "enum": ["git", "git2", "svn", "hg", "p4", "tfs"],
                            "description": "Version control system type"
                        },
                        "churn_type": {
                            "type": "string",
                            "enum": ["entity-churn", "author-churn", "abs-churn"],
                            "description": "Type of churn analysis to perform",
                            "default": "entity-churn"
                        },
                        "min_revs": {
                            "type": "integer",
                            "description": "Minimum revisions to include entity (default: 5)",
                            "default": 5
                        },
                        "rows": {
                            "type": "integer",
                            "description": "Maximum number of results to return"
                        }
                    },
                    "required": ["log_file", "vcs"]
                }
            ),
            Tool(
                name="run_age_analysis",
                description="Analyze code age and stability metrics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_file": {
                            "type": "string",
                            "description": "Path to the VCS log file"
                        },
                        "vcs": {
                            "type": "string",
                            "enum": ["git", "git2", "svn", "hg", "p4", "tfs"],
                            "description": "Version control system type"
                        },
                        "age_time_now": {
                            "type": "string",
                            "description": "Reference date for age calculation (YYYY-MM-DD format)"
                        },
                        "rows": {
                            "type": "integer",
                            "description": "Maximum number of results to return"
                        }
                    },
                    "required": ["log_file", "vcs"]
                }
            ),
            Tool(
                name="run_entity_effort_analysis",
                description="Analyze effort distribution among developers per entity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_file": {
                            "type": "string",
                            "description": "Path to the VCS log file"
                        },
                        "vcs": {
                            "type": "string",
                            "enum": ["git", "git2", "svn", "hg", "p4", "tfs"],
                            "description": "Version control system type"
                        },
                        "min_revs": {
                            "type": "integer",
                            "description": "Minimum revisions to include entity (default: 5)",
                            "default": 5
                        },
                        "rows": {
                            "type": "integer",
                            "description": "Maximum number of results to return"
                        }
                    },
                    "required": ["log_file", "vcs"]
                }
            ),
            Tool(
                name="run_communication_analysis",
                description="Analyze communication patterns between developers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_file": {
                            "type": "string",
                            "description": "Path to the VCS log file"
                        },
                        "vcs": {
                            "type": "string",
                            "enum": ["git", "git2", "svn", "hg", "p4", "tfs"],
                            "description": "Version control system type"
                        },
                        "min_shared_revs": {
                            "type": "integer",
                            "description": "Minimum shared revisions to include (default: 5)",
                            "default": 5
                        },
                        "rows": {
                            "type": "integer",
                            "description": "Maximum number of results to return"
                        }
                    },
                    "required": ["log_file", "vcs"]
                }
            )
        ]
    
    async def run_coupling_analysis(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute logical coupling analysis."""
        try:
            results = self.wrapper.run_analysis(
                log_file=arguments["log_file"],
                vcs=arguments["vcs"],
                analysis="coupling",
                min_coupling=arguments.get("min_coupling", 30),
                max_coupling=arguments.get("max_coupling", 100),
                min_revs=arguments.get("min_revs", 5),
                max_changeset_size=arguments.get("max_changeset_size", 30)
            )
            
            return [TextContent(
                type="text",
                text=self._format_coupling_results(results)
            )]
            
        except CodeMaatError as e:
            return [TextContent(
                type="text", 
                text=f"Error running coupling analysis: {str(e)}"
            )]
    
    async def run_summary_analysis(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute summary analysis."""
        try:
            results = self.wrapper.run_analysis(
                log_file=arguments["log_file"],
                vcs=arguments["vcs"],
                analysis="summary"
            )
            
            return [TextContent(
                type="text",
                text=self._format_summary_results(results)
            )]
            
        except CodeMaatError as e:
            return [TextContent(
                type="text",
                text=f"Error running summary analysis: {str(e)}"
            )]
    
    async def run_authors_analysis(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute authors analysis."""
        try:
            kwargs = {
                "min_revs": arguments.get("min_revs", 5)
            }
            if "rows" in arguments:
                kwargs["rows"] = arguments["rows"]
                
            results = self.wrapper.run_analysis(
                log_file=arguments["log_file"],
                vcs=arguments["vcs"],
                analysis="authors",
                **kwargs
            )
            
            return [TextContent(
                type="text",
                text=self._format_authors_results(results)
            )]
            
        except CodeMaatError as e:
            return [TextContent(
                type="text",
                text=f"Error running authors analysis: {str(e)}"
            )]
    
    async def run_churn_analysis(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute churn analysis."""
        try:
            churn_type = arguments.get("churn_type", "entity-churn")
            kwargs = {
                "min_revs": arguments.get("min_revs", 5)
            }
            if "rows" in arguments:
                kwargs["rows"] = arguments["rows"]
                
            results = self.wrapper.run_analysis(
                log_file=arguments["log_file"],
                vcs=arguments["vcs"],
                analysis=churn_type,
                **kwargs
            )
            
            return [TextContent(
                type="text",
                text=self._format_churn_results(results, churn_type)
            )]
            
        except CodeMaatError as e:
            return [TextContent(
                type="text",
                text=f"Error running churn analysis: {str(e)}"
            )]
    
    async def run_age_analysis(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute age analysis."""
        try:
            kwargs = {}
            if "age_time_now" in arguments:
                kwargs["age_time_now"] = arguments["age_time_now"]
            if "rows" in arguments:
                kwargs["rows"] = arguments["rows"]
                
            results = self.wrapper.run_analysis(
                log_file=arguments["log_file"],
                vcs=arguments["vcs"],
                analysis="age",
                **kwargs
            )
            
            return [TextContent(
                type="text",
                text=self._format_age_results(results)
            )]
            
        except CodeMaatError as e:
            return [TextContent(
                type="text",
                text=f"Error running age analysis: {str(e)}"
            )]
    
    async def run_entity_effort_analysis(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute entity effort analysis."""
        try:
            kwargs = {
                "min_revs": arguments.get("min_revs", 5)
            }
            if "rows" in arguments:
                kwargs["rows"] = arguments["rows"]
                
            results = self.wrapper.run_analysis(
                log_file=arguments["log_file"],
                vcs=arguments["vcs"],
                analysis="entity-effort",
                **kwargs
            )
            
            return [TextContent(
                type="text",
                text=self._format_entity_effort_results(results)
            )]
            
        except CodeMaatError as e:
            return [TextContent(
                type="text",
                text=f"Error running entity effort analysis: {str(e)}"
            )]
    
    async def run_communication_analysis(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute communication analysis."""
        try:
            kwargs = {
                "min_shared_revs": arguments.get("min_shared_revs", 5)
            }
            if "rows" in arguments:
                kwargs["rows"] = arguments["rows"]
                
            results = self.wrapper.run_analysis(
                log_file=arguments["log_file"],
                vcs=arguments["vcs"],
                analysis="communication",
                **kwargs
            )
            
            return [TextContent(
                type="text",
                text=self._format_communication_results(results)
            )]
            
        except CodeMaatError as e:
            return [TextContent(
                type="text",
                text=f"Error running communication analysis: {str(e)}"
            )]
    
    def _format_coupling_results(self, results: List[Dict[str, Any]]) -> str:
        """Format coupling analysis results."""
        if not results:
            return "No coupling relationships found."
        
        output = ["# Logical Coupling Analysis Results\n"]
        output.append("Modules that tend to change together:\n")
        
        for item in results:
            entity = item.get("entity", "")
            coupled = item.get("coupled", "")
            degree = item.get("degree", 0)
            avg_revs = item.get("average-revs", 0)
            
            output.append(f"- **{entity}** ↔ **{coupled}**")
            output.append(f"  - Coupling: {degree}%")
            output.append(f"  - Average revisions: {avg_revs}")
            output.append("")
        
        return "\n".join(output)
    
    def _format_summary_results(self, results: List[Dict[str, Any]]) -> str:
        """Format summary analysis results."""
        if not results:
            return "No summary data available."
        
        output = ["# Repository Summary\n"]
        
        for item in results:
            statistic = item.get("statistic", "")
            value = item.get("value", "")
            output.append(f"- **{statistic.replace('-', ' ').title()}**: {value}")
        
        return "\n".join(output)
    
    def _format_authors_results(self, results: List[Dict[str, Any]]) -> str:
        """Format authors analysis results."""
        if not results:
            return "No author data found."
        
        output = ["# Author Analysis Results\n"]
        output.append("Modules with multiple developers:\n")
        
        for item in results:
            entity = item.get("entity", "")
            n_authors = item.get("n-authors", 0)
            n_revs = item.get("n-revs", 0)
            
            output.append(f"- **{entity}**")
            output.append(f"  - Authors: {n_authors}")
            output.append(f"  - Revisions: {n_revs}")
            output.append("")
        
        return "\n".join(output)
    
    def _format_churn_results(self, results: List[Dict[str, Any]], churn_type: str) -> str:
        """Format churn analysis results."""
        if not results:
            return f"No {churn_type} data found."
        
        output = [f"# {churn_type.replace('-', ' ').title()} Analysis Results\n"]
        
        for item in results:
            if churn_type == "entity-churn":
                entity = item.get("entity", "")
                added = item.get("added", 0)
                deleted = item.get("deleted", 0)
                
                output.append(f"- **{entity}**")
                output.append(f"  - Added: {added} lines")
                output.append(f"  - Deleted: {deleted} lines")
                
            elif churn_type == "author-churn":
                author = item.get("author", "")
                added = item.get("added", 0)
                deleted = item.get("deleted", 0)
                
                output.append(f"- **{author}**")
                output.append(f"  - Added: {added} lines")
                output.append(f"  - Deleted: {deleted} lines")
                
            elif churn_type == "abs-churn":
                date = item.get("date", "")
                added = item.get("added", 0)
                deleted = item.get("deleted", 0)
                
                output.append(f"- **{date}**")
                output.append(f"  - Added: {added} lines")
                output.append(f"  - Deleted: {deleted} lines")
            
            output.append("")
        
        return "\n".join(output)
    
    def _format_age_results(self, results: List[Dict[str, Any]]) -> str:
        """Format age analysis results."""
        if not results:
            return "No age data found."
        
        output = ["# Code Age Analysis Results\n"]
        output.append("Age of modules (months since last change):\n")
        
        for item in results:
            entity = item.get("entity", "")
            age_months = item.get("age-months", 0)
            
            output.append(f"- **{entity}**: {age_months} months old")
        
        return "\n".join(output)
    
    def _format_entity_effort_results(self, results: List[Dict[str, Any]]) -> str:
        """Format entity effort analysis results."""
        if not results:
            return "No entity effort data found."
        
        output = ["# Entity Effort Analysis Results\n"]
        output.append("Developer effort per module:\n")
        
        for item in results:
            entity = item.get("entity", "")
            author = item.get("author", "")
            author_revs = item.get("author-revs", 0)
            total_revs = item.get("total-revs", 0)
            
            percentage = (author_revs / total_revs * 100) if total_revs > 0 else 0
            
            output.append(f"- **{entity}** → **{author}**")
            output.append(f"  - Author revisions: {author_revs}/{total_revs} ({percentage:.1f}%)")
            output.append("")
        
        return "\n".join(output)
    
    def _format_communication_results(self, results: List[Dict[str, Any]]) -> str:
        """Format communication analysis results."""
        if not results:
            return "No communication data found."
        
        output = ["# Communication Analysis Results\n"]
        output.append("Developer communication patterns:\n")
        
        for item in results:
            author = item.get("author", "")
            peer = item.get("peer", "")
            shared = item.get("shared", 0)
            
            output.append(f"- **{author}** ↔ **{peer}**")
            output.append(f"  - Shared entities: {shared}")
            output.append("")
        
        return "\n".join(output)