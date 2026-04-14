import React, { useState, useEffect } from 'react';
import {
  Table, Button, Space, Modal, Form, Input, Select, DatePicker,
  message, Popconfirm, Upload, Tag, Input as AntInput
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined,
  UploadOutlined, EyeOutlined, SearchOutlined
} from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';

const { Option } = Select;
const { TextArea } = AntInput;

const Students = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 50,
    total: 0
  });
  const [searchText, setSearchText] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  const [form] = Form.useForm();
  const [programs, setPrograms] = useState([]);

  useEffect(() => {
    fetchStudents();
    fetchPrograms();
  }, []);

  const fetchStudents = async (params = {}) => {
    setLoading(true);
    try {
      const response = await axios.get('/api/students', {
        params: {
          page: params.current || pagination.current,
          per_page: params.pageSize || pagination.pageSize,
          search: searchText,
          ...params
        }
      });

      setStudents(response.data.students);
      setPagination({
        ...pagination,
        ...response.data.pagination
      });
    } catch (error) {
      message.error('Failed to fetch students');
    } finally {
      setLoading(false);
    }
  };

  const fetchPrograms = async () => {
    try {
      const response = await axios.get('/api/students/programs');
      setPrograms(response.data.programs);
    } catch (error) {
      console.error('Failed to fetch programs');
    }
  };

  const handleSearch = (value) => {
    setSearchText(value);
    fetchStudents({ current: 1, search: value });
  };

  const handleTableChange = (pagination, filters, sorter) => {
    fetchStudents({
      current: pagination.current,
      pageSize: pagination.pageSize,
      sortField: sorter.field,
      sortOrder: sorter.order,
      ...filters
    });
  };

  const showModal = (student = null) => {
    setEditingStudent(student);
    setIsModalVisible(true);

    if (student) {
      form.setFieldsValue({
        ...student,
        dob: student.dob ? moment(student.dob) : null,
        enrollment_date: student.enrollment_date ? moment(student.enrollment_date) : null
      });
    } else {
      form.resetFields();
      // Generate student ID
      const studentId = `STU-${new Date().getFullYear()}-${Math.floor(Math.random() * 9000) + 1000}`;
      form.setFieldsValue({ student_id: studentId });
    }
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setEditingStudent(null);
    form.resetFields();
  };

  const handleSubmit = async (values) => {
    try {
      const data = {
        ...values,
        dob: values.dob ? values.dob.format('YYYY-MM-DD') : null,
        enrollment_date: values.enrollment_date ? values.enrollment_date.format('YYYY-MM-DD') : null
      };

      if (editingStudent) {
        await axios.put(`/api/students/${editingStudent.student_id}`, data);
        message.success('Student updated successfully');
      } else {
        await axios.post('/api/students', data);
        message.success('Student added successfully');
      }

      setIsModalVisible(false);
      setEditingStudent(null);
      form.resetFields();
      fetchStudents();
    } catch (error) {
      message.error(error.response?.data?.error || 'Operation failed');
    }
  };

  const handleDelete = async (studentId) => {
    try {
      await axios.delete(`/api/students/${studentId}`);
      message.success('Student deleted successfully');
      fetchStudents();
    } catch (error) {
      message.error('Failed to delete student');
    }
  };

  const columns = [
    {
      title: 'Student ID',
      dataIndex: 'student_id',
      key: 'student_id',
      sorter: true,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: true,
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Program',
      dataIndex: 'program',
      key: 'program',
      filters: programs.map(program => ({ text: program, value: program })),
    },
    {
      title: 'Gender',
      dataIndex: 'gender',
      key: 'gender',
      filters: [
        { text: 'Male', value: 'Male' },
        { text: 'Female', value: 'Female' },
        { text: 'Other', value: 'Other' }
      ],
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'Active' ? 'green' : 'red'}>
          {status}
        </Tag>
      ),
      filters: [
        { text: 'Active', value: 'Active' },
        { text: 'Inactive', value: 'Inactive' },
        { text: 'Graduated', value: 'Graduated' }
      ],
    },
    {
      title: 'GPA',
      dataIndex: 'gpa',
      key: 'gpa',
      render: (gpa) => gpa ? gpa.toFixed(2) : 'N/A',
      sorter: true,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => showModal(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Are you sure you want to delete this student?"
            onConfirm={() => handleDelete(record.student_id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Students Management</h1>
        <Space>
          <Input
            placeholder="Search students..."
            prefix={<SearchOutlined />}
            onChange={(e) => handleSearch(e.target.value)}
            style={{ width: 250 }}
          />
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => showModal()}
          >
            Add Student
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={students}
        rowKey="id"
        loading={loading}
        pagination={{
          ...pagination,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} students`
        }}
        onChange={handleTableChange}
        size="middle"
      />

      <Modal
        title={editingStudent ? "Edit Student" : "Add New Student"}
        open={isModalVisible}
        onCancel={handleCancel}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="student_id"
                label="Student ID"
                rules={[{ required: true, message: 'Please enter student ID' }]}
              >
                <Input disabled={!!editingStudent} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="name"
                label="Full Name"
                rules={[{ required: true, message: 'Please enter full name' }]}
              >
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="email" label="Email">
                <Input type="email" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="phone" label="Phone">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="gender" label="Gender">
                <Select placeholder="Select gender">
                  <Option value="Male">Male</Option>
                  <Option value="Female">Female</Option>
                  <Option value="Other">Other</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="dob" label="Date of Birth">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="program" label="Program">
                <Select placeholder="Select program" showSearch>
                  {programs.map(program => (
                    <Option key={program} value={program}>{program}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="address" label="Address">
            <TextArea rows={2} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="guardian_name" label="Guardian Name">
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="guardian_phone" label="Guardian Phone">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="status" label="Status" initialValue="Active">
            <Select>
              <Option value="Active">Active</Option>
              <Option value="Inactive">Inactive</Option>
              <Option value="Graduated">Graduated</Option>
            </Select>
          </Form.Item>

          <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
            <Space>
              <Button onClick={handleCancel}>
                Cancel
              </Button>
              <Button type="primary" htmlType="submit">
                {editingStudent ? 'Update' : 'Create'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Students;