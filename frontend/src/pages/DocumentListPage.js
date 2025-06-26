import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { Container, Table, Button, Spinner } from "react-bootstrap";

const DocumentListPage = () => {
  const [documents, setDocuments] = useState([]);     // Stores documents from backend
  const [loading, setLoading] = useState(true);       // Spinner loading state
  const navigate = useNavigate();                     // For route redirection
  const token = localStorage.getItem("token");        // JWT token from local storage

  // ✅ Fetch user's uploaded documents
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const res = await axios.get("http://localhost:8000/documents/me", {
          headers: {
            Authorization: `Bearer ${token}`,        // Include token in header
          },
        });
        setDocuments(res.data);                      // Update state with document list
      } catch (err) {
        console.error("Failed to fetch documents:", err);
        alert("Error loading documents. Please login again.");
        navigate("/login");                          // Redirect to login if error
      } finally {
        setLoading(false);                           // Hide spinner
      }
    };

    fetchDocuments();
  }, [navigate, token]);

  // ✅ Handler to redirect user to action page (chat, summarize, etc.)
  const handleAction = (docId, action) => {
    navigate(`/${action}?doc_id=${docId}`);
  };

  return (
    <Container className="mt-4">
      <h2 className="mb-4">Your Uploaded Documents</h2>

      {loading ? (
        <Spinner animation="border" />
      ) : documents.length === 0 ? (
        <p>No documents found. Please upload some files.</p>
      ) : (
        <Table striped bordered hover>
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
                    <a href={doc.blob_url} target="_blank" rel="noopener noreferrer">
                      View PDF
                    </a>
                  ) : (
                    "Not Available"
                  )}
                </td>
                <td>
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
