import React, { useState } from 'react';
import { Form, Button, Alert, Card, Spinner, Row, Col } from 'react-bootstrap';
import axios from 'axios';

const ConnectionTest = () => {
  const [formData, setFormData] = useState({
    domain: '',
    server: '',
    username: '',
    password: '',
    port: 389,
    use_ssl: false
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('/api/test-connection', formData);
      setResult(response.data);
    } catch (err) {
      console.error('Connection test error:', err);
      
      // Handle different types of errors
      if (err.response) {
        // The server responded with an error status code
        setError(err.response.data || { error: 'Failed to test connection' });
      } else if (err.request) {
        // The request was made but no response was received
        setError({ 
          error: 'No response from server', 
          details: 'The API server is not responding. Please check if it is running.',
          solutions: [
            'Verify the API server is running',
            'Check network connectivity',
            'Restart the application'
          ]
        });
      } else {
        // Something happened in setting up the request
        setError({ 
          error: 'Request configuration error', 
          details: err.message,
          solutions: [
            'Check browser console for more details',
            'Verify API endpoint is correct'
          ]
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">Test Domain Controller Connection</h5>
      </Card.Header>
      <Card.Body>
        <Form onSubmit={handleSubmit}>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Domain</Form.Label>
                <Form.Control
                  type="text"
                  name="domain"
                  value={formData.domain}
                  onChange={handleChange}
                  placeholder="e.g., example.com"
                  required
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Domain Controller IP/Hostname</Form.Label>
                <Form.Control
                  type="text"
                  name="server"
                  value={formData.server}
                  onChange={handleChange}
                  placeholder="e.g., 192.168.1.100 or dc01.example.com"
                />
                <Form.Text className="text-muted">
                  Optional. If left blank, the system will attempt to discover domain controllers automatically.
                </Form.Text>
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Username</Form.Label>
                <Form.Control
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Domain username"
                  required
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Password</Form.Label>
                <Form.Control
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Domain password"
                  required
                />
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Port</Form.Label>
                <Form.Control
                  type="number"
                  name="port"
                  value={formData.port}
                  onChange={handleChange}
                  placeholder="389 (LDAP) or 636 (LDAPS)"
                />
                <Form.Text className="text-muted">
                  Default: 389 for LDAP, 636 for LDAPS
                </Form.Text>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3 mt-4">
                <Form.Check
                  type="checkbox"
                  name="use_ssl"
                  label="Use SSL/TLS (LDAPS)"
                  checked={formData.use_ssl}
                  onChange={handleChange}
                />
              </Form.Group>
            </Col>
          </Row>

          <Button variant="primary" type="submit" disabled={loading}>
            {loading ? (
              <>
                <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                {' '}Testing Connection...
              </>
            ) : (
              'Test Connection'
            )}
          </Button>
        </Form>

        {error && (
          <Alert variant="danger" className="mt-3">
            <Alert.Heading>Connection Test Failed</Alert.Heading>
            <p>{error.error}</p>
            {error.details && <p>{error.details}</p>}
            {error.solutions && error.solutions.length > 0 && (
              <>
                <hr />
                <h6>Possible Solutions:</h6>
                <ul>
                  {error.solutions.map((solution, index) => (
                    <li key={index}>{solution}</li>
                  ))}
                </ul>
              </>
            )}
          </Alert>
        )}

        {result && result.success && (
          <Alert variant="success" className="mt-3">
            <Alert.Heading>Connection Test Successful</Alert.Heading>
            <p>{result.message}</p>
            {result.details && (
              <>
                <hr />
                <h6>Test Results:</h6>
                <ul>
                  <li>Basic Connection: {result.details.connection?.status || 'Success'}</li>
                  <li>Domain Controller Discovery: {result.details.domain_controllers?.status || 'Success'}</li>
                  <li>Authentication: {result.details.authentication?.status || 'Success'}</li>
                </ul>
              </>
            )}
            {result.details?.domain_controllers?.controllers && (
              <>
                <hr />
                <h6>Domain Controllers Found:</h6>
                <ul>
                  {result.details.domain_controllers.controllers.map((dc, index) => (
                    <li key={index}>{dc.name} ({dc.dNSHostName})</li>
                  ))}
                </ul>
              </>
            )}
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

export default ConnectionTest;
