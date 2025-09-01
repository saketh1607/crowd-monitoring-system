import React, { useState, useEffect, useContext } from 'react';
import { Row, Col, Card, Statistic, Alert, Timeline, Badge, Spin } from 'antd';
import { 
  FireOutlined, 
  MedicineBoxOutlined, 
  SecurityScanOutlined,
  UserOutlined,
  WarningOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import EmergencyMap from '../components/EmergencyMap';
import RealTimeMetrics from '../components/RealTimeMetrics';
import { WebSocketContext } from '../context/WebSocketContext';
import { apiService } from '../services/apiService';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState({
    activeEmergencies: 0,
    totalEvents: 0,
    availableResources: 0,
    riskLevel: 'medium'
  });
  const [emergencies, setEmergencies] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [riskTrends, setRiskTrends] = useState([]);
  const [emergencyTypes, setEmergencyTypes] = useState([]);
  
  const socket = useContext(WebSocketContext);

  useEffect(() => {
    loadDashboardData();
    
    // Set up real-time updates
    if (socket) {
      socket.on('emergency_created', handleEmergencyUpdate);
      socket.on('emergency_updated', handleEmergencyUpdate);
      socket.on('status_update', handleStatusUpdate);
    }

    // Refresh data every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);

    return () => {
      clearInterval(interval);
      if (socket) {
        socket.off('emergency_created', handleEmergencyUpdate);
        socket.off('emergency_updated', handleEmergencyUpdate);
        socket.off('status_update', handleStatusUpdate);
      }
    };
  }, [socket]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load dashboard statistics
      const [emergenciesRes, eventsRes, resourcesRes] = await Promise.all([
        apiService.getEmergencies({ status: 'active' }),
        apiService.getEvents(),
        apiService.getResources({ available: true })
      ]);

      setDashboardData({
        activeEmergencies: emergenciesRes.data.length,
        totalEvents: eventsRes.data.length,
        availableResources: resourcesRes.data.length,
        riskLevel: calculateOverallRisk(emergenciesRes.data)
      });

      setEmergencies(emergenciesRes.data.slice(0, 10)); // Latest 10

      // Generate mock data for charts
      generateMockChartData();
      generateRecentActivity(emergenciesRes.data);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEmergencyUpdate = (data) => {
    loadDashboardData(); // Refresh all data
  };

  const handleStatusUpdate = (data) => {
    // Update specific metrics without full reload
    setDashboardData(prev => ({
      ...prev,
      ...data.data
    }));
  };

  const calculateOverallRisk = (emergencies) => {
    if (emergencies.length === 0) return 'low';
    
    const criticalCount = emergencies.filter(e => e.severity === 'critical').length;
    const highCount = emergencies.filter(e => e.severity === 'high').length;
    
    if (criticalCount > 0) return 'critical';
    if (highCount > 2) return 'high';
    if (emergencies.length > 5) return 'medium';
    return 'low';
  };

  const generateMockChartData = () => {
    // Risk trends over time
    const trends = [];
    for (let i = 23; i >= 0; i--) {
      trends.push({
        time: `${i}:00`,
        risk: Math.random() * 100,
        incidents: Math.floor(Math.random() * 10)
      });
    }
    setRiskTrends(trends);

    // Emergency types distribution
    setEmergencyTypes([
      { name: 'Medical', value: 45, color: '#52c41a' },
      { name: 'Security', value: 30, color: '#1890ff' },
      { name: 'Fire', value: 15, color: '#ff4d4f' },
      { name: 'Other', value: 10, color: '#faad14' }
    ]);
  };

  const generateRecentActivity = (emergencies) => {
    const activity = emergencies.slice(0, 5).map((emergency, index) => ({
      id: emergency.id,
      time: new Date(emergency.detected_at).toLocaleTimeString(),
      type: emergency.type,
      description: `${emergency.type} emergency ${emergency.status}`,
      status: emergency.status,
      severity: emergency.severity
    }));
    setRecentActivity(activity);
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'critical': return '#ff4d4f';
      case 'high': return '#fa8c16';
      case 'medium': return '#faad14';
      case 'low': return '#52c41a';
      default: return '#d9d9d9';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'resolved': return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'responding': return <Spin size="small" />;
      case 'confirmed': return <WarningOutlined style={{ color: '#fa8c16' }} />;
      default: return <WarningOutlined style={{ color: '#ff4d4f' }} />;
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      {/* Alert Banner */}
      {dashboardData.riskLevel === 'critical' && (
        <Alert
          message="Critical Risk Level"
          description="Multiple high-severity emergencies detected. All response teams have been notified."
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Key Metrics */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Active Emergencies"
              value={dashboardData.activeEmergencies}
              prefix={<WarningOutlined />}
              valueStyle={{ color: dashboardData.activeEmergencies > 0 ? '#ff4d4f' : '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Active Events"
              value={dashboardData.totalEvents}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Available Resources"
              value={dashboardData.availableResources}
              prefix={<SecurityScanOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Risk Level"
              value={dashboardData.riskLevel.toUpperCase()}
              valueStyle={{ color: getRiskColor(dashboardData.riskLevel) }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        {/* Emergency Map */}
        <Col span={16}>
          <Card title="Emergency Locations" style={{ height: 400 }}>
            <EmergencyMap emergencies={emergencies} />
          </Card>
        </Col>

        {/* Recent Activity */}
        <Col span={8}>
          <Card title="Recent Activity" style={{ height: 400 }}>
            <Timeline>
              {recentActivity.map((activity) => (
                <Timeline.Item
                  key={activity.id}
                  dot={getStatusIcon(activity.status)}
                >
                  <div>
                    <Badge
                      status={activity.severity === 'critical' ? 'error' : 'processing'}
                      text={activity.description}
                    />
                    <div style={{ fontSize: '12px', color: '#999', marginTop: 4 }}>
                      {activity.time}
                    </div>
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        {/* Risk Trends */}
        <Col span={16}>
          <Card title="Risk Trends (24 Hours)">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={riskTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="risk" 
                  stroke="#1890ff" 
                  strokeWidth={2}
                  name="Risk Level"
                />
                <Line 
                  type="monotone" 
                  dataKey="incidents" 
                  stroke="#ff4d4f" 
                  strokeWidth={2}
                  name="Incidents"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Emergency Types */}
        <Col span={8}>
          <Card title="Emergency Types Distribution">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={emergencyTypes}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {emergencyTypes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Real-time Metrics */}
      <Row gutter={16}>
        <Col span={24}>
          <RealTimeMetrics />
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
