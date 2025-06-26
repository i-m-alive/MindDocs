import React, { useState, useEffect } from "react";
import api from "../services/api";
import { useNavigate } from "react-router-dom";
import logo from "../assets/logo.png";
import "./RegisterPage.css";

function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [domain, setDomain] = useState("retail");
  const [theme, setTheme] = useState("light");
  const [fieldError, setFieldError] = useState("");
  const [serverError, setServerError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const currentTheme = localStorage.getItem("theme") || "light";
    setTheme(currentTheme);
  }, []);

  const handleRegister = async () => {
    setFieldError("");
    setServerError("");

    try {
      await api.post("/auth/register", {
        username,
        email,
        password,
        domain,
      });

      navigate("/home");
    } catch (err) {
      if (err.response) {
        const status = err.response.status;
        if (status === 400) {
          setFieldError("Please fill all required fields correctly.");
        } else if (status === 409) {
          setFieldError("Username or email already exists.");
        } else if (status >= 500) {
          setServerError("Server error. Please try again later.");
        } else {
          setServerError("Registration failed. Please check your details.");
        }
      } else {
        setServerError("Network issue. Please check your connection.");
      }
    }
  };

  return (
    <div className={`register-wrapper ${theme}`}>
      <div className="register-card shadow">
        <div className="text-center mb-4">
          <img src={logo} alt="MindDocs Logo" height="60" className="mb-3" />
          <h3 className="fw-bold">Create Account</h3>
          <p className="text-muted">Register with MindDocs AI</p>
        </div>

        <input
          className={`form-control my-2 ${fieldError ? "is-invalid" : ""}`}
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <input
          className={`form-control my-2 ${fieldError ? "is-invalid" : ""}`}
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          className={`form-control my-2 ${fieldError ? "is-invalid" : ""}`}
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <select
          className="form-select my-2"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          required
        >
          <option value="retail">Retail</option>
          <option value="medical">Medical</option>
          <option value="finance">Finance</option>
          <option value="legal">Legal</option>
        </select>

        {fieldError && (
          <div className="invalid-feedback d-block text-center small">
            {fieldError}
          </div>
        )}
        {serverError && (
          <div className="text-danger text-center mt-2 small">{serverError}</div>
        )}

        <button className="btn btn-theme w-100 mt-3 fw-bold" onClick={handleRegister}>
          Register
        </button>

        <div className="text-center mt-3">
          <small>
            Already have an account? <a href="/login">Login here</a>
          </small>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
