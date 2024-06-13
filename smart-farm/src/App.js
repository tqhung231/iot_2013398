// src/App.js
import React, { useState } from 'react';
import { Layout, Menu } from 'antd';
import { DashboardOutlined, UnorderedListOutlined, ExperimentOutlined } from '@ant-design/icons';
import Dashboard from './components/Dashboard';
import Task from './components/Task';
import Fertilizer from './components/Fertilizer';
import './App.css';
import Logo from './assets/icon.svg';

const { Content, Sider } = Layout;

function App() {
  const [selectedKey, setSelectedKey] = useState('1');

  const handleMenuClick = e => {
    setSelectedKey(e.key);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider>
        <div className="logo-container">
          <img src={Logo} alt="Logo" className='logo-icon' />
          <span className="logo-text">Smart Farm</span>
        </div>
        <Menu
          theme="dark"
          defaultSelectedKeys={['1']}
          mode="inline"
          selectedKeys={[selectedKey]}
          onClick={handleMenuClick}
        >
          <Menu.Item key="1" icon={<DashboardOutlined />}>
            Dashboard
          </Menu.Item>
          <Menu.Item key="2" icon={<UnorderedListOutlined />}>
            Task
          </Menu.Item>
          <Menu.Item key="3" icon={<ExperimentOutlined />}>
            Fertilizer
          </Menu.Item>
        </Menu>
      </Sider>
      <Layout className="site-layout">
        <Content style={{ margin: '0 16px' }}>
          <div className="site-layout-background" style={{ padding: 24, minHeight: 360 }}>
            {selectedKey === '1' && <Dashboard />}
            {selectedKey === '2' && <Task />}
            {selectedKey === '3' && <Fertilizer />} {/* Add the new component */}
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
