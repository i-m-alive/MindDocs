import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { getToken } from '../utils/auth';
import logo from '../assets/logo.png';
import jsPDF from 'jspdf'; // ✅ PDF generation library
import './SummaryPage.css';

function SummaryPage() {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [ratio, setRatio] = useState(0.3);
  const [summaryResult, setSummaryResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // 🧾 Fetch uploaded user documents on component mount
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const res = await api.get('/chatbot/documents/mydocs', {
          headers: { Authorization: `Bearer ${getToken()}` }
        });
        setDocuments(res.data);
      } catch (err) {
        setError('❌ Failed to load your documents. Try re-logging in.');
      }
    };
    fetchDocuments();
  }, []);

  // 📤 Submit form to generate summary
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSummaryResult(null);
    setLoading(true);

    if (!selectedDoc) {
      setError('❗ Please select a document.');
      setLoading(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append('doc_name', selectedDoc);
      formData.append('ratio', ratio);

      const res = await api.post('/summarize', formData, {
        headers: {
          Authorization: `Bearer ${getToken()}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      setSummaryResult(res.data);
      setSuccess(`✅ Summary generated for "${res.data.doc_name}"`);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Unexpected error during summarization.';
      setError(`❌ ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  // 📥 Handle PDF download
  const handleDownloadPDF = () => {
    if (!summaryResult) return;

    const doc = new jsPDF();

    // 🖨️ Title
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text('📌 Document Summary', 10, 20);

    // 🧾 Meta Info
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text(`📄 Document: ${summaryResult.doc_name}`, 10, 35);
    doc.text(`📂 Domain: ${summaryResult.domain}`, 10, 45);
    doc.text(`🧮 Original Word Count: ${summaryResult.original_word_count}`, 10, 55);
    doc.text(`✂️ Summary Word Count: ${summaryResult.summary_word_count}`, 10, 65);
    doc.text(`⚖️ Compression Ratio: ${summaryResult.compression_ratio}`, 10, 75);

    // 📝 Summary Content
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('📋 Summary:', 10, 90);

    const summaryLines = doc.splitTextToSize(summaryResult.summary, 180);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text(summaryLines, 10, 100);

    // 💾 Save file
    doc.save(`${summaryResult.doc_name}_summary.pdf`);
  };

  return (
    <div className="summary-page container py-5" style={{ maxWidth: '850px' }}>
      <h2 className="text-center fw-bold mb-4 d-flex justify-content-center align-items-center gap-2 flex-wrap">
        <img src={logo} alt="MindDocs Logo" height="40" />
        <span>Document Summarization</span>
      </h2>

      {/* 🔴 Error Message */}
      {error && <div className="alert alert-danger">{error}</div>}

      {/* ✅ Success Message */}
      {success && <div className="alert alert-success">{success}</div>}

      {/* 🔘 Form */}
      <form onSubmit={handleSubmit} className="themed-card p-4 mb-5">
        <div className="form-floating mb-3">
          <select
            id="docSelect"
            className="form-select"
            value={selectedDoc}
            onChange={(e) => setSelectedDoc(e.target.value)}
            required
          >
            <option value="">-- Select uploaded document --</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.name}>
                {doc.name} ({doc.domain})
              </option>
            ))}
          </select>
          <label htmlFor="docSelect">📁 Choose Document</label>
        </div>

        <div className="form-floating mb-4">
          <input
            id="ratioInput"
            type="number"
            step="0.05"
            min="0.05"
            max="0.95"
            className="form-control"
            value={ratio}
            onChange={(e) => setRatio(parseFloat(e.target.value))}
            required
          />
          <label htmlFor="ratioInput">⚖️ Compression Ratio (e.g. 0.3 = 30%)</label>
        </div>

        <button
          type="submit"
          className="btn btn-primary w-100 rounded-pill fw-semibold"
          disabled={loading}
        >
          {loading ? '⏳ Summarizing...' : '✨ Generate Summary'}
        </button>
      </form>

      {/* 📋 Summary Output */}
      {summaryResult && (
        <div className="card themed-card shadow-sm border">
          <div className="card-header themed-header fw-bold fs-5">
            📌 Final Summary
          </div>
          <div className="card-body">
            <div className="summary-box">
              {summaryResult.summary}
            </div>

            <div className="summary-meta themed-card p-4 mt-4">
              <h6 className="fw-bold mt-4">📊 Summary Output</h6>
              <p><strong>📄 Document:</strong> <span className="text-info">{summaryResult.doc_name}</span></p>
              <p><strong>📂 Domain:</strong> <span className="badge bg-info text-dark">{summaryResult.domain}</span></p>
              <p><strong>🧮 Original Word Count:</strong> {summaryResult.original_word_count}</p>
              <p><strong>✂️ Summary Word Count:</strong> {summaryResult.summary_word_count}</p>
              <p><strong>⚖️ Ratio:</strong> {summaryResult.compression_ratio}</p>

              {/* ⬇️ Download Button */}
              <button
                onClick={handleDownloadPDF}
                className="btn btn-success mt-3 fw-semibold rounded-pill"
              >
                📥 Download Summary as PDF
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SummaryPage;
