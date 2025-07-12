"""
Unit tests for MCP analysis tools.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from src.tools.analysis_tools import AnalysisTools
from src.code_maat_wrapper import CodeMaatError


class TestAnalysisTools:
    """Test AnalysisTools class."""
    
    @pytest.fixture
    def analysis_tools(self):
        """Create AnalysisTools instance with mocked wrapper."""
        with patch('src.tools.analysis_tools.CodeMaatWrapper'):
            return AnalysisTools()
    
    def test_get_tools(self, analysis_tools):
        """Test getting list of tools."""
        tools = analysis_tools.get_tools()
        
        assert len(tools) > 0
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "run_coupling_analysis",
            "run_summary_analysis", 
            "run_authors_analysis",
            "run_churn_analysis",
            "run_age_analysis",
            "run_entity_effort_analysis",
            "run_communication_analysis"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    def test_tool_schemas(self, analysis_tools):
        """Test that all tools have proper schemas."""
        tools = analysis_tools.get_tools()
        
        for tool in tools:
            assert tool.name
            assert tool.description
            assert tool.inputSchema
            assert "type" in tool.inputSchema
            assert "properties" in tool.inputSchema
            assert "required" in tool.inputSchema
    
    @pytest.mark.asyncio
    async def test_run_coupling_analysis_success(self, analysis_tools):
        """Test successful coupling analysis."""
        # Mock successful wrapper response
        mock_results = [
            {"entity": "file1.java", "coupled": "file2.java", "degree": 78, "average-revs": 10}
        ]
        analysis_tools.wrapper.run_analysis.return_value = mock_results
        
        arguments = {
            "log_file": "test.log",
            "vcs": "git2",
            "min_coupling": 50
        }
        
        result = await analysis_tools.run_coupling_analysis(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "file1.java" in result[0].text
        assert "file2.java" in result[0].text
        assert "78%" in result[0].text
    
    @pytest.mark.asyncio
    async def test_run_coupling_analysis_error(self, analysis_tools):
        """Test coupling analysis with error."""
        # Mock error from wrapper
        analysis_tools.wrapper.run_analysis.side_effect = CodeMaatError("Test error")
        
        arguments = {
            "log_file": "test.log",
            "vcs": "git2"
        }
        
        result = await analysis_tools.run_coupling_analysis(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error running coupling analysis" in result[0].text
        assert "Test error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_run_summary_analysis_success(self, analysis_tools):
        """Test successful summary analysis."""
        mock_results = [
            {"statistic": "number-of-commits", "value": 919},
            {"statistic": "number-of-entities", "value": 730}
        ]
        analysis_tools.wrapper.run_analysis.return_value = mock_results
        
        arguments = {
            "log_file": "test.log",
            "vcs": "git2"
        }
        
        result = await analysis_tools.run_summary_analysis(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Repository Summary" in result[0].text
        assert "Number Of Commits**: 919" in result[0].text
        assert "Number Of Entities**: 730" in result[0].text
    
    @pytest.mark.asyncio
    async def test_run_authors_analysis_success(self, analysis_tools):
        """Test successful authors analysis."""
        mock_results = [
            {"entity": "InfoUtils.java", "n-authors": 12, "n-revs": 60}
        ]
        analysis_tools.wrapper.run_analysis.return_value = mock_results
        
        arguments = {
            "log_file": "test.log",
            "vcs": "git2",
            "min_revs": 5,
            "rows": 20
        }
        
        result = await analysis_tools.run_authors_analysis(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Author Analysis Results" in result[0].text
        assert "InfoUtils.java" in result[0].text
        assert "Authors: 12" in result[0].text
        assert "Revisions: 60" in result[0].text
    
    @pytest.mark.asyncio
    async def test_run_churn_analysis_entity_churn(self, analysis_tools):
        """Test entity churn analysis."""
        mock_results = [
            {"entity": "file1.java", "added": 150, "deleted": 30}
        ]
        analysis_tools.wrapper.run_analysis.return_value = mock_results
        
        arguments = {
            "log_file": "test.log",
            "vcs": "git2",
            "churn_type": "entity-churn"
        }
        
        result = await analysis_tools.run_churn_analysis(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Entity Churn Analysis Results" in result[0].text
        assert "file1.java" in result[0].text
        assert "Added: 150 lines" in result[0].text
        assert "Deleted: 30 lines" in result[0].text
    
    @pytest.mark.asyncio
    async def test_run_churn_analysis_author_churn(self, analysis_tools):
        """Test author churn analysis."""
        mock_results = [
            {"author": "John Doe", "added": 1500, "deleted": 300}
        ]
        analysis_tools.wrapper.run_analysis.return_value = mock_results
        
        arguments = {
            "log_file": "test.log",
            "vcs": "git2",
            "churn_type": "author-churn"
        }
        
        result = await analysis_tools.run_churn_analysis(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Author Churn Analysis Results" in result[0].text
        assert "John Doe" in result[0].text
        assert "Added: 1500 lines" in result[0].text
        assert "Deleted: 300 lines" in result[0].text
    
    @pytest.mark.asyncio
    async def test_run_age_analysis_success(self, analysis_tools):
        """Test successful age analysis."""
        mock_results = [
            {"entity": "old_file.java", "age-months": 24},
            {"entity": "new_file.java", "age-months": 2}
        ]
        analysis_tools.wrapper.run_analysis.return_value = mock_results
        
        arguments = {
            "log_file": "test.log",
            "vcs": "git2",
            "age_time_now": "2024-01-01"
        }
        
        result = await analysis_tools.run_age_analysis(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Code Age Analysis Results" in result[0].text
        assert "old_file.java**: 24 months old" in result[0].text
        assert "new_file.java**: 2 months old" in result[0].text
    
    @pytest.mark.asyncio
    async def test_run_entity_effort_analysis_success(self, analysis_tools):
        """Test successful entity effort analysis."""
        mock_results = [
            {"entity": "file1.java", "author": "John", "author-revs": 8, "total-revs": 10}
        ]
        analysis_tools.wrapper.run_analysis.return_value = mock_results
        
        arguments = {
            "log_file": "test.log",
            "vcs": "git2"
        }
        
        result = await analysis_tools.run_entity_effort_analysis(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Entity Effort Analysis Results" in result[0].text
        assert "file1.java" in result[0].text
        assert "John" in result[0].text
        assert "8/10 (80.0%)" in result[0].text
    
    @pytest.mark.asyncio
    async def test_run_communication_analysis_success(self, analysis_tools):
        """Test successful communication analysis."""
        mock_results = [
            {"author": "Alice", "peer": "Bob", "shared": 15}
        ]
        analysis_tools.wrapper.run_analysis.return_value = mock_results
        
        arguments = {
            "log_file": "test.log",
            "vcs": "git2",
            "min_shared_revs": 5
        }
        
        result = await analysis_tools.run_communication_analysis(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Communication Analysis Results" in result[0].text
        assert "Alice" in result[0].text
        assert "Bob" in result[0].text
        assert "Shared entities: 15" in result[0].text
    
    @pytest.mark.asyncio
    async def test_empty_results(self, analysis_tools):
        """Test handling of empty results."""
        analysis_tools.wrapper.run_analysis.return_value = []
        
        arguments = {
            "log_file": "test.log",
            "vcs": "git2"
        }
        
        result = await analysis_tools.run_coupling_analysis(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "No coupling relationships found" in result[0].text
    
    def test_format_coupling_results_empty(self, analysis_tools):
        """Test formatting empty coupling results."""
        result = analysis_tools._format_coupling_results([])
        assert "No coupling relationships found" in result
    
    def test_format_coupling_results_with_data(self, analysis_tools):
        """Test formatting coupling results with data."""
        results = [
            {"entity": "file1.java", "coupled": "file2.java", "degree": 78, "average-revs": 10}
        ]
        
        result = analysis_tools._format_coupling_results(results)
        
        assert "Logical Coupling Analysis Results" in result
        assert "file1.java" in result
        assert "file2.java" in result
        assert "78%" in result
        assert "10" in result
    
    def test_format_summary_results_with_data(self, analysis_tools):
        """Test formatting summary results with data."""
        results = [
            {"statistic": "number-of-commits", "value": 919},
            {"statistic": "number-of-authors", "value": 15}
        ]
        
        result = analysis_tools._format_summary_results(results)
        
        assert "Repository Summary" in result
        assert "Number Of Commits**: 919" in result
        assert "Number Of Authors**: 15" in result