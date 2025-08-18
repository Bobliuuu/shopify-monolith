import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MessageSquare, Home, BarChart3, Search, FileText } from 'lucide-react';

function Sidebar({ sidebarOpen, setSidebarOpen, activePage = "ai-assistant" }) {
  const navigate = useNavigate();
  const location = useLocation();

  const NavigationItem = ({ icon: Icon, label, active = false, onClick, path }) => (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
        active 
          ? 'bg-green-50 text-green-700 border-l-4 border-green-500' 
          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
      }`}
    >
      <Icon size={20} />
      <span className="font-medium">{label}</span>
    </button>
  );

  const handleNavigation = (path) => {
    if (path) {
      navigate(path);
      // Close sidebar on mobile after navigation
      if (sidebarOpen) {
        setSidebarOpen(false);
      }
    }
  };

  return (
    <div className={`${sidebarOpen ? 'block' : 'hidden'} lg:block w-64 bg-white border-r border-gray-200 min-h-screen`}>
      <nav className="p-4 space-y-2">
        <NavigationItem icon={Home} label="Home" />
        <NavigationItem 
          icon={Search} 
          label="Store Data" 
          active={location.pathname === "/storedata"}
          onClick={() => handleNavigation("/storedata")}
          path="/storedata"
        />
        <NavigationItem
          icon={Search}
          label="Query Builder"
          active={location.pathname === "/querydata"}
          onClick={() => handleNavigation("/querydata")}
          path="/querydata"
        />
        <NavigationItem
          icon={BarChart3}
          label="Insights Dashboard"
          active={location.pathname === "/dashboard"}
          onClick={() => handleNavigation("/dashboard")}
          path="/dashboard"
        />
        <NavigationItem
          icon={FileText}
          label="Reports"
          active={location.pathname === "/reports"}
          onClick={() => handleNavigation("/reports")}
          path="/reports"
        />
        <NavigationItem 
          icon={MessageSquare} 
          label="AI Assistant" 
          active={location.pathname === "/assistant"}
          onClick={() => handleNavigation("/assistant")}
          path="/assistant"
        />
      </nav>
    </div>
  );
}

export default Sidebar;
