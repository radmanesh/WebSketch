import { BaseExporter } from './BaseExporter';
import { WireframeStructure } from '../types';
import { SVGExporter } from './SVGExporter';

/**
 * Exports wireframe structure to PNG format
 * Uses SVG as intermediate format and converts to PNG via canvas
 */
export class PNGExporter extends BaseExporter {
  private pixelRatio: number;

  constructor(pixelRatio: number = 2) {
    super();
    this.pixelRatio = pixelRatio;
  }

  async export(structure: WireframeStructure): Promise<Blob> {
    // First export to SVG
    const svgExporter = new SVGExporter();
    const svgString = svgExporter.export(structure);

    // Convert SVG to PNG using canvas
    return this.svgToPng(svgString, structure.width, structure.height);
  }

  /**
   * Convert SVG string to PNG Blob
   */
  private async svgToPng(svgString: string, width: number, height: number): Promise<Blob> {
    return new Promise((resolve, reject) => {
      const img = new Image();

      // Clean and validate SVG string
      // Remove any potential issues with XML encoding
      const cleanSvg = svgString.trim();

      // Try URL-encoded data URI first (more reliable for SVG in many browsers)
      const encodedSvg = encodeURIComponent(cleanSvg);
      const dataUrl = `data:image/svg+xml;charset=utf-8,${encodedSvg}`;

      // Set a timeout for image loading (10 seconds)
      const timeout = setTimeout(() => {
        reject(new Error('SVG image loading timed out'));
      }, 10000);

      img.onload = () => {
        clearTimeout(timeout);
        try {
          // Create canvas with pixel ratio
          const canvas = document.createElement('canvas');
          canvas.width = width * this.pixelRatio;
          canvas.height = height * this.pixelRatio;

          const ctx = canvas.getContext('2d');
          if (!ctx) {
            reject(new Error('Could not get canvas context'));
            return;
          }

          // Set white background
          ctx.fillStyle = '#ffffff';
          ctx.fillRect(0, 0, width * this.pixelRatio, height * this.pixelRatio);

          // Scale context for high DPI
          ctx.scale(this.pixelRatio, this.pixelRatio);

          // Draw image to canvas
          ctx.drawImage(img, 0, 0, width, height);

          // Convert to blob
          canvas.toBlob(
            (blob) => {
              if (blob) {
                resolve(blob);
              } else {
                reject(new Error('Failed to create PNG blob from canvas'));
              }
            },
            'image/png',
            1.0
          );
        } catch (error) {
          clearTimeout(timeout);
          reject(error instanceof Error ? error : new Error('Unknown error during PNG conversion'));
        }
      };

      img.onerror = () => {
        clearTimeout(timeout);
        // Try fallback with base64 encoding
        this.tryBase64Fallback(cleanSvg, width, height)
          .then(resolve)
          .catch(() => {
            console.error('SVG Export Error:', cleanSvg.substring(0, 500));
            reject(new Error(`Failed to load SVG image. SVG may be invalid or too large. Please check browser console for details.`));
          });
      };

      img.src = dataUrl;
    });
  }

  /**
   * Fallback method using base64 encoding
   */
  private async tryBase64Fallback(svgString: string, width: number, height: number): Promise<Blob> {
    return new Promise((resolve, reject) => {
      const img = new Image();

      try {
        const svgBase64 = btoa(unescape(encodeURIComponent(svgString)));
        const dataUrl = `data:image/svg+xml;base64,${svgBase64}`;

        const timeout = setTimeout(() => {
          reject(new Error('SVG image loading timed out (base64 fallback)'));
        }, 10000);

        img.onload = () => {
          clearTimeout(timeout);
          try {
            const canvas = document.createElement('canvas');
            canvas.width = width * this.pixelRatio;
            canvas.height = height * this.pixelRatio;

            const ctx = canvas.getContext('2d');
            if (!ctx) {
              reject(new Error('Could not get canvas context'));
              return;
            }

            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, width * this.pixelRatio, height * this.pixelRatio);
            ctx.scale(this.pixelRatio, this.pixelRatio);
            ctx.drawImage(img, 0, 0, width, height);

            canvas.toBlob(
              (blob) => {
                if (blob) {
                  resolve(blob);
                } else {
                  reject(new Error('Failed to create PNG blob from canvas'));
                }
              },
              'image/png',
              1.0
            );
          } catch (error) {
            clearTimeout(timeout);
            reject(error instanceof Error ? error : new Error('Unknown error'));
          }
        };

        img.onerror = () => {
          clearTimeout(timeout);
          reject(new Error('Base64 fallback also failed'));
        };

        img.src = dataUrl;
      } catch (error) {
        reject(error instanceof Error ? error : new Error('Failed to encode SVG'));
      }
    });
  }
}

