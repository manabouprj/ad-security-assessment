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

const PrivateRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get('/api/auth/status');
        setIsAuthenticated(response.data.authenticated);
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

  return isAuthenticated ? children : <Navigate to="/login" />;
};

const App = () => {
  const [assessmentResults, setAssessmentResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
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
                    <PrivateRoute>
                      <Dashboard assessmentResults={assessmentResults} loading={loading} error={error} />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/results"
                  element={
                    <PrivateRoute>
                      <AssessmentResults assessmentResults={assessmentResults} loading={loading} error={error} />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/domain-controllers"
                  element={
                    <PrivateRoute>
                      <DomainControllers assessmentResults={assessmentResults} loading={loading} error={error} />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/computers"
                  element={
                    <PrivateRoute>
                      <Computers assessmentResults={assessmentResults} loading={loading} error={error} />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/domain-policies"
                  element={
                    <PrivateRoute>
                      <DomainPolicies assessmentResults={assessmentResults} loading={loading} error={error} />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/run-assessment"
                  element={
                    <PrivateRoute>
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
