import React, { useState } from 'react';
import api from '../services/api';
import { getToken } from '../utils/auth';

function UploadPage() {
  const [files, setFiles] = useState([]);
  const [names, setNames] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // 🔄 Handle file selection and prepare default names
  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    setNames(selectedFiles.map(file => file.name)); // default name = original file name
  };

  // 📝 Handle input change for custom names
  const handleNameChange = (index, value) => {
    const updatedNames = [...names];
    updatedNames[index] = value;
    setNames(updatedNames);
  };

  // 🚀 Upload to backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    if (files.length === 0) {
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

      setMessage(`✅ Uploaded ${response.data.uploaded_documents.length} file(s) as ${response.data.user} (${response.data.domain})`);
      setFiles([]);
      setNames([]);
    } catch (err) {
      console.error('Upload error:', err);
      setError('❌ Upload failed. Please check your files and try again.');
    }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: '600px' }}>
      <h2 className="mb-4">Upload Documents</h2>

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-danger">{error}</div>}

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

        {files.map((file, idx) => (
          <div key={idx} className="mb-2">
            <label className="form-label">Custom Name for <strong>{file.name}</strong></label>
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
  );
}

export default UploadPage;
