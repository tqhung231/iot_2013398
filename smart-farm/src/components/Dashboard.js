// src/components/Dashboard.js
import React, { useEffect, useState } from 'react';
import { Card, Col, Row, Progress, Switch, notification } from 'antd';

const conicColors = {
  '0%': '#108ee9',
  '100%': '#87d068',
};

const formatArea = (area) => {
  const textPart = area.match(/[a-zA-Z]+/)[0];
  const numberPart = area.match(/\d+/)[0];
  return textPart.charAt(0).toUpperCase() + textPart.slice(1).toLowerCase() + ' ' + numberPart;
};

const Dashboard = () => {
  const [soilData, setSoilData] = useState({
    area1: { temperature: 0, humidity: 0, moisture: 0 },
    area2: { temperature: 0, humidity: 0, moisture: 0 },
    area3: { temperature: 0, humidity: 0, moisture: 0 },
  });

  const [automatic, setAutomatic] = useState(false);
  const [watering, setWatering] = useState({
    area1: false,
    area2: false,
    area3: false,
  });
  const [waterLevel, setWaterLevel] = useState(0);

  useEffect(() => {
    const fetchSoilData = async () => {
      try {
        const response = await fetch('https://io.adafruit.com/api/v2/tqhung231/feeds/soil/data', {
          headers: {
            'X-AIO-Key': 'aio_'.concat('CprR50YfmiOFYFgsFmJFfpxwnffZ')
          }
        });
        const data = await response.json();
        const latestData = JSON.parse(data[0].value);
        setSoilData(latestData);
      } catch (error) {
        console.error('Error fetching soil data:', error);
      }
    };

    const fetchMonitorData = async () => {
      try {
        const response = await fetch('https://io.adafruit.com/api/v2/tqhung231/feeds/monitor/data', {
          headers: {
            'X-AIO-Key': 'aio_'.concat('CprR50YfmiOFYFgsFmJFfpxwnffZ')
          }
        });
        const data = await response.json();
        const latestMonitorData = JSON.parse(data[0].value);
        setAutomatic(latestMonitorData.automatic);
        setWatering(latestMonitorData.watering);
      } catch (error) {
        console.error('Error fetching monitor data:', error);
      }
    };

    const fetchWaterLevel = async () => {
      try {
        const response = await fetch('https://io.adafruit.com/api/v2/tqhung231/feeds/level/data', {
          headers: {
            'X-AIO-Key': 'aio_'.concat('CprR50YfmiOFYFgsFmJFfpxwnffZ')
          }
        });
        const data = await response.json();
        const latestData = JSON.parse(data[0].value)["water"];
        setWaterLevel(latestData);
      } catch (error) {
        console.error('Error fetching soil data:', error);
      }
    };

    fetchSoilData();
    fetchMonitorData();
    fetchWaterLevel();
    const interval = setInterval(() => {
      fetchSoilData();
      fetchMonitorData();
      fetchWaterLevel();
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleAutomaticToggle = async (checked) => {
    const newAutomatic = checked;
    setAutomatic(newAutomatic);

    try {
      await fetch('https://io.adafruit.com/api/v2/tqhung231/feeds/monitor/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-AIO-Key': 'aio_'.concat('CprR50YfmiOFYFgsFmJFfpxwnffZ'),
        },
        body: JSON.stringify({ value: JSON.stringify({ automatic: newAutomatic, watering }) }),
      });
      // notification.success({ message: 'Automatic mode updated successfully' });
    } catch (error) {
      console.error('Error updating automatic mode:', error);
      notification.error({ message: 'Error updating automatic mode' });
    }
  };

  const handleWateringToggle = async (area, checked) => {
    const newWatering = { ...watering, [area]: checked };
    setWatering(newWatering);
    setAutomatic(false);

    try {
      await fetch('https://io.adafruit.com/api/v2/tqhung231/feeds/monitor/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-AIO-Key': 'aio_'.concat('CprR50YfmiOFYFgsFmJFfpxwnffZ'),
        },
        body: JSON.stringify({ value: JSON.stringify({ automatic: false, watering: newWatering }) }),
      });
      // notification.success({ message: `Watering ${area} updated successfully` });
    } catch (error) {
      console.error(`Error updating watering ${area}:`, error);
      notification.error({ message: `Error updating watering ${area}` });
    }
  };

  return (
    <div className="dashboard">
      <Row gutter={16}>
        <Col span={16}>
          {Object.keys(soilData).map(area => (
            <Card title={formatArea(area)} bordered={false} key={area} style={{
              marginTop: '16px',
              border: '1px solid #e8e8e8', // Adds a light border
              boxShadow: '0 4px 8px 0 rgba(0,0,0,0.2)', // Adds a subtle shadow
              transition: '0.3s', // Smooth transition for hover effects
            }}>
              <Row gutter={16} align="middle" style={{ textAlign: 'center' }}>
                <Col span={8} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <p style={{ marginBottom: '8px' }}>Temperature</p>
                  <Progress
                    type="dashboard"
                    percent={soilData[area].temperature}
                    strokeColor={conicColors}
                    format={percent => `${percent} °C`}
                    className='custom-progress'
                  />
                </Col>
                <Col span={8} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <p style={{ marginBottom: '8px' }}>Humidity</p>
                  <Progress
                    type="dashboard"
                    percent={soilData[area].humidity}
                    strokeColor={conicColors}
                    format={percent => `${percent} %`}
                    className='custom-progress'
                  />
                </Col>
                <Col span={8} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <p style={{ marginBottom: '8px' }}>Moisture</p>
                  <Progress
                    type="dashboard"
                    percent={soilData[area].moisture}
                    strokeColor={conicColors}
                    format={percent => `${percent} %`}
                    className='custom-progress'
                  />
                </Col>
              </Row>
            </Card>
          ))}
        </Col>
        <Col span={8}>
          <Card title="Watering Controls" bordered={false} style={{
            marginTop: '16px',
            border: '1px solid #e8e8e8',
            boxShadow: '0 4px 8px 0 rgba(0,0,0,0.2)',
            transition: '0.3s',
          }}>
            <Row gutter={16} style={{ marginBottom: '16px' }}>
              <Col span={12} style={{ display: 'flex', alignItems: 'center' }}>
                <p style={{ marginBottom: 0 }}>Automatic Watering</p>
              </Col>
              <Col span={12} style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                <Switch
                  checked={automatic}
                  onChange={handleAutomaticToggle}
                  checkedChildren="ON"
                  unCheckedChildren="OFF"
                />
              </Col>
            </Row>
            {Object.keys(watering).map(area => (
              <Row gutter={16} key={area} style={{ marginBottom: '16px' }}>
                <Col span={12} style={{ display: 'flex', alignItems: 'center' }}>
                  <p style={{ marginBottom: 0 }}>Area {area.replace(/\D/g, '')} Watering</p>
                </Col>
                <Col span={12} style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                  <Switch
                    checked={watering[area]}
                    onChange={(checked) => handleWateringToggle(area, checked)}
                    checkedChildren="ON"
                    unCheckedChildren="OFF"
                  />
                </Col>
              </Row>
            ))}
          </Card>
          <Card title="Water Level" bordered={false} style={{
            marginTop: '16px',
            border: '1px solid #e8e8e8',
            boxShadow: '0 4px 8px 0 rgba(0,0,0,0.2)',
            transition: '0.3s',
          }}>
            <Col span={24} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Progress percent={waterLevel} status='normal' showInfo={false} />
            </Col>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
