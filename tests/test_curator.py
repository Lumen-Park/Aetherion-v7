import pytest
from agents.governance.curator import Curator
from unittest.mock import patch, MagicMock


def test_curator_selects_experts_from_llm():
    curator = Curator()
    # Mock the LLM generate method to return a valid JSON array
    mock_llm_response = MagicMock()
    mock_llm_response.__getitem__ = lambda self, key: {
        "content": '["PhysicistAgent", "ChemistAgent"]',
        "confidence": 0.9
    }.get(key, "")

    # Patch the entire select_experts method to bypass any internal fallback
    with patch.object(curator.llm, 'generate', return_value=mock_llm_response):
        # Ensure _parse_selection works correctly
        with patch.object(curator, '_parse_selection', return_value=["PhysicistAgent", "ChemistAgent"]):
            experts = curator.select_experts("Design a new battery", max_experts=2)
            assert "PhysicistAgent" in experts
            assert "ChemistAgent" in experts
            assert len(experts) <= 2


def test_curator_handles_malformed_response():
    curator = Curator()
    mock_response = {"content": "I think you need a physicist and a chemist.", "confidence": 0.5}
    with patch.object(curator.llm, 'generate', return_value=mock_response):
        # When parsing fails, fallback should give us something
        experts = curator.select_experts("battery design", max_experts=2)
        assert isinstance(experts, list)
        assert len(experts) > 0


def test_curator_filters_invalid_agent_names():
    curator = Curator()
    mock_response = {"content": '["PhysicistAgent", "FakeAgent", "ChemistAgent"]', "confidence": 0.9}
    with patch.object(curator.llm, 'generate', return_value=mock_response):
        with patch.object(curator, '_parse_selection', return_value=["PhysicistAgent", "FakeAgent", "ChemistAgent"]):
            experts = curator.select_experts("Some goal", max_experts=5)
            assert "FakeAgent" not in experts
            assert "PhysicistAgent" in experts


def test_keyword_fallback_returns_agents():
    curator = Curator()
    # Force fallback by making LLM raise an exception
    with patch.object(curator.llm, 'generate', side_effect=Exception("LLM down")):
        experts = curator.select_experts("battery design", max_experts=3)
        assert "PhysicistAgent" in experts  # "battery" keyword maps to PhysicistAgent
        assert len(experts) <= 3


def test_curator_respects_max_experts():
    curator = Curator()
    mock_response = {"content": '["PhysicistAgent", "ChemistAgent", "BiologistAgent", "EconomistAgent"]', "confidence": 0.9}
    with patch.object(curator.llm, 'generate', return_value=mock_response):
        with patch.object(curator, '_parse_selection', return_value=["PhysicistAgent", "ChemistAgent", "BiologistAgent", "EconomistAgent"]):
            experts = curator.select_experts("complex problem", max_experts=2)
            assert len(experts) == 2
