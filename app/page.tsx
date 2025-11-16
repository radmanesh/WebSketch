import PaletteSidebar from "@/components/PaletteSidebar";
import Toolbar from "@/components/Toolbar";
import CanvasContainer from "@/components/CanvasContainer";

export default function Home() {
  return (
    <div className="h-screen flex flex-col">
      {/* Toolbar at top */}
      <Toolbar />
      
      {/* Sidebar + Canvas */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <PaletteSidebar />
        
        {/* Canvas Area */}
        <CanvasContainer />
      </div>
    </div>
  );
}
