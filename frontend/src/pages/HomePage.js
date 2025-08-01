// src/pages/HomePage.jsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getToken } from '../utils/auth';
import logo from '../assets/logo.png';
import aiRobot from '../assets/lottie/AI Robot.json';          // ✅ Import Lottie animation
import LottieWrapper from '../components/LottieWrapper';       // ✅ Import wrapper
import './HomePage.css';

function HomePage() {
  const isAuthenticated = !!getToken();
  const navigate = useNavigate();

  const features = [
    {
      icon: '📤',
      title: 'Upload Documents',
      description: 'Easily upload PDFs or scanned files to start processing with AI.',
      path: '/upload'
    },
    {
      icon: '💬',
      title: 'AI Chatbot',
      description: 'Ask questions and interact with your document using smart retrieval-based AI.',
      path: '/chat'
    },
    {
      icon: '📑',
      title: 'Summarization',
      description: 'Generate compressed summaries for long documents — fast and accurate.',
      path: '/summary'
    },
    {
      icon: '🌐',
      title: 'Translation',
      description: 'Translate any document to multiple global languages with ease.',
      path: '/translate'
    }
  ];

  const steps = [
    {
      step: 1,
      title: "Upload a Document",
      description: "Go to the Upload page, select one or more PDFs or images, and submit them to the cloud."
    },
    {
      step: 2,
      title: "Choose an Action",
      description: "Select whether you want to chat with, summarize, or translate the uploaded document."
    },
    {
      step: 3,
      title: "Pick Your File",
      description: "From the dropdown or file list, pick the document you want to work on."
    }
  ];

  return (
    <div className="container py-5">

      {/* ✅ Lottie Animation */}
      <div className="text-center mb-4">
        <LottieWrapper animationData={aiRobot} height={280} />
      </div>

      <div className="text-center mb-5">
        <h1 className="display-5 fw-bold d-flex justify-content-center align-items-center gap-2 flex-wrap">
          {isAuthenticated ? '👋 Welcome Back to' : 'Welcome to'}
          <img src={logo} alt="MindDocs Logo" height="40" className="ms-2" />
          <span className="text-gradient">MindDocs AI</span>
        </h1>

        <p className="homepage-subtext">
          {isAuthenticated ? (
            <>Unlock the power of AI to chat, summarize, translate and manage your documents — all in one platform.</>
          ) : (
            <>Your all-in-one AI platform for document understanding and automation. Register or log in to get started.</>
          )}
        </p>

        {!isAuthenticated && (
          <div className="d-flex justify-content-center gap-3 mt-4">
            <Link to="/register" className="btn btn-primary btn-lg">Get Started</Link>
            <Link to="/login" className="btn btn-outline-light btn-lg">Login</Link>
          </div>
        )}
      </div>

      {/* 🧭 Getting Started Steps */}
      <div className="mb-5">
        <h3 className="text-center fw-bold mb-4">🧭 How to Use MindDocs AI</h3>
        <div className="row g-4 justify-content-center">
          {steps.map(({ step, title, description }) => (
            <div key={step} className="col-md-4">
              <div className="step-card h-100 text-center p-4 shadow-sm border-0">
                <div className="step-number">{step}</div>
                <h5 className="fw-bold mt-3">{title}</h5>
                <p className="text-muted small">{description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <hr className="mb-5" />

      {/* 🚀 Feature Cards */}
      <h3 className="text-center mb-4 fw-bold">🚀 Explore AI Features</h3>
      <div className="row g-4 justify-content-center">
        {features.map((feature, idx) => (
          <div key={idx} className="col-md-5 col-lg-4">
            <div
              className="card h-100 feature-card text-center border-0"
              onClick={() => navigate(feature.path)}
              style={{ cursor: 'pointer' }}
            >
              <div className="card-body py-4">
                <h5 className="card-title fw-bold fs-5">
                  <span style={{ fontSize: '1.5rem', marginRight: '8px' }}>{feature.icon}</span>
                  {feature.title}
                </h5>
                <p className="card-text mt-2">{feature.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HomePage;
