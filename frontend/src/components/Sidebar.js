import React from 'react';
import { Nav } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { 
  BarChartFill, 
  ListCheck, 
  Server, 
  Laptop, 
  Shield, 
  Gear 
} from 'react-bootstrap-icons';

const Sidebar = () => {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path;
  };
  
  return (
    <div className="sidebar" style={{ width: '250px' }}>
      <Nav className="flex-column">
        <Nav.Link 
          as={Link} 
          to="/" 
          className={`sidebar-link ${isActive('/') ? 'active' : ''}`}
        >
          <BarChartFill className="me-2" /> Dashboard
        </Nav.Link>
        <Nav.Link 
          as={Link} 
          to="/results" 
          className={`sidebar-link ${isActive('/results') ? 'active' : ''}`}
        >
          <ListCheck className="me-2" /> Assessment Results
        </Nav.Link>
        <Nav.Link 
          as={Link} 
          to="/domain-controllers" 
          className={`sidebar-link ${isActive('/domain-controllers') ? 'active' : ''}`}
        >
          <Server className="me-2" /> Domain Controllers
        </Nav.Link>
        <Nav.Link 
          as={Link} 
          to="/computers" 
          className={`sidebar-link ${isActive('/computers') ? 'active' : ''}`}
        >
          <Laptop className="me-2" /> Computers
        </Nav.Link>
        <Nav.Link 
          as={Link} 
          to="/domain-policies" 
          className={`sidebar-link ${isActive('/domain-policies') ? 'active' : ''}`}
        >
          <Shield className="me-2" /> Domain Policies
        </Nav.Link>
        <Nav.Link 
          as={Link} 
          to="/settings" 
          className={`sidebar-link ${isActive('/settings') ? 'active' : ''}`}
        >
          <Gear className="me-2" /> Settings
        </Nav.Link>
      </Nav>
    </div>
  );
};

export default Sidebar;
