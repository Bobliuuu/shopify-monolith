import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  ShoppingCart, 
  Users, 
  Package,
  Calendar,
  Download,
  RefreshCw,
  Filter,
  Settings,
  LogOut,
  Home,
  Database,
  Search,
  FileText,
  MessageSquare,
  BarChart3,
  Eye,
  EyeOff,
  Maximize2,
  Grid3X3,
  Layout,
  Plus,
  MoreVertical,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';
import TopBar from './components/topBar';
import Sidebar from './components/sidebar';

function InsightsDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [dashboardLayout, setDashboardLayout] = useState('grid');
  const [hiddenWidgets, setHiddenWidgets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Mock data for charts
  const revenueData = [
    { date: '2024-08-01', revenue: 12500, orders: 89, customers: 67 },
    { date: '2024-08-02', revenue: 15200, orders: 103, customers: 82 },
    { date: '2024-08-03', revenue: 11800, orders: 76, customers: 61 },
    { date: '2024-08-04', revenue: 18900, orders: 134, customers: 98 },
    { date: '2024-08-05', revenue: 16700, orders: 121, customers: 89 },
    { date: '2024-08-06', revenue: 21300, orders: 156, customers: 112 },
    { date: '2024-08-07', revenue: 19400, orders: 142, customers: 104 },
  ];

  const productData = [
    { name: 'Premium Coffee', sales: 234, revenue: 5850 },
    { name: 'Organic Tea', sales: 189, revenue: 3402 },
    { name: 'French Press', sales: 156, revenue: 7020 },
    { name: 'Coffee Grinder', sales: 98, revenue: 12740 },
    { name: 'Espresso Cups', sales: 167, revenue: 5509 },
  ];

  const customerSegmentData = [
    { name: 'New Customers', value: 35, color: '#10B981' },
    { name: 'Returning', value: 45, color: '#3B82F6' },
    { name: 'VIP', value: 20, color: '#8B5CF6' },
  ];

  const trafficSourceData = [
    { source: 'Organic Search', visits: 3400, conversions: 187 },
    { source: 'Direct', visits: 2800, conversions: 145 },
    { source: 'Social Media', visits: 1900, conversions: 89 },
    { source: 'Email Marketing', visits: 1200, conversions: 98 },
    { source: 'Paid Ads', visits: 800, conversions: 67 },
  ];

  const kpiData = {
    totalRevenue: { value: 115800, change: 12.5, trend: 'up' },
    totalOrders: { value: 821, change: 8.3, trend: 'up' },
    averageOrderValue: { value: 141.07, change: -2.1, trend: 'down' },
    conversionRate: { value: 3.2, change: 0.5, trend: 'up' },
    customerLifetimeValue: { value: 287.50, change: 15.2, trend: 'up' },
    cartAbandonmentRate: { value: 23.1, change: -4.2, trend: 'down' }
  };

  const timeRanges = [
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' },
    { value: '1y', label: 'Last Year' }
  ];

  const refreshDashboard = () => {
    setIsLoading(true);
    setTimeout(() => {
      setLastUpdated(new Date());
      setIsLoading(false);
    }, 1500);
  };

  const toggleWidget = (widgetId) => {
    setHiddenWidgets(prev => 
      prev.includes(widgetId) 
        ? prev.filter(id => id !== widgetId)
        : [...prev, widgetId]
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

  const KPICard = ({ title, value, change, trend, format = 'number', icon: Icon }) => {
    const formatValue = (val) => {
      if (format === 'currency') return `$${val.toLocaleString()}`;
      if (format === 'percentage') return `${val}%`;
      return val.toLocaleString();
    };

    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-sm transition-shadow">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Icon size={20} className="text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">{title}</p>
              <p className="text-2xl font-bold text-gray-900">{formatValue(value)}</p>
            </div>
          </div>
          <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-sm font-medium ${
            trend === 'up' 
              ? 'bg-green-100 text-green-800' 
              : trend === 'down'
              ? 'bg-red-100 text-red-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            {trend === 'up' && <ArrowUp size={14} />}
            {trend === 'down' && <ArrowDown size={14} />}
            {trend === 'neutral' && <Minus size={14} />}
            {Math.abs(change)}%
          </div>
        </div>
      </div>
    );
  };

  const ChartCard = ({ title, children, widgetId, actions = [] }) => {
    const isHidden = hiddenWidgets.includes(widgetId);
    
    return (
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <div className="flex items-center gap-2">
            {actions.map((action, idx) => (
              <button key={idx} onClick={action.onClick} className="p-1.5 text-gray-400 hover:text-gray-600 rounded">
                <action.icon size={16} />
              </button>
            ))}
            <button
              onClick={() => toggleWidget(widgetId)}
              className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
            >
              {isHidden ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>
        {!isHidden && (
          <div className="p-6">
            {children}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <TopBar 
        sidebarOpen={sidebarOpen} 
        setSidebarOpen={setSidebarOpen}
        pageTitle="Store Analytics"
        pageSubtitle="Insights Dashboard"/>

      <div className="flex">
        <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} activePage="dashboard" />
  

        {/* Main Content */}
        <div className="flex-1">
          {/* Dashboard Header */}
          <div className="p-6 border-b border-gray-200 bg-white">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Insights Dashboard</h1>
                <p className="text-gray-600">
                  Last updated: {lastUpdated.toLocaleTimeString()}
                </p>
              </div>
              
              <div className="flex items-center gap-3">
                {/* Time Range Selector */}
                <select
                  value={selectedTimeRange}
                  onChange={(e) => setSelectedTimeRange(e.target.value)}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  {timeRanges.map(range => (
                    <option key={range.value} value={range.value}>{range.label}</option>
                  ))}
                </select>

                {/* Layout Toggle */}
                <div className="flex bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setDashboardLayout('grid')}
                    className={`p-2 rounded-md transition-colors ${
                      dashboardLayout === 'grid' 
                        ? 'bg-white text-green-600 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Grid3X3 size={16} />
                  </button>
                  <button
                    onClick={() => setDashboardLayout('list')}
                    className={`p-2 rounded-md transition-colors ${
                      dashboardLayout === 'list' 
                        ? 'bg-white text-green-600 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Layout size={16} />
                  </button>
                </div>

                {/* Actions */}
                <button className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                  <Filter size={16} />
                  Filter
                </button>
                <button
                  onClick={refreshDashboard}
                  disabled={isLoading}
                  className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                >
                  <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
                  Refresh
                </button>
                <button className="flex items-center gap-2 px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">
                  <Download size={16} />
                  Export
                </button>
              </div>
            </div>
          </div>

          {/* Dashboard Content */}
          <div className="p-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
              <KPICard
                title="Total Revenue"
                value={kpiData.totalRevenue.value}
                change={kpiData.totalRevenue.change}
                trend={kpiData.totalRevenue.trend}
                format="currency"
                icon={DollarSign}
              />
              <KPICard
                title="Total Orders"
                value={kpiData.totalOrders.value}
                change={kpiData.totalOrders.change}
                trend={kpiData.totalOrders.trend}
                icon={ShoppingCart}
              />
              <KPICard
                title="Avg Order Value"
                value={kpiData.averageOrderValue.value}
                change={kpiData.averageOrderValue.change}
                trend={kpiData.averageOrderValue.trend}
                format="currency"
                icon={TrendingUp}
              />
              <KPICard
                title="Conversion Rate"
                value={kpiData.conversionRate.value}
                change={kpiData.conversionRate.change}
                trend={kpiData.conversionRate.trend}
                format="percentage"
                icon={Users}
              />
              <KPICard
                title="Customer LTV"
                value={kpiData.customerLifetimeValue.value}
                change={kpiData.customerLifetimeValue.change}
                trend={kpiData.customerLifetimeValue.trend}
                format="currency"
                icon={TrendingUp}
              />
              <KPICard
                title="Cart Abandonment"
                value={kpiData.cartAbandonmentRate.value}
                change={kpiData.cartAbandonmentRate.change}
                trend={kpiData.cartAbandonmentRate.trend}
                format="percentage"
                icon={ShoppingCart}
              />
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Revenue Trend */}
              <ChartCard 
                title="Revenue Trend" 
                widgetId="revenue-trend"
                actions={[
                  { icon: Maximize2, onClick: () => {} },
                  { icon: Download, onClick: () => {} }
                ]}
              >
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px'
                      }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="revenue" 
                      stroke="#10B981" 
                      fill="#10B981"
                      fillOpacity={0.1}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartCard>

              {/* Top Products */}
              <ChartCard 
                title="Top Selling Products" 
                widgetId="top-products"
                actions={[
                  { icon: Maximize2, onClick: () => {} },
                  { icon: Download, onClick: () => {} }
                ]}
              >
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={productData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="sales" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>

              {/* Customer Segments */}
              <ChartCard 
                title="Customer Segments" 
                widgetId="customer-segments"
                actions={[
                  { icon: Maximize2, onClick: () => {} },
                  { icon: Download, onClick: () => {} }
                ]}
              >
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={customerSegmentData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      dataKey="value"
                      label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {customerSegmentData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </ChartCard>

              {/* Traffic Sources */}
              <ChartCard 
                title="Traffic Sources" 
                widgetId="traffic-sources"
                actions={[
                  { icon: Maximize2, onClick: () => {} },
                  { icon: Download, onClick: () => {} }
                ]}
              >
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={trafficSourceData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis type="number" tick={{ fontSize: 12 }} />
                    <YAxis dataKey="source" type="category" tick={{ fontSize: 12 }} width={100} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="visits" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            {/* Recent Activity */}
            <div className="mt-8">
              <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100">
                  <h3 className="font-semibold text-gray-900">Recent Activity</h3>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                        <TrendingUp size={16} className="text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Revenue increased by 15%</p>
                        <p className="text-sm text-gray-600">Compared to last week</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                        <Users size={16} className="text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">156 new customers acquired</p>
                        <p className="text-sm text-gray-600">In the last 7 days</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
                      <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                        <Package size={16} className="text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Premium Coffee is trending</p>
                        <p className="text-sm text-gray-600">Top selling product this week</p>
                      </div>
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

export default InsightsDashboard;