import React from 'react';
import { Card, Table, Badge } from 'react-bootstrap';
import LoadingSpinner from '../components/LoadingSpinner';

const DomainControllers = ({ assessmentResults, loading, error }) => {
  if (loading) {
    return <LoadingSpinner message="Loading domain controller data..." />;
  }

  if (error) {
    return (
      <div className="text-center my-5">
        <h3 className="text-danger">Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!assessmentResults || !assessmentResults.domain_controllers || assessmentResults.domain_controllers.length === 0) {
    return (
      <div className="text-center my-5">
        <h3>No Domain Controller Data</h3>
        <p>Run an assessment to see domain controller information.</p>
      </div>
    );
  }

  const { domain_controllers } = assessmentResults;

  return (
    <div>
      <h1 className="mb-4">Domain Controllers</h1>
      
      <Card className="dashboard-card mb-4">
        <Card.Header className="dashboard-card-header">Overview</Card.Header>
        <Card.Body>
          <p>
            <strong>Total Domain Controllers:</strong> {domain_controllers.length}
          </p>
          <p>
            <strong>Domain:</strong> {assessmentResults.domain}
          </p>
        </Card.Body>
      </Card>
      
      <Card className="dashboard-card">
        <Card.Header className="dashboard-card-header">Domain Controllers</Card.Header>
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table hover>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Operating System</th>
                  <th>Compliance</th>
                  <th>Issues</th>
                </tr>
              </thead>
              <tbody>
                {domain_controllers.map((dc, index) => {
                  // Calculate compliance percentage
                  const totalChecks = dc.results ? dc.results.length : 0;
                  const passedChecks = dc.results ? dc.results.filter(r => r.status === 'pass').length : 0;
                  const compliancePercentage = totalChecks > 0 ? Math.round((passedChecks / totalChecks) * 100) : 0;
                  
                  // Count issues by severity
                  const highIssues = dc.results ? dc.results.filter(r => r.status === 'fail' && r.severity === 'high').length : 0;
                  const mediumIssues = dc.results ? dc.results.filter(r => r.status === 'fail' && r.severity === 'medium').length : 0;
                  const lowIssues = dc.results ? dc.results.filter(r => r.status === 'fail' && r.severity === 'low').length : 0;
                  
                  return (
                    <tr key={index}>
                      <td>
                        <strong>{dc.name}</strong>
                        {dc.dNSHostName && <div className="text-muted small">{dc.dNSHostName}</div>}
                      </td>
                      <td>
                        {dc.os} {dc.os_version}
                      </td>
                      <td>
                        <div className={`fw-bold ${compliancePercentage >= 80 ? 'compliance-high' : compliancePercentage >= 60 ? 'compliance-medium' : 'compliance-low'}`}>
                          {compliancePercentage}%
                        </div>
                        <div className="text-muted small">
                          {passedChecks} of {totalChecks} checks passed
                        </div>
                      </td>
                      <td>
                        {highIssues > 0 && (
                          <Badge bg="danger" className="me-1">
                            {highIssues} High
                          </Badge>
                        )}
                        {mediumIssues > 0 && (
                          <Badge bg="warning" text="dark" className="me-1">
                            {mediumIssues} Medium
                          </Badge>
                        )}
                        {lowIssues > 0 && (
                          <Badge bg="success">
                            {lowIssues} Low
                          </Badge>
                        )}
                        {highIssues === 0 && mediumIssues === 0 && lowIssues === 0 && (
                          <span className="text-muted">No issues</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>
      
      {domain_controllers.map((dc, dcIndex) => (
        <Card className="dashboard-card mt-4" key={dcIndex}>
          <Card.Header className="dashboard-card-header">
            {dc.name} - Issues
          </Card.Header>
          <Card.Body className="p-0">
            <div className="table-responsive">
              <Table hover>
                <thead>
                  <tr>
                    <th>Setting</th>
                    <th>Baseline Value</th>
                    <th>Actual Value</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {dc.results && dc.results.filter(r => r.status === 'fail').length > 0 ? (
                    dc.results
                      .filter(r => r.status === 'fail')
                      .map((result, resultIndex) => (
                        <tr 
                          key={resultIndex} 
                          className={`severity-${result.severity}`}
                        >
                          <td>
                            {result.setting_name}
                            {result.setting_path && (
                              <div className="text-muted small">{result.setting_path}</div>
                            )}
                          </td>
                          <td>{result.baseline_value}</td>
                          <td>{result.actual_value}</td>
                          <td>
                            <Badge 
                              bg={
                                result.severity === 'high' ? 'danger' : 
                                result.severity === 'medium' ? 'warning' : 
                                'success'
                              }
                              text={result.severity === 'medium' ? 'dark' : 'white'}
                            >
                              {result.severity.toUpperCase()}
                            </Badge>
                          </td>
                        </tr>
                      ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="text-center py-4">
                        No issues found for this domain controller.
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </div>
          </Card.Body>
        </Card>
      ))}
    </div>
  );
};

export default DomainControllers;
