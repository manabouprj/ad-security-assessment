import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Button, ProgressBar, Table } from 'react-bootstrap';
import { Pie, Bar } from 'react-chartjs-2';
import { Chart, ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import LoadingSpinner from '../components/LoadingSpinner';
import { downloadReport, getAssessmentProgress, getAssessmentHistory } from '../services/api';

// Register Chart.js components
Chart.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = ({ assessmentResults, loading, error }) => {
  const [assessmentProgress, setAssessmentProgress] = useState(null);
  const [assessmentHistory, setAssessmentHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  
  // Fetch assessment progress periodically
  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const progress = await getAssessmentProgress();
        setAssessmentProgress(progress);
      } catch (err) {
        console.error('Error fetching assessment progress:', err);
      }
    };
    
    // Initial fetch
    fetchProgress();
    
    // Set up interval to fetch progress every 3 seconds
    const intervalId = setInterval(fetchProgress, 3000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);
  
  // Fetch assessment history
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setHistoryLoading(true);
        const history = await getAssessmentHistory();
        setAssessmentHistory(history);
      } catch (err) {
        console.error('Error fetching assessment history:', err);
      } finally {
        setHistoryLoading(false);
      }
    };
    
    fetchHistory();
  }, []);
  if (loading) {
    return <LoadingSpinner message="Loading assessment results..." />;
  }

  if (error) {
    return (
      <div className="text-center my-5">
        <h3 className="text-danger">Error</h3>
        <p>{error}</p>
        <Button variant="primary" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </div>
    );
  }

  if (!assessmentResults) {
    return (
      <div className="text-center my-5">
        <h3>No Assessment Results</h3>
        <p>Run an assessment to see results here.</p>
        <Button variant="primary" href="/run-assessment">
          Run Assessment
        </Button>
      </div>
    );
  }

  const { summary } = assessmentResults;
  const { total_checks, passed, failed, warning, not_applicable, compliance_percentage } = summary;

  // Data for compliance pie chart
  const complianceData = {
    labels: ['Compliant', 'Non-Compliant'],
    datasets: [
      {
        data: [compliance_percentage, 100 - compliance_percentage],
        backgroundColor: ['#28a745', '#dc3545'],
        borderWidth: 0,
      },
    ],
  };

  // Data for status breakdown chart
  const statusData = {
    labels: ['Passed', 'Failed', 'Warning', 'Not Applicable'],
    datasets: [
      {
        label: 'Number of Checks',
        data: [passed, failed, warning, not_applicable],
        backgroundColor: ['#28a745', '#dc3545', '#ffc107', '#6c757d'],
        borderWidth: 0,
      },
    ],
  };

  // Data for severity breakdown
  const highSeverity = assessmentResults.recommendations?.filter(r => r.severity === 'high').length || 0;
  const mediumSeverity = assessmentResults.recommendations?.filter(r => r.severity === 'medium').length || 0;
  const lowSeverity = assessmentResults.recommendations?.filter(r => r.severity === 'low').length || 0;

  const severityData = {
    labels: ['High', 'Medium', 'Low'],
    datasets: [
      {
        label: 'Issues by Severity',
        data: [highSeverity, mediumSeverity, lowSeverity],
        backgroundColor: ['#dc3545', '#ffc107', '#28a745'],
        borderWidth: 0,
      },
    ],
  };

  const handleDownloadReport = async (type) => {
    try {
      await downloadReport(type);
    } catch (error) {
      console.error(`Error downloading ${type} report:`, error);
      alert(`Failed to download ${type} report. Please try again later.`);
    }
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Dashboard</h1>
        <div>
          <Button 
            variant="outline-primary" 
            className="me-2" 
            onClick={() => handleDownloadReport('csv')}
          >
            Download CSV
          </Button>
          <Button 
            variant="outline-primary" 
            onClick={() => handleDownloadReport('pdf')}
          >
            Download PDF
          </Button>
        </div>
      </div>
      
      {/* Assessment Progress Card */}
      {assessmentProgress && assessmentProgress.isRunning && (
        <Card className="mb-4 dashboard-card">
          <Card.Header className="dashboard-card-header">Assessment in Progress</Card.Header>
          <Card.Body>
            <h5>{assessmentProgress.currentTask || 'Running assessment...'}</h5>
            <ProgressBar 
              now={assessmentProgress.percentComplete} 
              label={`${assessmentProgress.percentComplete}%`} 
              variant="primary" 
              className="mb-3" 
              animated
            />
            <div className="d-flex justify-content-between">
              <small className="text-muted">Started: {new Date(assessmentProgress.startTime).toLocaleString()}</small>
              <small className="text-muted">Estimated completion: {assessmentProgress.estimatedCompletion ? new Date(assessmentProgress.estimatedCompletion).toLocaleString() : 'Calculating...'}</small>
            </div>
          </Card.Body>
        </Card>
      )}

      <Row>
        <Col md={6} lg={3} className="mb-4">
          <Card className="h-100 dashboard-card">
            <Card.Body className="text-center">
              <h1 className={`display-4 ${compliance_percentage >= 80 ? 'compliance-high' : compliance_percentage >= 60 ? 'compliance-medium' : 'compliance-low'}`}>
                {compliance_percentage}%
              </h1>
              <p className="text-muted">Overall Compliance</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6} lg={3} className="mb-4">
          <Card className="h-100 dashboard-card">
            <Card.Body className="text-center">
              <h1 className="display-4">{total_checks}</h1>
              <p className="text-muted">Total Checks</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6} lg={3} className="mb-4">
          <Card className="h-100 dashboard-card">
            <Card.Body className="text-center">
              <h1 className="display-4 compliance-high">{passed}</h1>
              <p className="text-muted">Passed Checks</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6} lg={3} className="mb-4">
          <Card className="h-100 dashboard-card">
            <Card.Body className="text-center">
              <h1 className="display-4 compliance-low">{failed}</h1>
              <p className="text-muted">Failed Checks</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col md={6} className="mb-4">
          <Card className="dashboard-card h-100">
            <Card.Header className="dashboard-card-header">Compliance Overview</Card.Header>
            <Card.Body>
              <div className="chart-container">
                <Pie 
                  data={complianceData} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom',
                      },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            return context.label + ': ' + context.raw + '%';
                          }
                        }
                      }
                    }
                  }}
                />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6} className="mb-4">
          <Card className="dashboard-card h-100">
            <Card.Header className="dashboard-card-header">Status Breakdown</Card.Header>
            <Card.Body>
              <div className="chart-container">
                <Bar 
                  data={statusData} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true
                      }
                    }
                  }}
                />
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col md={6} className="mb-4">
          <Card className="dashboard-card h-100">
            <Card.Header className="dashboard-card-header">Issues by Severity</Card.Header>
            <Card.Body>
              <div className="chart-container">
                <Pie 
                  data={severityData} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom',
                      }
                    }
                  }}
                />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6} className="mb-4">
          <Card className="dashboard-card h-100">
            <Card.Header className="dashboard-card-header">Top Recommendations</Card.Header>
            <Card.Body>
              {assessmentResults.recommendations && assessmentResults.recommendations.length > 0 ? (
                <ul className="list-group list-group-flush">
                  {assessmentResults.recommendations.slice(0, 5).map((recommendation, index) => (
                    <li key={index} className="list-group-item">
                      <div className={`badge ${recommendation.severity === 'high' ? 'bg-danger' : recommendation.severity === 'medium' ? 'bg-warning text-dark' : 'bg-success'} me-2`}>
                        {recommendation.severity.toUpperCase()}
                      </div>
                      <strong>{recommendation.target}:</strong> {recommendation.recommendation}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-center text-muted">No recommendations available.</p>
              )}
              <div className="text-center mt-3">
                <Button variant="outline-primary" href="/results">
                  View All Results
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* Previous Assessments */}
      <Row className="mt-4">
        <Col md={12}>
          <Card className="dashboard-card">
            <Card.Header className="dashboard-card-header">Previous Assessments</Card.Header>
            <Card.Body>
              {historyLoading ? (
                <div className="text-center py-3">
                  <LoadingSpinner message="Loading assessment history..." />
                </div>
              ) : assessmentHistory.length > 0 ? (
                <Table striped hover responsive>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Domain</th>
                      <th>Compliance Score</th>
                      <th>Passed Checks</th>
                      <th>Failed Checks</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {assessmentHistory.slice(0, 5).map((assessment, index) => (
                      <tr key={index}>
                        <td>{new Date(assessment.timestamp).toLocaleString()}</td>
                        <td>{assessment.domain}</td>
                        <td>
                          <span className={`badge ${
                            assessment.compliance_percentage >= 80 ? 'bg-success' : 
                            assessment.compliance_percentage >= 60 ? 'bg-warning' : 
                            'bg-danger'
                          }`}>
                            {assessment.compliance_percentage}%
                          </span>
                        </td>
                        <td>{assessment.passed_checks}</td>
                        <td>{assessment.failed_checks}</td>
                        <td>
                          <Button size="sm" variant="outline-primary" href={`/results?id=${assessment.id}`}>
                            View Details
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-3">
                  <p className="text-muted">No previous assessments found.</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
