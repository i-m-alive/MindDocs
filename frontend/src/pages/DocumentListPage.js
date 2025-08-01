import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Container, Table, Button, Spinner } from "react-bootstrap";
import api from '../services/api';                               // ✅ Centralized axios instance
import { getToken } from "../utils/auth";           // ✅ Consistent token access

const DocumentListPage = () => {
  const [documents, setDocuments] = useState([]);   // 🧠 Stores document data from API
  const [loading, setLoading] = useState(true);     // ⏳ Controls spinner visibility
  const navigate = useNavigate();                   // 🔁 Used for route redirection

  // 🚀 Fetch user-uploaded documents on mount
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const res = await api.get("/documents/me", {
          headers: {
            Authorization: `Bearer ${getToken()}`,  // 🔐 Attach JWT token
          },
        });
        setDocuments(res.data);                     // 🗂️ Update state with fetched documents
      } catch (err) {
        console.error("❌ Failed to fetch documents:", err);
        alert("Error loading documents. Please login again.");
        navigate("/login");                         // ⛔ Redirect on auth or fetch error
      } finally {
        setLoading(false);                          // ✅ Hide spinner regardless of outcome
      }
    };

    fetchDocuments();
  }, [navigate]);

  // 🧭 Route to document-specific action (chat, summary, etc.)
  const handleAction = (docId, action) => {
    navigate(`/${action}?doc_id=${docId}`);         // 📎 Pass doc_id as query param
  };

  return (
    <Container className="mt-4">
      <h2 className="mb-4">Your Uploaded Documents</h2>

      {loading ? (
        <Spinner animation="border" />              // ⏳ Show while loading
      ) : documents.length === 0 ? (
        <p>No documents found. Please upload some files.</p>  // 📭 No docs available
      ) : (
        <Table striped bordered hover responsive>   {/* 📄 Document Table */}
          <thead>
            <tr>
              <th>Name</th>
              <th>Domain</th>
              <th>Uploaded On</th>
              <th>Azure Blob</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id}>
                <td>{doc.name}</td>
                <td>{doc.domain}</td>
                <td>{new Date(doc.created_at).toLocaleString()}</td>
                <td>
                  {doc.blob_url ? (
                    <a
                      href={doc.blob_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View PDF
                    </a>
                  ) : (
                    "Not Available"
                  )}
                </td>
                <td>
                  {/* 🎯 Each button redirects to corresponding action page */}
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleAction(doc.id, "chat")}
                    className="me-2"
                  >
                    Chat
                  </Button>
                  <Button
                    variant="info"
                    size="sm"
                    onClick={() => handleAction(doc.id, "summary")}
                    className="me-2"
                  >
                    Summarize
                  </Button>
                  <Button
                    variant="warning"
                    size="sm"
                    onClick={() => handleAction(doc.id, "translate")}
                    className="me-2"
                  >
                    Translate
                  </Button>
                  <Button
                    variant="success"
                    size="sm"
                    onClick={() => handleAction(doc.id, "extract")}
                  >
                    Extract
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Container>
  );
};

export default DocumentListPage;
