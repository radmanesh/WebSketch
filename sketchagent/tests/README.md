# Testing Guide

This directory contains the test suite for the WebSketch Agent service.

## Test Structure

```
tests/
├── conftest.py          # Pytest fixtures and configuration
├── fixtures.py          # Test data fixtures
├── helpers.py          # Test utility functions
├── unit/               # Unit tests for individual components
│   ├── test_analyzer_node.py
│   ├── test_modifier_node.py
│   ├── test_validator_node.py
│   └── test_executor_node.py
├── integration/        # Integration tests
│   ├── test_agent_workflow.py
│   └── test_api_endpoints.py
├── error/              # Error handling tests
│   ├── test_validation_errors.py
│   └── test_execution_errors.py
└── edge/               # Edge case tests
    ├── test_empty_sketch.py
    └── test_single_component.py
```

## Running Tests

### Run All Tests
```bash
poetry run pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
poetry run pytest tests/unit/

# Integration tests only
poetry run pytest tests/integration/

# Error handling tests
poetry run pytest tests/error/

# Edge case tests
poetry run pytest tests/edge/
```

### Run with Markers
```bash
# Run only unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration

# Run error tests
poetry run pytest -m error

# Run edge case tests
poetry run pytest -m edge
```

### Run Specific Test File
```bash
poetry run pytest tests/unit/test_validator_node.py
```

### Run Specific Test Function
```bash
poetry run pytest tests/unit/test_validator_node.py::TestValidatorNode::test_validate_success -v
```

### Run with Coverage
```bash
poetry run pytest --cov=app --cov-report=html
```

### Verbose Output
```bash
poetry run pytest -v
```

### Stop on First Failure
```bash
poetry run pytest -x
```

## Test Fixtures

### Available Fixtures

- `sample_sketch`: A sample sketch with multiple components
- `empty_sketch`: An empty sketch
- `single_component_sketch`: A sketch with a single component
- `mock_llm_service`: Mock LLM service for testing
- `mock_redis_service`: Mock Redis service with in-memory storage
- `agent_state`: Sample agent state

## Writing New Tests

### Unit Test Example
```python
import pytest
from ..fixtures import create_sample_sketch
from ..helpers import create_agent_state, assert_state_step
from ...app.agent.nodes.analyzer import analyze_node

@pytest.mark.unit
class TestMyNode:
    def test_my_function(self, sample_sketch):
        state = create_agent_state(
            current_sketch=sample_sketch,
            step="analyze",
        )
        result = analyze_node(state)
        assert_state_step(result, "modify")
```

### Integration Test Example
```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestMyAPI:
    def test_my_endpoint(self, test_client):
        response = test_client.get("/api/v1/endpoint")
        assert response.status_code == 200
```

## Debug Mode

To enable debug endpoints and enhanced logging:

1. Set `LOG_LEVEL=DEBUG` in your `.env` file, or
2. Set `DEBUG_MODE=true` in your `.env` file

Debug endpoints (only available in DEBUG mode):
- `GET /api/v1/debug/state/{session_id}` - Inspect agent state
- `POST /api/v1/debug/test-node` - Test individual nodes
- `GET /api/v1/debug/graph/{session_id}` - View graph execution history

## Test Coverage

Aim for high test coverage. Run coverage reports regularly:

```bash
poetry run pytest --cov=app --cov-report=term-missing
```

## Continuous Integration

Tests should pass before committing. Run:

```bash
poetry run pytest
poetry run black .
poetry run ruff check .
poetry run mypy app
```

