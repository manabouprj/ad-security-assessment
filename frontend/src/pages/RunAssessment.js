import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Alert, Spinner, Modal } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { runAssessment, runInteractiveAssessment, getConfig } from '../services/api';
import BaselineSelector from '../components/BaselineSelector';

const RunAssessment = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [configLoading, setConfigLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [interactiveMode, setInteractiveMode] = useState(false);
  const [showOutputModal, setShowOutputModal] = useState(false);
  const [outputText, setOutputText] = useState('');
  const [formData, setFormData] = useState({
    domain: '',
    server: '',
    username: '',
    password: '',
    use_ssl: true,
    verify_ssl: true,
    mock_mode: false,
    baseline: null
  });

  useEffect(() => {
    const loadConfig = async () => {
      try {
        setConfigLoading(true);
        const config = await getConfig();
        setFormData({
          domain: config.domain || '',
          server: config.server || '',
          username: config.username || '',
          password: '',  // Don't load password from config for security
          use_ssl: config.use_ssl !== undefined ? config.use_ssl : true,
          verify_ssl: config.verify_ssl !== undefined ? config.verify_ssl : true,
          mock_mode: config.mock_mode || false
        });
      } catch (err) {
        console.error('Error loading configuration:', err);
        // Don't set error, just use default values
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

  const handleBaselineSelect = (baselineInfo) => {
    setFormData({
      ...formData,
      baseline: baselineInfo
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    setOutputText('');

    // Validate baseline selection
    if (!formData.baseline) {
      setError('Please select a compliance baseline before running the assessment.');
      setLoading(false);
      return;
    }

    try {
      if (interactiveMode) {
        // Run in interactive mode
        const result = await runInteractiveAssessment(formData);
        
        if (result.output) {
          setOutputText(result.output);
          setShowOutputModal(true);
        }
        
        setSuccess(true);
        // Don't navigate away automatically in interactive mode
      } else {
        // Run in normal mode
        await runAssessment(formData);
        setSuccess(true);
        setTimeout(() => {
          navigate('/');
        }, 2000);
      }
    } catch (err) {
      if (err.response && err.response.data) {
        const errorData = err.response.data;
        if (errorData.output) {
          setOutputText(errorData.output);
          setShowOutputModal(true);
        }
        setError(errorData.message || 'Failed to run assessment. Please check your settings and try again.');
      } else {
        setError('Failed to run assessment. Please check your settings and try again.');
      }
      console.error('Error running assessment:', err);
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
    <div>
      <h1 className="mb-4">Run Assessment</h1>
      
      {/* Modal for displaying interactive output */}
      <Modal
        show={showOutputModal}
        onHide={() => setShowOutputModal(false)}
        size="lg"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Interactive Assessment Output</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="bg-dark text-light p-3 rounded" style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', maxHeight: '400px', overflow: 'auto' }}>
            {outputText}
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowOutputModal(false)}>
            Close
          </Button>
          <Button variant="primary" onClick={() => navigate('/')}>
            Go to Dashboard
          </Button>
        </Modal.Footer>
      </Modal>
      
      <BaselineSelector onBaselineSelect={handleBaselineSelect} />
      
      <Card className="dashboard-card">
        <Card.Header className="dashboard-card-header">Assessment Configuration</Card.Header>
        <Card.Body>
          {error && (
            <Alert variant="danger" className="mb-4">
              {error}
            </Alert>
          )}
          
          {success && (
            <Alert variant="success" className="mb-4">
              {interactiveMode 
                ? "Interactive assessment completed successfully! Check the output for details."
                : "Assessment started successfully! Redirecting to dashboard..."
              }
            </Alert>
          )}
          
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                id="interactive-mode"
                name="interactive_mode"
                label="Use Interactive Mode"
                checked={interactiveMode}
                onChange={(e) => setInteractiveMode(e.target.checked)}
              />
              <Form.Text className="text-muted">
                Enable this option to run the assessment in interactive mode, which will guide you through the configuration process step by step.
              </Form.Text>
            </Form.Group>
            
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
                Enable this option to run the assessment with simulated data, without connecting to an actual Active Directory server.
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
                  required={!formData.mock_mode}
                  placeholder="example.com"
                />
                <Form.Text className="text-muted">
                  The Active Directory domain name to assess.
                </Form.Text>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Domain Controller</Form.Label>
                <Form.Control
                  type="text"
                  name="server"
                  value={formData.server}
                  onChange={handleChange}
                  disabled={formData.mock_mode}
                  required={!formData.mock_mode}
                  placeholder="dc.example.com"
                />
                <Form.Text className="text-muted">
                  The hostname or IP address of a domain controller.
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
                <Form.Text className="text-muted">
                  Username with appropriate permissions to query AD. Leave blank to use current credentials.
                </Form.Text>
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
                  Password for the specified user. Leave blank to use current credentials.
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
                <Form.Text className="text-muted">
                  Enable to use secure LDAP (LDAPS) for encrypted communications.
                </Form.Text>
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
                  <Form.Text className="text-muted">
                    Enable to verify SSL certificates. Disable if using self-signed certificates.
                  </Form.Text>
                </Form.Group>
              )}
            </div>
            
            <div className="d-flex justify-content-end mt-4">
              <Button variant="secondary" className="me-2" onClick={() => navigate('/')}>
                Cancel
              </Button>
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
                    Running...
                  </>
                ) : (
                  'Run Assessment'
                )}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default RunAssessment;
