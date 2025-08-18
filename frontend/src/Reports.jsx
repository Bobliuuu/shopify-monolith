import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  Calendar, 
  TrendingUp, 
  DollarSign, 
  Users, 
  ShoppingCart, 
  Package,
  Clock,
  Eye,
  Trash2,
  Plus,
  Settings,
  LogOut,
  Home,
  Database,
  Search,
  BarChart3,
  MessageSquare,
  Filter,
  RefreshCw,
  Send,
  BookOpen,
  PieChart,
  BarChart,
  Activity,
  Target,
  Zap,
  CheckCircle,
  AlertCircle,
  XCircle,
  PlayCircle,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';
import TopBar from './components/topBar';
import Sidebar from './components/sidebar';

function Reports() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('generate');
  const [selectedReportType, setSelectedReportType] = useState('quarterly');
  const [selectedPeriod, setSelectedPeriod] = useState('Q3-2024');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedReports, setGeneratedReports] = useState([]);
  const [reportTemplates, setReportTemplates] = useState([]);
  const [selectedMetrics, setSelectedMetrics] = useState(['revenue', 'orders', 'customers']);

  // Mock data for report templates
  const reportTypes = [
    {
      id: 'quarterly',
      name: 'Quarterly Business Report',
      description: 'Comprehensive quarterly performance analysis',
      icon: BarChart,
      color: 'bg-blue-500',
      estimatedTime: '2-3 minutes',
      sections: ['Executive Summary', 'Financial Performance', 'Customer Analytics', 'Product Performance', 'Market Trends']
    },
    {
      id: 'financial',
      name: 'Financial Statement',
      description: 'Detailed financial performance and P&L analysis',
      icon: DollarSign,
      color: 'bg-green-500',
      estimatedTime: '3-4 minutes',
      sections: ['Revenue Analysis', 'Cost Breakdown', 'Profit Margins', 'Cash Flow', 'Tax Information']
    },
    {
      id: 'sales',
      name: 'Sales Performance Report',
      description: 'Sales metrics, trends, and forecasting',
      icon: TrendingUp,
      color: 'bg-purple-500',
      estimatedTime: '2 minutes',
      sections: ['Sales Overview', 'Product Performance', 'Channel Analysis', 'Sales Team Metrics', 'Forecasting']
    },
    {
      id: 'customer',
      name: 'Customer Analytics Report',
      description: 'Customer behavior, segmentation, and retention',
      icon: Users,
      color: 'bg-orange-500',
      estimatedTime: '3 minutes',
      sections: ['Customer Segments', 'Lifetime Value', 'Acquisition Costs', 'Retention Analysis', 'Satisfaction Scores']
    },
    {
      id: 'inventory',
      name: 'Inventory & Supply Report',
      description: 'Stock levels, turnover, and supply chain metrics',
      icon: Package,
      color: 'bg-indigo-500',
      estimatedTime: '2-3 minutes',
      sections: ['Stock Levels', 'Turnover Rates', 'Demand Forecasting', 'Supplier Performance', 'Cost Analysis']
    },
    {
      id: 'marketing',
      name: 'Marketing Performance Report',
      description: 'Campaign effectiveness and ROI analysis',
      icon: Target,
      color: 'bg-pink-500',
      estimatedTime: '2 minutes',
      sections: ['Campaign Overview', 'Channel Performance', 'ROI Analysis', 'Attribution Models', 'Budget Allocation']
    }
  ];

  const timePeriods = {
    quarterly: ['Q1-2024', 'Q2-2024', 'Q3-2024', 'Q4-2024', 'Q1-2023', 'Q2-2023', 'Q3-2023', 'Q4-2023'],
    monthly: ['Aug 2024', 'Jul 2024', 'Jun 2024', 'May 2024', 'Apr 2024', 'Mar 2024'],
    yearly: ['2024', '2023', '2022', '2021']
  };

  const availableMetrics = [
    { id: 'revenue', name: 'Revenue Analysis', icon: DollarSign },
    { id: 'orders', name: 'Order Metrics', icon: ShoppingCart },
    { id: 'customers', name: 'Customer Analytics', icon: Users },
    { id: 'products', name: 'Product Performance', icon: Package },
    { id: 'marketing', name: 'Marketing ROI', icon: Target },
    { id: 'costs', name: 'Cost Analysis', icon: Activity },
    { id: 'conversion', name: 'Conversion Rates', icon: TrendingUp },
    { id: 'retention', name: 'Customer Retention', icon: Users }
  ];

  // Mock generated reports
  const mockReports = [
    {
      id: 1,
      name: 'Q3 2024 Quarterly Report',
      type: 'Quarterly Business Report',
      period: 'Q3-2024',
      status: 'completed',
      generatedAt: '2024-08-15 10:30:00',
      fileSize: '2.4 MB',
      pages: 24,
      metrics: ['revenue', 'orders', 'customers', 'products'],
      downloadUrl: '#'
    },
    {
      id: 2,
      name: 'July 2024 Financial Statement',
      type: 'Financial Statement',
      period: 'Jul 2024',
      status: 'completed',
      generatedAt: '2024-08-01 14:15:00',
      fileSize: '1.8 MB',
      pages: 18,
      metrics: ['revenue', 'costs', 'marketing'],
      downloadUrl: '#'
    },
    {
      id: 3,
      name: 'Customer Analytics - Q2 2024',
      type: 'Customer Analytics Report',
      period: 'Q2-2024',
      status: 'generating',
      generatedAt: '2024-08-15 11:45:00',
      progress: 65,
      metrics: ['customers', 'retention', 'conversion']
    },
    {
      id: 4,
      name: 'Sales Performance August',
      type: 'Sales Performance Report',
      period: 'Aug 2024',
      status: 'failed',
      generatedAt: '2024-08-15 09:20:00',
      error: 'Insufficient data for selected period',
      metrics: ['revenue', 'orders', 'conversion']
    }
  ];

  useEffect(() => {
    setGeneratedReports(mockReports);
  }, []);

  const generateReport = async () => {
    setIsGenerating(true);
    
    const selectedType = reportTypes.find(type => type.id === selectedReportType);
    const newReport = {
      id: Date.now(),
      name: `${selectedType.name} - ${selectedPeriod}`,
      type: selectedType.name,
      period: selectedPeriod,
      status: 'generating',
      generatedAt: new Date().toLocaleString(),
      progress: 0,
      metrics: selectedMetrics
    };

    setGeneratedReports(prev => [newReport, ...prev]);

    // Simulate report generation progress
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 200));
      setGeneratedReports(prev => 
        prev.map(report => 
          report.id === newReport.id 
            ? { ...report, progress }
            : report
        )
      );
    }

    // Complete the report
    setTimeout(() => {
      setGeneratedReports(prev => 
        prev.map(report => 
          report.id === newReport.id 
            ? { 
                ...report, 
                status: 'completed',
                fileSize: `${(Math.random() * 3 + 1).toFixed(1)} MB`,
                pages: Math.floor(Math.random() * 20 + 10),
                downloadUrl: '#'
              }
            : report
        )
      );
      setIsGenerating(false);
    }, 500);
  };

  const deleteReport = (reportId) => {
    setGeneratedReports(prev => prev.filter(report => report.id !== reportId));
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

  const ReportTypeCard = ({ reportType, selected, onSelect }) => (
    <div
      onClick={() => onSelect(reportType.id)}
      className={`p-6 border-2 rounded-lg cursor-pointer transition-all ${
        selected 
          ? 'border-green-500 bg-green-50' 
          : 'border-gray-200 hover:border-green-300 hover:bg-gray-50'
      }`}
    >
      <div className="flex items-start gap-4">
        <div className={`w-12 h-12 ${reportType.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
          <reportType.icon size={24} className="text-white" />
        </div>
        <div className="flex-1">
          <h3 className={`font-semibold mb-2 ${selected ? 'text-green-800' : 'text-gray-900'}`}>
            {reportType.name}
          </h3>
          <p className="text-sm text-gray-600 mb-3">{reportType.description}</p>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <Clock size={14} />
              {reportType.estimatedTime}
            </div>
            <div className="flex items-center gap-1">
              <FileText size={14} />
              {reportType.sections.length} sections
            </div>
          </div>
          <div className="mt-3 flex flex-wrap gap-1">
            {reportType.sections.slice(0, 3).map((section, idx) => (
              <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                {section}
              </span>
            ))}
            {reportType.sections.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                +{reportType.sections.length - 3} more
              </span>
            )}
          </div>
        </div>
        {selected && (
          <div className="flex-shrink-0">
            <CheckCircle size={20} className="text-green-600" />
          </div>
        )}
      </div>
    </div>
  );

  const ReportCard = ({ report }) => {
    const getStatusIcon = () => {
      switch (report.status) {
        case 'completed': return <CheckCircle size={16} className="text-green-600" />;
        case 'generating': return <PlayCircle size={16} className="text-blue-600" />;
        case 'failed': return <XCircle size={16} className="text-red-600" />;
        default: return <Clock size={16} className="text-gray-400" />;
      }
    };

    const getStatusColor = () => {
      switch (report.status) {
        case 'completed': return 'bg-green-100 text-green-800';
        case 'generating': return 'bg-blue-100 text-blue-800';
        case 'failed': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
      }
    };

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-sm transition-shadow">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-1">{report.name}</h3>
            <p className="text-sm text-gray-600">{report.type}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${getStatusColor()}`}>
              {getStatusIcon()}
              {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
            </span>
          </div>
        </div>

        {report.status === 'generating' && (
          <div className="mb-4">
            <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
              <span>Generating report...</span>
              <span>{report.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${report.progress}%` }}
              />
            </div>
          </div>
        )}

        {report.status === 'failed' && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle size={16} className="text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-800">Generation Failed</p>
                <p className="text-sm text-red-700 mt-1">{report.error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Calendar size={14} />
              {report.period}
            </div>
            {report.fileSize && (
              <div className="flex items-center gap-1">
                <FileText size={14} />
                {report.fileSize}
              </div>
            )}
            {report.pages && (
              <div className="flex items-center gap-1">
                <BookOpen size={14} />
                {report.pages} pages
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {report.status === 'completed' && (
              <>
                <button className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50">
                  <Eye size={16} />
                </button>
                <button className="p-2 text-gray-400 hover:text-green-600 rounded-lg hover:bg-green-50">
                  <Download size={16} />
                </button>
              </>
            )}
            <button 
              onClick={() => deleteReport(report.id)}
              className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50"
            >
              <Trash2 size={16} />
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <TopBar 
        sidebarOpen={sidebarOpen} 
        setSidebarOpen={setSidebarOpen}
        pageTitle="Store Analytics"
        pageSubtitle="Report Generator"/>

      <div className="flex">
        <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} activePage="reports" />

        {/* Main Content */}
        <div className="flex-1">
          {/* Header */}
          <div className="p-6 border-b border-gray-200 bg-white">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Report Generator</h1>
                <p className="text-gray-600">Generate comprehensive business reports and analytics</p>
              </div>
              
              {/* Tabs */}
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setActiveTab('generate')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'generate' 
                      ? 'bg-white text-green-700 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Plus size={16} className="inline mr-2" />
                  Generate
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'history' 
                      ? 'bg-white text-green-700 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Clock size={16} className="inline mr-2" />
                  History
                </button>
              </div>
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'generate' && (
              <div className="max-w-4xl mx-auto">
                {/* Report Type Selection */}
                <div className="mb-8">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Report Type</h2>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {reportTypes.map((type) => (
                      <ReportTypeCard
                        key={type.id}
                        reportType={type}
                        selected={selectedReportType === type.id}
                        onSelect={setSelectedReportType}
                      />
                    ))}
                  </div>
                </div>

                {/* Configuration */}
                <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
                  <h3 className="font-semibold text-gray-900 mb-6">Report Configuration</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Time Period */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Time Period
                      </label>
                      <select
                        value={selectedPeriod}
                        onChange={(e) => setSelectedPeriod(e.target.value)}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        {timePeriods.quarterly.map(period => (
                          <option key={period} value={period}>{period}</option>
                        ))}
                      </select>
                    </div>

                    {/* Format */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Output Format
                      </label>
                      <select className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500">
                        <option value="pdf">PDF Document</option>
                        <option value="excel">Excel Spreadsheet</option>
                        <option value="powerpoint">PowerPoint Presentation</option>
                      </select>
                    </div>
                  </div>

                  {/* Metrics Selection */}
                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Include Metrics
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {availableMetrics.map((metric) => (
                        <label key={metric.id} className="flex items-center gap-2 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={selectedMetrics.includes(metric.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedMetrics(prev => [...prev, metric.id]);
                              } else {
                                setSelectedMetrics(prev => prev.filter(id => id !== metric.id));
                              }
                            }}
                            className="rounded text-green-600"
                          />
                          <metric.icon size={16} className="text-gray-400" />
                          <span className="text-sm text-gray-700">{metric.name}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Generate Button */}
                <div className="text-center">
                  <button
                    onClick={generateReport}
                    disabled={isGenerating}
                    className="px-8 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-3 mx-auto"
                  >
                    {isGenerating ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Generating Report...
                      </>
                    ) : (
                      <>
                        <Zap size={20} />
                        Generate Report
                      </>
                    )}
                  </button>
                  {selectedReportType && (
                    <p className="text-sm text-gray-600 mt-2">
                      Estimated time: {reportTypes.find(type => type.id === selectedReportType)?.estimatedTime}
                    </p>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'history' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Report History</h2>
                  <div className="flex items-center gap-3">
                    <button className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                      <Filter size={16} />
                      Filter
                    </button>
                    <button className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                      <RefreshCw size={16} />
                      Refresh
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {generatedReports.map((report) => (
                    <ReportCard key={report.id} report={report} />
                  ))}
                </div>

                {generatedReports.length === 0 && (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <FileText size={24} className="text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Reports Yet</h3>
                    <p className="text-gray-600 mb-4">
                      Generate your first report to see it appear here
                    </p>
                    <button
                      onClick={() => setActiveTab('generate')}
                      className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                    >
                      Create Report
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Reports;