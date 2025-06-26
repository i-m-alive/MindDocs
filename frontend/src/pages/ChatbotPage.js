import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { getToken } from '../utils/auth';
import './ChatbotPage.css';
import logo from '../assets/logo.png';

function ChatbotPage() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [aiTyping, setAiTyping] = useState(false);

  const messagesEndRef = useRef(null);
  const chatWindowRef = useRef(null);

  // 🔁 Fetch documents from backend
  const fetchDocuments = useCallback(async () => {
    try {
      const res = await axios.get('http://localhost:8000/chatbot/documents/mydocs', {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setDocuments(res.data);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load your documents. Try re-logging in.');
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // 📜 Scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, aiTyping]);

  // 📜 Fetch previous chat history for selected doc
  const fetchChatHistory = async (docName) => {
    try {
      const res = await axios.get(`http://localhost:8000/chatbot/history/${docName}`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      const chatMsgs = res.data.flatMap(item => [
        { sender: 'user', text: item.question },
        { sender: 'ai', text: item.answer }
      ]);
      setMessages(chatMsgs);
    } catch (err) {
      console.error('Error loading chat history:', err);
      setMessages([]);
    }
  };

  const handleDocSelect = (e) => {
    const value = e.target.value;
    if (streaming) {
      setSelectedDocs([value]);
      setMessages([]);
    } else {
      const selected = Array.from(e.target.selectedOptions, opt => opt.value);
      setSelectedDocs(selected);
      if (selected.length === 1) fetchChatHistory(selected[0]);
      else setMessages([]);
    }
  };

  const handleStreamingToggle = () => {
    setStreaming(prev => {
      const next = !prev;
      const lastSelected = selectedDocs[0] || '';
      setSelectedDocs(lastSelected ? [lastSelected] : []);
      setMessages([]);
      return next;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setAiTyping(true);

    const docName = selectedDocs[0];
    if (!question.trim() || !docName) {
      setError('Please enter a question and select a document.');
      setLoading(false);
      setAiTyping(false);
      return;
    }

    setMessages(prev => [...prev, { sender: 'user', text: question }]);

    try {
      const formData = new FormData();
      formData.append('question', question);

      if (streaming) {
        formData.append('doc_name', docName);

        const response = await fetch('http://localhost:8000/chatbot/chat/stream', {
          method: 'POST',
          headers: { Authorization: `Bearer ${getToken()}` },
          body: formData
        });

        if (!response.ok || !response.body) throw new Error('Streaming failed');

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let fullResponse = '';
        let indexToUpdate = null;

        // 💬 Insert empty AI message first
        setMessages(prev => {
          indexToUpdate = prev.length;
          return [...prev, { sender: 'ai', text: '' }];
        });

        // 🌀 Read and stream chunks
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          console.log("📦 Chunk:", chunk); 
          fullResponse += chunk;

          setMessages(prev => {
            const updated = [...prev];
            if (updated[indexToUpdate]) {
              updated[indexToUpdate] = { ...updated[indexToUpdate], text: fullResponse };
            }
            return updated;
          });
        }

      } else {
        selectedDocs.forEach(doc => formData.append('doc_names', doc));
        const res = await axios.post('http://localhost:8000/chatbot/chat', formData, {
          headers: {
            Authorization: `Bearer ${getToken()}`,
            'Content-Type': 'multipart/form-data'
          }
        });
        setMessages(prev => [...prev, { sender: 'ai', text: res.data.reply }]);
      }

    } catch (err) {
      console.error('Chat error:', err);
      setError('❌ Chatbot failed to respond.');
    } finally {
      setLoading(false);
      setAiTyping(false);
      setQuestion('');
    }
  };

  return (
    <div className="chatbot-container container py-4">
      <h2 className="mb-4 text-center d-flex align-items-center justify-content-center gap-2">
        <img src={logo} alt="logo" style={{ height: '32px' }} />
        Chat with Your Document
      </h2>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="mb-3">
        <label><strong>Select Document{streaming ? '' : '(s)'}:</strong></label>
        <select
          multiple={!streaming}
          size={streaming ? 1 : Math.min(5, documents.length)}
          className="form-control"
          onChange={handleDocSelect}
          value={streaming ? selectedDocs[0] || '' : selectedDocs}
        >
          {documents.map((doc) => (
            <option key={doc.id} value={doc.name}>
              {doc.name} ({doc.domain})
            </option>
          ))}
        </select>
        <small className="form-text text-muted">
          {streaming ? 'Only one document allowed in streaming mode.' : 'You can select multiple documents.'}
        </small>
      </div>

      <div className="form-check form-switch mb-3">
        <input
          className="form-check-input"
          type="checkbox"
          id="streamToggle"
          checked={streaming}
          onChange={handleStreamingToggle}
        />
        <label className="form-check-label" htmlFor="streamToggle">
          Enable Streaming Chat
        </label>
      </div>

      <div className="chat-window" ref={chatWindowRef}>
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.sender}`}>
              <div className="d-flex align-items-start gap-2">
                {msg.sender === 'ai' && <img src={logo} alt="AI" className="chat-logo" />}
                <span>{msg.text}</span>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
          {aiTyping && (
            <div className="chat-message ai">
              <div className="typing-indicator">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            </div>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form mt-3">
        <div className="input-group custom-chat-input">
          <textarea
            className="form-control chat-textarea"
            rows="2"
            placeholder="Ask your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            style={{ resize: 'none' }}
          />
          <button
            type="submit"
            className="btn send-btn"
            disabled={loading}
            title="Send"
          >
            ➤
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatbotPage;
