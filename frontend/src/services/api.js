import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Fetch assessment results
export const fetchAssessmentResults = async () => {
  try {
    const response = await api.get('/assessment/results');
    return response.data;
  } catch (error) {
    console.error('Error fetching assessment results:', error);
    throw error;
  }
};

// Run a new assessment
export const runAssessment = async (config) => {
  try {
    const response = await api.post('/assessment/run', config);
    return response.data;
  } catch (error) {
    console.error('Error running assessment:', error);
    throw error;
  }
};

// Run a new interactive assessment using main.py
export const runInteractiveAssessment = async (config) => {
  try {
    const response = await api.post('/assessment/run-interactive', config);
    return response.data;
  } catch (error) {
    console.error('Error running interactive assessment:', error);
    throw error;
  }
};

// Fetch domain controllers
export const fetchDomainControllers = async () => {
  try {
    const response = await api.get('/domain-controllers');
    return response.data;
  } catch (error) {
    console.error('Error fetching domain controllers:', error);
    throw error;
  }
};

// Fetch computers
export const fetchComputers = async () => {
  try {
    const response = await api.get('/computers');
    return response.data;
  } catch (error) {
    console.error('Error fetching computers:', error);
    throw error;
  }
};

// Fetch domain policies
export const fetchDomainPolicies = async () => {
  try {
    const response = await api.get('/domain-policies');
    return response.data;
  } catch (error) {
    console.error('Error fetching domain policies:', error);
    throw error;
  }
};

// Update configuration
export const updateConfig = async (config) => {
  try {
    const response = await api.put('/config', config);
    return response.data;
  } catch (error) {
    console.error('Error updating configuration:', error);
    throw error;
  }
};

// Get configuration
export const getConfig = async () => {
  try {
    const response = await api.get('/config');
    return response.data;
  } catch (error) {
    console.error('Error fetching configuration:', error);
    throw error;
  }
};

// Download report
export const downloadReport = async (reportType) => {
  try {
    const response = await api.get(`/reports/${reportType}`, {
      responseType: 'blob',
    });
    
    // Create a URL for the blob
    const url = window.URL.createObjectURL(new Blob([response.data]));
    
    // Create a temporary link and trigger download
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `ad_assessment_${reportType}_${new Date().toISOString().split('T')[0]}.${reportType === 'csv' ? 'csv' : 'pdf'}`);
    document.body.appendChild(link);
    link.click();
    
    // Clean up
    window.URL.revokeObjectURL(url);
    document.body.removeChild(link);
    
    return true;
  } catch (error) {
    console.error(`Error downloading ${reportType} report:`, error);
    throw error;
  }
};

export default api;
