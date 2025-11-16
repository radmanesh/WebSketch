'use client';

import { useState, useRef } from 'react';
import PaletteSidebar from '@/components/PaletteSidebar';
import Toolbar from '@/components/Toolbar';
import CanvasContainer from '@/components/CanvasContainer';
import { PlacedComponent, ComponentType, Mode } from '@/types/types';
import type { KonvaStage } from '@/types/konva';
import { WireframeGenerator, SVGExporter, PNGExporter } from '@/lib/wireframe';

export default function Home() {
  const [components, setComponents] = useState<PlacedComponent[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>('select');
  const [currentType, setCurrentType] = useState<ComponentType>('Container');
  const stageRef = useRef<KonvaStage | null>(null);

  const addComponent = (type: ComponentType, box: { x: number; y: number; width: number; height: number }) => {
    const id = `component-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newComponent: PlacedComponent = {
      id,
      type,
      x: box.x,
      y: box.y,
      width: box.width,
      height: box.height,
      props: {},
    };
    setComponents([...components, newComponent]);
    setSelectedId(id);
    setMode('select');
  };

  const handleBoxDrawn = (box: { x: number; y: number; width: number; height: number }) => {
    addComponent(currentType, box);
  };

  const handleSelectType = (type: ComponentType) => {
    setCurrentType(type);
    setMode('draw');
  };

  const handleMove = (id: string, x: number, y: number) => {
    setComponents(components.map(c =>
      c.id === id ? { ...c, x, y } : c
    ));
  };

  const handleResize = (id: string, width: number, height: number, x: number, y: number) => {
    setComponents(components.map(c =>
      c.id === id ? { ...c, width, height, x, y } : c
    ));
  };

  const handleDeleteSelected = () => {
    if (selectedId) {
      setComponents(components.filter(c => c.id !== selectedId));
      setSelectedId(null);
    }
  };

  const handleClearAll = () => {
    setComponents([]);
    setSelectedId(null);
  };

  const handleExportJSON = () => {
    const json = JSON.stringify(components, null, 2);
    // Create a download link
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'websketch-layout.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImportJSON = (json: string) => {
    try {
      const parsed = JSON.parse(json);
      if (Array.isArray(parsed)) {
        setComponents(parsed);
        setSelectedId(null);
      } else {
        alert('Invalid JSON format. Expected an array of components.');
      }
    } catch (error) {
      alert('Failed to parse JSON: ' + (error as Error).message);
    }
  };

  const handleExportPNG = async () => {
    if (components.length === 0) {
      alert('No components to export.');
      return;
    }

    try {
      // Generate wireframe structure
      const generator = new WireframeGenerator();
      const structure = generator.generate(components);

      // Export to PNG
      const exporter = new PNGExporter(2);
      const blob = await exporter.export(structure);

      // Download the image
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.download = 'websketch-wireframe.png';
      link.href = url;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting PNG:', error);
      alert('Failed to export PNG. Please try again.');
    }
  };

  const handleExportSVG = () => {
    if (components.length === 0) {
      alert('No components to export.');
      return;
    }

    try {
      // Generate wireframe structure
      const generator = new WireframeGenerator();
      const structure = generator.generate(components);

      // Export to SVG
      const exporter = new SVGExporter();
      const svgString = exporter.export(structure);

      // Download the SVG
      const blob = new Blob([svgString], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.download = 'websketch-wireframe.svg';
      link.href = url;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting SVG:', error);
      alert('Failed to export SVG. Please try again.');
    }
  };

  const handleStageRef = (stage: KonvaStage | null) => {
    stageRef.current = stage;
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <PaletteSidebar onSelectType={handleSelectType} currentType={currentType} />
      <div className="flex flex-col flex-1">
        <Toolbar
          mode={mode}
          onSetMode={setMode}
          onDeleteSelected={handleDeleteSelected}
          onClearAll={handleClearAll}
          onExportJSON={handleExportJSON}
          onImportJSON={handleImportJSON}
          onExportPNG={handleExportPNG}
          onExportSVG={handleExportSVG}
          hasSelection={selectedId !== null}
        />
        <CanvasContainer
          components={components}
          selectedId={selectedId}
          mode={mode}
          onBoxDrawn={handleBoxDrawn}
          onSelectComponent={setSelectedId}
          onMove={handleMove}
          onResize={handleResize}
          onStageRef={handleStageRef}
        />
      </div>
    </div>
  );
}
