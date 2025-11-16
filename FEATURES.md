# WebSketch - Wireframe Editor

A Next.js-based wireframe editor with drag-and-drop components, built using React-Konva.

## Features Implemented

### ✅ Step 2: Base Layout
- **PaletteSidebar**: Left sidebar with component palette
- **Toolbar**: Top toolbar with mode switching and actions
- **CanvasContainer**: Main canvas area for drawing wireframes

### ✅ Step 3: React-Konva Integration
- Konva Stage and Layer properly integrated
- Client-side rendering to avoid SSR issues
- Responsive canvas that adapts to window size

### ✅ Step 4: Component Data Model
- TypeScript types for `ComponentType` and `PlacedComponent`
- Central state management in main page component
- State includes:
  - `components`: Array of placed components
  - `selectedId`: Currently selected component ID
  - `mode`: Drawing mode ('draw' or 'select')
  - `currentType`: Component type to place

### ✅ Step 5: Drawing Bounding Boxes
- Click and drag on canvas in 'draw' mode to create components
- Visual preview while drawing (dashed rectangle)
- Normalized coordinates (handles dragging left/up)

### ✅ Step 6: Placed Components
- Components are rendered as colored rectangles on the canvas
- Each component type has a unique color:
  - Container: Blue (#e3f2fd)
  - Button: Purple (#f3e5f5)
  - Input: Orange (#fff3e0)
  - ImagePlaceholder: Green (#e8f5e9)
- Component labels displayed on each shape
- Clicking a component selects it

### ✅ Step 7: Move & Resize
- **Dragging**: All components are draggable
- **Resizing**: Selected components show Konva Transformer handles
- **State Updates**: Position and size changes are persisted to state

### ✅ Step 8: Component Type Selection
- Click any component type in the sidebar to:
  - Set that type as current
  - Automatically switch to draw mode
- Draw a box to place that component type

### ✅ Step 9: Toolbar Actions
- **Select Mode**: Switch to selection/editing mode
- **Draw Mode**: Switch to drawing mode
- **Delete Selected**: Remove the currently selected component
- **Clear All**: Remove all components from canvas

### ✅ Step 11: JSON Export/Import
- **Export JSON**: Downloads layout as JSON file
- **Import JSON**: Paste JSON to restore a saved layout
- Validates JSON format before importing

## Running the Application

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Visit `http://localhost:3000` to use the application.

## Usage Guide

1. **Select a Component**: Click on a component type in the left sidebar (Container, Button, Input, or ImagePlaceholder)
2. **Draw the Component**: Click and drag on the canvas to draw a box where the component should appear
3. **Select and Edit**: Click on any component to select it, then:
   - Drag to move it
   - Use corner handles to resize it
4. **Delete**: Select a component and click "Delete Selected" in the toolbar
5. **Export/Import**: Use the Export/Import JSON buttons to save and restore your layouts

## Technology Stack

- **Next.js 16**: React framework
- **React 19**: UI library  
- **React-Konva**: Canvas rendering library
- **Konva**: HTML5 canvas library
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **@dnd-kit**: Drag and drop (ready for future enhancements)

## Project Structure

```
src/
├── app/
│   ├── page.tsx          # Main application with state management
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles
├── components/
│   ├── PaletteSidebar.tsx       # Component palette sidebar
│   ├── Toolbar.tsx              # Top toolbar with actions
│   ├── CanvasContainer.tsx      # Konva canvas container
│   └── PlacedComponentShape.tsx # Individual component renderer
└── types/
    └── types.ts          # TypeScript type definitions
```

## Future Enhancements (Step 10 - Optional)

The application is ready for drag-and-drop enhancements using `@dnd-kit`:
- Drag components from palette directly onto canvas
- Drop to create components at specific positions
- Default component sizes for dropped items
