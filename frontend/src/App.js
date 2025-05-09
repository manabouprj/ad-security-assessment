import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import Navigation from './components/Navigation';
import Login from './pages/Login';
import Settings from './pages/Settings';
import axios from 'axios';

// Components
import Sidebar from './components/Sidebar';

// Pages
import Dashboard from './pages/Dashboard';
import AssessmentResults from './pages/AssessmentResults';
import DomainControllers from './pages/DomainControllers';
import Computers from './pages/Computers';
import DomainPolicies from './pages/DomainPolicies';
import RunAssessment from './pages/RunAssessment';

// Services
import { fetchAssessmentResults } from './services/api';

const PrivateRoute = ({ children, requireConnection = false }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isFirstLogin, setIsFirstLogin] = useState(false);
  const [connectionVerified, setConnectionVerified] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get('/api/auth/status');
        setIsAuthenticated(response.data.authenticated);
        
        // Check if this is the first successful login
        const passwordChanged = sessionStorage.getItem('passwordChanged');
        setIsFirstLogin(passwordChanged === 'true');
        
        // Check if connection has been verified
        const connStatus = sessionStorage.getItem('connectionVerified');
        setConnectionVerified(connStatus === 'true');
      } catch (err) {
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  // If user just logged in, redirect to settings page
  if (isFirstLogin) {
    sessionStorage.setItem('passwordChanged', 'false');
    return <Navigate to="/settings" />;
  }

  // If connection verification is required but not done, redirect to settings
  if (requireConnection && !connectionVerified) {
    return <Navigate to="/settings" />;
  }

  return children;
};

const App = () => {
  const [assessmentResults, setAssessmentResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [connectionVerified, setConnectionVerified] = useState(false);

  useEffect(() => {
    // Check if connection has been verified
    const connectionStatus = sessionStorage.getItem('connectionVerified');
    if (connectionStatus === 'true') {
      setConnectionVerified(true);
    }

    const loadAssessmentResults = async () => {
      try {
        setLoading(true);
        const data = await fetchAssessmentResults();
        setAssessmentResults(data);
        setError(null);
      } catch (err) {
        setError('Failed to load assessment results. Please try again later.');
        console.error('Error loading assessment results:', err);
      } finally {
        setLoading(false);
      }
    };

    loadAssessmentResults();
  }, []);

  return (
    <Router>
      <div className="d-flex flex-column min-vh-100">
        <Navigation />
        <div className="d-flex flex-grow-1">
          <Sidebar />
          <main className="flex-grow-1 main-content">
            <Container fluid>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route
                  path="/"
                  element={
                    <PrivateRoute requireConnection={true}>
                      <Dashboard assessmentResults={assessmentResults} loading={loading} error={error} />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/results"
                  element={
                    <PrivateRoute requireConnection={true}>
                      <AssessmentResults assessmentResults={assessmentResults} loading={loading} error={error} />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/domain-controllers"
                  element={
                    <PrivateRoute requireConnection={true}>
                      <DomainControllers assessmentResults={assessmentResults} loading={loading} error={error} />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/computers"
                  element={
                    <PrivateRoute requireConnection={true}>
                      <Computers assessmentResults={assessmentResults} loading={loading} error={error} />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/domain-policies"
                  element={
                    <PrivateRoute requireConnection={true}>
                      <DomainPolicies assessmentResults={assessmentResults} loading={loading} error={error} />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/run-assessment"
                  element={
                    <PrivateRoute requireConnection={true}>
                      <RunAssessment />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <PrivateRoute>
                      <Settings />
                    </PrivateRoute>
                  }
                />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Container>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
