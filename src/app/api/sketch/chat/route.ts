import { NextRequest, NextResponse } from 'next/server';
import { SketchAgent } from '@/lib/agent/sketchAgent';
import { ChatRequest, AgentResponse } from '@/types/agent';
import { PlacedComponent } from '@/types/types';

export async function POST(request: NextRequest) {
  try {
    const body: ChatRequest = await request.json();

    // Validate request
    if (!body.message || !body.currentSketch) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields: message and currentSketch' },
        { status: 400 }
      );
    }

    if (!Array.isArray(body.currentSketch)) {
      return NextResponse.json(
        { success: false, error: 'currentSketch must be an array' },
        { status: 400 }
      );
    }

    // Validate sketch components
    const sketch = body.currentSketch as PlacedComponent[];
    for (const component of sketch) {
      if (!component.id || !component.type || typeof component.x !== 'number' ||
          typeof component.y !== 'number' || typeof component.width !== 'number' ||
          typeof component.height !== 'number') {
        return NextResponse.json(
          { success: false, error: 'Invalid component format in currentSketch' },
          { status: 400 }
        );
      }
    }

    // Check for API key
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { success: false, error: 'OpenAI API key not configured' },
        { status: 500 }
      );
    }

    // Initialize agent and process request
    const agent = new SketchAgent(apiKey);
    const modification = await agent.modifySketch(body.message, sketch);

    const response: AgentResponse = {
      modification,
      success: true,
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Error in chat API route:', error);

    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';

    return NextResponse.json(
      {
        success: false,
        error: `Failed to process request: ${errorMessage}`,
      },
      { status: 500 }
    );
  }
}

