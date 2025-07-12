"""
Integration tests for the MCP server.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock

from src.mcp_server import CodeMaatMCPServer


class TestCodeMaatMCPServer:
    """Integration tests for CodeMaatMCPServer."""
    
    @pytest.fixture
    def mock_jar_file(self):
        """Create a mock JAR file."""
        with tempfile.NamedTemporaryFile(suffix='.jar', delete=False) as temp_jar:
            jar_path = temp_jar.name
        
        yield jar_path
        
        if os.path.exists(jar_path):
            os.unlink(jar_path)
    
    @pytest.fixture
    def server(self, mock_jar_file):
        """Create server instance with mocked dependencies."""
        with patch('src.mcp_server.AnalysisTools') as mock_analysis:
            with patch('src.mcp_server.UtilityTools') as mock_utility:
                server = CodeMaatMCPServer()
                
                # Configure mock analysis tools
                mock_analysis_instance = mock_analysis.return_value
                mock_analysis_instance.wrapper.config.jar_path = mock_jar_file
                mock_analysis_instance.get_tools.return_value = [
                    MagicMock(name="run_coupling_analysis"),
                    MagicMock(name="run_summary_analysis")
                ]
                
                # Configure mock utility tools
                mock_utility_instance = mock_utility.return_value
                mock_utility_instance.get_tools.return_value = [
                    MagicMock(name="generate_git_log"),
                    MagicMock(name="validate_log_file")
                ]
                
                yield server
    
    def test_server_initialization(self, server):
        """Test server initializes correctly."""
        assert server.server.name == "code-maat-mcp-server"
        assert server.analysis_tools is not None
        assert server.utility_tools is not None
        assert isinstance(server.result_cache, dict)
    
    @pytest.mark.asyncio
    async def test_handle_list_tools(self, server):
        """Test listing tools."""
        # Get the handler function
        handlers = server.server._tool_handlers
        list_tools_handler = None
        for handler_name, handler_func in handlers.items():
            if "list_tools" in handler_name:
                list_tools_handler = handler_func
                break
        
        assert list_tools_handler is not None
        
        tools = await list_tools_handler()
        
        assert len(tools) > 0
        # Should include both analysis and utility tools
        assert len(tools) >= 4  # At least the mocked tools
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_analysis(self, server):
        """Test calling analysis tool."""
        # Mock the analysis tool method
        mock_method = MagicMock()
        mock_method.return_value = [MagicMock(type="text", text="Test result")]
        server.analysis_tools.run_coupling_analysis = mock_method
        
        # Get the handler function
        handlers = server.server._tool_handlers
        call_tool_handler = None
        for handler_name, handler_func in handlers.items():
            if "call_tool" in handler_name:
                call_tool_handler = handler_func
                break
        
        assert call_tool_handler is not None
        
        arguments = {
            "log_file": "test.log",
            "vcs": "git2"
        }
        
        result = await call_tool_handler("run_coupling_analysis", arguments)
        
        assert len(result) == 1
        assert result[0].text == "Test result"
        mock_method.assert_called_once_with(arguments)
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_utility(self, server):
        """Test calling utility tool."""
        # Mock the utility tool method
        mock_method = MagicMock()
        mock_method.return_value = [MagicMock(type="text", text="Utility result")]
        server.utility_tools.generate_git_log = mock_method
        
        # Get the handler function
        handlers = server.server._tool_handlers
        call_tool_handler = None
        for handler_name, handler_func in handlers.items():
            if "call_tool" in handler_name:
                call_tool_handler = handler_func
                break
        
        assert call_tool_handler is not None
        
        arguments = {
            "repo_path": "/test/repo"
        }
        
        result = await call_tool_handler("generate_git_log", arguments)
        
        assert len(result) == 1
        assert result[0].text == "Utility result"
        mock_method.assert_called_once_with(arguments)
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_unknown(self, server):
        """Test calling unknown tool."""
        # Get the handler function
        handlers = server.server._tool_handlers
        call_tool_handler = None
        for handler_name, handler_func in handlers.items():
            if "call_tool" in handler_name:
                call_tool_handler = handler_func
                break
        
        assert call_tool_handler is not None
        
        result = await call_tool_handler("unknown_tool", {})
        
        assert len(result) == 1
        assert "Unknown tool: unknown_tool" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_error(self, server):
        """Test tool call with error."""
        # Mock the analysis tool method to raise an error
        mock_method = MagicMock()
        mock_method.side_effect = Exception("Test error")
        server.analysis_tools.run_coupling_analysis = mock_method
        
        # Get the handler function
        handlers = server.server._tool_handlers
        call_tool_handler = None
        for handler_name, handler_func in handlers.items():
            if "call_tool" in handler_name:
                call_tool_handler = handler_func
                break
        
        assert call_tool_handler is not None
        
        result = await call_tool_handler("run_coupling_analysis", {})
        
        assert len(result) == 1
        assert "Error executing run_coupling_analysis: Test error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_list_resources(self, server):
        """Test listing resources."""
        # Get the handler function
        handlers = server.server._resource_handlers
        list_resources_handler = None
        for handler_name, handler_func in handlers.items():
            if "list_resources" in handler_name:
                list_resources_handler = handler_func
                break
        
        assert list_resources_handler is not None
        
        resources = await list_resources_handler()
        
        assert len(resources) >= 3
        
        resource_uris = [r.uri for r in resources]
        assert "code-maat://config" in resource_uris
        assert "code-maat://analyses" in resource_uris
        assert "code-maat://help/getting-started" in resource_uris
    
    @pytest.mark.asyncio
    async def test_handle_read_resource_config(self, server, mock_jar_file):
        """Test reading config resource."""
        # Get the handler function
        handlers = server.server._resource_handlers
        read_resource_handler = None
        for handler_name, handler_func in handlers.items():
            if "read_resource" in handler_name:
                read_resource_handler = handler_func
                break
        
        assert read_resource_handler is not None
        
        # Configure the wrapper config
        server.analysis_tools.wrapper.config.jar_path = mock_jar_file
        server.analysis_tools.wrapper.config.java_executable = "java"
        server.analysis_tools.wrapper.config.java_opts = ["-Xmx4g"]
        server.analysis_tools.wrapper.SUPPORTED_VCS = {"git", "git2"}
        server.analysis_tools.wrapper.SUPPORTED_ANALYSES = {"coupling", "summary"}
        
        result = await read_resource_handler("code-maat://config")
        
        config = json.loads(result)
        assert config["server_name"] == "code-maat-mcp-server"
        assert config["version"] == "0.1.0"
        assert config["code_maat_jar"] == mock_jar_file
        assert config["java_executable"] == "java"
        assert "git" in config["supported_vcs"]
        assert "coupling" in config["supported_analyses"]
    
    @pytest.mark.asyncio
    async def test_handle_read_resource_analyses(self, server):
        """Test reading analyses resource."""
        # Get the handler function
        handlers = server.server._resource_handlers
        read_resource_handler = None
        for handler_name, handler_func in handlers.items():
            if "read_resource" in handler_name:
                read_resource_handler = handler_func
                break
        
        assert read_resource_handler is not None
        
        # Mock the get_analysis_info method
        server.analysis_tools.wrapper.SUPPORTED_ANALYSES = {"coupling", "summary"}
        server.analysis_tools.wrapper.get_analysis_info.side_effect = lambda analysis: {
            "description": f"Description for {analysis}",
            "use_case": f"Use case for {analysis}"
        }
        
        result = await read_resource_handler("code-maat://analyses")
        
        analyses = json.loads(result)
        assert len(analyses) == 2
        assert any(a["name"] == "coupling" for a in analyses)
        assert any(a["name"] == "summary" for a in analyses)
    
    @pytest.mark.asyncio
    async def test_handle_read_resource_help(self, server):
        """Test reading help resource."""
        # Get the handler function
        handlers = server.server._resource_handlers
        read_resource_handler = None
        for handler_name, handler_func in handlers.items():
            if "read_resource" in handler_name:
                read_resource_handler = handler_func
                break
        
        assert read_resource_handler is not None
        
        result = await read_resource_handler("code-maat://help/getting-started")
        
        assert isinstance(result, str)
        assert "Getting Started with Code Maat MCP Server" in result
        assert "Prerequisites" in result
        assert "Quick Start" in result
        assert "Available Tools" in result
    
    @pytest.mark.asyncio
    async def test_handle_read_resource_unknown(self, server):
        """Test reading unknown resource."""
        # Get the handler function
        handlers = server.server._resource_handlers
        read_resource_handler = None
        for handler_name, handler_func in handlers.items():
            if "read_resource" in handler_name:
                read_resource_handler = handler_func
                break
        
        assert read_resource_handler is not None
        
        with pytest.raises(ValueError, match="Unknown resource"):
            await read_resource_handler("unknown://resource")
    
    def test_get_getting_started_guide(self, server):
        """Test getting started guide generation."""
        guide = server._get_getting_started_guide()
        
        assert isinstance(guide, str)
        assert "Getting Started with Code Maat MCP Server" in guide
        assert "Prerequisites" in guide
        assert "Quick Start" in guide
        assert "Available Tools" in guide
        assert "Analysis Tools" in guide
        assert "Utility Tools" in guide
        assert "Tips" in guide
        assert "Troubleshooting" in guide
        
        # Check that it contains example usage
        assert "run_summary_analysis" in guide
        assert "generate_git_log" in guide
        assert "git2" in guide