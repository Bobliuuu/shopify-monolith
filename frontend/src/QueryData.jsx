import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Search, 
  Play, 
  Save, 
  Download, 
  Copy, 
  Clock, 
  BookOpen, 
  Zap,
  Settings, 
  LogOut, 
  Home,
  BarChart3,
  FileText,
  MessageSquare,
  ChevronRight,
  Code,
  Table,
  Filter,
  TrendingUp,
  Calendar,
  Users,
  ShoppingCart,
  DollarSign,
  Eye,
  Trash2,
  Plus,
  Star,
  StarOff
} from 'lucide-react';
import TopBar from './components/topBar';
import Sidebar from './components/sidebar';

function QueryBuilder() {
  const [query, setQuery] = useState('SELECT * FROM orders WHERE created_at >= "2024-08-01" LIMIT 10;');
  const [isExecuting, setIsExecuting] = useState(false);
  const [queryResults, setQueryResults] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [savedQueries, setSavedQueries] = useState([]);
  const [queryHistory, setQueryHistory] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('builder');

  // Mock data for templates and saved queries
  const queryTemplates = [
    {
      id: 1,
      name: 'Top Selling Products',
      category: 'Products',
      description: 'Find your best performing products by sales volume',
      query: `SELECT 
  p.title, 
  p.price, 
  COUNT(oi.product_id) as sales_count,
  SUM(oi.quantity * oi.price) as total_revenue
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
WHERE o.created_at >= "2024-07-01"
GROUP BY p.id, p.title, p.price
ORDER BY sales_count DESC
LIMIT 20;`,
      icon: TrendingUp,
      color: 'bg-green-500'
    },
    {
      id: 2,
      name: 'Monthly Revenue Trend',
      category: 'Finance',
      description: 'Track revenue trends over the past 12 months',
      query: `SELECT 
  DATE_FORMAT(created_at, '%Y-%m') as month,
  COUNT(*) as order_count,
  SUM(total_price) as monthly_revenue,
  AVG(total_price) as avg_order_value
FROM orders
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
  AND financial_status = 'paid'
GROUP BY month
ORDER BY month ASC;`,
      icon: DollarSign,
      color: 'bg-blue-500'
    },
    {
      id: 3,
      name: 'Customer Lifetime Value',
      category: 'Customers',
      description: 'Calculate customer lifetime value and order frequency',
      query: `SELECT 
  c.email,
  c.first_name,
  c.last_name,
  COUNT(o.id) as total_orders,
  SUM(o.total_price) as lifetime_value,
  AVG(o.total_price) as avg_order_value,
  MIN(o.created_at) as first_order,
  MAX(o.created_at) as last_order
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.financial_status = 'paid'
GROUP BY c.id
ORDER BY lifetime_value DESC
LIMIT 50;`,
      icon: Users,
      color: 'bg-purple-500'
    },
    {
      id: 4,
      name: 'Cart Abandonment Analysis',
      category: 'Analytics',
      description: 'Analyze cart abandonment patterns and recovery opportunities',
      query: `SELECT 
  DATE(created_at) as date,
  COUNT(*) as abandoned_carts,
  SUM(total_price) as lost_revenue,
  AVG(total_price) as avg_cart_value
FROM abandoned_checkouts
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(created_at)
ORDER BY date DESC;`,
      icon: ShoppingCart,
      color: 'bg-orange-500'
    }
  ];

  const mockQueryResults = {
    columns: ['id', 'customer_email', 'total_amount', 'status', 'created_at'],
    rows: [
      [1001, 'john.doe@email.com', '$125.99', 'fulfilled', '2024-08-10 14:30:00'],
      [1002, 'jane.smith@email.com', '$67.50', 'pending', '2024-08-10 16:20:00'],
      [1003, 'bob.wilson@email.com', '$234.00', 'fulfilled', '2024-08-09 09:15:00'],
      [1004, 'alice.brown@email.com', '$89.99', 'cancelled', '2024-08-09 18:45:00'],
      [1005, 'charlie.davis@email.com', '$156.75', 'fulfilled', '2024-08-08 13:10:00']
    ],
    executionTime: 0.045,
    rowCount: 5
  };

  useEffect(() => {
    // Load saved queries and history from localStorage simulation
    const mockSavedQueries = [
      {
        id: 1,
        name: 'Weekly Sales Report',
        query: 'SELECT * FROM orders WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY);',
        createdAt: '2024-08-10',
        favorite: true
      },
      {
        id: 2,
        name: 'Customer Analysis',
        query: 'SELECT customer_id, COUNT(*) as order_count FROM orders GROUP BY customer_id;',
        createdAt: '2024-08-09',
        favorite: false
      }
    ];

    const mockHistory = [
      {
        id: 1,
        query: 'SELECT * FROM products WHERE inventory < 10;',
        executedAt: '2024-08-10 15:30:00',
        executionTime: 0.023
      },
      {
        id: 2,
        query: 'SELECT COUNT(*) FROM orders WHERE created_at >= "2024-08-01";',
        executedAt: '2024-08-10 14:15:00',
        executionTime: 0.012
      }
    ];

    setSavedQueries(mockSavedQueries);
    setQueryHistory(mockHistory);
  }, []);

  const executeQuery = async () => {
    setIsExecuting(true);
    
    // Add to history
    const historyEntry = {
      id: Date.now(),
      query: query,
      executedAt: new Date().toLocaleString(),
      executionTime: Math.random() * 0.1
    };
    setQueryHistory(prev => [historyEntry, ...prev.slice(0, 9)]);

    // Simulate API call
    setTimeout(() => {
      setQueryResults(mockQueryResults);
      setIsExecuting(false);
    }, 1000);
  };

  const loadTemplate = (template) => {
    setQuery(template.query);
    setSelectedTemplate(template.id);
  };

  const saveQuery = () => {
    const name = prompt('Enter a name for this query:');
    if (name) {
      const newQuery = {
        id: Date.now(),
        name,
        query,
        createdAt: new Date().toISOString().split('T')[0],
        favorite: false
      };
      setSavedQueries(prev => [newQuery, ...prev]);
    }
  };

  const toggleFavorite = (queryId) => {
    setSavedQueries(prev => 
      prev.map(q => q.id === queryId ? {...q, favorite: !q.favorite} : q)
    );
  };

  const NavigationItem = ({ icon: Icon, label, active = false, onClick }) => (
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

  const TemplateCard = ({ template }) => (
    <div 
      onClick={() => loadTemplate(template)}
      className="p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:shadow-sm cursor-pointer transition-all group"
    >
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 ${template.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
          <template.icon size={20} className="text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-900 group-hover:text-green-700 transition-colors">
            {template.name}
          </h4>
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">
            {template.description}
          </p>
          <div className="flex items-center gap-2 mt-2">
            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
              {template.category}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <TopBar 
        sidebarOpen={sidebarOpen} 
        setSidebarOpen={setSidebarOpen}
        pageTitle="Store Analytics"
        pageSubtitle="Query Builder"/>

      <div className="flex">
        <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} activePage="querydata" />

        {/* Main Content */}
        <div className="flex-1 flex">
          {/* Query Sidebar */}
          <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
            {/* Tabs */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setActiveTab('builder')}
                  className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'builder' 
                      ? 'bg-white text-green-700 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Code size={16} className="inline mr-2" />
                  Builder
                </button>
                <button
                  onClick={() => setActiveTab('templates')}
                  className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'templates' 
                      ? 'bg-white text-green-700 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <BookOpen size={16} className="inline mr-2" />
                  Templates
                </button>
              </div>
            </div>

            {activeTab === 'builder' && (
              <div className="flex-1 overflow-y-auto">
                {/* Saved Queries */}
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium text-gray-900">Saved Queries</h3>
                    <button className="text-green-600 hover:text-green-700">
                      <Plus size={16} />
                    </button>
                  </div>
                  <div className="space-y-2">
                    {savedQueries.map((savedQuery) => (
                      <div
                        key={savedQuery.id}
                        className="p-3 border border-gray-200 rounded-lg hover:border-green-300 cursor-pointer transition-colors group"
                        onClick={() => setQuery(savedQuery.query)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-sm text-gray-900 truncate group-hover:text-green-700">
                              {savedQuery.name}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              {savedQuery.createdAt}
                            </div>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleFavorite(savedQuery.id);
                            }}
                            className="p-1 hover:bg-gray-100 rounded"
                          >
                            {savedQuery.favorite ? (
                              <Star size={14} className="text-yellow-500 fill-current" />
                            ) : (
                              <StarOff size={14} className="text-gray-400" />
                            )}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Query History */}
                <div className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium text-gray-900">Recent History</h3>
                    <Clock size={16} className="text-gray-400" />
                  </div>
                  <div className="space-y-2">
                    {queryHistory.map((historyItem) => (
                      <div
                        key={historyItem.id}
                        className="p-3 border border-gray-200 rounded-lg hover:border-green-300 cursor-pointer transition-colors group"
                        onClick={() => setQuery(historyItem.query)}
                      >
                        <div className="text-xs font-mono text-gray-700 line-clamp-2 group-hover:text-green-700">
                          {historyItem.query}
                        </div>
                        <div className="flex items-center justify-between mt-2">
                          <div className="text-xs text-gray-500">
                            {historyItem.executedAt}
                          </div>
                          <div className="text-xs text-gray-500">
                            {historyItem.executionTime.toFixed(3)}s
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'templates' && (
              <div className="flex-1 overflow-y-auto p-4">
                <div className="space-y-3">
                  {queryTemplates.map((template) => (
                    <TemplateCard key={template.id} template={template} />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Query Editor & Results */}
          <div className="flex-1 flex flex-col">
            {/* Header */}
            <div className="p-6 border-b border-gray-200 bg-white">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Query Builder</h1>
                  <p className="text-gray-600">Write and execute custom queries on your store data</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={saveQuery}
                    className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    <Save size={16} />
                    Save
                  </button>
                  <button className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                    <Copy size={16} />
                    Copy
                  </button>
                </div>
              </div>
            </div>

            {/* Query Editor */}
            <div className="p-6 border-b border-gray-200 bg-white">
              <div className="relative">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full h-48 p-4 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                  placeholder="Enter your SQL query here..."
                />
                <div className="absolute bottom-3 right-3">
                  <button
                    onClick={executeQuery}
                    disabled={isExecuting || !query.trim()}
                    className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                  >
                    {isExecuting ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Executing...
                      </>
                    ) : (
                      <>
                        <Play size={16} />
                        Execute Query
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Query Stats */}
              <div className="flex items-center gap-6 mt-4 text-sm text-gray-600">
                <div>Lines: {query.split('\n').length}</div>
                <div>Characters: {query.length}</div>
                {queryResults && (
                  <>
                    <div>Execution time: {queryResults.executionTime}s</div>
                    <div>Rows returned: {queryResults.rowCount}</div>
                  </>
                )}
              </div>
            </div>

            {/* Results */}
            <div className="flex-1 p-6 bg-gray-50">
              {queryResults ? (
                <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                    <h3 className="font-medium text-gray-900">Query Results</h3>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">
                        {queryResults.rowCount} rows
                      </span>
                      <button className="p-2 text-gray-400 hover:text-green-600">
                        <Download size={16} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          {queryResults.columns.map((column, idx) => (
                            <th key={idx} className="px-6 py-3 text-left font-medium text-gray-900 text-sm">
                              {column}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {queryResults.rows.map((row, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            {row.map((cell, cellIdx) => (
                              <td key={cellIdx} className="px-6 py-4 text-sm text-gray-900">
                                {cell}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Search size={24} className="text-gray-400" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Query</h3>
                  <p className="text-gray-600 mb-4">
                    Write your SQL query above and click "Execute Query" to see results
                  </p>
                  <div className="text-sm text-gray-500">
                    💡 Tip: Try one of the query templates to get started quickly
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default QueryBuilder;