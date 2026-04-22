# Contributing to Aetherion

Thank you for helping build the first autonomous AI research institution!

## Adding a New Domain Agent

1. Open `agents/colleges/all_colleges.py`.
2. Add a new class inheriting from `CollegeAgent`:

```python
class MyNewAgent(CollegeAgent):
    college = "Your College Name"
    expertise = "Brief description of expertise"

    def _build_system_prompt(self) -> str:
        return "You are an expert in..."
```

1. Add the agent name to COLLEGE_MAPPING at the bottom of the file.
2. Run python scripts/audit_agents.py to verify your agent instantiates correctly.
3. Add a test in tests/test_colleges.py.

Adding a New Council Judge

1. Open agents/council/council.py.
2. Add the judge name to the self.judges list in AetherionCouncil.__init__.
3. Add a corresponding prompt in _judge_prompt().
4. Update tests/test_council_security.py with a test for your judge.

Code Style

We use black (line length 79) and isort. Run before committing:

```bash
black agents/ core/ tests/ mission/ utils/ api/ --line-length 79
isort agents/ core/ tests/ mission/ utils/ api/
```

Testing

```bash
pytest --cov=core --cov=agents/council --cov=agents/governance
```

Coverage must remain ≥60%. New features should include tests.

Questions?

Open an issue or start a discussion. The Council is always in session.

