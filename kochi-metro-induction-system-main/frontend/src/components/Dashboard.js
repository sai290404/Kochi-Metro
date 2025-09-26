import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { Train, AlertTriangle, CheckCircle, Clock, Settings } from 'lucide-react';
import apiService from '../services/api';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [trains, setTrains] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [summaryRes, trainsRes, alertsRes] = await Promise.all([
        apiService.getDashboardSummary(),
        apiService.getAllTrains(),
        apiService.getAlerts()
      ]);

      setSummary(summaryRes.data.summary);
      setTrains(trainsRes.data.trains);
      setAlerts(alertsRes.data.alerts);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const runOptimization = async () => {
    try {
      setOptimizing(true);
      await apiService.runOptimization({ target_service_trains: 18 });
      await loadDashboardData(); // Refresh data after optimization
    } catch (error) {
      console.error('Error running optimization:', error);
    } finally {
      setOptimizing(false);
    }
  };

  const refreshData = async () => {
    try {
      setLoading(true);
      await apiService.refreshData();
      await loadDashboardData();
    } catch (error) {
      console.error('Error refreshing data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-metro-blue mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Chart data for train allocation
  const allocationData = {
    labels: ['Service', 'Standby', 'Maintenance'],
    datasets: [
      {
        data: [
          summary?.current_allocation?.service_count || 0,
          summary?.current_allocation?.standby_count || 0,
          summary?.current_allocation?.maintenance_count || 0
        ],
        backgroundColor: ['#059669', '#3b82f6', '#ea580c'],
        borderWidth: 0,
      },
    ],
  };

  // Chart data for readiness scores
  const readinessData = {
    labels: trains.map(t => t.train_id.split('-')[1]),
    datasets: [
      {
        label: 'Readiness Score',
        data: trains.map(t => t.readiness_score),
        backgroundColor: trains.map(t => 
          t.readiness_score >= 80 ? '#059669' : 
          t.readiness_score >= 60 ? '#eab308' : '#dc2626'
        ),
        borderWidth: 0,
      },
    ],
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Service': return 'bg-green-100 text-green-800';
      case 'Standby': return 'bg-blue-100 text-blue-800';
      case 'Maintenance': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Service': return <CheckCircle className="w-4 h-4" />;
      case 'Standby': return <Clock className="w-4 h-4" />;
      case 'Maintenance': return <Settings className="w-4 h-4" />;
      default: return <Train className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Kochi Metro Induction System</h1>
              <p className="text-gray-600">Train Fleet Management Dashboard</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={refreshData}
                disabled={loading}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
              >
                Refresh Data
              </button>
              <button
                onClick={runOptimization}
                disabled={optimizing}
                className="px-6 py-2 bg-metro-blue text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {optimizing ? 'Optimizing...' : 'Run Optimization'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Train className="w-8 h-8 text-metro-blue" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Trains</p>
                <p className="text-2xl font-bold text-gray-900">{summary?.total_trains || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">In Service</p>
                <p className="text-2xl font-bold text-gray-900">{summary?.current_allocation?.service_count || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Standby</p>
                <p className="text-2xl font-bold text-gray-900">{summary?.current_allocation?.standby_count || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <AlertTriangle className="w-8 h-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Alerts</p>
                <p className="text-2xl font-bold text-gray-900">{summary?.alerts_count || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Train Allocation Chart */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Train Allocation</h3>
            <div className="h-64 flex items-center justify-center">
              <Doughnut 
                data={allocationData} 
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom',
                    },
                  },
                }}
              />
            </div>
          </div>

          {/* Readiness Scores Chart */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Train Readiness Scores</h3>
            <div className="h-64">
              <Bar 
                data={readinessData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 100,
                    },
                  },
                  plugins: {
                    legend: {
                      display: false,
                    },
                  },
                }}
              />
            </div>
          </div>
        </div>

        {/* Alerts Section */}
        {alerts.length > 0 && (
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Active Alerts</h3>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                {alerts.slice(0, 5).map((alert, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                    <p className="text-sm text-red-800">{alert}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Trains Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Train Fleet Status</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Train ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Readiness
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Branding Priority
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Issues
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {trains.map((train) => (
                  <tr key={train.train_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {train.train_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(train.status)}`}>
                        {getStatusIcon(train.status)}
                        <span className="ml-1">{train.status}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              train.readiness_score >= 80 ? 'bg-green-600' : 
                              train.readiness_score >= 60 ? 'bg-yellow-600' : 'bg-red-600'
                            }`}
                            style={{ width: `${train.readiness_score}%` }}
                          ></div>
                        </div>
                        <span className="ml-2 text-sm text-gray-900">{train.readiness_score}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {train.branding_priority}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {train.issues.length > 0 ? train.issues.join(', ') : 'None'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
