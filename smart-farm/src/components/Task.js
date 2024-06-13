// src/components/Task.js
import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Form, Input, InputNumber, TimePicker, Button, Table, notification, Spin } from 'antd';
import moment from 'moment';

const Task = () => {
  const [taskList, setTaskList] = useState([]);

  useEffect(() => {
    // Fetch task list data
    const fetchTaskListData = async () => {
      try {
        const response = await fetch('https://io.adafruit.com/api/v2/tqhung231/feeds/tasklist/data', {
          headers: { 'X-AIO-Key': 'aio_'.concat('CprR50YfmiOFYFgsFmJFfpxwnffZ') },
        });
        const data = await response.json();
        const latestTaskListData = JSON.parse(data[0].value);
        setTaskList(latestTaskListData);
      } catch (error) {
        console.error('Error fetching task list data:', error);
      }
    };

    fetchTaskListData();
    const interval = setInterval(() => {
      fetchTaskListData();
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleFormSubmit = async (values) => {
    const taskData = {
      name: values.name,
      cycle: values.cycle,
      task: { mixer1: values.mixer1, mixer2: values.mixer2, mixer3: values.mixer3 },
      isActive: false,
      startTime: values.startTime.format('HH:mm'),
      endTime: values.endTime.format('HH:mm'),
    };

    try {
      await fetch('https://io.adafruit.com/api/v2/tqhung231/feeds/task/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-AIO-Key': 'aio_'.concat('CprR50YfmiOFYFgsFmJFfpxwnffZ'),
        },
        body: JSON.stringify({ value: JSON.stringify(taskData) }),
      });
      notification.success({ message: 'Task updated successfully' });
    } catch (error) {
      console.error('Error updating task:', error);
      notification.error({ message: 'Error updating task' });
    }
  };

  const columns = [
    { title: 'Task Name', dataIndex: 'name', key: 'name' },
    { title: 'Cycle', dataIndex: 'cycle', key: 'cycle', align: 'center' },
    { title: 'Mixer 1', dataIndex: ['task', 'mixer1'], key: 'mixer1', align: 'center' },
    { title: 'Mixer 2', dataIndex: ['task', 'mixer2'], key: 'mixer2', align: 'center' },
    { title: 'Mixer 3', dataIndex: ['task', 'mixer3'], key: 'mixer3', align: 'center' },
    { title: 'Start Time', dataIndex: 'startTime', key: 'startTime', align: 'center' },
    { title: 'End Time', dataIndex: 'endTime', key: 'endTime', align: 'center' },
    { title: 'Status', dataIndex: 'isActive', key: 'isActive', align: 'center', render: isActive => isActive ? <Spin /> : ' ' },
  ];

  return (
    <div className="task">
      <Card title="Task List" bordered={false} style={{
        marginTop: '16px',
        border: '1px solid #e8e8e8', // Adds a light border
        boxShadow: '0 4px 8px 0 rgba(0,0,0,0.2)', // Adds a subtle shadow
        transition: '0.3s', // Smooth transition for hover effects
      }}>
        <Table columns={columns} dataSource={taskList} rowKey="name" pagination={{ pageSize: 5 }} />
      </Card>
      <Card title="Create New Task" bordered={false} style={{
        marginTop: '16px',
        border: '1px solid #e8e8e8', // Adds a light border
        boxShadow: '0 4px 8px 0 rgba(0,0,0,0.2)', // Adds a subtle shadow
        transition: '0.3s', // Smooth transition for hover effects
      }}>
        <Form
          layout="vertical"
          onFinish={handleFormSubmit}
          initialValues={{
            name: '',
            cycle: 1,
            mixer1: 0,
            mixer2: 0,
            mixer3: 0,
            startTime: moment('00:00', 'HH:mm'),
            endTime: moment('00:00', 'HH:mm'),
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="name"
                label="Task Name"
                rules={[{ required: true, message: 'Please input the task name!' }]}
              >
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="cycle"
                label="Cycle"
                rules={[{ required: true, message: 'Please input the cycle!' }]}
              >
                <InputNumber min={1} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="mixer1"
                label="Mixer 1"
                rules={[{ required: true, message: 'Please input the value for Mixer 1!' }]}
              >
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="mixer2"
                label="Mixer 2"
                rules={[{ required: true, message: 'Please input the value for Mixer 2!' }]}
              >
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="mixer3"
                label="Mixer 3"
                rules={[{ required: true, message: 'Please input the value for Mixer 3!' }]}
              >
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="startTime"
                label="Start Time"
                rules={[{ required: true, message: 'Please select the start time!' }]}
              >
                <TimePicker format="HH:mm" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="endTime"
                label="End Time"
                rules={[{ required: true, message: 'Please select the end time!' }]}
              >
                <TimePicker format="HH:mm" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ width: '100%' }}>
              Create Task
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Task;
