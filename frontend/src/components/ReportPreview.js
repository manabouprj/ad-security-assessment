import React, { useState, useEffect } from 'react';
import { Card, Button, Tabs, Tab, Form, Alert, Spinner } from 'react-bootstrap';
import { getReportPreview, downloadReport } from '../services/api';

const ReportPreview = ({ assessmentResults }) => {
  const [reportType, setReportType] = useState('technical');
  const [reportFormat, setReportFormat] = useState('pdf');
  const [previewContent, setPreviewContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [downloadStarted, setDownloadStarted] = useState(false);

  useEffect(() => {
    if (assessmentResults) {
      loadPreview();
    }
  }, [reportType, assessmentResults]);

  const loadPreview = async () => {
    try {
      setLoading(true);
      setError(null);
      const preview = await getReportPreview(reportType, 'html');
      setPreviewContent(preview.html);
    } catch (err) {
      console.error('Error loading report preview:', err);
      setError('Failed to load report preview. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      setDownloadStarted(true);
      await downloadReport(reportType, reportFormat);
      setTimeout(() => setDownloadStarted(false), 3000);
    } catch (err) {
      console.error('Error downloading report:', err);
      setError('Failed to download report. Please try again.');
      setDownloadStarted(false);
    }
  };

  if (!assessmentResults) {
    return null;
  }

  return (
    <Card className="mb-4 dashboard-card">
      <Card.Header className="dashboard-card-header d-flex justify-content-between align-items-center">
        <span>Report Preview</span>
        <div>
          <Form.Select 
            className="d-inline-block me-2" 
            style={{ width: 'auto' }}
            value={reportFormat}
            onChange={(e) => setReportFormat(e.target.value)}
          >
            <option value="pdf">PDF</option>
            <option value="csv">CSV</option>
          </Form.Select>
          <Button 
            variant="primary" 
            onClick={handleDownload}
            disabled={downloadStarted}
          >
            {downloadStarted ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-2"
                />
                Downloading...
              </>
            ) : (
              'Download Report'
            )}
          </Button>
        </div>
      </Card.Header>
      <Card.Body>
        {error && (
          <Alert variant="danger" onClose={() => setError(null)} dismissible>
            {error}
          </Alert>
        )}
        
        <Tabs
          activeKey={reportType}
          onSelect={(k) => setReportType(k)}
          className="mb-3"
        >
          <Tab eventKey="technical" title="Technical Report">
            {loading ? (
              <div className="text-center my-5">
                <Spinner animation="border" role="status">
                  <span className="visually-hidden">Loading...</span>
                </Spinner>
                <p className="mt-2">Loading technical report preview...</p>
              </div>
            ) : (
              <div className="report-preview-container">
                {previewContent ? (
                  <div 
                    className="report-preview" 
                    dangerouslySetInnerHTML={{ __html: previewContent }}
                    style={{ 
                      border: '1px solid #ddd', 
                      padding: '20px',
                      maxHeight: '500px',
                      overflowY: 'auto',
                      backgroundColor: '#fff'
                    }}
                  />
                ) : (
                  <p className="text-center">No preview available</p>
                )}
              </div>
            )}
          </Tab>
          <Tab eventKey="executive" title="Executive Summary">
            {loading ? (
              <div className="text-center my-5">
                <Spinner animation="border" role="status">
                  <span className="visually-hidden">Loading...</span>
                </Spinner>
                <p className="mt-2">Loading executive summary preview...</p>
              </div>
            ) : (
              <div className="report-preview-container">
                {previewContent ? (
                  <div 
                    className="report-preview" 
                    dangerouslySetInnerHTML={{ __html: previewContent }}
                    style={{ 
                      border: '1px solid #ddd', 
                      padding: '20px',
                      maxHeight: '500px',
                      overflowY: 'auto',
                      backgroundColor: '#fff'
                    }}
                  />
                ) : (
                  <p className="text-center">No preview available</p>
                )}
              </div>
            )}
          </Tab>
        </Tabs>
      </Card.Body>
    </Card>
  );
};

export default ReportPreview;
