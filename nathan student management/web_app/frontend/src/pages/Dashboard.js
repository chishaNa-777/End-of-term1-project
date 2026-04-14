import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Spin, Alert } from 'antd';
import {
  UserOutlined,
  BookOutlined,
  CalendarOutlined,
  TrophyOutlined,
  TeamOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import axios from 'axios';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch student stats
      const studentsResponse = await axios.get('/api/students/stats');
      const studentsStats = studentsResponse.data;

      // Fetch subjects stats
      const subjectsResponse = await axios.get('/api/subjects/stats');
      const subjectsStats = subjectsResponse.data;

      // Fetch attendance stats
      const attendanceResponse = await axios.get('/api/attendance/stats');
      const attendanceStats = attendanceResponse.data;

      setStats({
        students: studentsStats,
        subjects: subjectsStats,
        attendance: attendanceStats
      });

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Error"
        description={error}
        type="error"
        showIcon
        style={{ marginBottom: 20 }}
      />
    );
  }

  return (
    <div>
      <h1 style={{ marginBottom: 30, color: '#1890ff' }}>Dashboard</h1>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 30 }}>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic
              title="Total Students"
              value={stats?.students?.total_students || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic
              title="Active Students"
              value={stats?.students?.status_distribution?.Active || 0}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic
              title="Total Subjects"
              value={stats?.subjects?.total_subjects || 0}
              prefix={<BookOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic
              title="Avg Attendance %"
              value={stats?.attendance?.average_percentage || 0}
              suffix="%"
              prefix={<CalendarOutlined />}
              valueStyle={{ color: '#722ed1' }}
              precision={1}
            />
          </Card>
        </Col>
      </Row>

      {/* Recent Activity */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Student Distribution by Program" style={{ height: 300 }}>
            {stats?.students?.program_distribution && Object.keys(stats.students.program_distribution).length > 0 ? (
              <div style={{ padding: 20 }}>
                {Object.entries(stats.students.program_distribution).map(([program, count]) => (
                  <div key={program} style={{ marginBottom: 10 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                      <span>{program}</span>
                      <span>{count} students</span>
                    </div>
                    <div style={{
                      height: 8,
                      background: '#f0f0f0',
                      borderRadius: 4,
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${(count / stats.students.total_students) * 100}%`,
                        height: '100%',
                        background: '#1890ff',
                        borderRadius: 4
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                No program data available
              </div>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Gender Distribution" style={{ height: 300 }}>
            {stats?.students?.gender_distribution && Object.keys(stats.students.gender_distribution).length > 0 ? (
              <div style={{ padding: 20 }}>
                {Object.entries(stats.students.gender_distribution).map(([gender, count]) => (
                  <div key={gender} style={{ marginBottom: 15 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                      <span>{gender || 'Not specified'}</span>
                      <span>{count} students</span>
                    </div>
                    <div style={{
                      height: 12,
                      background: '#f0f0f0',
                      borderRadius: 6,
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${(count / stats.students.total_students) * 100}%`,
                        height: '100%',
                        background: gender === 'Male' ? '#1890ff' : gender === 'Female' ? '#fa8c16' : '#52c41a',
                        borderRadius: 6
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                No gender data available
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Top Performers Preview */}
      <Row style={{ marginTop: 20 }}>
        <Col span={24}>
          <Card title="Quick Stats" size="small">
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="Average GPA"
                  value={stats?.subjects?.average_gpa || 0}
                  prefix={<TrophyOutlined />}
                  valueStyle={{ color: '#faad14' }}
                  precision={2}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="Pass Rate"
                  value={stats?.subjects?.pass_rate || 0}
                  suffix="%"
                  prefix={<BarChartOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                  precision={1}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="Total Records"
                  value={(stats?.subjects?.total_subjects || 0) + (stats?.attendance?.total_records || 0)}
                  prefix={<BookOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;