import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import AuthContextProvider from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
import Subjects from './pages/Subjects';
import Attendance from './pages/Attendance';
import Tutorials from './pages/Tutorials';
import StudyNotes from './pages/StudyNotes';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import UserManagement from './pages/UserManagement';
import AppHeader from './components/AppHeader';
import AppSider from './components/AppSider';
import './App.css';

const { Content } = Layout;

function App() {
  return (
    <AuthContextProvider>
      <Router>
        <Layout style={{ minHeight: '100vh' }}>
          <AppSider />
          <Layout>
            <AppHeader />
            <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={
                  <PrivateRoute>
                    <Dashboard />
                  </PrivateRoute>
                } />
                <Route path="/students" element={
                  <PrivateRoute>
                    <Students />
                  </PrivateRoute>
                } />
                <Route path="/subjects" element={
                  <PrivateRoute>
                    <Subjects />
                  </PrivateRoute>
                } />
                <Route path="/attendance" element={
                  <PrivateRoute>
                    <Attendance />
                  </PrivateRoute>
                } />
                <Route path="/tutorials" element={
                  <PrivateRoute>
                    <Tutorials />
                  </PrivateRoute>
                } />
                <Route path="/notes" element={
                  <PrivateRoute>
                    <StudyNotes />
                  </PrivateRoute>
                } />
                <Route path="/analytics" element={
                  <PrivateRoute>
                    <Analytics />
                  </PrivateRoute>
                } />
                <Route path="/settings" element={
                  <PrivateRoute>
                    <Settings />
                  </PrivateRoute>
                } />
                <Route path="/users" element={
                  <PrivateRoute adminOnly={true}>
                    <UserManagement />
                  </PrivateRoute>
                } />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Router>
    </AuthContextProvider>
  );
}

export default App;