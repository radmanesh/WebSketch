import { ChatOpenAI } from '@langchain/openai';
import { HumanMessage, SystemMessage } from '@langchain/core/messages';
import { PlacedComponent } from '@/types/types';
import { SketchModificationJSONSchema, type SketchModification } from './schemas';
import { parseSketch } from './sketchParser';
import { getSystemPrompt, buildUserPrompt } from './prompts';

export class SketchAgent {
  private model: ChatOpenAI;

  constructor(apiKey?: string) {
    this.model = new ChatOpenAI({
      modelName: 'gpt-4o-mini',
      temperature: 0.3,
      openAIApiKey: apiKey || process.env.OPENAI_API_KEY,
    });
  }

  async modifySketch(
    userMessage: string,
    currentSketch: PlacedComponent[]
  ): Promise<SketchModification> {
    try {
      // Parse and analyze current sketch
      const layoutAnalysis = parseSketch(currentSketch);

      // Build prompts
      const systemPrompt = getSystemPrompt();
      const userPrompt = buildUserPrompt(userMessage, currentSketch, layoutAnalysis);

      // Add JSON schema instructions to the prompt
      const schemaInstructions = `\n\nYou must respond with a valid JSON object matching this schema:\n${JSON.stringify(SketchModificationJSONSchema, null, 2)}\n\nRespond only with valid JSON, no markdown formatting.`;

      // Create messages
      const messages = [
        new SystemMessage(systemPrompt + schemaInstructions),
        new HumanMessage(userPrompt),
      ];

      // Call LLM
      const response = await this.model.invoke(messages);

      // Parse the response
      let content = typeof response.content === 'string'
        ? response.content
        : JSON.stringify(response.content);

      // Try to extract JSON from markdown code blocks if present
      const jsonMatch = content.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
      if (jsonMatch) {
        content = jsonMatch[1];
      }

      // Parse and validate JSON
      let parsed: SketchModification;
      try {
        parsed = JSON.parse(content);
      } catch (parseError) {
        throw new Error(`Failed to parse JSON response: ${parseError instanceof Error ? parseError.message : 'Unknown error'}`);
      }

      // Basic validation
      if (!parsed.operations || !Array.isArray(parsed.operations)) {
        throw new Error('Invalid response: operations must be an array');
      }
      if (typeof parsed.reasoning !== 'string') {
        throw new Error('Invalid response: reasoning must be a string');
      }
      if (typeof parsed.description !== 'string') {
        throw new Error('Invalid response: description must be a string');
      }

      return parsed;
    } catch (error) {
      console.error('Error in sketch agent:', error);
      throw new Error(
        `Failed to process sketch modification: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }
}

