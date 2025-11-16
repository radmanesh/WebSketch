import { BaseExporter } from './BaseExporter';
import { WireframeStructure, WireframeElement } from '../types';

/**
 * Exports wireframe structure to SVG format
 */
export class SVGExporter extends BaseExporter {
  export(structure: WireframeStructure): string {
    const { width, height, elements, config } = structure;

    const svgElements = elements.map(el => this.renderElement(el)).join('\n    ');

    return `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="${config.backgroundColor}"/>
  ${svgElements}
</svg>`;
  }

  /**
   * Render a wireframe element to SVG string
   */
  private renderElement(element: WireframeElement, indent: string = '  '): string {
    switch (element.type) {
      case 'rect': {
        const { x, y, width, height, fill, stroke, strokeWidth, opacity } = element;
        // Handle transparent fill - use 'none' for SVG (more compatible)
        const fillValue = !fill || fill === 'transparent' || fill === 'none' ? 'none' : fill;
        const attrs = this.buildAttributes({
          x: x.toString(),
          y: y.toString(),
          width: width.toString(),
          height: height.toString(),
          fill: fillValue,
          stroke: stroke || 'none',
          'stroke-width': strokeWidth?.toString() || '1',
          opacity: opacity?.toString(),
        });
        return `${indent}<rect${attrs} />`;
      }

      case 'line': {
        const { points, stroke, strokeWidth, dash, opacity } = element;
        // Convert points array [x1, y1, x2, y2, ...] to SVG points string "x1,y1 x2,y2 ..."
        const pointsStr: string[] = [];
        for (let i = 0; i < points.length; i += 2) {
          if (i + 1 < points.length) {
            pointsStr.push(`${points[i]},${points[i + 1]}`);
          }
        }

        const attrs = this.buildAttributes({
          points: pointsStr.join(' '),
          fill: 'none',
          stroke: stroke || 'none',
          'stroke-width': strokeWidth?.toString() || '1',
          'stroke-dasharray': dash?.join(','),
          opacity: opacity?.toString(),
        });
        return `${indent}<polyline${attrs} />`;
      }

      case 'text': {
        const { x, y, text, fontSize, fill, fontFamily, opacity } = element;
        const attrs = this.buildAttributes({
          x: x.toString(),
          y: (y + (fontSize || 14)).toString(),
          'font-size': fontSize?.toString() || '14',
          'font-family': fontFamily || 'Arial',
          fill: fill || 'black',
          opacity: opacity?.toString(),
        });
        return `${indent}<text${attrs}>${this.escapeSVGText(text)}</text>`;
      }

      case 'circle': {
        const { x, y, radius, fill, stroke, strokeWidth, opacity } = element;
        // Handle transparent fill - use 'none' for SVG
        const fillValue = !fill || fill === 'transparent' || fill === 'none' ? 'none' : fill;
        const attrs = this.buildAttributes({
          cx: x.toString(),
          cy: y.toString(),
          r: radius.toString(),
          fill: fillValue,
          stroke: stroke || 'none',
          'stroke-width': strokeWidth?.toString() || '1',
          opacity: opacity?.toString(),
        });
        return `${indent}<circle${attrs} />`;
      }

      case 'path': {
        const { data, stroke, strokeWidth, fill, opacity } = element;
        const attrs = this.buildAttributes({
          d: data,
          fill: fill || 'none',
          stroke: stroke || 'none',
          'stroke-width': strokeWidth?.toString() || '1',
          opacity: opacity?.toString(),
        });
        return `${indent}<path${attrs} />`;
      }

      case 'group': {
        const { x, y, elements, opacity } = element;
        const transform = x !== undefined || y !== undefined
          ? ` transform="translate(${x || 0},${y || 0})"`
          : '';
        const opacityAttr = opacity !== undefined ? ` opacity="${opacity}"` : '';

        const childElements = elements
          .map(el => this.renderElement(el, indent + '  '))
          .join('\n');

        return `${indent}<g${transform}${opacityAttr}>\n${childElements}\n${indent}</g>`;
      }

      default:
        return '';
    }
  }

  /**
   * Build attributes string for SVG element
   */
  private buildAttributes(attrs: Record<string, string | undefined>): string {
    const attrString = Object.entries(attrs)
      .filter(([, value]) => value !== undefined)
      .map(([key, value]) => `${key}="${value}"`)
      .join(' ');

    // Add leading space if there are attributes
    return attrString ? ` ${attrString}` : '';
  }
}

