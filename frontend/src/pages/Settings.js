import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Alert, Spinner, Container } from 'react-bootstrap';
import { getConfig, updateConfig } from '../services/api';
import ConnectionTest from '../components/ConnectionTest';

const Settings = () => {
  const [loading, setLoading] = useState(false);
  const [configLoading, setConfigLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    domain: '',
    server: '',
    username: '',
    password: '',
    use_ssl: true,
    verify_ssl: true,
    mock_mode: false,
    max_computers_to_assess: 100,
    report: {
      company_name: 'Your Company',
      include_recommendations: true,
      include_charts: true,
      include_executive_summary: true
    },
    logging: {
      level: 'INFO',
      file_rotation: true,
      max_log_files: 5,
      max_file_size_mb: 10
    }
  });

  useEffect(() => {
    const loadConfig = async () => {
      try {
        setConfigLoading(true);
        const config = await getConfig();
        setFormData({
          ...config,
          password: '',  // Don't load password from config for security
          report: {
            ...formData.report,
            ...config.report
          },
          logging: {
            ...formData.logging,
            ...config.logging
          }
        });
      } catch (err) {
        console.error('Error loading configuration:', err);
        setError('Failed to load configuration. Using default values.');
      } finally {
        setConfigLoading(false);
      }
    };

    loadConfig();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleNestedChange = (section, name, value, type = 'text') => {
    setFormData({
      ...formData,
      [section]: {
        ...formData[section],
        [name]: type === 'checkbox' ? value : 
                type === 'number' ? parseInt(value, 10) : 
                value
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Don't send password if it's empty
      const configToSave = { ...formData };
      if (!configToSave.password) {
        delete configToSave.password;
      }
      
      await updateConfig(configToSave);
      setSuccess(true);
      
      // Clear password field after successful save
      setFormData({
        ...formData,
        password: ''
      });
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccess(false);
      }, 3000);
    } catch (err) {
      setError('Failed to save configuration. Please try again.');
      console.error('Error saving configuration:', err);
    } finally {
      setLoading(false);
    }
  };

  if (configLoading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-2">Loading configuration...</p>
      </div>
    );
  }

  return (
    <Container className="py-4">
      <h2 className="mb-4">Settings</h2>
      <ConnectionTest />
      
      <Form onSubmit={handleSubmit}>
        {error && (
          <Alert variant="danger" className="mb-4">
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert variant="success" className="mb-4">
            Configuration saved successfully!
          </Alert>
        )}
        
        <Card className="dashboard-card mb-4">
          <Card.Header className="dashboard-card-header">Connection Settings</Card.Header>
          <Card.Body>
            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                id="mock-mode"
                name="mock_mode"
                label="Use Mock Mode (No actual AD connection)"
                checked={formData.mock_mode}
                onChange={handleChange}
              />
              <Form.Text className="text-muted">
                Enable this option to use simulated data, without connecting to an actual Active Directory server.
              </Form.Text>
            </Form.Group>
            
            <div className={formData.mock_mode ? 'opacity-50' : ''}>
              <Form.Group className="mb-3">
                <Form.Label>Domain Name</Form.Label>
                <Form.Control
                  type="text"
                  name="domain"
                  value={formData.domain}
                  onChange={handleChange}
                  disabled={formData.mock_mode}
                  placeholder="example.com"
                />
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Domain Controller IP Address</Form.Label>
                <Form.Control
                  type="text"
                  name="server"
                  value={formData.server}
                  onChange={handleChange}
                  disabled={formData.mock_mode}
                  placeholder="192.168.1.100"
                />
                <Form.Text className="text-muted">
                  Enter the IP address of your domain controller for more reliable connections.
                </Form.Text>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Username</Form.Label>
                <Form.Control
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  disabled={formData.mock_mode}
                  placeholder="username@example.com"
                />
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Password</Form.Label>
                <Form.Control
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={formData.mock_mode}
                  placeholder="••••••••"
                />
                <Form.Text className="text-muted">
                  Leave blank to keep the current password.
                </Form.Text>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  id="use-ssl"
                  name="use_ssl"
                  label="Use SSL/TLS (LDAPS)"
                  checked={formData.use_ssl}
                  onChange={handleChange}
                  disabled={formData.mock_mode}
                />
              </Form.Group>
              
              {formData.use_ssl && (
                <Form.Group className="mb-3">
                  <Form.Check
                    type="checkbox"
                    id="verify-ssl"
                    name="verify_ssl"
                    label="Verify SSL Certificates"
                    checked={formData.verify_ssl}
                    onChange={handleChange}
                    disabled={formData.mock_mode}
                  />
                </Form.Group>
              )}
            </div>
          </Card.Body>
        </Card>
        
        <Card className="dashboard-card mb-4">
          <Card.Header className="dashboard-card-header">Assessment Settings</Card.Header>
          <Card.Body>
            <Form.Group className="mb-3">
              <Form.Label>Maximum Computers to Assess</Form.Label>
              <Form.Control
                type="number"
                name="max_computers_to_assess"
                value={formData.max_computers_to_assess}
                onChange={handleChange}
                min="1"
                max="1000"
              />
              <Form.Text className="text-muted">
                Limit the number of computers to assess in large environments.
              </Form.Text>
            </Form.Group>
          </Card.Body>
        </Card>
        
        <Card className="dashboard-card mb-4">
          <Card.Header className="dashboard-card-header">Report Settings</Card.Header>
          <Card.Body>
            <Form.Group className="mb-3">
              <Form.Label>Company Name</Form.Label>
              <Form.Control
                type="text"
                value={formData.report.company_name}
                onChange={(e) => handleNestedChange('report', 'company_name', e.target.value)}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                id="include-recommendations"
                checked={formData.report.include_recommendations}
                onChange={(e) => handleNestedChange('report', 'include_recommendations', e.target.checked, 'checkbox')}
                label="Include Recommendations"
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                id="include-charts"
                checked={formData.report.include_charts}
                onChange={(e) => handleNestedChange('report', 'include_charts', e.target.checked, 'checkbox')}
                label="Include Charts"
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                id="include-executive-summary"
                checked={formData.report.include_executive_summary}
                onChange={(e) => handleNestedChange('report', 'include_executive_summary', e.target.checked, 'checkbox')}
                label="Include Executive Summary"
              />
            </Form.Group>
          </Card.Body>
        </Card>
        
        <Card className="dashboard-card mb-4">
          <Card.Header className="dashboard-card-header">Logging Settings</Card.Header>
          <Card.Body>
            <Form.Group className="mb-3">
              <Form.Label>Log Level</Form.Label>
              <Form.Select
                value={formData.logging.level}
                onChange={(e) => handleNestedChange('logging', 'level', e.target.value)}
              >
                <option value="DEBUG">DEBUG</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
                <option value="CRITICAL">CRITICAL</option>
              </Form.Select>
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                id="file-rotation"
                checked={formData.logging.file_rotation}
                onChange={(e) => handleNestedChange('logging', 'file_rotation', e.target.checked, 'checkbox')}
                label="Enable Log File Rotation"
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Maximum Log Files</Form.Label>
              <Form.Control
                type="number"
                value={formData.logging.max_log_files}
                onChange={(e) => handleNestedChange('logging', 'max_log_files', e.target.value, 'number')}
                min="1"
                max="100"
                disabled={!formData.logging.file_rotation}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Maximum File Size (MB)</Form.Label>
              <Form.Control
                type="number"
                value={formData.logging.max_file_size_mb}
                onChange={(e) => handleNestedChange('logging', 'max_file_size_mb', e.target.value, 'number')}
                min="1"
                max="100"
                disabled={!formData.logging.file_rotation}
              />
            </Form.Group>
          </Card.Body>
        </Card>
        
        <div className="d-flex justify-content-end mt-4">
          <Button variant="primary" type="submit" disabled={loading}>
            {loading ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-2"
                />
                Saving...
              </>
            ) : (
              'Save Settings'
            )}
          </Button>
        </div>
      </Form>
    </Container>
  );
};

export default Settings;
