// ✅ React Component: Enhanced TranslationPage.js
// Features: Removed section headers + Added PDF download

import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { getToken } from '../utils/auth';
import jsPDF from 'jspdf';
import logo from '../assets/logo.png';
import './TranslationPage.css';

function TranslationPage() {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [targetLang, setTargetLang] = useState('');
  const [translationResult, setTranslationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const supportedLanguages = ["English", "Hindi", "French", "German", "Spanish", "Chinese", "Arabic"];

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const res = await api.get('/chatbot/documents/mydocs', {
          headers: { Authorization: `Bearer ${getToken()}` }
        });
        setDocuments(res.data);
      } catch (err) {
        console.error('Document fetch error:', err);
        setErrorMsg('❌ Could not load your documents. Try again.');
      }
    };
    fetchDocs();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');
    setTranslationResult(null);
    setLoading(true);

    if (!selectedDoc || !targetLang) {
      setErrorMsg('❗ Please select both a document and a target language.');
      setLoading(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append('doc_name', selectedDoc);
      formData.append('target_language', targetLang);

      const res = await api.post('/translate', formData, {
        headers: {
          Authorization: `Bearer ${getToken()}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      // 🪄 Strip section headers before setting result
      const cleaned = res.data.translation.replace(/--- Section \d+ ---/g, '').trim();
      setTranslationResult({ ...res.data, translation: cleaned });
      setSuccessMsg(`✅ Translation completed for "${res.data.doc_name}"`);
    } catch (err) {
      console.error('Translation error:', err);
      const msg = err.response?.data?.detail || 'Unexpected translation error.';
      setErrorMsg(`❌ ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    if (!translationResult) return;

    const doc = new jsPDF();
    const lines = doc.splitTextToSize(translationResult.translation, 180);
    doc.setFont('Helvetica');
    doc.setFontSize(12);
    doc.text(`📄 Translation of: ${translationResult.doc_name}`, 10, 10);
    doc.text(lines, 10, 20);
    doc.save(`${translationResult.doc_name}_${translationResult.language}_Translation.pdf`);
  };

  return (
    <div className="container py-5" style={{ maxWidth: '850px' }}>
      <h2 className="mb-4 fw-bold d-flex align-items-center gap-3">
        <img src={logo} alt="MindDocs Logo" height="40" />
        <span className="text-gradient">Document Translation</span>
      </h2>

      {errorMsg && <div className="alert alert-danger">{errorMsg}</div>}
      {successMsg && <div className="alert alert-success">{successMsg}</div>}

      {translationResult && (
        <div className="mb-5">
          <h5 className="mb-3">📝 Translated Output</h5>
          <div
            className="p-3 rounded"
            style={{
              backgroundColor: 'var(--bg-color)',
              color: 'var(--text-color)',
              border: '1px solid rgba(255,255,255,0.1)',
              whiteSpace: 'pre-wrap',
              maxHeight: '300px',
              overflowY: 'auto'
            }}
          >
            {translationResult.translation}
          </div>
          <button onClick={handleDownloadPDF} className="btn btn-outline-primary mt-3">
            ⬇️ Download PDF
          </button>
        </div>
      )}

      {/* Translation Form */}
      <form onSubmit={handleSubmit} className="p-4 rounded border shadow-sm mb-5"
        style={{ backgroundColor: 'var(--bg-color)', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-color)' }}>

        <h5 className="mb-4 fw-semibold">Translate Your Uploaded Document</h5>

        <div className="mb-3">
          <label className="form-label fw-semibold">📄 Select a Document:</label>
          <select className="form-select" value={selectedDoc} onChange={(e) => setSelectedDoc(e.target.value)} required>
            <option value="">-- Choose from uploaded documents --</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.name}>{doc.name} ({doc.domain})</option>
            ))}
          </select>
        </div>

        <div className="mb-4">
          <label className="form-label fw-semibold">🌍 Target Language:</label>
          <select className="form-select" value={targetLang} onChange={(e) => setTargetLang(e.target.value)} required>
            <option value="">-- Select language --</option>
            {supportedLanguages.map((lang) => (
              <option key={lang} value={lang}>{lang}</option>
            ))}
          </select>
        </div>

        <button type="submit" className="btn btn-primary w-100 fw-bold" disabled={loading}>
          {loading ? 'Translating...' : 'Translate'}
        </button>
      </form>

      {translationResult && (
        <div className="p-4 rounded" style={{ backgroundColor: 'var(--bg-color)', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-color)' }}>
          <h5 className="mb-3">📄 Translation Details</h5>
          <p><strong>Document:</strong> {translationResult.doc_name}</p>
          <p><strong>Domain:</strong> {translationResult.domain}</p>
          <p><strong>Language:</strong> {translationResult.language}</p>
          <p><strong>Chunks Translated:</strong> {translationResult.total_chunks}</p>
        </div>
      )}
    </div>
  );
}

export default TranslationPage;
