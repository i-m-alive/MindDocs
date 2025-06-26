import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { getToken } from '../utils/auth';

function ExtractionPage() {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [extractedData, setExtractedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // 📄 Fetch uploaded documents on mount
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await api.get('/chatbot/documents/mydocs', {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        });
        setDocuments(response.data);
      } catch (err) {
        console.error('Error fetching documents:', err);
        setError('❌ Failed to load user documents.');
      }
    };

    fetchDocuments();
  }, []);

  // 🚀 Trigger backend extraction
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Clear previous states
    setMessage('');
    setError('');
    setExtractedData(null);
    setLoading(true);

    // Validate selection
    if (!selectedDoc) {
      setError('❗ Please select a document to extract from.');
      setLoading(false);
      return;
    }

    try {
      // Prepare form data for FastAPI backend
      const formData = new FormData();
      formData.append('doc_name', selectedDoc);

      const response = await api.post('/extract', formData, {
        headers: {
          Authorization: `Bearer ${getToken()}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      // Format JSON nicely for viewing
      const extracted = response.data.extracted_fields;
      setExtractedData(JSON.stringify(extracted, null, 2));

      setMessage(`✅ Extraction completed for document: ${response.data.doc_name}`);
    } catch (err) {
      console.error('❌ Extraction error:', err);
      const msg = err.response?.data?.detail || 'Unexpected error during extraction.';
      setError(`❌ ${msg}`);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="container mt-5" style={{ maxWidth: '800px' }}>
      <h2 className="mb-4">📄 Structured Data Extraction</h2>

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSubmit}>
        {/* 📂 Document dropdown */}
        <div className="mb-3">
          <label className="form-label">Select Document:</label>
          <select
            className="form-select"
            value={selectedDoc}
            onChange={(e) => setSelectedDoc(e.target.value)}
            required
          >
            <option value="">-- Choose a document --</option>
            {documents.map((doc, index) => (
              <option key={index} value={doc.name}>
                {doc.name} ({doc.domain})
              </option>
            ))}
          </select>
        </div>

        <button type="submit" className="btn btn-primary w-100" disabled={loading}>
          {loading ? 'Extracting...' : 'Extract Data'}
        </button>
      </form>

      {/* 📋 Output display */}
      {extractedData && (
        <div className="mt-4">
          <h4>📊 Extracted Information</h4>
          <pre className="bg-light p-3 border rounded">
            {JSON.stringify(extractedData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default ExtractionPage;
