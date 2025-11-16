import { ComponentType } from '@/types/types';

interface PaletteSidebarProps {
  onSelectType: (type: ComponentType) => void;
  currentType: ComponentType;
}

export default function PaletteSidebar({ onSelectType, currentType }: PaletteSidebarProps) {
  const componentTypes: ComponentType[] = [
    'Container',
    'Button',
    'Input',
    'ImagePlaceholder',
    'Text',
    'HorizontalLine',
    'Heading',
    'Footer',
    'NavigationBox',
    'List',
    'Table'
  ];

  return (
    <div className="w-64 h-full bg-gray-100 border-r border-gray-300 p-4">
      <h2 className="text-lg font-semibold mb-4 text-gray-900">Components</h2>
      <div className="flex flex-col gap-2">
        {componentTypes.map((type) => (
          <button
            key={type}
            onClick={() => onSelectType(type)}
            className={`px-4 py-2 text-left rounded border font-medium ${
              currentType === type
                ? 'bg-blue-500 text-white border-blue-600'
                : 'bg-white border-gray-300 hover:bg-gray-50 text-gray-900'
            }`}
          >
            {type}
          </button>
        ))}
      </div>
    </div>
  );
}
