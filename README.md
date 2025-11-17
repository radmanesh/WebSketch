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
- OpenAI API key

### Setup

1. Clone the repository
2. Create environment files:
   - `sketchagent/.env` (see `sketchagent/.env.example`)
   - Set `OPENAI_API_KEY` in the environment file

3. Run with Docker Compose:
```bash
docker-compose up
```

This will start:
- Redis (port 6379)
- Python Agent Service (port 8000)
- Next.js Frontend (port 3000)

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

## Features

- Interactive wireframe canvas
- AI-powered layout modifications via natural language
- Session management with Redis
- Multi-agent architecture using LangGraph
- Streaming API responses
- Undo/redo support (operation history)

## API Documentation

The Python agent service provides a REST API at `http://localhost:8000`:

- `POST /api/v1/chat` - Chat endpoint
- `POST /api/v1/chat/stream` - Streaming chat endpoint
- `POST /api/v1/session` - Create session
- `GET /api/v1/session/{id}` - Get session
- `DELETE /api/v1/session/{id}` - Delete session

See `sketchagent/README.md` for more details.
