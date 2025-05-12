import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Card, Alert, Spinner, Modal, Tabs, Tab, ListGroup } from 'react-bootstrap';
import axios from 'axios';
import { registerUser } from '../services/api';

// Configure axios to send credentials
axios.defaults.withCredentials = true;

const Login = () => {
  const navigate = useNavigate();
  const [state, setState] = useState({
    formData: {
      username: '',
      password: '',
      confirmPassword: ''
    },
    registerData: {
      username: '',
      password: '',
      confirmPassword: ''
    },
    loading: false,
    error: null,
    showChangePassword: false,
    changePasswordData: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    },
    passwordRequirements: {
      length: false,
      uppercase: false,
      lowercase: false,
      numbers: false,
      special: false
    },
    isFirstLogin: false,
    showPasswordPrompt: false,
    passwordPromptData: {
      username: '',
      password: ''
    }
  });

  // Simple password validation - just check if passwords match
  const validatePassword = (password, confirmPassword) => {
    return password === confirmPassword && password.length > 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setState(prev => ({
      ...prev,
      formData: {
        ...prev.formData,
        [name]: value
      }
    }));
  };

  const handleRegisterChange = (e) => {
    const { name, value } = e.target;
    setState(prev => ({
      ...prev,
      registerData: {
        ...prev.registerData,
        [name]: value
      }
    }));
  };

  const handleChangePasswordChange = (e) => {
    const { name, value } = e.target;
    setState(prev => ({
      ...prev,
      changePasswordData: {
        ...prev.changePasswordData,
        [name]: value
      }
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
        // Login with provided credentials
        const response = await axios.post('/api/auth/login', {
            username: state.formData.username,
            password: state.formData.password
        }, {
            withCredentials: true
        });

        console.log('Login response:', response.data); // Debug log

        if (response.data.message === 'Login successful') {
            // Store credentials for password prompt if this is a first-time login
            if (!response.data.password_changed) {
                setState(prev => ({
                    ...prev,
                    showPasswordPrompt: true,
                    passwordPromptData: {
                        username: state.formData.username,
                        password: state.formData.password
                    },
                    loading: false
                }));
                return;
            }
            
            // Normal login flow
            sessionStorage.setItem('isAuthenticated', 'true');
            sessionStorage.setItem('username', state.formData.username);
            sessionStorage.setItem('passwordChanged', response.data.password_changed ? 'true' : 'false');
            navigate('/');
        } else if (response.data.message === 'Password created successfully') {
            // Show password prompt after initial password creation
            setState(prev => ({
                ...prev,
                showPasswordPrompt: true,
                passwordPromptData: {
                    username: state.formData.username,
                    password: state.formData.password
                },
                loading: false
            }));
        } else {
            setState(prev => ({
                ...prev,
                error: response.data.error || 'Login failed',
                loading: false
            }));
        }
    } catch (err) {
        console.error('Login error:', err.response?.data || err);
        setState(prev => ({
            ...prev,
            error: err.response?.data?.error || 'Login failed. Please check your credentials.',
            loading: false
        }));
    }
  };
  
  const handlePasswordPromptLogin = async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
        // Login with the same credentials to verify
        const response = await axios.post('/api/auth/login', {
            username: state.passwordPromptData.username,
            password: state.passwordPromptData.password
        }, {
            withCredentials: true
        });
        
        if (response.data.message === 'Login successful') {
            sessionStorage.setItem('isAuthenticated', 'true');
            sessionStorage.setItem('username', state.passwordPromptData.username);
            sessionStorage.setItem('passwordChanged', 'true');
            navigate('/');
        } else {
            setState(prev => ({
                ...prev,
                error: 'Verification failed. Please try logging in again.',
                showPasswordPrompt: false,
                loading: false
            }));
        }
    } catch (err) {
        console.error('Password prompt login error:', err.response?.data || err);
        setState(prev => ({
            ...prev,
            error: err.response?.data?.error || 'Verification failed. Please try logging in again.',
            showPasswordPrompt: false,
            loading: false
        }));
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    
    // Check if passwords match
    if (state.registerData.password !== state.registerData.confirmPassword) {
      setState(prev => ({ ...prev, error: 'Passwords do not match' }));
      return;
    }
    
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      // Register new user
      const response = await registerUser({
        username: state.registerData.username,
        password: state.registerData.password
      });
      
      // Auto-login after successful registration
      if (response.message === 'User registered successfully') {
        try {
          const loginResponse = await axios.post('/api/auth/login', {
            username: state.registerData.username,
            password: state.registerData.password
          }, {
            withCredentials: true
          });
          
          if (loginResponse.data.message === 'Login successful') {
            sessionStorage.setItem('isAuthenticated', 'true');
            sessionStorage.setItem('username', state.registerData.username);
            sessionStorage.setItem('passwordChanged', 'true');
            navigate('/');
          } else {
            setState(prev => ({
              ...prev,
              error: 'Registration successful but login failed. Please try logging in.',
              loading: false
            }));
          }
        } catch (loginError) {
          setState(prev => ({
            ...prev,
            error: 'Registration successful but login failed. Please try logging in.',
            loading: false
          }));
        }
      } else {
        setState(prev => ({
          ...prev,
          error: response.error || 'Registration failed',
          loading: false
        }));
      }
    } catch (err) {
      console.error('Registration error:', err.response?.data || err);
      setState(prev => ({
        ...prev,
        error: err.response?.data?.error || 'Registration failed. Please try again.',
        loading: false
      }));
    }
  };

  const handleChangePassword = async () => {
    if (state.changePasswordData.newPassword !== state.changePasswordData.confirmPassword) {
      setState(prev => ({ ...prev, error: 'New passwords do not match' }));
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      await axios.post('/api/auth/change-password', {
        current_password: state.changePasswordData.currentPassword,
        new_password: state.changePasswordData.newPassword
      });
      
      setState(prev => ({
        ...prev,
        showChangePassword: false,
        changePasswordData: {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        },
        formData: {
          ...prev.formData,
          password: ''
        },
        error: 'Password changed successfully. Please log in with your new password.'
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err.response?.data?.error || 'Failed to change password'
      }));
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get('/api/auth/status', {
          withCredentials: true
        });
        console.log('Auth status response:', response.data); // Debug log
        
        if (response.data.authenticated) {
          sessionStorage.setItem('isAuthenticated', 'true');
          sessionStorage.setItem('username', response.data.username);
          sessionStorage.setItem('passwordChanged', response.data.password_changed ? 'true' : 'false');
          navigate('/');
        } else {
          sessionStorage.removeItem('isAuthenticated');
          sessionStorage.removeItem('username');
          sessionStorage.removeItem('passwordChanged');
        }
      } catch (err) {
        console.error('Error checking auth status:', err);
        sessionStorage.removeItem('isAuthenticated');
        sessionStorage.removeItem('username');
        sessionStorage.removeItem('passwordChanged');
      }
    };

    checkAuth();
  }, [navigate]);

  const getRequirementClass = (met) => met ? 'text-success' : 'text-danger';

  return (
    <div className="d-flex justify-content-center align-items-center min-vh-100 bg-light">
      <Card className="w-100" style={{ maxWidth: '500px' }}>
        <Card.Header className="text-center">
          <h4 className="mb-0">AD Security Assessment</h4>
        </Card.Header>
        <Card.Body>
          {state.loading && (
            <div className="text-center mb-3">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
              <p className="mt-2">Processing your request...</p>
            </div>
          )}
          {state.error && !state.loading && (
            <Alert variant={state.error.includes('successfully') ? 'success' : 'danger'} className="mb-3">
              {state.error}
            </Alert>
          )}
          
          <Tabs defaultActiveKey="login" id="auth-tabs" className="mb-3">
            <Tab eventKey="login" title="Login">
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Username</Form.Label>
                  <Form.Control
                    type="text"
                    name="username"
                    value={state.formData.username}
                    onChange={handleChange}
                    placeholder="Enter username"
                    required
                    disabled={state.loading}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Password</Form.Label>
                  <Form.Control
                    type="password"
                    name="password"
                    value={state.formData.password}
                    onChange={handleChange}
                    placeholder="Enter password"
                    required
                    disabled={state.loading}
                  />
                </Form.Group>

                <Button 
                  variant="primary" 
                  type="submit" 
                  className="w-100" 
                  disabled={state.loading}
                >
                  {state.loading ? (
                    <>
                      <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                      {' '}Processing...
                    </>
                  ) : (
                    'Login'
                  )}
                </Button>
              </Form>
            </Tab>
            
            <Tab eventKey="register" title="Register">
              <Form onSubmit={handleRegister}>
                <Form.Group className="mb-3">
                  <Form.Label>Username</Form.Label>
                  <Form.Control
                    type="text"
                    name="username"
                    value={state.registerData.username}
                    onChange={handleRegisterChange}
                    placeholder="Choose a username"
                    required
                    disabled={state.loading}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Password</Form.Label>
                  <Form.Control
                    type="password"
                    name="password"
                    value={state.registerData.password}
                    onChange={handleRegisterChange}
                    placeholder="Choose a password"
                    required
                    disabled={state.loading}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Confirm Password</Form.Label>
                  <Form.Control
                    type="password"
                    name="confirmPassword"
                    value={state.registerData.confirmPassword}
                    onChange={handleRegisterChange}
                    placeholder="Confirm password"
                    required
                    disabled={state.loading}
                  />
                </Form.Group>

                <Button 
                  variant="primary" 
                  type="submit" 
                  className="w-100" 
                  disabled={state.loading || !validatePassword(state.registerData.password, state.registerData.confirmPassword)}
                >
                  {state.loading ? (
                    <>
                      <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                      {' '}Processing...
                    </>
                  ) : (
                    'Register'
                  )}
                </Button>
              </Form>
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>

      {/* Password Change Modal */}
      <Modal show={state.showChangePassword} onHide={() => setState(prev => ({ ...prev, showChangePassword: false }))}>
        <Modal.Header closeButton>
          <Modal.Title>Change Password</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Current Password</Form.Label>
              <Form.Control
                type="password"
                name="currentPassword"
                value={state.changePasswordData.currentPassword}
                onChange={handleChangePasswordChange}
                placeholder="Enter current password"
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>New Password</Form.Label>
              <Form.Control
                type="password"
                name="newPassword"
                value={state.changePasswordData.newPassword}
                onChange={handleChangePasswordChange}
                placeholder="Enter new password"
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Confirm New Password</Form.Label>
              <Form.Control
                type="password"
                name="confirmPassword"
                value={state.changePasswordData.confirmPassword}
                onChange={handleChangePasswordChange}
                placeholder="Confirm new password"
                required
              />
            </Form.Group>

            <Card className="mb-3">
              <Card.Header>Password Requirements</Card.Header>
              <Card.Body>
                <ListGroup variant="flush">
                  <ListGroup.Item className={getRequirementClass(state.passwordRequirements.length)}>
                    <i className={`bi bi-${state.passwordRequirements.length ? 'check' : 'x'}-circle me-2`} />
                    Minimum 12 characters
                  </ListGroup.Item>
                  <ListGroup.Item className={getRequirementClass(state.passwordRequirements.uppercase)}>
                    <i className={`bi bi-${state.passwordRequirements.uppercase ? 'check' : 'x'}-circle me-2`} />
                    At least 2 uppercase letters
                  </ListGroup.Item>
                  <ListGroup.Item className={getRequirementClass(state.passwordRequirements.lowercase)}>
                    <i className={`bi bi-${state.passwordRequirements.lowercase ? 'check' : 'x'}-circle me-2`} />
                    At least 3 lowercase letters
                  </ListGroup.Item>
                  <ListGroup.Item className={getRequirementClass(state.passwordRequirements.numbers)}>
                    <i className={`bi bi-${state.passwordRequirements.numbers ? 'check' : 'x'}-circle me-2`} />
                    At least 2 numbers
                  </ListGroup.Item>
                  <ListGroup.Item className={getRequirementClass(state.passwordRequirements.special)}>
                    <i className={`bi bi-${state.passwordRequirements.special ? 'check' : 'x'}-circle me-2`} />
                    At least 1 special character
                  </ListGroup.Item>
                </ListGroup>
              </Card.Body>
            </Card>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setState(prev => ({ ...prev, showChangePassword: false }))}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={handleChangePassword}
            disabled={state.loading || !Object.values(state.passwordRequirements).every(req => req)}
          >
            {state.loading ? (
              <>
                <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                {' '}Processing...
              </>
            ) : (
              'Change Password'
            )}
          </Button>
        </Modal.Footer>
      </Modal>
      
      {/* Password Prompt Modal */}
      <Modal show={state.showPasswordPrompt} backdrop="static" keyboard={false}>
        <Modal.Header>
          <Modal.Title>Sign in with New Password</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Your password has been created successfully. Please sign in with your new password to continue.</p>
          <Alert variant="info">
            This additional verification step helps ensure you remember your password and confirms your account is secure.
          </Alert>
          
          <div className="text-center mt-4">
            <Button 
              variant="primary" 
              onClick={handlePasswordPromptLogin}
              disabled={state.loading}
              className="px-4"
            >
              {state.loading ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                  {' '}Processing...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </div>
        </Modal.Body>
      </Modal>
    </div>
  );
};

export default Login;
