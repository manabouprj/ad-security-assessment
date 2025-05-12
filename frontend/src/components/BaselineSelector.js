import React, { useState, useEffect } from 'react';
import { Card, Form, Button, ListGroup, Badge, Alert, Spinner, Modal, Nav, Tab } from 'react-bootstrap';
import { getAvailableBaselines, uploadCustomBaseline } from '../services/api';

const BaselineSelector = ({ onBaselineSelect, selectedBaseline }) => {
  const [baselines, setBaselines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadName, setUploadName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  useEffect(() => {
    loadBaselines();
  }, []);

  const loadBaselines = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getAvailableBaselines();
      setBaselines(response.baselines || []);
    } catch (err) {
      console.error('Error loading baselines:', err);
      setError('Failed to load compliance baselines. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBaselineSelect = (baseline) => {
    if (onBaselineSelect) {
      onBaselineSelect(baseline);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadFile(file);
      setUploadName(file.name);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) {
      setUploadError('Please select a file to upload');
      return;
    }

    try {
      setUploading(true);
      setUploadError(null);
      await uploadCustomBaseline(uploadFile, uploadName);
      setShowUploadModal(false);
      setUploadFile(null);
      setUploadName('');
      // Reload baselines to include the newly uploaded one
      await loadBaselines();
    } catch (err) {
      console.error('Error uploading baseline:', err);
      setUploadError('Failed to upload baseline. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const renderBaselineItem = (baseline) => {
    const isSelected = selectedBaseline && selectedBaseline.id === baseline.id;
    
    return (
      <ListGroup.Item 
        key={baseline.id}
        action
        active={isSelected}
        onClick={() => handleBaselineSelect(baseline)}
        className="d-flex justify-content-between align-items-center"
      >
        <div>
          <div className="fw-bold">{baseline.name}</div>
          <div className="text-muted small">{baseline.description}</div>
        </div>
        <Badge bg={baseline.type === 'built-in' ? 'primary' : 'success'}>
          {baseline.type === 'built-in' ? 'Built-in' : 'Custom'}
        </Badge>
      </ListGroup.Item>
    );
  };

  const renderBaselineGroups = () => {
    // Filter baselines by category
    const cisBaselines = baselines.filter(b => b.name && b.name.includes('CIS'));
    const stigBaselines = baselines.filter(b => b.name && b.name.includes('STIG'));
    const microsoftBaselines = baselines.filter(b => b.name && b.name.includes('Microsoft'));
    
    // Any remaining built-in baselines
    const otherBuiltInBaselines = baselines.filter(b => 
      b.type === 'built-in' && 
      !b.name.includes('CIS') && 
      !b.name.includes('STIG') && 
      !b.name.includes('Microsoft')
    );
    
    // Custom baselines
    const customBaselines = baselines.filter(b => b.type === 'custom');

    return (
      <Tab.Container defaultActiveKey="cis">
        <Nav variant="tabs" className="mb-3">
          <Nav.Item>
            <Nav.Link eventKey="cis">CIS Benchmarks</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey="stig">STIG Benchmarks</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey="microsoft">Microsoft Security</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey="other">Other Built-in</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey="custom">Custom</Nav.Link>
          </Nav.Item>
        </Nav>
        
        <Tab.Content>
          <Tab.Pane eventKey="cis">
            <ListGroup className="mb-3">
              {cisBaselines.length > 0 ? (
                cisBaselines.map(renderBaselineItem)
              ) : (
                <ListGroup.Item>No CIS benchmarks available</ListGroup.Item>
              )}
            </ListGroup>
            <p className="text-muted small">
              CIS benchmarks provide consensus-based best practices for securely configuring systems.
            </p>
          </Tab.Pane>
          
          <Tab.Pane eventKey="stig">
            <ListGroup className="mb-3">
              {stigBaselines.length > 0 ? (
                stigBaselines.map(renderBaselineItem)
              ) : (
                <ListGroup.Item>No STIG benchmarks available</ListGroup.Item>
              )}
            </ListGroup>
            <p className="text-muted small">
              STIG (Security Technical Implementation Guides) are the configuration standards for DOD IA and IA-enabled devices/systems.
            </p>
          </Tab.Pane>
          
          <Tab.Pane eventKey="microsoft">
            <ListGroup className="mb-3">
              {microsoftBaselines.length > 0 ? (
                microsoftBaselines.map(renderBaselineItem)
              ) : (
                <ListGroup.Item>No Microsoft Security baselines available</ListGroup.Item>
              )}
            </ListGroup>
            <p className="text-muted small">
              Microsoft Security baselines are Microsoft-recommended security configuration baselines for Windows and other Microsoft products.
            </p>
          </Tab.Pane>
          
          <Tab.Pane eventKey="other">
            <ListGroup className="mb-3">
              {otherBuiltInBaselines.length > 0 ? (
                otherBuiltInBaselines.map(renderBaselineItem)
              ) : (
                <ListGroup.Item>No other built-in baselines available</ListGroup.Item>
              )}
            </ListGroup>
          </Tab.Pane>
          
          <Tab.Pane eventKey="custom">
            <ListGroup className="mb-3">
              {customBaselines.length > 0 ? (
                customBaselines.map(renderBaselineItem)
              ) : (
                <ListGroup.Item>No custom baselines uploaded</ListGroup.Item>
              )}
            </ListGroup>
            <p className="text-muted small">
              Custom baselines are user-uploaded compliance standards that can be in JSON, CSV, or PDF format.
            </p>
          </Tab.Pane>
        </Tab.Content>
      </Tab.Container>
    );
  };

  return (
    <>
      <Card className="mb-4 dashboard-card">
        <Card.Header className="dashboard-card-header d-flex justify-content-between align-items-center">
          <span>Compliance Baselines</span>
          <Button 
            variant="outline-primary" 
            size="sm"
            onClick={() => setShowUploadModal(true)}
          >
            Upload Custom Baseline
          </Button>
        </Card.Header>
        <Card.Body>
          {error && (
            <Alert variant="danger" onClose={() => setError(null)} dismissible>
              {error}
            </Alert>
          )}
          
          {loading ? (
            <div className="text-center my-4">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
              <p className="mt-2">Loading compliance baselines...</p>
            </div>
          ) : (
            renderBaselineGroups()
          )}
          
          <div className="mt-3">
            <p className="text-muted small">
              <strong>Note:</strong> Select a compliance baseline to use for your assessment. 
              The baseline defines the security standards against which your Active Directory 
              environment will be evaluated.
            </p>
          </div>
        </Card.Body>
      </Card>

      {/* Upload Modal */}
      <Modal show={showUploadModal} onHide={() => setShowUploadModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Upload Custom Baseline</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {uploadError && (
            <Alert variant="danger" onClose={() => setUploadError(null)} dismissible>
              {uploadError}
            </Alert>
          )}
          
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Select Baseline File</Form.Label>
              <Form.Control 
                type="file" 
                onChange={handleFileChange}
                accept=".json,.csv,.pdf"
                disabled={uploading}
              />
              <div className="mt-2">
                <Badge bg="info" className="me-2">JSON</Badge>
                <Badge bg="info" className="me-2">CSV</Badge>
                <Badge bg="info">PDF</Badge>
              </div>
              <Form.Text className="text-muted">
                Supported formats: JSON, CSV, PDF
              </Form.Text>
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Baseline Name (Optional)</Form.Label>
              <Form.Control 
                type="text" 
                placeholder="Enter a name for this baseline"
                value={uploadName}
                onChange={(e) => setUploadName(e.target.value)}
                disabled={uploading}
              />
              <Form.Text className="text-muted">
                If left blank, the file name will be used
              </Form.Text>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowUploadModal(false)} disabled={uploading}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleUpload} disabled={uploading}>
            {uploading ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-2"
                />
                Uploading...
              </>
            ) : (
              'Upload'
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default BaselineSelector;
