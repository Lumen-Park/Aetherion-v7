import pytest
from utils.sandbox import SandboxExecutor

def test_sandbox_with_gvisor():
    executor = SandboxExecutor(runtime="runsc", timeout=5)
    code = "print('Hello from gVisor')"
    result = executor.run(code)
    assert result["passed"] is True
    assert "Hello from gVisor" in result["stdout"]

def test_sandbox_with_docker_fallback():
    executor = SandboxExecutor(runtime="runc", timeout=5)
    code = "print('Hello from Docker')"
    result = executor.run(code)
    assert result["passed"] is True
    assert "Hello from Docker" in result["stdout"]
