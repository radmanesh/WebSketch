import { WireframeStructure } from '../types';

/**
 * Base interface for all exporters
 */
export interface IWireframeExporter {
  /**
   * Export wireframe structure to specific format
   */
  export(structure: WireframeStructure): string | Blob | Promise<string | Blob>;
}

/**
 * Base exporter class
 */
export abstract class BaseExporter implements IWireframeExporter {
  abstract export(structure: WireframeStructure): string | Blob | Promise<string | Blob>;

  /**
   * Helper method to escape SVG text content
   */
  protected escapeSVGText(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }
}

