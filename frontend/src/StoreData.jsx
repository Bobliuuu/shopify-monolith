import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Table, 
  Search, 
  Filter, 
  Download, 
  RefreshCw, 
  ChevronRight, 
  ChevronDown,
  Eye,
  Edit,
  Trash2,
  Plus
} from 'lucide-react';
import TopBar from './components/topBar';
import Sidebar from './components/sidebar';

function StoreDataExplorer() {
  const [selectedDatabase, setSelectedDatabase] = useState('store_insights');
  const [selectedTable, setSelectedTable] = useState('orders');
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedDatabases, setExpandedDatabases] = useState(['store_insights']);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage] = useState(10);

  // Mock database structure
  const databases = {
    store_insights: {
      tables: {
        orders: {
          description: 'Customer order data with metrics',
          rowCount: 15420,
          columns: ['id', 'customer_id', 'total_amount', 'status', 'created_at', 'updated_at']
        },
        products: {
          description: 'Product catalog and performance',
          rowCount: 856,
          columns: ['id', 'title', 'price', 'inventory', 'category', 'sales_count']
        },
        customers: {
          description: 'Customer profiles and behavior',
          rowCount: 3241,
          columns: ['id', 'email', 'first_name', 'last_name', 'total_spent', 'orders_count']
        },
        analytics_sessions: {
          description: 'User session analytics data',
          rowCount: 89642,
          columns: ['id', 'session_id', 'user_id', 'page_views', 'duration', 'conversion']
        },
        inventory_movements: {
          description: 'Stock movement tracking',
          rowCount: 12893,
          columns: ['id', 'product_id', 'movement_type', 'quantity', 'timestamp', 'reason']
        }
      }
    },
    marketing_data: {
      tables: {
        campaigns: {
          description: 'Marketing campaign performance',
          rowCount: 234,
          columns: ['id', 'name', 'type', 'spend', 'impressions', 'clicks', 'conversions']
        },
        email_metrics: {
          description: 'Email marketing analytics',
          rowCount: 5678,
          columns: ['id', 'campaign_id', 'sent', 'opened', 'clicked', 'unsubscribed']
        }
      }
    }
  };

  // Mock table data
  const mockData = {
    orders: [
      { id: 1001, customer_id: 501, total_amount: '$125.99', status: 'fulfilled', created_at: '2024-08-10 14:30', updated_at: '2024-08-10 15:45' },
      { id: 1002, customer_id: 502, total_amount: '$67.50', status: 'pending', created_at: '2024-08-10 16:20', updated_at: '2024-08-10 16:20' },
      { id: 1003, customer_id: 503, total_amount: '$234.00', status: 'fulfilled', created_at: '2024-08-09 09:15', updated_at: '2024-08-09 11:30' },
      { id: 1004, customer_id: 504, total_amount: '$89.99', status: 'cancelled', created_at: '2024-08-09 18:45', updated_at: '2024-08-10 08:20' },
      { id: 1005, customer_id: 505, total_amount: '$156.75', status: 'fulfilled', created_at: '2024-08-08 13:10', updated_at: '2024-08-08 14:25' }
    ],
    products: [
      { id: 201, title: 'Premium Coffee Beans', price: '$24.99', inventory: 150, category: 'Coffee', sales_count: 89 },
      { id: 202, title: 'Organic Tea Blend', price: '$18.50', inventory: 75, category: 'Tea', sales_count: 45 },
      { id: 203, title: 'French Press', price: '$45.00', inventory: 25, category: 'Equipment', sales_count: 23 },
      { id: 204, title: 'Coffee Grinder', price: '$129.99', inventory: 12, category: 'Equipment', sales_count: 15 },
      { id: 205, title: 'Espresso Cups Set', price: '$32.99', inventory: 40, category: 'Accessories', sales_count: 67 }
    ],
    customers: [
      { id: 501, email: 'john.doe@email.com', first_name: 'John', last_name: 'Doe', total_spent: '$450.75', orders_count: 5 },
      { id: 502, email: 'jane.smith@email.com', first_name: 'Jane', last_name: 'Smith', total_spent: '$234.50', orders_count: 3 },
      { id: 503, email: 'bob.wilson@email.com', first_name: 'Bob', last_name: 'Wilson', total_spent: '$678.90', orders_count: 8 },
      { id: 504, email: 'alice.brown@email.com', first_name: 'Alice', last_name: 'Brown', total_spent: '$123.25', orders_count: 2 },
      { id: 505, email: 'charlie.davis@email.com', first_name: 'Charlie', last_name: 'Davis', total_spent: '$890.40', orders_count: 12 }
    ]
  };

  useEffect(() => {
    loadTableData();
  }, [selectedTable]);

  const loadTableData = () => {
    setLoading(true);
    setTimeout(() => {
      setTableData(mockData[selectedTable] || []);
      setLoading(false);
    }, 500);
  };

  const toggleDatabase = (dbName) => {
    setExpandedDatabases(prev => 
      prev.includes(dbName) 
        ? prev.filter(name => name !== dbName)
        : [...prev, dbName]
    );
  };

  const selectTable = (dbName, tableName) => {
    setSelectedDatabase(dbName);
    setSelectedTable(tableName);
  };

  const filteredData = tableData.filter(row =>
    Object.values(row).some(value =>
      value.toString().toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  const paginatedData = filteredData.slice(
    (currentPage - 1) * rowsPerPage,
    currentPage * rowsPerPage
  );

  const totalPages = Math.ceil(filteredData.length / rowsPerPage);



  const DatabaseTree = () => (
    <div className="space-y-1">
      {Object.entries(databases).map(([dbName, dbData]) => (
        <div key={dbName}>
          <button
            onClick={() => toggleDatabase(dbName)}
            className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-gray-50 rounded-lg"
          >
            {expandedDatabases.includes(dbName) ? (
              <ChevronDown size={16} />
            ) : (
              <ChevronRight size={16} />
            )}
            <Database size={16} className="text-blue-600" />
            <span className="font-medium text-gray-700">{dbName}</span>
          </button>
          
          {expandedDatabases.includes(dbName) && (
            <div className="ml-6 space-y-1">
              {Object.entries(dbData.tables).map(([tableName, tableInfo]) => (
                <button
                  key={tableName}
                  onClick={() => selectTable(dbName, tableName)}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-left rounded-lg transition-colors ${
                    selectedTable === tableName && selectedDatabase === dbName
                      ? 'bg-green-50 text-green-700'
                      : 'hover:bg-gray-50 text-gray-600'
                  }`}
                >
                  <Table size={14} />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">{tableName}</div>
                    <div className="text-xs text-gray-500">{tableInfo.rowCount.toLocaleString()} rows</div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <TopBar 
        sidebarOpen={sidebarOpen} 
        setSidebarOpen={setSidebarOpen}
        pageTitle="Store Analytics"
        pageSubtitle="Store Data Explorer"
      />

      <div className="flex">
        <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

        {/* Main Content */}
        <div className="flex-1 flex">
          {/* Database Explorer */}
          <div className="w-80 bg-white border-r border-gray-200 p-4">
            <div className="mb-4">
              <h2 className="font-semibold text-gray-900 mb-2">Database Explorer</h2>
              <div className="relative">
                <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search databases..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <DatabaseTree />
            </div>
          </div>

          {/* Data View */}
          <div className="flex-1 p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    {selectedDatabase}.{selectedTable}
                  </h1>
                  <p className="text-gray-600">
                    {databases[selectedDatabase]?.tables[selectedTable]?.description}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={loadTableData}
                    className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw size={16} />
                    Refresh
                  </button>
                  <button className="flex items-center gap-2 px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">
                    <Download size={16} />
                    Export
                  </button>
                </div>
              </div>

              {/* Table Controls */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search table data..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>
                  <button className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                    <Filter size={16} />
                    Filter
                  </button>
                </div>
                <div className="text-sm text-gray-600">
                  Showing {paginatedData.length} of {filteredData.length} rows
                </div>
              </div>
            </div>

            {/* Data Table */}
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              {loading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-gray-600">Loading table data...</span>
                  </div>
                </div>
              ) : (
                <>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left">
                            <input type="checkbox" className="rounded" />
                          </th>
                          {tableData.length > 0 && Object.keys(tableData[0]).map((column) => (
                            <th key={column} className="px-4 py-3 text-left font-medium text-gray-900">
                              {column}
                            </th>
                          ))}
                          <th className="px-4 py-3 text-left font-medium text-gray-900">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {paginatedData.map((row, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-4 py-3">
                              <input type="checkbox" className="rounded" />
                            </td>
                            {Object.values(row).map((value, i) => (
                              <td key={i} className="px-4 py-3 text-sm text-gray-900">
                                {value}
                              </td>
                            ))}
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                <button className="p-1 text-gray-400 hover:text-blue-600">
                                  <Eye size={16} />
                                </button>
                                <button className="p-1 text-gray-400 hover:text-green-600">
                                  <Edit size={16} />
                                </button>
                                <button className="p-1 text-gray-400 hover:text-red-600">
                                  <Trash2 size={16} />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination */}
                  <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      Page {currentPage} of {totalPages}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                        disabled={currentPage === 1}
                        className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                        disabled={currentPage === totalPages}
                        className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default StoreDataExplorer;