import React from 'react';
import { Row, Col, Card, Button } from 'react-bootstrap';
import { Pie, Bar } from 'react-chartjs-2';
import { Chart, ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import LoadingSpinner from '../components/LoadingSpinner';
import { downloadReport } from '../services/api';

// Register Chart.js components
Chart.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = ({ assessmentResults, loading, error }) => {
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
    </div>
  );
};

export default Dashboard;
