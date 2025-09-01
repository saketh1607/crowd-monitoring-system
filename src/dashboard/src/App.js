import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout, ConfigProvider, theme } from 'antd';
import io from 'socket.io-client';
import './App.css';

// Components
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Events from './pages/Events';
import Emergencies from './pages/Emergencies';
import Resources from './pages/Resources';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';

// Context
import { WebSocketContext } from './context/WebSocketContext';
import { NotificationContext } from './context/NotificationContext';

const { Content } = Layout;

function App() {
  const [socket, setSocket] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    // Initialize WebSocket connection
    const newSocket = io('ws://localhost:8000', {
      transports: ['websocket']
    });

    newSocket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    newSocket.on('emergency_alert', (data) => {
      addNotification({
        type: 'error',
        title: 'Emergency Alert',
        message: `${data.type} emergency detected at ${data.location}`,
        timestamp: new Date().toISOString()
      });
    });

    newSocket.on('emergency_created', (data) => {
      addNotification({
        type: 'warning',
        title: 'New Emergency',
        message: `${data.data.type} emergency reported`,
        timestamp: new Date().toISOString()
      });
    });

    newSocket.on('emergency_updated', (data) => {
      addNotification({
        type: 'info',
        title: 'Emergency Update',
        message: `Emergency status updated to ${data.data.status}`,
        timestamp: new Date().toISOString()
      });
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const addNotification = (notification) => {
    const newNotification = {
      ...notification,
      id: Date.now() + Math.random(),
      read: false
    };
    setNotifications(prev => [newNotification, ...prev.slice(0, 49)]); // Keep last 50
  };

  const markNotificationAsRead = (id) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  const toggleTheme = () => {
    setDarkMode(!darkMode);
  };

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: darkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <WebSocketContext.Provider value={socket}>
        <NotificationContext.Provider value={{
          notifications,
          addNotification,
          markNotificationAsRead,
          clearNotifications
        }}>
          <Router>
            <Layout style={{ minHeight: '100vh' }}>
              <Sidebar collapsed={collapsed} />
              <Layout>
                <Header
                  darkMode={darkMode}
                  toggleTheme={toggleTheme}
                  collapsed={collapsed}
                  toggleSidebar={toggleSidebar}
                />
                <Content style={{ margin: '16px' }}>
                  <div style={{ 
                    padding: 24, 
                    minHeight: 360,
                    background: darkMode ? '#141414' : '#fff',
                    borderRadius: 8
                  }}>
                    <Routes>
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/events" element={<Events />} />
                      <Route path="/emergencies" element={<Emergencies />} />
                      <Route path="/resources" element={<Resources />} />
                      <Route path="/analytics" element={<Analytics />} />
                      <Route path="/settings" element={<Settings />} />
                    </Routes>
                  </div>
                </Content>
              </Layout>
            </Layout>
          </Router>
        </NotificationContext.Provider>
      </WebSocketContext.Provider>
    </ConfigProvider>
  );
}

export default App;
