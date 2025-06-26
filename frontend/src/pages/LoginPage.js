import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { saveToken } from '../utils/auth';
import logo from '../assets/logo.png'; // ✅ your logo path
import './LoginPage.css'; // ✅ add a new CSS file

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isDark, setIsDark] = useState(() => localStorage.getItem('theme') === 'dark');
  const navigate = useNavigate();

  useEffect(() => {
    setIsDark(document.body.getAttribute('data-theme') === 'dark');
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      const response = await api.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      saveToken(response.data.access_token);
      navigate('/home');
    } catch (err) {
      setError('❌ Invalid credentials or server error.');
    }
  };

  return (
    <div className={`login-wrapper ${isDark ? 'dark' : 'light'}`}>
      <div className="login-card shadow">
        <div className="text-center mb-4">
          <img src={logo} alt="MindDocs AI Logo" height="48" className="mb-3" />
          <h3 className="fw-bold">Welcome Back</h3>
          <p className="text-muted small">Login to MindDocs AI</p>
        </div>

        {error && <div className="alert alert-danger py-2 small">{error}</div>}

        <form onSubmit={handleLogin}>
          <div className="form-group mb-3">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              className="form-control"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="form-group mb-4">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="form-control"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn btn-theme w-100 fw-bold">
            Sign In
          </button>
        </form>

        <div className="text-center mt-3">
          <small>
            Don’t have an account? <a href="/register" className="link-register">Register here</a>
          </small>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
