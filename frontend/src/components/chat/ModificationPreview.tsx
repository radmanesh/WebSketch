'use client';

interface ModificationPreviewProps {
  modification: {
    modifiedSketch: any[];
    operations: any[];
    reasoning: string;
    description: string;
  };
  onAccept: () => void;
  onReject: () => void;
}

export default function ModificationPreview({
  modification,
  onAccept,
  onReject,
}: ModificationPreviewProps) {
  return (
    <div className="border-t border-gray-300 bg-blue-50 p-3">
      <div className="mb-2">
        <h4 className="font-semibold text-sm text-gray-800 mb-1">Proposed Changes</h4>
        <p className="text-sm text-gray-600 mb-2">{modification.description}</p>
        <p className="text-xs text-gray-500 italic">{modification.reasoning}</p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={onAccept}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm font-medium"
        >
          Apply Changes
        </button>
        <button
          onClick={onReject}
          className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors text-sm font-medium"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

