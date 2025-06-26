// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import './App.css';

// ⚡️ Set theme BEFORE React renders
const theme = localStorage.getItem('theme') || 'dark';
document.body.setAttribute('data-theme', theme);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);
