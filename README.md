# WebSketch

A powerful wireframe editor application built with Next.js and TypeScript. Create, edit, and export wireframe layouts with an intuitive drag-and-drop interface.

![WebSketch UI](https://github.com/user-attachments/assets/e65586be-b829-4d4c-8310-a13779a75b08)

## Features

### Core Functionality
- **Component Palette**: 4 wireframe components (Container, Button, Input, ImagePlaceholder)
- **Drawing Mode**: Click and drag on canvas to create components with visual preview
- **Selection Mode**: Click to select, drag to move, and resize with handles
- **Color-Coded Components**: Each component type has a distinct color for easy identification
- **Toolbar Actions**: Switch modes, delete selected components, clear canvas
- **JSON Export/Import**: Save and restore layouts as JSON files

### Technical Stack
- Built with Next.js 16 and React 19
- TypeScript for type safety
- Canvas rendering with react-konva and konva
- Tailwind CSS for styling
- Ready for drag-and-drop enhancements with @dnd-kit

## Usage Guide

1. **Select a Component Type**: Click any component in the left sidebar (Container, Button, Input, or ImagePlaceholder)
   - This automatically switches you to Draw Mode
2. **Draw on Canvas**: Click and drag on the canvas to create a bounding box
   - Release to place the component
3. **Select and Edit**: Click on any placed component to select it
   - Drag to move the component
   - Use corner handles to resize
4. **Toolbar Actions**:
   - **Select Mode**: Switch to selection/editing mode
   - **Draw Mode**: Switch to drawing mode
   - **Delete Selected**: Remove the currently selected component
   - **Clear All**: Remove all components from canvas
   - **Export JSON**: Download your layout as a JSON file
   - **Import JSON**: Load a previously saved layout

## Getting Started

First, install dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Build

To build the project for production:

```bash
npm run build
```

## Lint

To run the linter:

```bash
npm run lint
```

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

## Implementation Details

This project implements a complete wireframe editor following a step-by-step approach:

1. **Base Layout** (Step 2): Three-region layout with sidebar, toolbar, and canvas
2. **React-Konva Integration** (Step 3): Canvas rendering with proper SSR handling
3. **Data Model** (Step 4): TypeScript types and centralized state management
4. **Drawing Mode** (Step 5): Click-drag interaction to create components
5. **Component Rendering** (Step 6): Visual representation of placed components
6. **Move & Resize** (Step 7): Interactive editing with Konva Transformer
7. **Component Selection** (Step 8): Palette-driven component type selection
8. **Toolbar Actions** (Step 9): Mode switching and component management
9. **JSON Persistence** (Step 11): Export and import layout data

See [FEATURES.md](./FEATURES.md) for detailed feature documentation.

## Future Enhancements

- Drag-and-drop from palette (Step 10) - infrastructure ready with @dnd-kit
- Component properties editor
- Undo/redo functionality
- Multiple page support
- Export to HTML/React code
- Collaboration features
