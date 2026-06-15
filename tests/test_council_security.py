from unittest.mock import patch

import pytest

from agents.council.council import AetherionCouncil, JudgeVote, Verdict


def test_security_veto_blocks_approval():
    council = AetherionCouncil()
    mock_votes = [
        JudgeVote("Critic", Verdict.APPROVE, 0.9, 8.0, "Good"),
        JudgeVote("Security", Verdict.REJECT, 0.95, 0.0, "eval() detected"),
        JudgeVote("Alignment", Verdict.APPROVE, 0.8, 7.5, "Aligned"),
        JudgeVote("Constraint", Verdict.APPROVE, 0.7, 7.0, "OK"),
        JudgeVote("Evaluator", Verdict.APPROVE, 0.85, 8.2, "Solid"),
        JudgeVote("Documentation", Verdict.APPROVE, 0.6, 6.5, "Clear"),
        JudgeVote("AetherionPrime", Verdict.APPROVE, 0.8, 7.8, "Safe"),
    ]
    with patch.object(council, "_collect_votes", return_value=mock_votes):
        verdict = council.deliberate("code with eval()", "Write safe code")
        assert verdict["verdict"] == "REJECTED"
        assert verdict["reason"].startswith("Security absolute veto")
        assert verdict["score"] == 0.0


def test_security_veto_overrides_majority():
    council = AetherionCouncil()
    mock_votes = [
        JudgeVote("Critic", Verdict.APPROVE, 0.9, 9.0, "Excellent"),
        JudgeVote("Security", Verdict.REJECT, 1.0, 0.0, "Unsafe pattern"),
        JudgeVote("Alignment", Verdict.APPROVE, 0.9, 9.0, "Perfect"),
        JudgeVote("Constraint", Verdict.APPROVE, 0.9, 9.0, "Within scope"),
        JudgeVote("Evaluator", Verdict.APPROVE, 0.9, 9.0, "High quality"),
        JudgeVote(
            "Documentation", Verdict.APPROVE, 0.9, 9.0, "Well documented"
        ),
        JudgeVote("AetherionPrime", Verdict.APPROVE, 0.9, 9.0, "Approve"),
    ]
    with patch.object(council, "_collect_votes", return_value=mock_votes):
        verdict = council.deliberate("some output", "some goal")
        assert verdict["verdict"] == "REJECTED"
        assert verdict["reason"].startswith("Security absolute veto")
        assert verdict["score"] == 0.0


def test_majority_approval_without_veto():
    council = AetherionCouncil()
    mock_votes = [
        JudgeVote("Critic", Verdict.APPROVE, 0.9, 8.0, "Good"),
        JudgeVote("Security", Verdict.APPROVE, 0.9, 8.0, "Safe"),
        JudgeVote("Alignment", Verdict.APPROVE, 0.8, 7.5, "Aligned"),
        JudgeVote("Constraint", Verdict.APPROVE, 0.7, 7.0, "OK"),
        JudgeVote("Evaluator", Verdict.APPROVE, 0.85, 8.2, "Solid"),
        JudgeVote("Documentation", Verdict.APPROVE, 0.6, 6.5, "Clear"),
        JudgeVote("AetherionPrime", Verdict.APPROVE, 0.8, 7.8, "Safe"),
    ]
    with patch.object(council, "_collect_votes", return_value=mock_votes):
        verdict = council.deliberate("safe code", "Write safe code")
        assert verdict["verdict"] == "APPROVED"
        assert verdict["score"] > 0.0


def test_revision_required_on_split():
    council = AetherionCouncil()
    mock_votes = [
        JudgeVote("Critic", Verdict.REJECT, 0.6, 4.0, "Needs work"),
        JudgeVote("Security", Verdict.APPROVE, 0.8, 7.0, "OK"),
        JudgeVote("Alignment", Verdict.APPROVE, 0.7, 6.0, "Acceptable"),
        JudgeVote("Constraint", Verdict.APPROVE, 0.7, 6.0, "OK"),
        JudgeVote("Evaluator", Verdict.APPROVE, 0.5, 5.0, "Average"),
        JudgeVote("Documentation", Verdict.REJECT, 0.4, 3.0, "Unclear"),
        JudgeVote("AetherionPrime", Verdict.ABSTAIN, 0.5, 5.0, "Split"),
    ]
    with patch.object(council, "_collect_votes", return_value=mock_votes):
        verdict = council.deliberate("mediocre output", "goal")
        assert verdict["verdict"] in ("REVISION_REQUIRED", "REJECTED")
