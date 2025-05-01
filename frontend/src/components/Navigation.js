import React from 'react';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Navigation = () => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout');
      navigate('/login');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="py-2">
      <Container fluid>
        <Navbar.Brand as={Link} to="/" className="d-flex align-items-center">
          <img
            src="/logo.svg"
            width="32"
            height="32"
            className="d-inline-block align-middle me-2"
            alt="AD Security Assessment Logo"
            style={{ marginTop: '-2px' }}
          />
          <span className="align-middle">AD Security Assessment</span>
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            <Button 
              as={Link} 
              to="/run-assessment" 
              variant="outline-light" 
              size="sm" 
              className="me-2"
            >
              Run Assessment
            </Button>
            <Nav.Link as={Link} to="/settings">Settings</Nav.Link>
            <Button
              variant="outline-light"
              size="sm"
              className="ms-2"
              onClick={handleLogout}
            >
              Logout
            </Button>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation;
