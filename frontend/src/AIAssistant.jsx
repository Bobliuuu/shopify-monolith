import React, { useState, useEffect } from 'react';
import TopBar from './components/topBar';
import Sidebar from './components/sidebar';
import ChatBot from './components/chatbot';

function AIAssistant() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Ensure page starts at the top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <TopBar 
        sidebarOpen={sidebarOpen} 
        setSidebarOpen={setSidebarOpen}
        pageTitle="Store Analytics"
        pageSubtitle="AI Assistant"/>
    
        <div className="flex">
          <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} activePage="ai-assistant" />
  
          {/* Main Content */}
          <div className="flex-1 p-6">
            <div className="max-w-7xl mx-auto">
              <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
                <p className="text-gray-600">Get insights and answers about your store data</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Chat Interface */}
                <ChatBot />

                {/* Side Panel */}
                <div className="space-y-6">
                  {/* Quick Stats */}
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="font-semibold text-gray-900 mb-4">Quick Stats</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Orders</span>
                        <span className="font-semibold text-gray-900">1,234</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Revenue (MTD)</span>
                        <span className="font-semibold text-gray-900">$45,678</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Conversion Rate</span>
                        <span className="font-semibold text-gray-900">3.2%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Active Customers</span>
                        <span className="font-semibold text-gray-900">892</span>
                      </div>
                    </div>
                  </div>

                  {/* AI Capabilities */}
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="font-semibold text-gray-900 mb-4">AI Capabilities</h3>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-sm text-gray-700">Store Performance Analysis</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-sm text-gray-700">Customer Behavior Insights</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-sm text-gray-700">Product Performance Reports</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-sm text-gray-700">Financial Analytics</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-sm text-gray-700">Query Builder Assistant</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-sm text-gray-700">Custom Report Generation</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>
  );
}

export default AIAssistant;