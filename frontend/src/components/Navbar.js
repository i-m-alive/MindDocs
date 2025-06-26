import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getToken, removeToken } from '../utils/auth';
import logo from '../assets/logo.png';
import './Navbar.css'; // Optional: for animation or extra styles

function Navbar() {
  const navigate = useNavigate();
  const isAuthenticated = !!getToken();
  const [collapsed, setCollapsed] = useState(true);

  const toggleNavbar = () => setCollapsed(!collapsed);

  const handleLogout = () => {
    removeToken();
    navigate('/home');
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark fixed-top shadow-sm px-4 py-2">
      <Link className="navbar-brand d-flex align-items-center brand-animate gap-2" to="/home">
        <img
          src={logo}
          alt="MindDocs AI"
          height="40"
          width="40"
          style={{ borderRadius: '8px', objectFit: 'contain' }}
        />
        <div className="d-flex flex-column justify-content-center">
          <span className="fw-bold text-white" style={{ fontSize: '1.1rem', lineHeight: '1rem' }}>
            MindDocs <span className="text-info">AI</span>
          </span>
          <small className="text-muted" style={{ fontSize: '0.75rem', marginTop: '2px' }}>
            Document Intelligence
          </small>
        </div>
      </Link>


      <button
        className="navbar-toggler"
        type="button"
        onClick={toggleNavbar}
        aria-controls="navbarContent"
        aria-expanded={!collapsed}
        aria-label="Toggle navigation"
      >
        <span className="navbar-toggler-icon"></span>
      </button>

      <div className={`collapse navbar-collapse ${collapsed ? '' : 'show'} ms-3`} id="navbarContent">
        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
          {isAuthenticated && (
            <>
              <li className="nav-item"><Link className="nav-link" to="/upload">Upload</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/chat">Chat</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/summary">Summarize</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/translate">Translate</Link></li>
            </>
          )}
        </ul>

        <ul className="navbar-nav">
          {!isAuthenticated ? (
            <>
              <li className="nav-item"><Link className="nav-link" to="/login">Login</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/register">Register</Link></li>
            </>
          ) : (
            <li className="nav-item">
              <button className="btn btn-outline-info ms-2" onClick={handleLogout}>Logout</button>
            </li>
          )}
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
