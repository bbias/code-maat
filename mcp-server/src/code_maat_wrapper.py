"""
Code Maat wrapper module for executing analysis via the standalone JAR.
"""

import json
import os
import subprocess
import tempfile
import csv
import io
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class CodeMaatConfig:
    """Configuration for Code Maat execution."""
    jar_path: str
    java_executable: str = "java"
    java_opts: List[str] = None
    
    def __post_init__(self):
        if self.java_opts is None:
            self.java_opts = ["-Xmx4g", "-Djava.awt.headless=true", "-Xss512M"]


class CodeMaatError(Exception):
    """Base exception for Code Maat execution errors."""
    pass


class CodeMaatWrapper:
    """Wrapper for executing Code Maat analyses."""
    
    SUPPORTED_VCS = {"git", "git2", "svn", "hg", "p4", "tfs"}
    SUPPORTED_ANALYSES = {
        "authors", "revisions", "coupling", "soc", "summary", "identity",
        "abs-churn", "author-churn", "entity-churn", "entity-ownership",
        "main-dev", "refactoring-main-dev", "entity-effort", "main-dev-by-revs",
        "fragmentation", "communication", "messages", "age"
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the wrapper with configuration."""
        self.config = self._load_config(config_path)
        self._validate_config()
    
    def _load_config(self, config_path: Optional[str] = None) -> CodeMaatConfig:
        """Load configuration from file or use defaults."""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "..", "mcp_config.json")
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                code_maat_config = config_data.get("code_maat", {})
                
                return CodeMaatConfig(
                    jar_path=code_maat_config.get("jar_path", "../target/code-maat-1.0.5-SNAPSHOT-standalone.jar"),
                    java_executable=code_maat_config.get("java_executable", "java"),
                    java_opts=code_maat_config.get("java_opts", ["-Xmx4g", "-Djava.awt.headless=true", "-Xss512M"])
                )
        except (FileNotFoundError, json.JSONDecodeError):
            # Use defaults if config file not found or invalid
            return CodeMaatConfig(
                jar_path="../target/code-maat-1.0.5-SNAPSHOT-standalone.jar"
            )
    
    def _validate_config(self):
        """Validate that Code Maat JAR exists and is accessible."""
        jar_path = Path(self.config.jar_path)
        if not jar_path.is_absolute():
            # Resolve relative to the mcp-server directory
            base_dir = Path(__file__).parent.parent
            jar_path = (base_dir / jar_path).resolve()
        
        if not jar_path.exists():
            raise CodeMaatError(f"Code Maat JAR not found at: {jar_path}")
        
        self.config.jar_path = str(jar_path)
    
    def validate_inputs(self, log_file: str, vcs: str, analysis: str) -> bool:
        """Validate input parameters."""
        if not os.path.exists(log_file):
            raise CodeMaatError(f"Log file not found: {log_file}")
        
        if vcs not in self.SUPPORTED_VCS:
            raise CodeMaatError(f"Unsupported VCS: {vcs}. Supported: {', '.join(self.SUPPORTED_VCS)}")
        
        if analysis not in self.SUPPORTED_ANALYSES:
            raise CodeMaatError(f"Unsupported analysis: {analysis}. Supported: {', '.join(self.SUPPORTED_ANALYSES)}")
        
        return True
    
    def run_analysis(self, 
                    log_file: str,
                    vcs: str,
                    analysis: str,
                    **kwargs) -> List[Dict[str, Any]]:
        """
        Run a Code Maat analysis and return structured results.
        
        Args:
            log_file: Path to the VCS log file
            vcs: VCS type (git, git2, svn, hg, p4, tfs)
            analysis: Analysis type
            **kwargs: Additional Code Maat options
        
        Returns:
            List of dictionaries containing analysis results
        """
        self.validate_inputs(log_file, vcs, analysis)
        
        # Build command
        cmd = [
            self.config.java_executable,
            *self.config.java_opts,
            "-jar", self.config.jar_path,
            "-l", log_file,
            "-c", vcs,
            "-a", analysis
        ]
        
        # Add optional parameters
        self._add_optional_params(cmd, kwargs)
        
        try:
            # Execute Code Maat
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse CSV output
            return self._parse_csv_output(result.stdout)
            
        except subprocess.CalledProcessError as e:
            raise CodeMaatError(f"Code Maat execution failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise CodeMaatError("Code Maat execution timed out")
    
    def _add_optional_params(self, cmd: List[str], kwargs: Dict[str, Any]):
        """Add optional parameters to the command."""
        param_mapping = {
            'rows': '-r',
            'group': '-g',
            'team_map_file': '-p',
            'min_revs': '-n',
            'min_shared_revs': '-m',
            'min_coupling': '-i',
            'max_coupling': '-x',
            'max_changeset_size': '-s',
            'expression_to_match': '-e',
            'temporal_period': '-t',
            'age_time_now': '-d',
            'input_encoding': '--input-encoding'
        }
        
        for param, value in kwargs.items():
            if value is not None and param in param_mapping:
                flag = param_mapping[param]
                cmd.extend([flag, str(value)])
        
        # Handle boolean flags
        if kwargs.get('verbose_results'):
            cmd.append('--verbose-results')
    
    def _parse_csv_output(self, csv_output: str) -> List[Dict[str, Any]]:
        """Parse CSV output into structured data."""
        if not csv_output.strip():
            return []
        
        try:
            reader = csv.DictReader(io.StringIO(csv_output))
            results = []
            
            for row in reader:
                # Convert numeric strings to appropriate types
                converted_row = {}
                for key, value in row.items():
                    converted_row[key] = self._convert_value(value)
                results.append(converted_row)
            
            return results
            
        except Exception as e:
            raise CodeMaatError(f"Failed to parse CSV output: {e}")
    
    def _convert_value(self, value: str) -> Union[str, int, float]:
        """Convert string values to appropriate types."""
        if not value or value.strip() == '':
            return None
        
        # Try to convert to int
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value.strip()
    
    def generate_git_log(self, 
                        repo_path: str,
                        output_file: str,
                        format_type: str = "git2",
                        after_date: Optional[str] = None,
                        exclude_paths: Optional[List[str]] = None) -> str:
        """
        Generate a git log file suitable for Code Maat analysis.
        
        Args:
            repo_path: Path to git repository
            output_file: Output log file path
            format_type: "git" or "git2" format
            after_date: Date filter (YYYY-MM-DD)
            exclude_paths: Paths to exclude from analysis
        
        Returns:
            Path to generated log file
        """
        if not os.path.exists(repo_path):
            raise CodeMaatError(f"Repository path not found: {repo_path}")
        
        # Build git log command
        if format_type == "git2":
            cmd = [
                "git", "log", "--all", "--numstat", "--date=short",
                "--pretty=format:--%h--%ad--%aN", "--no-renames"
            ]
        else:  # git format
            cmd = [
                "git", "log", "--pretty=format:[%h] %aN %ad %s",
                "--date=short", "--numstat"
            ]
        
        if after_date:
            cmd.extend([f"--after={after_date}"])
        
        # Add path exclusions
        if exclude_paths:
            cmd.append("--")
            cmd.append(".")
            for path in exclude_paths:
                cmd.append(f":(exclude){path}")
        
        try:
            # Change to repository directory and run git log
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Write output to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            
            return output_file
            
        except subprocess.CalledProcessError as e:
            raise CodeMaatError(f"Git log generation failed: {e.stderr}")
    
    def get_analysis_info(self, analysis: str) -> Dict[str, Any]:
        """Get information about a specific analysis type."""
        analysis_info = {
            "authors": {
                "description": "Number of authors per module and revision count",
                "output_columns": ["entity", "n-authors", "n-revs"],
                "use_case": "Identify modules with high communication overhead"
            },
            "coupling": {
                "description": "Logical coupling between modules that tend to change together",
                "output_columns": ["entity", "coupled", "degree", "average-revs"],
                "use_case": "Find hidden dependencies and refactoring candidates"
            },
            "summary": {
                "description": "Overview statistics of the repository",
                "output_columns": ["statistic", "value"],
                "use_case": "Get high-level metrics about the codebase"
            },
            "churn": {
                "description": "Code churn metrics showing change frequency",
                "output_columns": ["entity", "added", "deleted"],
                "use_case": "Identify unstable code areas"
            },
            "age": {
                "description": "Code age showing how long since modules were last changed",
                "output_columns": ["entity", "age-months"],
                "use_case": "Find stable vs frequently changing code"
            }
        }
        
        return analysis_info.get(analysis, {
            "description": f"Analysis type: {analysis}",
            "output_columns": ["varies"],
            "use_case": "Refer to Code Maat documentation for details"
        })