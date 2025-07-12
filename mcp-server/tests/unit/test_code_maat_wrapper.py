"""
Unit tests for Code Maat wrapper module.
"""

import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock

from src.code_maat_wrapper import CodeMaatWrapper, CodeMaatError, CodeMaatConfig


class TestCodeMaatConfig:
    """Test CodeMaatConfig dataclass."""
    
    def test_default_initialization(self):
        """Test default config initialization."""
        config = CodeMaatConfig(jar_path="/path/to/jar")
        
        assert config.jar_path == "/path/to/jar"
        assert config.java_executable == "java"
        assert config.java_opts == ["-Xmx4g", "-Djava.awt.headless=true", "-Xss512M"]
    
    def test_custom_initialization(self):
        """Test custom config initialization."""
        custom_opts = ["-Xmx2g", "-Djava.awt.headless=true"]
        config = CodeMaatConfig(
            jar_path="/custom/path",
            java_executable="custom-java",
            java_opts=custom_opts
        )
        
        assert config.jar_path == "/custom/path"
        assert config.java_executable == "custom-java"
        assert config.java_opts == custom_opts


class TestCodeMaatWrapper:
    """Test CodeMaatWrapper class."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file."""
        config_data = {
            "code_maat": {
                "jar_path": "/test/path/code-maat.jar",
                "java_executable": "test-java",
                "java_opts": ["-Xmx2g"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        yield temp_path
        os.unlink(temp_path)
    
    @pytest.fixture
    def mock_jar_file(self):
        """Create mock JAR file."""
        with tempfile.NamedTemporaryFile(suffix='.jar', delete=False) as f:
            temp_path = f.name
        
        yield temp_path
        os.unlink(temp_path)
    
    def test_load_config_from_file(self, temp_config_file):
        """Test loading config from file."""
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper(config_path=temp_config_file)
            
            assert wrapper.config.jar_path == "/test/path/code-maat.jar"
            assert wrapper.config.java_executable == "test-java"
            assert wrapper.config.java_opts == ["-Xmx2g"]
    
    def test_load_config_defaults(self):
        """Test loading default config when file not found."""
        with patch('os.path.exists', return_value=False):
            wrapper = CodeMaatWrapper(config_path="/nonexistent/config.json")
            
            assert "../target/code-maat-1.0.5-SNAPSHOT-standalone.jar" in wrapper.config.jar_path
            assert wrapper.config.java_executable == "java"
    
    def test_validate_inputs_success(self, mock_jar_file):
        """Test successful input validation."""
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            # Should not raise exception
            result = wrapper.validate_inputs("logfile.log", "git2", "coupling")
            assert result is True
    
    def test_validate_inputs_missing_log_file(self, mock_jar_file):
        """Test validation with missing log file."""
        with patch('os.path.exists', side_effect=lambda path: path == mock_jar_file):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            with pytest.raises(CodeMaatError, match="Log file not found"):
                wrapper.validate_inputs("/nonexistent/logfile.log", "git2", "coupling")
    
    def test_validate_inputs_invalid_vcs(self, mock_jar_file):
        """Test validation with invalid VCS."""
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            with pytest.raises(CodeMaatError, match="Unsupported VCS"):
                wrapper.validate_inputs("logfile.log", "invalid_vcs", "coupling")
    
    def test_validate_inputs_invalid_analysis(self, mock_jar_file):
        """Test validation with invalid analysis."""
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            with pytest.raises(CodeMaatError, match="Unsupported analysis"):
                wrapper.validate_inputs("logfile.log", "git2", "invalid_analysis")
    
    @patch('subprocess.run')
    def test_run_analysis_success(self, mock_run, mock_jar_file):
        """Test successful analysis execution."""
        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.stdout = "entity,coupled,degree\nfile1.java,file2.java,78\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            results = wrapper.run_analysis("logfile.log", "git2", "coupling")
            
            assert len(results) == 1
            assert results[0]["entity"] == "file1.java"
            assert results[0]["coupled"] == "file2.java"
            assert results[0]["degree"] == 78
    
    @patch('subprocess.run')
    def test_run_analysis_failure(self, mock_run, mock_jar_file):
        """Test analysis execution failure."""
        # Mock failed subprocess execution
        mock_run.side_effect = Exception("Command failed")
        
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            with pytest.raises(CodeMaatError):
                wrapper.run_analysis("logfile.log", "git2", "coupling")
    
    def test_convert_value_integer(self, mock_jar_file):
        """Test value conversion to integer."""
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            assert wrapper._convert_value("123") == 123
            assert wrapper._convert_value("0") == 0
    
    def test_convert_value_float(self, mock_jar_file):
        """Test value conversion to float."""
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            assert wrapper._convert_value("123.45") == 123.45
            assert wrapper._convert_value("0.0") == 0.0
    
    def test_convert_value_string(self, mock_jar_file):
        """Test value conversion to string."""
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            assert wrapper._convert_value("text") == "text"
            assert wrapper._convert_value("  spaced  ") == "spaced"
    
    def test_convert_value_empty(self, mock_jar_file):
        """Test value conversion of empty strings."""
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            assert wrapper._convert_value("") is None
            assert wrapper._convert_value("   ") is None
    
    def test_get_analysis_info_known(self, mock_jar_file):
        """Test getting info for known analysis."""
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            info = wrapper.get_analysis_info("coupling")
            
            assert "description" in info
            assert "output_columns" in info
            assert "use_case" in info
    
    def test_get_analysis_info_unknown(self, mock_jar_file):
        """Test getting info for unknown analysis."""
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            info = wrapper.get_analysis_info("unknown_analysis")
            
            assert "description" in info
            assert "unknown_analysis" in info["description"]
    
    @patch('subprocess.run')
    def test_generate_git_log_success(self, mock_run, mock_jar_file):
        """Test successful git log generation."""
        mock_result = MagicMock()
        mock_result.stdout = "--hash--date--author\nfile1.java\t10\t5\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                output_file = temp_file.name
            
            try:
                result = wrapper.generate_git_log("/test/repo", output_file)
                
                assert result == output_file
                assert os.path.exists(output_file)
                
                with open(output_file, 'r') as f:
                    content = f.read()
                    assert "--hash--date--author" in content
                    
            finally:
                if os.path.exists(output_file):
                    os.unlink(output_file)
    
    @patch('subprocess.run')
    def test_generate_git_log_failure(self, mock_run, mock_jar_file):
        """Test git log generation failure."""
        mock_run.side_effect = Exception("Git command failed")
        
        with patch('os.path.exists', return_value=True):
            wrapper = CodeMaatWrapper()
            wrapper.config.jar_path = mock_jar_file
            
            with pytest.raises(CodeMaatError):
                wrapper.generate_git_log("/test/repo", "/tmp/output.log")