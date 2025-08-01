// src/pages/UploadPage.js

import React, { useState } from 'react';
import api from '../services/api';
import { getToken } from '../utils/auth';
import './UploadPage.css'; // ✅ Reuses card styles

// ✅ Importing Lottie assets and wrapper
import uploadingAnimation from '../assets/lottie/Uploading.json';
import LottieWrapper from '../components/LottieWrapper';

function UploadPage() {
  // ✅ State for files, names, messages
  const [files, setFiles] = useState([]);
  const [names, setNames] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // ✅ Handle file selection
  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    setNames(selectedFiles.map(file => file.name));
  };

  // ✅ Handle input name change for each file
  const handleNameChange = (index, value) => {
    const updatedNames = [...names];
    updatedNames[index] = value;
    setNames(updatedNames);
  };

  // ✅ Submit form and upload to backend API
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    if (!files || files.length === 0) {
      setError('❗ Please select at least one PDF file.');
      return;
    }

    if (files.length !== names.length) {
      setError('❗ Each file must have a custom name.');
      return;
    }

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    names.forEach(name => formData.append('names', name));

    try {
      const response = await api.post('/documents/upload', formData, {
        headers: {
          'Authorization': `Bearer ${getToken()}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      const uploaded = response?.data?.uploaded_documents;
      const uploadedCount = Array.isArray(uploaded) ? uploaded.length : 0;
      const user = response?.data?.user || 'Unknown User';
      const domain = response?.data?.domain || 'Unknown Domain';

      setMessage(`✅ Uploaded ${uploadedCount} file(s) as ${user} (${domain})`);
      setFiles([]);
      setNames([]);
    } catch (err) {
      console.error('❌ Upload error:', err);
      if (err.response) {
        console.error('🔍 Response data:', err.response.data);
        console.error('🔍 Status:', err.response.status);
        console.error('🔍 Headers:', err.response.headers);
      }
      setError('❌ Upload failed. Please check your files and try again.');
    }
  };

  return (
    <>
      {/* 📂 Upload Section (Narrow Container) */}
      <div className="container mt-5" style={{ maxWidth: '600px' }}>
        {/* 📤 Lottie animation */}
        <LottieWrapper animationData={uploadingAnimation} height={260} />
        {/*
          - Plays the Uploading.json animation
          - Positioned above the heading
          - Adjust height if needed (default: 260px)
        */}

        <h2 className="mb-4 text-center">Upload Documents</h2>

        {/* ✅ Success or Error messages */}
        {message && <div className="alert alert-success">{message}</div>}
        {error && <div className="alert alert-danger">{error}</div>}

        {/* ✅ Upload form */}
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Select PDF Documents:</label>
            <input
              type="file"
              multiple
              accept="application/pdf"
              className="form-control"
              onChange={handleFileChange}
            />
          </div>

          {/* ✅ Dynamic name fields */}
          {files.map((file, idx) => (
            <div key={idx} className="mb-2">
              <label className="form-label">
                Custom Name for <strong>{file.name}</strong>
              </label>
              <input
                type="text"
                className="form-control"
                required
                value={names[idx]}
                onChange={e => handleNameChange(idx, e.target.value)}
              />
            </div>
          ))}

          <button type="submit" className="btn btn-primary mt-3 w-100">Upload</button>
        </form>
      </div>

      {/* 🚀 Feature Cards Section (Visible after upload) */}
      {message && (
        <div className="container mt-5">
          <h4 className="text-center fw-bold">📂 Available Actions</h4>
          <div className="row row-cols-1 row-cols-sm-2 row-cols-md-3 g-4 justify-content-center mt-3">
            {[
              {
                icon: '💬',
                title: 'AI Chatbot',
                description: 'Ask questions about your uploaded document.',
                path: '/chat'
              },
              {
                icon: '📑',
                title: 'Summarization',
                description: 'Summarize the uploaded content instantly.',
                path: '/summary'
              },
              {
                icon: '🌐',
                title: 'Translation',
                description: 'Translate the uploaded document to any language.',
                path: '/translate'
              }
            ].map((feature, idx) => (
              <div key={idx} className="col">
                <div
                  className="card feature-card text-center border-0 h-100"
                  onClick={() => (window.location.href = feature.path)}
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
      )}
    </>
  );
}

export default UploadPage;
