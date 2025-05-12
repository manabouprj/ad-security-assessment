import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Button, ProgressBar, Table, Modal, ListGroup, Alert } from 'react-bootstrap';
import { Pie, Bar, Line } from 'react-chartjs-2';
import { Chart, ArcElement, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import LoadingSpinner from '../components/LoadingSpinner';
import { downloadReport, getAssessmentProgress, getAssessmentHistory } from '../services/api';
import { useNavigate } from 'react-router-dom';

// Register Chart.js components
Chart.register(ArcElement, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend);

const Dashboard = ({ assessmentResults, loading, error }) => {
  const navigate = useNavigate();
  const [assessmentProgress, setAssessmentProgress] = useState(null);
  const [assessmentHistory, setAssessmentHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [showWelcomeModal, setShowWelcomeModal] = useState(false);
  
  // Check if this is the first login
  useEffect(() => {
    const isFirstLogin = sessionStorage.getItem('isFirstLogin') !== 'false';
    if (isFirstLogin) {
      setShowWelcomeModal(true);
      sessionStorage.setItem('isFirstLogin', 'false');
    }
  }, []);

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
      <div>
        <h1 className="mb-4">Dashboard</h1>
        
        {/* Application Summary Card */}
        <Card className="mb-4 dashboard-card">
          <Card.Header className="dashboard-card-header">Active Directory Security Assessment</Card.Header>
          <Card.Body>
            <Row>
              <Col md={8}>
                <h4>Welcome to the AD Security Assessment Tool</h4>
                <p>
                  This application helps you evaluate the security posture of your Active Directory environment
                  against industry-standard compliance benchmarks. Identify security gaps, get remediation steps,
                  and track your compliance improvements over time.
                </p>
                <div className="d-flex mt-4">
                  <Button 
                    variant="primary" 
                    size="lg" 
                    className="me-3"
                    onClick={() => navigate('/run-assessment')}
                  >
                    Start New Assessment
                  </Button>
                  <Button 
                    variant="outline-secondary"
                    onClick={() => setShowWelcomeModal(true)}
                  >
                    Learn More
                  </Button>
                </div>
              </Col>
              <Col md={4} className="d-flex align-items-center justify-content-center">
                <div className="text-center">
                  <i className="bi bi-shield-check" style={{ fontSize: '5rem', color: '#0d6efd' }}></i>
                  <h5 className="mt-3">Secure Your AD Environment</h5>
                </div>
              </Col>
            </Row>
          </Card.Body>
        </Card>
        
        {/* Assessment Status Card */}
        {assessmentProgress && assessmentProgress.isRunning ? (
          <Card className="mb-4 dashboard-card border-primary">
            <Card.Header className="dashboard-card-header bg-primary text-white">
              <i className="bi bi-arrow-repeat me-2"></i> Assessment in Progress
            </Card.Header>
            <Card.Body>
              <h5>{assessmentProgress.currentTask || 'Running assessment...'}</h5>
              <ProgressBar 
                now={assessmentProgress.percentComplete} 
                label={`${assessmentProgress.percentComplete}%`} 
                variant="primary" 
                className="mb-3" 
                animated
                style={{ height: '25px' }}
              />
              <div className="d-flex justify-content-between">
                <small className="text-muted">Started: {new Date(assessmentProgress.startTime).toLocaleString()}</small>
                <small className="text-muted">Estimated completion: {assessmentProgress.estimatedCompletion ? new Date(assessmentProgress.estimatedCompletion).toLocaleString() : 'Calculating...'}</small>
              </div>
            </Card.Body>
          </Card>
        ) : (
          <Alert variant="info" className="mb-4">
            <div className="d-flex align-items-center">
              <i className="bi bi-info-circle-fill me-3" style={{ fontSize: '1.5rem' }}></i>
              <div>
                <h5 className="mb-1">No Assessment Results Available</h5>
                <p className="mb-0">Run your first assessment to see security insights and compliance status.</p>
              </div>
            </div>
          </Alert>
        )}
        
        {/* Previous Assessments Card */}
        <Card className="mb-4 dashboard-card">
          <Card.Header className="dashboard-card-header">Previous Assessments</Card.Header>
          <Card.Body>
            {historyLoading ? (
              <div className="text-center py-3">
                <LoadingSpinner message="Loading assessment history..." />
              </div>
            ) : assessmentHistory.length > 0 ? (
              <>
                <div className="chart-container mb-4" style={{ height: '250px' }}>
                  <Line
                    data={{
                      labels: assessmentHistory.slice(0, 5).map(a => new Date(a.timestamp).toLocaleDateString()).reverse(),
                      datasets: [
                        {
                          label: 'Compliance Score (%)',
                          data: assessmentHistory.slice(0, 5).map(a => a.compliance_percentage).reverse(),
                          borderColor: '#0d6efd',
                          backgroundColor: 'rgba(13, 110, 253, 0.1)',
                          fill: true,
                          tension: 0.3
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: {
                          beginAtZero: true,
                          max: 100,
                          title: {
                            display: true,
                            text: 'Compliance Score (%)'
                          }
                        },
                        x: {
                          title: {
                            display: true,
                            text: 'Assessment Date'
                          }
                        }
                      },
                      plugins: {
                        title: {
                          display: true,
                          text: 'Compliance Trend'
                        }
                      }
                    }}
                  />
                </div>
                <Table striped hover responsive>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Domain</th>
                      <th>Compliance Score</th>
                      <th>Passed/Failed</th>
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
                        <td>{assessment.passed_checks} / {assessment.failed_checks}</td>
                        <td>
                          <Button size="sm" variant="outline-primary" href={`/results?id=${assessment.id}`}>
                            View Details
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </>
            ) : (
              <div className="text-center py-4">
                <i className="bi bi-clipboard-data" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
                <p className="text-muted mt-3">No previous assessments found.</p>
                <p className="text-muted">Run your first assessment to start tracking your security compliance.</p>
              </div>
            )}
          </Card.Body>
        </Card>
        
        {/* Welcome Modal with Use Cases */}
        <Modal 
          show={showWelcomeModal} 
          onHide={() => setShowWelcomeModal(false)}
          size="lg"
          centered
        >
          <Modal.Header closeButton>
            <Modal.Title>Welcome to AD Security Assessment</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <h5 className="mb-3">What You Can Do With This Application:</h5>
            
            <ListGroup variant="flush" className="mb-4">
              <ListGroup.Item>
                <div className="d-flex">
                  <div className="me-3">
                    <span className="badge bg-primary rounded-circle p-2">1</span>
                  </div>
                  <div>
                    <strong>Run Security Assessments</strong>
                    <p className="mb-0 text-muted">Evaluate your Active Directory environment against industry-standard security baselines</p>
                  </div>
                </div>
              </ListGroup.Item>
              
              <ListGroup.Item>
                <div className="d-flex">
                  <div className="me-3">
                    <span className="badge bg-primary rounded-circle p-2">2</span>
                  </div>
                  <div>
                    <strong>Choose Compliance Baselines</strong>
                    <p className="mb-0 text-muted">Select from CIS, STIG, Microsoft Security benchmarks or upload your own custom baselines</p>
                  </div>
                </div>
              </ListGroup.Item>
              
              <ListGroup.Item>
                <div className="d-flex">
                  <div className="me-3">
                    <span className="badge bg-primary rounded-circle p-2">3</span>
                  </div>
                  <div>
                    <strong>Get Detailed Reports</strong>
                    <p className="mb-0 text-muted">View technical or executive reports with remediation steps for failed compliance checks</p>
                  </div>
                </div>
              </ListGroup.Item>
              
              <ListGroup.Item>
                <div className="d-flex">
                  <div className="me-3">
                    <span className="badge bg-primary rounded-circle p-2">4</span>
                  </div>
                  <div>
                    <strong>Monitor Compliance Over Time</strong>
                    <p className="mb-0 text-muted">Track your security posture improvements with historical assessment data</p>
                  </div>
                </div>
              </ListGroup.Item>
            </ListGroup>
            
            <div className="text-center mt-4">
              <Button 
                variant="primary" 
                size="lg" 
                onClick={() => {
                  setShowWelcomeModal(false);
                  navigate('/run-assessment');
                }}
              >
                Start Your First Assessment
              </Button>
            </div>
          </Modal.Body>
        </Modal>
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
      
      {/* Assessment Status Card */}
      {assessmentProgress && assessmentProgress.isRunning && (
        <Card className="mb-4 dashboard-card border-primary">
          <Card.Header className="dashboard-card-header bg-primary text-white">
            <i className="bi bi-arrow-repeat me-2"></i> Assessment in Progress
          </Card.Header>
          <Card.Body>
            <h5>{assessmentProgress.currentTask || 'Running assessment...'}</h5>
            <ProgressBar 
              now={assessmentProgress.percentComplete} 
              label={`${assessmentProgress.percentComplete}%`} 
              variant="primary" 
              className="mb-3" 
              animated
              style={{ height: '25px' }}
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
      
      {/* Previous Assessments with Trend */}
      <Row className="mt-4">
        <Col md={12}>
          <Card className="dashboard-card">
            <Card.Header className="dashboard-card-header">Compliance Trend</Card.Header>
            <Card.Body>
              {historyLoading ? (
                <div className="text-center py-3">
                  <LoadingSpinner message="Loading assessment history..." />
                </div>
              ) : assessmentHistory.length > 0 ? (
                <div className="chart-container" style={{ height: '300px' }}>
                  <Line
                    data={{
                      labels: assessmentHistory.slice(0, 5).map(a => new Date(a.timestamp).toLocaleDateString()).reverse(),
                      datasets: [
                        {
                          label: 'Compliance Score (%)',
                          data: assessmentHistory.slice(0, 5).map(a => a.compliance_percentage).reverse(),
                          borderColor: '#0d6efd',
                          backgroundColor: 'rgba(13, 110, 253, 0.1)',
                          fill: true,
                          tension: 0.3
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: {
                          beginAtZero: true,
                          max: 100,
                          title: {
                            display: true,
                            text: 'Compliance Score (%)'
                          }
                        },
                        x: {
                          title: {
                            display: true,
                            text: 'Assessment Date'
                          }
                        }
                      }
                    }}
                  />
                </div>
              ) : (
                <div className="text-center py-4">
                  <i className="bi bi-graph-up" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
                  <p className="text-muted mt-3">No trend data available yet.</p>
                  <p className="text-muted">Run multiple assessments to see your compliance trend over time.</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* Quick Actions Card */}
      <Row className="mt-4">
        <Col md={12}>
          <Card className="dashboard-card">
            <Card.Header className="dashboard-card-header">Quick Actions</Card.Header>
            <Card.Body>
              <Row>
                <Col md={4} className="text-center mb-3">
                  <div className="p-4 rounded bg-light">
                    <i className="bi bi-play-circle" style={{ fontSize: '2.5rem', color: '#0d6efd' }}></i>
                    <h5 className="mt-3">Run Assessment</h5>
                    <p className="text-muted">Start a new security assessment</p>
                    <Button 
                      variant="primary" 
                      onClick={() => navigate('/run-assessment')}
                    >
                      Start Now
                    </Button>
                  </div>
                </Col>
                <Col md={4} className="text-center mb-3">
                  <div className="p-4 rounded bg-light">
                    <i className="bi bi-gear" style={{ fontSize: '2.5rem', color: '#6c757d' }}></i>
                    <h5 className="mt-3">Settings</h5>
                    <p className="text-muted">Configure assessment parameters</p>
                    <Button 
                      variant="outline-secondary" 
                      onClick={() => navigate('/settings')}
                    >
                      Configure
                    </Button>
                  </div>
                </Col>
                <Col md={4} className="text-center mb-3">
                  <div className="p-4 rounded bg-light">
                    <i className="bi bi-file-earmark-text" style={{ fontSize: '2.5rem', color: '#198754' }}></i>
                    <h5 className="mt-3">View Reports</h5>
                    <p className="text-muted">Access previous assessment reports</p>
                    <Button 
                      variant="outline-success" 
                      onClick={() => navigate('/results')}
                    >
                      View Reports
                    </Button>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
