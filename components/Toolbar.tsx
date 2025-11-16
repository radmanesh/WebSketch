export default function Toolbar() {
  return (
    <div className="h-14 bg-white border-b border-gray-300 px-4 flex items-center gap-4">
      <h1 className="text-lg font-semibold">WebSketch</h1>
      <div className="flex gap-2">
        <button className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded">
          Toolbar actions
        </button>
      </div>
    </div>
  );
}
