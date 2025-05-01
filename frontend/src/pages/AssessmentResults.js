import React, { useState } from 'react';
import { Table, Card, Form, InputGroup, Button, Badge } from 'react-bootstrap';
import LoadingSpinner from '../components/LoadingSpinner';

const AssessmentResults = ({ assessmentResults, loading, error }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [filterTarget, setFilterTarget] = useState('all');

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

  // Collect all results from different sources
  const allResults = [];

  // Add domain controller results
  assessmentResults.domain_controllers?.forEach(dc => {
    dc.results?.forEach(result => {
      allResults.push({
        ...result,
        target: `DC: ${dc.name}`,
        targetType: 'domain-controller'
      });
    });
  });

  // Add computer results
  assessmentResults.computers?.forEach(computer => {
    computer.results?.forEach(result => {
      allResults.push({
        ...result,
        target: `Computer: ${computer.name}`,
        targetType: 'computer'
      });
    });
  });

  // Add domain policy results
  if (assessmentResults.domain_policies?.password_policy) {
    assessmentResults.domain_policies.password_policy.results?.forEach(result => {
      allResults.push({
        ...result,
        target: 'Domain Password Policy',
        targetType: 'policy'
      });
    });
  }

  // Filter results
  const filteredResults = allResults.filter(result => {
    // Search term filter
    const searchMatch = 
      searchTerm === '' || 
      result.target.toLowerCase().includes(searchTerm.toLowerCase()) ||
      result.setting_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      result.setting_path?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      result.baseline_value?.toString().toLowerCase().includes(searchTerm.toLowerCase()) ||
      result.actual_value?.toString().toLowerCase().includes(searchTerm.toLowerCase());
    
    // Status filter
    const statusMatch = filterStatus === 'all' || result.status === filterStatus;
    
    // Severity filter
    const severityMatch = filterSeverity === 'all' || result.severity === filterSeverity;
    
    // Target filter
    const targetMatch = 
      filterTarget === 'all' || 
      (filterTarget === 'domain-controller' && result.targetType === 'domain-controller') ||
      (filterTarget === 'computer' && result.targetType === 'computer') ||
      (filterTarget === 'policy' && result.targetType === 'policy');
    
    return searchMatch && statusMatch && severityMatch && targetMatch;
  });

  return (
    <div>
      <h1 className="mb-4">Assessment Results</h1>
      
      <Card className="mb-4 dashboard-card">
        <Card.Header className="dashboard-card-header">Filters</Card.Header>
        <Card.Body>
          <div className="row">
            <div className="col-md-6 mb-3">
              <InputGroup>
                <Form.Control
                  placeholder="Search..."
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
            </div>
            <div className="col-md-6 mb-3">
              <div className="row">
                <div className="col-md-4">
                  <Form.Select 
                    value={filterStatus} 
                    onChange={(e) => setFilterStatus(e.target.value)}
                  >
                    <option value="all">All Statuses</option>
                    <option value="pass">Pass</option>
                    <option value="fail">Fail</option>
                    <option value="warning">Warning</option>
                    <option value="not_applicable">Not Applicable</option>
                  </Form.Select>
                </div>
                <div className="col-md-4">
                  <Form.Select 
                    value={filterSeverity} 
                    onChange={(e) => setFilterSeverity(e.target.value)}
                  >
                    <option value="all">All Severities</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </Form.Select>
                </div>
                <div className="col-md-4">
                  <Form.Select 
                    value={filterTarget} 
                    onChange={(e) => setFilterTarget(e.target.value)}
                  >
                    <option value="all">All Targets</option>
                    <option value="domain-controller">Domain Controllers</option>
                    <option value="computer">Computers</option>
                    <option value="policy">Domain Policies</option>
                  </Form.Select>
                </div>
              </div>
            </div>
          </div>
        </Card.Body>
      </Card>
      
      <Card className="dashboard-card">
        <Card.Header className="dashboard-card-header">
          Results ({filteredResults.length} of {allResults.length})
        </Card.Header>
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table hover>
              <thead>
                <tr>
                  <th>Target</th>
                  <th>Setting</th>
                  <th>Baseline Value</th>
                  <th>Actual Value</th>
                  <th>Status</th>
                  <th>Severity</th>
                </tr>
              </thead>
              <tbody>
                {filteredResults.length > 0 ? (
                  filteredResults.map((result, index) => (
                    <tr 
                      key={index} 
                      className={result.status === 'fail' ? `severity-${result.severity}` : ''}
                    >
                      <td>{result.target}</td>
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
                            result.status === 'pass' ? 'success' : 
                            result.status === 'fail' ? 'danger' : 
                            result.status === 'warning' ? 'warning' : 
                            'secondary'
                          }
                          text={result.status === 'warning' ? 'dark' : 'white'}
                        >
                          {result.status.toUpperCase()}
                        </Badge>
                      </td>
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
                    <td colSpan="6" className="text-center py-4">
                      No results match your filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default AssessmentResults;
