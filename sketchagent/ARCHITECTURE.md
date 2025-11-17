# WebSketch Agent - Architecture & Workflow Documentation

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Agent Workflow](#agent-workflow)
4. [Node Details](#node-details)
5. [State Management](#state-management)
6. [Services](#services)
7. [API Endpoints](#api-endpoints)
8. [Data Flow](#data-flow)
9. [Error Handling](#error-handling)
10. [Testing & Debugging](#testing--debugging)

---

## Overview

The WebSketch Agent is an AI-powered service that processes natural language requests to modify web wireframe sketches. It uses a multi-agent workflow built with LangGraph to analyze, plan, validate, and execute modifications to sketch layouts.

### Key Features

- **Natural Language Processing**: Converts user requests into sketch modifications
- **Multi-Agent Workflow**: Four specialized agents work together (Analyzer, Modifier, Validator, Executor)
- **Session Management**: Maintains state across multiple requests using Redis
- **Operation Validation**: Ensures all modifications are valid before execution
- **Error Recovery**: Graceful error handling with fallback mechanisms

---

## System Architecture

### High-Level Architecture

```
┌──────────────┐
│   Frontend   │   Next.js (Port 3000)
└──────┬───────┘
       │  HTTP/REST
       ▼
┌─────────────────────────────────────────────┐
│           SketchAgent Service               │
│             FastAPI (Port 8000)             │
├─────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────┐ │
│ │            API Layer (FastAPI)          │ │
│ │  • /api/v1/chat                         │ │
│ │  • /api/v1/session                      │ │
│ │  • /api/v1/debug/* (debug mode)         │ │
│ └───────────────┬─────────────────────────┘ │
│                 │                           │
│ ┌───────────────▼─────────────────────────┐ │
│ │        Agent Workflow (LangGraph)       │ │
│ │ ┌────────┐  ┌────────┐  ┌────────┐      │ │
│ │ │Analyzer│→ │Modifier│→ │Validator│→┐   │ │
│ │ └────────┘  └────────┘  └────────┘ │    │ │
│ │                                  ┌─▼─┐  │ │
│ │                                  │Exe│  │ │
│ │                                  │cut│  │ │
│ │                                  │or │  │ │
│ │                                  └───┘  │ │
│ └─────────────────────────────────────────┘ │
│                 │                           │
│ ┌───────────────▼─────────────────────────┐ │
│ │            Services Layer               │ │
│ │  • LLMService (OpenAI)                  │ │
│ │  • RedisService (Session State)         │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
         │                         │
         ▼                         ▼
┌──────────────┐         ┌────────────────┐
│ Redis (6379) │         │  OpenAI API    │
└──────────────┘         └────────────────┘
```

### Component Overview

1. **API Layer** (`app/api/`): FastAPI routes handling HTTP requests
2. **Agent Workflow** (`app/agent/`): LangGraph state machine with 4 nodes
3. **Services** (`app/services/`): LLM and Redis service abstractions
4. **Tools** (`app/tools/`): Sketch parsing and operation execution
5. **Schemas** (`app/schemas/`): Pydantic models for data validation

---

## Agent Workflow

The agent uses **LangGraph** to orchestrate a multi-step workflow. Each step is handled by a specialized node.

### Workflow Graph

```
          ┌────────┐
          │ START  │
          └────┬───┘
               │
               ▼
      ┌──────────────────┐
      │   ANALYZE        │  Analyze sketch layout
      │ (analyzer node)  │  • Parse components
      └──────┬───────────┘  • Identify relationships
             │              • Generate stats
             ▼
      ┌──────────────────┐
      │   MODIFY         │  Generate operations
      │ (modifier node)  │  • Build prompts
      └──────┬───────────┘  • Call LLM & parse JSON
             │              • Produce operations
             ▼
      ┌──────────────────┐
      │   VALIDATE       │  Validate operations
      │ (validator node) │  • Check IDs & coords
      └──────┬───────────┘  • Enforce constraints
             │
             ▼
      ┌──────────────────┐
      │   EXECUTE        │  Execute operations
      │ (executor node)  │  • Apply to sketch
      └──────┬───────────┘  • Validate result
             │
             ▼
          ┌──────┐
          │ END  │
          └──────┘
```

### State Transitions

Each node updates the `step` field in the state to control flow:

- `analyze` → `modify` (after analysis)
- `modify` → `validate` (after operation generation)
- `validate` → `execute` (after validation passes)
- `execute` → `complete` (after execution)
- Any node → `error` (on failure)

### Conditional Routing

Each node has a routing function that determines the next step:

- **After Analyze**: `should_continue_after_analyze()` → `modify` or `end`
- **After Modify**: `should_continue_after_modify()` → `validate` or `end`
- **After Validate**: `should_continue_after_validate()` → `execute` or `end`
- **After Execute**: `should_continue_after_execute()` → `end`

If `step == "error"`, all routing functions return `end` to terminate the workflow.

---

## Node Details

### 1. Analyzer Node (`analyze_node`)

**Purpose**: Analyze the current sketch layout and extract structural information.

**Input**:
- `current_sketch`: List of PlacedComponent objects

**Process**:
1. Parse sketch layout using `parse_sketch_layout()`
2. Calculate canvas bounds
3. Generate component descriptions
4. Identify spatial relationships (above, below, left, right, overlapping, aligned)
5. Analyze layout structure (columns, sections, groups)
6. Generate overall description

**Output**:
- `layout_analysis`: LayoutAnalysis object containing:
  - `description`: Human-readable layout description
  - `components`: List of component descriptions
  - `spatialRelationships`: List of relationships between components
  - `layoutStats`: Statistics (component count, types, groups)

**State Changes**:
- Sets `step = "modify"`
- Sets `layout_analysis` with analysis results

**Error Handling**:
- On failure: Sets `step = "error"` and `error = "Analysis failed: {error}"`

---

### 2. Modifier Node (`modify_node`)

**Purpose**: Generate modification operations from user intent using LLM.

**Input**:
- `user_message`: Natural language request
- `layout_analysis`: Analysis from analyzer node
- `current_sketch`: Current sketch state

**Process**:
1. Build system prompt with operation schema and guidelines
2. Build user prompt with:
   - Layout description
   - Component details
   - Spatial relationships
   - Current sketch JSON
   - User's request
3. Call LLM service with prompts
4. Parse JSON response (handles markdown code blocks)
5. Validate and create `SketchModification` object
6. Extract operations list

**Output**:
- `operations`: List of ComponentOperation objects
- `modification`: SketchModification with operations, reasoning, and description

**State Changes**:
- Sets `step = "validate"`
- Sets `operations` and `modification`

**Error Handling**:
- JSON parsing errors: Sets `step = "error"` with parsing error
- LLM errors: Sets `step = "error"` with LLM error message
- Validation errors: Sets `step = "error"` with validation error

**LLM Prompt Structure**:
- **System Prompt**: Defines operation types, component types, coordinate system, and response format
- **User Prompt**: Includes layout analysis, current sketch JSON, and user request

---

### 3. Validator Node (`validate_node`)

**Purpose**: Validate operations before execution to ensure they're safe and correct.

**Input**:
- `operations`: List of ComponentOperation objects
- `current_sketch`: Current sketch state

**Process**:
1. Check if operations exist
2. Check if current_sketch exists
3. For each operation:
   - Validate operation type
   - Check required fields (componentId, coordinates, dimensions)
   - Verify component exists (for move/resize/delete)
   - Validate dimensions (minimum sizes)
   - Check target IDs (for align/distribute)
4. Return validation result

**Validation Rules**:
- **Move/Resize/Delete/Modify**: Requires `componentId` and component must exist
- **Move**: Requires `x` and `y` coordinates
- **Resize**: Requires `width` and `height` (min 20px, except HorizontalLine: 2px)
- **Add**: Requires `componentType`, `x`, `y`, `width`, `height`
- **Align**: Requires at least 2 `targetIds` and `alignment` type
- **Distribute**: Requires at least 2 `targetIds` and `spacing` value

**Output**:
- Validation passes: Sets `step = "execute"`
- Validation fails: Sets `step = "error"` with error message

**State Changes**:
- On success: Sets `step = "execute"`
- On failure: Sets `step = "error"` and `error = "Validation failed: {details}"`

---

### 4. Executor Node (`execute_node`)

**Purpose**: Execute validated operations and apply them to the sketch.

**Input**:
- `operations`: Validated list of ComponentOperation objects
- `current_sketch`: Current sketch state

**Process**:
1. Check if operations exist
2. Execute operations sequentially:
   - **Move**: Update component x, y coordinates
   - **Resize**: Update component width, height (enforce minimums)
   - **Add**: Create new component with generated ID
   - **Delete**: Remove component from sketch
   - **Modify**: Update component properties
   - **Align**: Align multiple components (left/right/center/top/bottom)
   - **Distribute**: Distribute components with spacing
3. Validate result (check all components meet size requirements)
4. Update state with modified sketch

**Output**:
- `modified_sketch`: New sketch with operations applied
- `latest_sketch`: Updated latest sketch for fallback

**State Changes**:
- On success: Sets `step = "complete"`, `modified_sketch`, and `latest_sketch`
- On failure: Sets `step = "error"` and falls back to `latest_sketch` or `initial_sketch`

**Post-Execution Validation**:
- All components must have valid dimensions
- Width >= 20px (except HorizontalLine)
- Height >= 2px (HorizontalLine) or >= 20px (others)

---

## State Management

### AgentState Structure

The `AgentState` is a TypedDict that flows through the entire workflow:

```python
{
    # Session Management
    "session_id": str,

    # Input
    "user_message": str,
    "current_sketch": list[PlacedComponent],
    "message_history": Optional[list[dict]],

    # Analysis Step Output
    "layout_analysis": Optional[LayoutAnalysis],

    # Modification Step Output
    "operations": Optional[list[ComponentOperation]],
    "modification": Optional[SketchModification],

    # Execution Step Output
    "modified_sketch": Optional[list[PlacedComponent]],

    # State Tracking
    "step": str,  # "analyze" | "modify" | "validate" | "execute" | "complete" | "error"
    "error": Optional[str],

    # Fallback Data
    "initial_sketch": list[PlacedComponent],
    "latest_sketch": list[PlacedComponent],
    "retry_count": int,
}
```

### State Flow Through Nodes

```
Initial State:
  step = "analyze"
  layout_analysis = None
  operations = None
  modification = None
  modified_sketch = None

After Analyzer:
  step = "modify"
  layout_analysis = {...}  ✓

After Modifier:
  step = "validate"
  operations = [...]  ✓
  modification = {...}  ✓

After Validator:
  step = "execute"
  (operations validated)  ✓

After Executor:
  step = "complete"
  modified_sketch = [...]  ✓
  latest_sketch = [...]  ✓
```

### Session State (Redis)

Sessions are stored in Redis with the following structure:

```json
{
  "session_id": "uuid",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp",
  "initial_sketch": [...],
  "latest_sketch": [...],
  "current_sketch": [...],
  "operation_history": [...],
  "message_history": [...]
}
```

**Session Lifecycle**:
1. **Creation**: When first request comes without `session_id`, a new session is created
2. **Update**: Each successful modification updates `current_sketch` and adds to `operation_history`
3. **TTL**: Sessions expire after 1 hour of inactivity
4. **Retrieval**: Subsequent requests with `session_id` load previous state

---

## Services

### LLM Service (`LLMService`)

**Purpose**: Interface with OpenAI's API to generate modification operations.

**Features**:
- Async/await support
- Retry logic (3 attempts with exponential backoff)
- Error handling and logging
- Configurable model and temperature

**Configuration**:
- Model: `gpt-4o-mini` (default, configurable)
- Temperature: `0.3` (default, configurable)
- Retry: 3 attempts with exponential backoff (2-10 seconds)

**Methods**:
- `invoke(system_prompt, user_prompt, session_id)`: Call LLM and return response text

**Error Handling**:
- Raises `LLMError` on API failures
- Retries on transient errors
- Logs all requests/responses (sanitized)

---

### Redis Service (`RedisService`)

**Purpose**: Manage session state persistence.

**Features**:
- Async Redis operations
- Session TTL management (1 hour)
- Operation history tracking
- Message history tracking

**Key Structure**:
- Key format: `sketchagent:session:{session_id}`
- TTL: 3600 seconds (1 hour)

**Methods**:
- `create_session(initial_sketch, session_id)`: Create new session
- `get_session(session_id)`: Retrieve session data
- `update_session(session_id, **kwargs)`: Update session (sketch, operations, messages)
- `delete_session(session_id)`: Delete session
- `get_latest_sketch(session_id)`: Get latest sketch for fallback
- `extend_session_ttl(session_id)`: Extend session expiration

**Session Data Structure**:
- `initial_sketch`: Original sketch when session was created
- `latest_sketch`: Most recent successful modification
- `current_sketch`: Current state (may be modified)
- `operation_history`: List of all operations applied (for undo/redo)
- `message_history`: Conversation history

---

## API Endpoints

### Chat Endpoints

#### `POST /api/v1/chat`

Non-streaming chat endpoint that processes a user request and returns the modified sketch.

**Request**:
```json
{
  "message": "Move the input field to the right",
  "currentSketch": [...],
  "messageHistory": [...],
  "sessionId": "optional-session-id"
}
```

**Response**:
```json
{
  "success": true,
  "modifiedSketch": [...],
  "operations": [...],
  "reasoning": "Moved input component 200px to the right",
  "description": "Input field repositioned",
  "sessionId": "session-uuid"
}
```

**Process**:
1. Get or create session
2. Initialize agent state
3. Run agent graph
4. Update session with results
5. Return response

---

#### `POST /api/v1/chat/stream`

Streaming chat endpoint using Server-Sent Events (SSE).

**Response Events**:
- `analysis`: Analysis step in progress
- `modification`: Modification step in progress
- `validation`: Validation step in progress
- `execution`: Execution step in progress
- `result`: Final result
- `error`: Error occurred

---

### Session Endpoints

#### `POST /api/v1/session`

Create a new session with an initial sketch.

**Request**: Array of PlacedComponent objects

**Response**:
```json
{
  "sessionId": "uuid",
  "createdAt": "ISO timestamp"
}
```

---

#### `GET /api/v1/session/{session_id}`

Get current session state.

**Response**:
```json
{
  "sessionId": "uuid",
  "createdAt": "ISO timestamp",
  "updatedAt": "ISO timestamp",
  "currentSketch": [...],
  "operationHistory": [...]
}
```

---

#### `DELETE /api/v1/session/{session_id}`

Delete a session and all its data.

---

### Debug Endpoints (DEBUG mode only)

#### `GET /api/v1/debug/state/{session_id}`

Inspect current agent state for a session.

#### `POST /api/v1/debug/test-node`

Test an individual node in isolation with custom state.

**Request**:
```json
{
  "node_name": "analyze|modify|validate|execute",
  "state_data": {...}
}
```

#### `GET /api/v1/debug/graph/{session_id}`

View graph execution history for a session.

---

## Data Flow

### Complete Request Flow

```
1. Frontend sends POST /api/v1/chat
   ↓
2. API routes.py receives ChatRequest
   ↓
3. _process_chat_request() called
   ↓
4. Get or create session in Redis
   ↓
5. Initialize AgentState:
   - session_id
   - user_message
   - current_sketch (from session or request)
   - step = "analyze"
   ↓
6. Create agent graph
   ↓
7. Run graph.astream(initial_state, config)
   ↓
8. ANALYZE NODE:
   - Parse sketch layout
   - Generate layout analysis
   - step = "modify"
   ↓
9. MODIFY NODE:
   - Build prompts
   - Call LLM service
   - Parse JSON response
   - Create operations
   - step = "validate"
   ↓
10. VALIDATE NODE:
    - Validate operations
    - Check component IDs
    - Verify coordinates/dimensions
    - step = "execute"
    ↓
11. EXECUTE NODE:
    - Apply operations to sketch
    - Validate result
    - step = "complete"
    ↓
12. Update Redis session:
    - current_sketch = modified_sketch
    - operation_history.append(operations)
    ↓
13. Return ChatResponse to frontend
```

### Error Flow

If any node fails:

```
Node detects error
  ↓
Sets step = "error"
Sets error = "Error message"
  ↓
Routing function returns "end"
  ↓
Graph terminates
  ↓
_process_chat_request() catches error
  ↓
Falls back to latest_sketch or initial_sketch
  ↓
Updates session with fallback
  ↓
Returns ChatResponse with success=False
```

---

## Error Handling

### Error Types

1. **AgentError**: Base exception for agent errors
2. **ValidationError**: Operation validation failures
3. **ExecutionError**: Operation execution failures
4. **LLMError**: LLM API failures
5. **RedisError**: Redis operation failures

### Error Recovery

**At Node Level**:
- Each node catches exceptions and sets `step = "error"`
- Error message stored in `state["error"]`
- Node returns state with error flag

**At Graph Level**:
- Routing functions check for `step == "error"` and return `"end"`
- Graph terminates gracefully

**At API Level**:
- Catches `AgentError` exceptions
- Falls back to `latest_sketch` or `initial_sketch`
- Returns `ChatResponse` with `success=False` and error details
- Never crashes - always returns valid response

### Fallback Strategy

1. **Primary**: Use `modified_sketch` from executor
2. **Secondary**: Use `latest_sketch` from state
3. **Tertiary**: Use `initial_sketch` from state
4. **Last Resort**: Use `current_sketch` from request

---

## Testing & Debugging

### Running Tests

```bash
# All tests
poetry run pytest

# Specific categories
poetry run pytest -m unit
poetry run pytest -m integration
poetry run pytest -m error
poetry run pytest -m edge

# With coverage
poetry run pytest --cov=app --cov-report=html
```

### Debug Mode

Enable debug mode by setting `LOG_LEVEL=DEBUG` or `DEBUG_MODE=true` in `.env`.

**Debug Features**:
- Enhanced logging with state snapshots
- Node execution timing
- LLM request/response logging (sanitized)
- Debug API endpoints enabled

### Debug Endpoints Usage

**Inspect State**:
```bash
curl -H "X-API-Key: your-key" \
  http://localhost:8000/api/v1/debug/state/{session_id}
```

**Test Individual Node**:
```bash
curl -X POST -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"node_name": "analyze", "state_data": {...}}' \
  http://localhost:8000/api/v1/debug/test-node
```

### Logging

Structured logging using `structlog`:
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Format**: JSON (production) or console (development)
- **Context**: Session ID, node name, operation type, etc.

**Example Log Entry**:
```json
{
  "event": "Node execution completed",
  "node": "modify",
  "session_id": "abc-123",
  "duration_seconds": 2.345
}
```

---

## Component Types

The agent supports the following component types:

- **Container**: Generic container/box
- **Button**: Clickable button element
- **Input**: Text input field
- **ImagePlaceholder**: Image placeholder with X mark
- **Text**: Text content block
- **HorizontalLine**: Horizontal divider line (min height: 2px)
- **Heading**: Heading/title text
- **Footer**: Footer section
- **NavigationBox**: Navigation menu
- **List**: List of items (bulleted)
- **Table**: Data table with rows and columns

---

## Operation Types

The agent can perform these operations:

1. **move**: Move component to new position
   - Requires: `componentId`, `x`, `y`

2. **resize**: Change component dimensions
   - Requires: `componentId`, `width`, `height`
   - Constraints: width >= 20px, height >= 20px (2px for HorizontalLine)

3. **add**: Add new component
   - Requires: `componentType`, `x`, `y`, `width`, `height`
   - Generates unique ID: `component-{timestamp}-{random}`

4. **delete**: Remove component
   - Requires: `componentId`

5. **modify**: Change component properties
   - Requires: `componentId`, `props`

6. **align**: Align multiple components
   - Requires: `targetIds` (array), `alignment` (left/right/center/top/bottom)

7. **distribute**: Distribute components with spacing
   - Requires: `targetIds` (array), `spacing` (number)

---

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key (required)
- `OPENAI_MODEL`: Model name (default: `gpt-4o-mini`)
- `OPENAI_TEMPERATURE`: Temperature (default: `0.3`)
- `REDIS_URL`: Redis connection URL (default: `redis://localhost:6379`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `LOG_JSON`: JSON logging format (default: `false`)
- `DEBUG_MODE`: Enable debug mode (default: `false`)
- `API_KEY`: Optional API key for authentication
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

---

## Performance Considerations

### LLM Calls
- **Retry Logic**: 3 attempts with exponential backoff
- **Timeout**: Handled by LangChain/OpenAI SDK
- **Caching**: Not currently implemented (future enhancement)

### Redis Operations
- **TTL**: Sessions expire after 1 hour
- **Connection Pooling**: Handled by redis.asyncio
- **Serialization**: JSON serialization for session data

### Graph Execution
- **Async**: All nodes are async-capable
- **State Updates**: Incremental updates through graph
- **Memory**: Uses MemorySaver for checkpointing (in-memory)

---

## Future Enhancements

### Potential Improvements

1. **Retry Logic**: Add retry mechanism for failed operations
2. **Operation History**: Implement undo/redo functionality
3. **Caching**: Cache LLM responses for similar requests
4. **Batch Operations**: Support multiple operations in single request
5. **Graph Persistence**: Store graph execution history for debugging
6. **Metrics**: Add Prometheus metrics for monitoring
7. **Rate Limiting**: Add rate limiting per session
8. **WebSocket**: Real-time updates via WebSocket

---

## Glossary

- **Agent State**: The TypedDict that flows through the LangGraph workflow
- **Component**: A UI element in the sketch (Button, Input, etc.)
- **Operation**: A modification action (move, resize, add, delete, etc.)
- **Session**: A persistent state container in Redis
- **Sketch**: A collection of placed components representing a wireframe
- **Node**: A processing step in the LangGraph workflow
- **Layout Analysis**: Structured analysis of component positions and relationships

---

## References

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **LangChain Documentation**: https://python.langchain.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Redis Documentation**: https://redis.io/docs/

---

*Last Updated: 2024*
