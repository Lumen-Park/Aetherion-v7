import pytest
from unittest.mock import patch, MagicMock
from agents.colleges.all_colleges import (
    PythonDataAnalystAgent,
    HypothesisTesterAgent,
    ExternalToolAgent,
)


class TestPythonDataAnalystAgent:
    def test_run_analysis_without_data(self):
        agent = PythonDataAnalystAgent(name="TestAnalyst")
        with patch('utils.sandbox.SandboxExecutor') as mock_sandbox:
            mock_sandbox.return_value.run.return_value = {
                "passed": True,
                "stdout": "result",
                "stderr": "",
            }
            with patch.object(agent.llm, 'generate') as mock_gen:
                mock_gen.return_value = {"content": "interpretation"}
                result = agent.run_analysis("print('hello')")
                assert result["success"] is True
                assert result["stdout"] == "result"
                assert result["analysis"] == "interpretation"

    def test_run_analysis_with_data(self):
        agent = PythonDataAnalystAgent(name="TestAnalyst")
        with patch('utils.sandbox.SandboxExecutor') as mock_sandbox:
            mock_sandbox.return_value.run.return_value = {
                "passed": False,
                "stdout": "",
                "stderr": "error",
            }
            with patch.object(agent.llm, 'generate') as mock_gen:
                mock_gen.return_value = {"content": "error interpretation"}
                result = agent.run_analysis("code", data={"x": 1})
                assert result["success"] is False
                assert result["stderr"] == "error"


class TestHypothesisTesterAgent:
    def test_design_experiment(self):
        agent = HypothesisTesterAgent(name="TestHypothesis")
        with patch.object(agent.llm, 'generate') as mock_gen:
            mock_gen.return_value = {"content": "experiment design", "confidence": 0.8}
            result = agent.design_experiment("H0", ["var1", "var2"])
            assert result["design"] == "experiment design"
            assert result["confidence"] == 0.8

    def test_evaluate_results_supported(self):
        agent = HypothesisTesterAgent(name="TestHypothesis")
        with patch.object(agent.llm, 'generate') as mock_gen:
            mock_gen.return_value = {
                "content": '{"verdict": "supported", "confidence": 0.9, "reasoning": "clear"}'
            }
            result = agent.evaluate_results("H0", {}, "analysis")
            assert result["verdict"] == "supported"
            assert result["confidence"] == 0.9

    def test_evaluate_results_parse_failure(self):
        agent = HypothesisTesterAgent(name="TestHypothesis")
        with patch.object(agent.llm, 'generate') as mock_gen:
            mock_gen.return_value = {"content": "not json"}
            result = agent.evaluate_results("H0", {}, "analysis")
            assert result["verdict"] == "inconclusive"
            assert result["confidence"] == 0.5


class TestExternalToolAgent:
    def test_call_tool_registered(self):
        agent = ExternalToolAgent(name="TestTool")
        # Ensure tools are registered
        agent._register_default_tools()
        result = agent.call_tool("get_weather", city="London")
        assert result["success"] is True
        assert "result" in result

    def test_call_tool_unregistered(self):
        agent = ExternalToolAgent(name="TestTool")
        result = agent.call_tool("nonexistent_tool")
        assert result["success"] is False
        assert "error" in result

    def test_get_weather_tool(self):
        agent = ExternalToolAgent(name="TestTool")
        agent._register_default_tools()
        tool_func = agent._tool_wrapper.tools["get_weather"]["func"]
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.return_value.read.return_value = b"Sunny 20C"
            result = tool_func("London")
            assert "Sunny" in result

    def test_get_stock_price_tool_no_key(self):
        agent = ExternalToolAgent(name="TestTool")
        agent._register_default_tools()
        tool_func = agent._tool_wrapper.tools["get_stock_price"]["func"]
        with patch.dict('os.environ', {}, clear=True):
            result = tool_func("AAPL")
            assert "API key not configured" in result
