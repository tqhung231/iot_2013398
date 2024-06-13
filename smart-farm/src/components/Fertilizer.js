import React, { useState } from 'react';
import { Form, Input, Button, Select, message, Card } from 'antd';
import axios from 'axios';

const { Option } = Select;

const Fertilizer = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/predict-fertilizer', values);
      setResult(response.data);
      message.success('Fertilizer recommendation received!');
    } catch (error) {
      message.error('Error getting recommendation.');
    }
    setLoading(false);
  };

  const soilTypes = ['Sandy', 'Loamy', 'Black', 'Red', 'Clayey'];
  const cropTypes = [
    'Maize', 'Sugarcane', 'Cotton', 'Tobacco', 'Paddy', 'Barley',
    'Wheat', 'Millets', 'Oil seeds', 'Pulses', 'Ground Nuts'
  ];

  return (
    <Card title="Fertilizer Recommendation" bordered={false} style={{
      marginTop: '16px',
      border: '1px solid #e8e8e8', // Adds a light border
      boxShadow: '0 4px 8px 0 rgba(0,0,0,0.2)', // Adds a subtle shadow
      transition: '0.3s', // Smooth transition for hover effects
    }}>
      <Form onFinish={onFinish}>
        <Form.Item
          name="temparature"
          label="Temparature"
          rules={[{ required: true, message: 'Please input the temparature!' }]}
        >
          <Input type="number" />
        </Form.Item>
        <Form.Item
          name="humidity"
          label="Humidity"
          rules={[{ required: true, message: 'Please input the humidity!' }]}
        >
          <Input type="number" />
        </Form.Item>
        <Form.Item
          name="moisture"
          label="Moisture"
          rules={[{ required: true, message: 'Please input the moisture!' }]}
        >
          <Input type="number" />
        </Form.Item>
        <Form.Item
          name="soilType"
          label="Soil Type"
          rules={[{ required: true, message: 'Please select the soil type!' }]}
        >
          <Select>
            {soilTypes.map(soil => (
              <Option key={soil} value={soil}>{soil}</Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item
          name="cropType"
          label="Crop Type"
          rules={[{ required: true, message: 'Please select the crop type!' }]}
        >
          <Select>
            {cropTypes.map(crop => (
              <Option key={crop} value={crop}>{crop}</Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item
          name="nitrogen"
          label="Nitrogen"
          rules={[{ required: true, message: 'Please input the nitrogen level!' }]}
        >
          <Input type="number" />
        </Form.Item>
        <Form.Item
          name="phosphorous"
          label="Phosphorous"
          rules={[{ required: true, message: 'Please input the phosphorous level!' }]}
        >
          <Input type="number" />
        </Form.Item>
        <Form.Item
          name="potassium"
          label="Potassium"
          rules={[{ required: true, message: 'Please input the potassium level!' }]}
        >
          <Input type="number" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            Get Recommendation
          </Button>
        </Form.Item>
      </Form>
      {result && (
        <div>
          <h3>Recommended Fertilizer: {result.fertilizer}</h3>
        </div>
      )}
    </Card>
  );
};

export default Fertilizer;
