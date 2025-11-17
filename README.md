## Overview

- **Frontend**: Next.js (port `3000`) interactive canvas
- **SketchAgent**: FastAPI + LangGraph service (port `8000`)
- **Redis**: Session persistence (port `6379`)
- **Documentation**: See `sketchagent/ARCHITECTURE.md` for detailed architecture and workflow
# WebSketch

A web-based wireframe sketch tool with AI-powered layout modification capabilities.

## Project Structure

```
WebSketch/
├── frontend/          # Next.js frontend application
├── sketchagent/       # Python A2A agent service
└── docker-compose.yml # Unified orchestrator
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.12 + Poetry (for local agent dev)
- OpenAI API key (`OPENAI_API_KEY`)

### Setup

1. Clone the repository
2. Create environment files:
   - `sketchagent/.env` (copy from `.env.example`)
   - Set `OPENAI_API_KEY`, `REDIS_URL`, and optional `DEBUG_MODE`

3. Run everything via Docker Compose:

```bash
docker-compose up
```

Services exposed:

| Service    | Port | Description                |
|------------|------|----------------------------|
| Frontend   | 3000 | Next.js wireframe studio   |
| SketchAgent| 8000 | FastAPI + LangGraph agent  |
| Redis      | 6379 | Session store              |

> Need detailed internals? See `sketchagent/ARCHITECTURE.md`.

### Development

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Python Agent
```bash
cd sketchagent
poetry install
poetry run uvicorn app.main:app --reload
```

#### Running Tests
```bash
cd sketchagent
poetry run pytest
```

Add coverage:
```bash
poetry run pytest --cov=app --cov-report=html
```

## Features

- Interactive wireframe canvas
- AI-powered layout modifications via natural language
- Session management with Redis
- Multi-agent architecture using LangGraph (Analyze → Modify → Validate → Execute)
- Streaming API responses with SSE
- Undo/redo support via Redis operation history
- Debug endpoints (`/api/v1/debug/*`) when `DEBUG_MODE=true`

## API Documentation

The Python agent service provides a REST API at `http://localhost:8000`:

- `POST /api/v1/chat` - Chat endpoint
- `POST /api/v1/chat/stream` - Streaming chat endpoint
- `POST /api/v1/session` - Create session
- `GET /api/v1/session/{id}` - Get session
- `DELETE /api/v1/session/{id}` - Delete session
- `GET /api/v1/debug/state/{id}` - Inspect session state (debug mode)
- `POST /api/v1/debug/test-node` - Run a single node (debug mode)

See `sketchagent/ARCHITECTURE.md` for detailed architecture, workflows, and data flow.
