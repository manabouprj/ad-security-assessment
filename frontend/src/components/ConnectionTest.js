import React, { useState } from 'react';
import { Form, Button, Alert, Card, Spinner } from 'react-bootstrap';
import axios from 'axios';

const ConnectionTest = () => {
  const [formData, setFormData] = useState({
    domain: '',
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
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
      setError(err.response?.data || { error: 'Failed to test connection' });
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

          <Form.Group className="mb-3">
            <Form.Label>Domain Controller IP</Form.Label>
            <Form.Control
              type="text"
              name="server"
              value={formData.server}
              onChange={handleChange}
              placeholder="e.g., 192.168.1.100"
            />
            <Form.Text className="text-muted">
              Optional: Enter the IP address of your domain controller for more reliable connections.
            </Form.Text>
          </Form.Group>

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
              {(() => {
                // Set connection verified in session storage
                sessionStorage.setItem('connectionVerified', 'true');
                return null;
              })()}
            </Alert>
          )}
      </Card.Body>
    </Card>
  );
};

export default ConnectionTest;
