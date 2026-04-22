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

    def test_system_prompt(self):
        agent = PythonDataAnalystAgent(name="Test")
        prompt = agent._build_system_prompt()
        assert "data scientist" in prompt.lower()


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

    def test_system_prompt(self):
        agent = HypothesisTesterAgent(name="Test")
        prompt = agent._build_system_prompt()
        assert "experiment" in prompt.lower()


class TestExternalToolAgent:
    def test_call_tool_registered(self, monkeypatch):
        agent = ExternalToolAgent(name="TestTool")
        mock_wrapper = MagicMock()
        mock_wrapper.tools = {
            "get_weather": {"func": lambda city: f"Weather in {city}: sunny"}
        }
        monkeypatch.setattr(agent, '_tool_wrapper', mock_wrapper, raising=False)
        result = agent.call_tool("get_weather", city="London")
        assert result["success"] is True
        assert "sunny" in result["result"]

    def test_call_tool_unregistered(self):
        agent = ExternalToolAgent(name="TestTool")
        agent._tool_wrapper = MagicMock()
        agent._tool_wrapper.tools = {}
        result = agent.call_tool("nonexistent_tool")
        assert result["success"] is False
        assert "error" in result

    def test_register_default_tools_creates_wrapper(self):
        agent = ExternalToolAgent(name="TestTool")
        assert not hasattr(agent, '_tool_wrapper')
        agent._register_default_tools()
        assert hasattr(agent, '_tool_wrapper')
        assert "get_weather" in agent._tool_wrapper.tools
        assert "get_stock_price" in agent._tool_wrapper.tools

    def test_system_prompt(self):
        agent = ExternalToolAgent(name="Test")
        prompt = agent._build_system_prompt()
        assert "API" in prompt or "tool" in prompt.lower()
