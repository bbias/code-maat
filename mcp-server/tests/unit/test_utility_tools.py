"""
Unit tests for MCP utility tools.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from src.tools.utility_tools import UtilityTools
from src.code_maat_wrapper import CodeMaatError


class TestUtilityTools:
    """Test UtilityTools class."""
    
    @pytest.fixture
    def utility_tools(self):
        """Create UtilityTools instance with mocked wrapper."""
        with patch('src.tools.utility_tools.CodeMaatWrapper'):
            return UtilityTools()
    
    def test_get_tools(self, utility_tools):
        """Test getting list of utility tools."""
        tools = utility_tools.get_tools()
        
        assert len(tools) > 0
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "generate_git_log",
            "list_available_analyses",
            "validate_log_file",
            "get_analysis_info",
            "check_code_maat_status"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_generate_git_log_success(self, utility_tools):
        """Test successful git log generation."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            output_file = temp_file.name
            temp_file.write(b"--hash--date--author\nfile1.java\t10\t5\n")
        
        try:
            utility_tools.wrapper.generate_git_log.return_value = output_file
            
            arguments = {
                "repo_path": "/test/repo",
                "format_type": "git2"
            }
            
            result = await utility_tools.generate_git_log(arguments)
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Git Log Generated Successfully" in result[0].text
            assert output_file in result[0].text
            assert "Format**: git2" in result[0].text
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    @pytest.mark.asyncio
    async def test_generate_git_log_with_temp_file(self, utility_tools):
        """Test git log generation with temporary file."""
        temp_output = "/tmp/temp_log_12345.log"
        
        with patch('tempfile.mkstemp', return_value=(1, temp_output)):
            with patch('os.close'):
                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.readlines.return_value = [
                        "--hash1--2024-01-01--Author1\n",
                        "--hash2--2024-01-02--Author2\n"
                    ]
                    
                    utility_tools.wrapper.generate_git_log.return_value = temp_output
                    
                    arguments = {
                        "repo_path": "/test/repo"
                    }
                    
                    result = await utility_tools.generate_git_log(arguments)
                    
                    assert len(result) == 1
                    assert result[0].type == "text"
                    assert temp_output in result[0].text
                    assert "Estimated commits**: 2" in result[0].text
    
    @pytest.mark.asyncio
    async def test_generate_git_log_error(self, utility_tools):
        """Test git log generation error."""
        utility_tools.wrapper.generate_git_log.side_effect = CodeMaatError("Git error")
        
        arguments = {
            "repo_path": "/test/repo"
        }
        
        result = await utility_tools.generate_git_log(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error generating git log" in result[0].text
        assert "Git error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_list_available_analyses_with_details(self, utility_tools):
        """Test listing analyses with details."""
        arguments = {"include_details": True}
        
        result = await utility_tools.list_available_analyses(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Available Code Maat Analyses" in result[0].text
        assert "## authors" in result[0].text
        assert "## coupling" in result[0].text
        assert "Description**:" in result[0].text
        assert "Use case**:" in result[0].text
    
    @pytest.mark.asyncio
    async def test_list_available_analyses_without_details(self, utility_tools):
        """Test listing analyses without details."""
        arguments = {"include_details": False}
        
        result = await utility_tools.list_available_analyses(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Available Analyses" in result[0].text
        assert "`authors`:" in result[0].text
        assert "`coupling`:" in result[0].text
        # Should not contain detailed descriptions
        assert "Description**:" not in result[0].text
    
    @pytest.mark.asyncio
    async def test_validate_log_file_success(self, utility_tools):
        """Test successful log file validation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("--hash1--2024-01-01--Author1\nfile1.java\t10\t5\n")
            temp_file.flush()
            log_file = temp_file.name
        
        try:
            # Mock successful analysis
            utility_tools.wrapper.run_analysis.return_value = [{"some": "data"}]
            
            arguments = {
                "log_file": log_file,
                "vcs": "git2"
            }
            
            result = await utility_tools.validate_log_file(arguments)
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Log File Validation Results" in result[0].text
            assert "✅ Git2 format detected" in result[0].text
            assert "✅ Log file parsed successfully" in result[0].text
            
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    @pytest.mark.asyncio
    async def test_validate_log_file_not_found(self, utility_tools):
        """Test validation of non-existent log file."""
        arguments = {
            "log_file": "/nonexistent/file.log",
            "vcs": "git2"
        }
        
        result = await utility_tools.validate_log_file(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "❌ Log file not found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_validate_log_file_empty(self, utility_tools):
        """Test validation of empty log file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file = temp_file.name
        
        try:
            arguments = {
                "log_file": log_file,
                "vcs": "git2"
            }
            
            result = await utility_tools.validate_log_file(arguments)
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "❌ Log file is empty" in result[0].text
            
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    @pytest.mark.asyncio
    async def test_validate_log_file_parsing_error(self, utility_tools):
        """Test validation with parsing error."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("--hash1--2024-01-01--Author1\n")
            temp_file.flush()
            log_file = temp_file.name
        
        try:
            # Mock parsing error
            utility_tools.wrapper.run_analysis.side_effect = CodeMaatError("Parse failed")
            
            arguments = {
                "log_file": log_file,
                "vcs": "git2"
            }
            
            result = await utility_tools.validate_log_file(arguments)
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "❌ Parsing failed: Parse failed" in result[0].text
            
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_validate_log_format_git2_success(self, utility_tools):
        """Test git2 format validation success."""
        lines = ["--abc123--2024-01-01--John Doe", "file1.java\t10\t5"]
        
        result = utility_tools._validate_log_format(lines, "git2")
        
        assert "✅ Git2 format detected" in result
    
    def test_validate_log_format_git2_failure(self, utility_tools):
        """Test git2 format validation failure."""
        lines = ["[abc123] John Doe 2024-01-01 commit message", "file1.java | 15 ++++++"]
        
        result = utility_tools._validate_log_format(lines, "git2")
        
        assert "⚠️  Git2 format not detected" in result
    
    def test_validate_log_format_git_success(self, utility_tools):
        """Test git format validation success."""
        lines = ["[abc123] John Doe 2024-01-01 commit message", "file1.java | 15 ++++++"]
        
        result = utility_tools._validate_log_format(lines, "git")
        
        assert "✅ Git format detected" in result
    
    def test_validate_log_format_svn_success(self, utility_tools):
        """Test SVN format validation success."""
        lines = ["<?xml version=\"1.0\"?>", "<log>", "<logentry>"]
        
        result = utility_tools._validate_log_format(lines, "svn")
        
        assert "✅ SVN XML format detected" in result
    
    def test_validate_log_format_empty(self, utility_tools):
        """Test format validation with empty lines."""
        lines = ["", "", ""]
        
        result = utility_tools._validate_log_format(lines, "git2")
        
        assert "❌ File appears to be empty" in result
    
    @pytest.mark.asyncio
    async def test_get_analysis_info_success(self, utility_tools):
        """Test getting analysis info successfully."""
        mock_info = {
            "description": "Test analysis description",
            "use_case": "Test use case",
            "output_columns": ["col1", "col2"]
        }
        utility_tools.wrapper.get_analysis_info.return_value = mock_info
        
        arguments = {"analysis": "coupling"}
        
        result = await utility_tools.get_analysis_info(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "# Coupling Analysis" in result[0].text
        assert "Test analysis description" in result[0].text
        assert "Test use case" in result[0].text
        assert "col1, col2" in result[0].text
        assert "run_coupling_analysis" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_analysis_info_not_found(self, utility_tools):
        """Test getting info for unknown analysis."""
        utility_tools.wrapper.get_analysis_info.return_value = {}
        
        arguments = {"analysis": "unknown"}
        
        result = await utility_tools.get_analysis_info(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Analysis type 'unknown' not found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_check_code_maat_status_success(self, utility_tools):
        """Test Code Maat status check success."""
        with tempfile.NamedTemporaryFile(suffix='.jar', delete=False) as temp_jar:
            jar_path = temp_jar.name
        
        try:
            utility_tools.wrapper.config.jar_path = jar_path
            utility_tools.wrapper.config.java_executable = "java"
            utility_tools.wrapper.config.java_opts = ["-Xmx4g"]
            
            with patch('subprocess.run') as mock_run:
                # Mock Java version check
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stderr = "openjdk version \"11.0.0\""
                mock_run.return_value = mock_result
                
                arguments = {}
                
                result = await utility_tools.check_code_maat_status(arguments)
                
                assert len(result) == 1
                assert result[0].type == "text"
                assert "Code Maat Status Check" in result[0].text
                assert "✅ **JAR File**: Found" in result[0].text
                assert "✅ **Java**:" in result[0].text
                
        finally:
            if os.path.exists(jar_path):
                os.unlink(jar_path)
    
    @pytest.mark.asyncio
    async def test_check_code_maat_status_jar_not_found(self, utility_tools):
        """Test Code Maat status check with missing JAR."""
        utility_tools.wrapper.config.jar_path = "/nonexistent/code-maat.jar"
        
        arguments = {}
        
        result = await utility_tools.check_code_maat_status(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "❌ **JAR File**: Not found" in result[0].text