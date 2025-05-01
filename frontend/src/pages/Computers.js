import React, { useState } from 'react';
import { Card, Table, Badge, Form, InputGroup, Button } from 'react-bootstrap';
import LoadingSpinner from '../components/LoadingSpinner';

const Computers = ({ assessmentResults, loading, error }) => {
  const [searchTerm, setSearchTerm] = useState('');

  if (loading) {
    return <LoadingSpinner message="Loading computer data..." />;
  }

  if (error) {
    return (
      <div className="text-center my-5">
        <h3 className="text-danger">Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!assessmentResults || !assessmentResults.computers || assessmentResults.computers.length === 0) {
    return (
      <div className="text-center my-5">
        <h3>No Computer Data</h3>
        <p>Run an assessment to see computer information.</p>
      </div>
    );
  }

  const { computers } = assessmentResults;
  
  // Filter computers based on search term
  const filteredComputers = computers.filter(computer => 
    computer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (computer.dNSHostName && computer.dNSHostName.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (computer.operatingSystem && computer.operatingSystem.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div>
      <h1 className="mb-4">Computers</h1>
      
      <Card className="dashboard-card mb-4">
        <Card.Header className="dashboard-card-header">Overview</Card.Header>
        <Card.Body>
          <p>
            <strong>Total Computers:</strong> {computers.length}
          </p>
          <p>
            <strong>Domain:</strong> {assessmentResults.domain}
          </p>
        </Card.Body>
      </Card>
      
      <Card className="dashboard-card mb-4">
        <Card.Header className="dashboard-card-header">Search</Card.Header>
        <Card.Body>
          <InputGroup>
            <Form.Control
              placeholder="Search computers by name, hostname, or OS..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            {searchTerm && (
              <Button 
                variant="outline-secondary" 
                onClick={() => setSearchTerm('')}
              >
                Clear
              </Button>
            )}
          </InputGroup>
        </Card.Body>
      </Card>
      
      <Card className="dashboard-card">
        <Card.Header className="dashboard-card-header">
          Computers ({filteredComputers.length} of {computers.length})
        </Card.Header>
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
                {filteredComputers.length > 0 ? (
                  filteredComputers.map((computer, index) => {
                    // Calculate compliance percentage
                    const totalChecks = computer.results ? computer.results.length : 0;
                    const passedChecks = computer.results ? computer.results.filter(r => r.status === 'pass').length : 0;
                    const compliancePercentage = totalChecks > 0 ? Math.round((passedChecks / totalChecks) * 100) : 0;
                    
                    // Count issues by severity
                    const highIssues = computer.results ? computer.results.filter(r => r.status === 'fail' && r.severity === 'high').length : 0;
                    const mediumIssues = computer.results ? computer.results.filter(r => r.status === 'fail' && r.severity === 'medium').length : 0;
                    const lowIssues = computer.results ? computer.results.filter(r => r.status === 'fail' && r.severity === 'low').length : 0;
                    
                    return (
                      <tr key={index}>
                        <td>
                          <strong>{computer.name}</strong>
                          {computer.dNSHostName && <div className="text-muted small">{computer.dNSHostName}</div>}
                        </td>
                        <td>
                          {computer.operatingSystem} {computer.operatingSystemVersion}
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
                  })
                ) : (
                  <tr>
                    <td colSpan="4" className="text-center py-4">
                      No computers match your search.
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>
      
      {filteredComputers.map((computer, computerIndex) => {
        // Only show computers with issues
        const hasIssues = computer.results && computer.results.some(r => r.status === 'fail');
        if (!hasIssues) return null;
        
        return (
          <Card className="dashboard-card mt-4" key={computerIndex}>
            <Card.Header className="dashboard-card-header">
              {computer.name} - Issues
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
                    {computer.results
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
                      ))}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        );
      })}
    </div>
  );
};

export default Computers;
