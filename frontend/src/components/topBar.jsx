import React from 'react';
import { Settings, LogOut } from 'lucide-react';

function TopBar({ sidebarOpen, setSidebarOpen, pageTitle = "Store Analytics", pageSubtitle = "AI Assistant" }) {
  return (
    <div className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 rounded-md hover:bg-gray-100"
          >
            <div className="w-5 h-5 flex flex-col justify-center gap-1">
              <div className="w-full h-0.5 bg-gray-600"></div>
              <div className="w-full h-0.5 bg-gray-600"></div>
              <div className="w-full h-0.5 bg-gray-600"></div>
            </div>
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">S</span>
            </div>
            <div>
              <h1 className="font-semibold text-gray-900">{pageTitle}</h1>
              <p className="text-sm text-gray-500">{pageSubtitle}</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-2 rounded-md hover:bg-gray-100">
            <Settings size={18} />
          </button>
          <button className="p-2 rounded-md hover:bg-gray-100">
            <LogOut size={18} />
          </button>
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white font-medium text-sm">SA</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TopBar;
