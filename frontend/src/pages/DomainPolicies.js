import React from 'react';
import { Card, Table, Badge } from 'react-bootstrap';
import LoadingSpinner from '../components/LoadingSpinner';

const DomainPolicies = ({ assessmentResults, loading, error }) => {
  if (loading) {
    return <LoadingSpinner message="Loading domain policy data..." />;
  }

  if (error) {
    return (
      <div className="text-center my-5">
        <h3 className="text-danger">Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!assessmentResults || !assessmentResults.domain_policies) {
    return (
      <div className="text-center my-5">
        <h3>No Domain Policy Data</h3>
        <p>Run an assessment to see domain policy information.</p>
      </div>
    );
  }

  const { domain_policies } = assessmentResults;
  
  // Extract password policy results
  const passwordPolicy = domain_policies.password_policy || {};
  const passwordPolicyResults = passwordPolicy.results || [];
  
  // Calculate compliance percentage for password policy
  const totalPasswordChecks = passwordPolicyResults.length;
  const passedPasswordChecks = passwordPolicyResults.filter(r => r.status === 'pass').length;
  const passwordCompliancePercentage = totalPasswordChecks > 0 
    ? Math.round((passedPasswordChecks / totalPasswordChecks) * 100) 
    : 0;
  
  // Count password policy issues by severity
  const highPasswordIssues = passwordPolicyResults.filter(r => r.status === 'fail' && r.severity === 'high').length;
  const mediumPasswordIssues = passwordPolicyResults.filter(r => r.status === 'fail' && r.severity === 'medium').length;
  const lowPasswordIssues = passwordPolicyResults.filter(r => r.status === 'fail' && r.severity === 'low').length;
  
  // Extract account lockout policy results
  const lockoutPolicy = domain_policies.lockout_policy || {};
  const lockoutPolicyResults = lockoutPolicy.results || [];
  
  // Calculate compliance percentage for lockout policy
  const totalLockoutChecks = lockoutPolicyResults.length;
  const passedLockoutChecks = lockoutPolicyResults.filter(r => r.status === 'pass').length;
  const lockoutCompliancePercentage = totalLockoutChecks > 0 
    ? Math.round((passedLockoutChecks / totalLockoutChecks) * 100) 
    : 0;
  
  // Count lockout policy issues by severity
  const highLockoutIssues = lockoutPolicyResults.filter(r => r.status === 'fail' && r.severity === 'high').length;
  const mediumLockoutIssues = lockoutPolicyResults.filter(r => r.status === 'fail' && r.severity === 'medium').length;
  const lowLockoutIssues = lockoutPolicyResults.filter(r => r.status === 'fail' && r.severity === 'low').length;
  
  // Extract audit policy results
  const auditPolicy = domain_policies.audit_policy || {};
  const auditPolicyResults = auditPolicy.results || [];
  
  // Calculate compliance percentage for audit policy
  const totalAuditChecks = auditPolicyResults.length;
  const passedAuditChecks = auditPolicyResults.filter(r => r.status === 'pass').length;
  const auditCompliancePercentage = totalAuditChecks > 0 
    ? Math.round((passedAuditChecks / totalAuditChecks) * 100) 
    : 0;
  
  // Count audit policy issues by severity
  const highAuditIssues = auditPolicyResults.filter(r => r.status === 'fail' && r.severity === 'high').length;
  const mediumAuditIssues = auditPolicyResults.filter(r => r.status === 'fail' && r.severity === 'medium').length;
  const lowAuditIssues = auditPolicyResults.filter(r => r.status === 'fail' && r.severity === 'low').length;

  return (
    <div>
      <h1 className="mb-4">Domain Policies</h1>
      
      <Card className="dashboard-card mb-4">
        <Card.Header className="dashboard-card-header">Overview</Card.Header>
        <Card.Body>
          <p>
            <strong>Domain:</strong> {assessmentResults.domain}
          </p>
          <p>
            <strong>Policies Assessed:</strong> Password Policy, Account Lockout Policy, Audit Policy
          </p>
        </Card.Body>
      </Card>
      
      <Card className="dashboard-card mb-4">
        <Card.Header className="dashboard-card-header">Policy Compliance</Card.Header>
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table hover>
              <thead>
                <tr>
                  <th>Policy Type</th>
                  <th>Compliance</th>
                  <th>Issues</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <strong>Password Policy</strong>
                  </td>
                  <td>
                    <div className={`fw-bold ${passwordCompliancePercentage >= 80 ? 'compliance-high' : passwordCompliancePercentage >= 60 ? 'compliance-medium' : 'compliance-low'}`}>
                      {passwordCompliancePercentage}%
                    </div>
                    <div className="text-muted small">
                      {passedPasswordChecks} of {totalPasswordChecks} checks passed
                    </div>
                  </td>
                  <td>
                    {highPasswordIssues > 0 && (
                      <Badge bg="danger" className="me-1">
                        {highPasswordIssues} High
                      </Badge>
                    )}
                    {mediumPasswordIssues > 0 && (
                      <Badge bg="warning" text="dark" className="me-1">
                        {mediumPasswordIssues} Medium
                      </Badge>
                    )}
                    {lowPasswordIssues > 0 && (
                      <Badge bg="success">
                        {lowPasswordIssues} Low
                      </Badge>
                    )}
                    {highPasswordIssues === 0 && mediumPasswordIssues === 0 && lowPasswordIssues === 0 && (
                      <span className="text-muted">No issues</span>
                    )}
                  </td>
                </tr>
                <tr>
                  <td>
                    <strong>Account Lockout Policy</strong>
                  </td>
                  <td>
                    <div className={`fw-bold ${lockoutCompliancePercentage >= 80 ? 'compliance-high' : lockoutCompliancePercentage >= 60 ? 'compliance-medium' : 'compliance-low'}`}>
                      {lockoutCompliancePercentage}%
                    </div>
                    <div className="text-muted small">
                      {passedLockoutChecks} of {totalLockoutChecks} checks passed
                    </div>
                  </td>
                  <td>
                    {highLockoutIssues > 0 && (
                      <Badge bg="danger" className="me-1">
                        {highLockoutIssues} High
                      </Badge>
                    )}
                    {mediumLockoutIssues > 0 && (
                      <Badge bg="warning" text="dark" className="me-1">
                        {mediumLockoutIssues} Medium
                      </Badge>
                    )}
                    {lowLockoutIssues > 0 && (
                      <Badge bg="success">
                        {lowLockoutIssues} Low
                      </Badge>
                    )}
                    {highLockoutIssues === 0 && mediumLockoutIssues === 0 && lowLockoutIssues === 0 && (
                      <span className="text-muted">No issues</span>
                    )}
                  </td>
                </tr>
                <tr>
                  <td>
                    <strong>Audit Policy</strong>
                  </td>
                  <td>
                    <div className={`fw-bold ${auditCompliancePercentage >= 80 ? 'compliance-high' : auditCompliancePercentage >= 60 ? 'compliance-medium' : 'compliance-low'}`}>
                      {auditCompliancePercentage}%
                    </div>
                    <div className="text-muted small">
                      {passedAuditChecks} of {totalAuditChecks} checks passed
                    </div>
                  </td>
                  <td>
                    {highAuditIssues > 0 && (
                      <Badge bg="danger" className="me-1">
                        {highAuditIssues} High
                      </Badge>
                    )}
                    {mediumAuditIssues > 0 && (
                      <Badge bg="warning" text="dark" className="me-1">
                        {mediumAuditIssues} Medium
                      </Badge>
                    )}
                    {lowAuditIssues > 0 && (
                      <Badge bg="success">
                        {lowAuditIssues} Low
                      </Badge>
                    )}
                    {highAuditIssues === 0 && mediumAuditIssues === 0 && lowAuditIssues === 0 && (
                      <span className="text-muted">No issues</span>
                    )}
                  </td>
                </tr>
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>
      
      {/* Password Policy Issues */}
      {passwordPolicyResults.filter(r => r.status === 'fail').length > 0 && (
        <Card className="dashboard-card mt-4">
          <Card.Header className="dashboard-card-header">
            Password Policy Issues
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
                  {passwordPolicyResults
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
      )}
      
      {/* Account Lockout Policy Issues */}
      {lockoutPolicyResults.filter(r => r.status === 'fail').length > 0 && (
        <Card className="dashboard-card mt-4">
          <Card.Header className="dashboard-card-header">
            Account Lockout Policy Issues
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
                  {lockoutPolicyResults
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
      )}
      
      {/* Audit Policy Issues */}
      {auditPolicyResults.filter(r => r.status === 'fail').length > 0 && (
        <Card className="dashboard-card mt-4">
          <Card.Header className="dashboard-card-header">
            Audit Policy Issues
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
                  {auditPolicyResults
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
      )}
    </div>
  );
};

export default DomainPolicies;
