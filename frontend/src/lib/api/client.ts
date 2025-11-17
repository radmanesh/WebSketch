/**
 * API client for communicating with Python agent service
 */

// Use window.location.origin in browser, fallback to env var or localhost
const getAgentApiUrl = () => {
  if (typeof window !== 'undefined') {
    // In browser, use same origin or env var
    return process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8000';
  }
  return process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8000';
};

const AGENT_API_URL = getAgentApiUrl();

export interface ChatRequest {
  message: string;
  currentSketch: any[];
  messageHistory?: Array<{ role: string; content: string; timestamp?: string }>;
  sessionId?: string;
}

export interface ChatResponse {
  success: boolean;
  modifiedSketch: any[];
  operations: any[];
  reasoning: string;
  description: string;
  sessionId: string;
}

export interface ErrorResponse {
  success: false;
  error: string;
  sessionId?: string;
}

export interface SessionCreateResponse {
  sessionId: string;
  createdAt: string;
}

class AgentAPIClient {
  private baseUrl: string;
  private sessionId: string | null = null;

  constructor(baseUrl: string = AGENT_API_URL) {
    this.baseUrl = baseUrl;
    // Try to get session ID from localStorage
    if (typeof window !== 'undefined') {
      this.sessionId = localStorage.getItem('sketchagent_session_id');
    }
  }

  getSessionId(): string | null {
    return this.sessionId;
  }

  setSessionId(sessionId: string): void {
    this.sessionId = sessionId;
    if (typeof window !== 'undefined') {
      localStorage.setItem('sketchagent_session_id', sessionId);
    }
  }

  async createSession(initialSketch: any[]): Promise<SessionCreateResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(initialSketch),
    });

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.statusText}`);
    }

    const data = await response.json();
    this.setSessionId(data.sessionId);
    return data;
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': '', // API key if needed
      },
      body: JSON.stringify({
        ...request,
        sessionId: request.sessionId || this.sessionId,
      }),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.error || 'Failed to process request');
    }

    // Update session ID if provided
    if (data.sessionId) {
      this.setSessionId(data.sessionId);
    }

    return data;
  }

  async chatStream(
    request: ChatRequest,
    onEvent: (event: string, data: any) => void
  ): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': '', // API key if needed
      },
      body: JSON.stringify({
        ...request,
        sessionId: request.sessionId || this.sessionId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to process request');
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No response body');
    }

    let finalResult: ChatResponse | null = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n\n');

      for (const line of lines) {
        if (line.startsWith('event:')) {
          const event = line.split('event:')[1].trim();
          const dataLine = lines[lines.indexOf(line) + 1];
          if (dataLine?.startsWith('data:')) {
            const data = JSON.parse(dataLine.split('data:')[1].trim());
            onEvent(event, data);

            if (event === 'result') {
              finalResult = data;
            }
          }
        }
      }
    }

    if (!finalResult) {
      throw new Error('No result received from stream');
    }

    // Update session ID if provided
    if (finalResult.sessionId) {
      this.setSessionId(finalResult.sessionId);
    }

    return finalResult;
  }
}

export const agentClient = new AgentAPIClient();

