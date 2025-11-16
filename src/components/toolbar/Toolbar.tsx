import { Mode } from '@/types/types';

interface ToolbarProps {
  mode: Mode;
  onSetMode: (mode: Mode) => void;
  onDeleteSelected: () => void;
  onClearAll: () => void;
  onExportJSON: () => void;
  onImportJSON: (json: string) => void;
  onExportPNG?: () => void;
  onExportSVG?: () => void;
  hasSelection: boolean;
}

export default function Toolbar({
  mode,
  onSetMode,
  onDeleteSelected,
  onClearAll,
  onExportJSON,
  onImportJSON,
  onExportPNG,
  onExportSVG,
  hasSelection,
}: ToolbarProps) {
  const handleImport = () => {
    const json = prompt('Paste JSON data:');
    if (json) {
      onImportJSON(json);
    }
  };

  return (
    <div className="h-14 bg-white border-b border-gray-300 px-4 flex items-center gap-2 overflow-x-auto">
      <button
        onClick={() => onSetMode('select')}
        className={`px-4 py-2 rounded ${
          mode === 'select'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 hover:bg-gray-300'
        }`}
      >
        Select Mode
      </button>
      <button
        onClick={() => onSetMode('draw')}
        className={`px-4 py-2 rounded ${
          mode === 'draw'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 hover:bg-gray-300'
        }`}
      >
        Draw Mode
      </button>
      <div className="w-px h-8 bg-gray-300 mx-2" />
      <button
        onClick={onDeleteSelected}
        disabled={!hasSelection}
        className={`px-4 py-2 rounded ${
          hasSelection
            ? 'bg-red-500 text-white hover:bg-red-600'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
        }`}
      >
        Delete Selected
      </button>
      <button
        onClick={onClearAll}
        className="px-4 py-2 rounded bg-red-500 text-white hover:bg-red-600"
      >
        Clear All
      </button>
      <div className="w-px h-8 bg-gray-300 mx-2" />
      <button
        onClick={onExportJSON}
        className="px-4 py-2 rounded bg-green-500 text-white hover:bg-green-600"
      >
        Export JSON
      </button>
      <button
        onClick={handleImport}
        className="px-4 py-2 rounded bg-green-500 text-white hover:bg-green-600"
      >
        Import JSON
      </button>
      <div className="w-px h-8 bg-gray-300 mx-2" />
      {onExportPNG && (
        <button
          onClick={onExportPNG}
          className="px-4 py-2 rounded bg-purple-500 text-white hover:bg-purple-600"
        >
          Generate PNG
        </button>
      )}
      {onExportSVG && (
        <button
          onClick={onExportSVG}
          className="px-4 py-2 rounded bg-purple-500 text-white hover:bg-purple-600"
        >
          Generate SVG
        </button>
      )}
    </div>
  );
}
