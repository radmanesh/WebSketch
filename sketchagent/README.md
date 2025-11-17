# WebSketch Agent Service

A2A Agent service for WebSketch using LangChain and LangGraph.

## Setup

1. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Copy environment file:
```bash
cp .env.example .env
```

4. Update `.env` with your OpenAI API key and other settings.

## Running

### Development
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/v1/chat` - Chat endpoint (non-streaming)
- `POST /api/v1/chat/stream` - Chat endpoint with streaming
- `POST /api/v1/session` - Create new session
- `GET /api/v1/session/{session_id}` - Get session state
- `DELETE /api/v1/session/{session_id}` - Delete session
- `GET /health` - Health check

## Architecture

- **Multi-agent workflow** using LangGraph
- **Redis** for session state management
- **FastAPI** for REST API
- **Structured logging** with observability

