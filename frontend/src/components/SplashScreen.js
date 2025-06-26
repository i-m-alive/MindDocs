import React from 'react';
import './SplashScreen.css';
import logo from '../assets/logo.png'; // Make sure your actual file name matches

function SplashScreen() {
  return (
    <div className="splash-screen">
      <img src={logo} alt="MindDocs AI Logo" className="splash-logo" />
      <h2 className="splash-text">MindDocs AI</h2>
    </div>
  );
}

export default SplashScreen;
