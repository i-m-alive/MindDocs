import React, { useState, useEffect, useCallback, useRef } from 'react';
import api from '../services/api';
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
  const [aiTyping, setAiTyping] = useState(false);
  const [speakingMsgIndex, setSpeakingMsgIndex] = useState(null);
  const [isPaused, setIsPaused] = useState(false);

  const messagesEndRef = useRef(null);
  const chatWindowRef = useRef(null);
  const utteranceRef = useRef(null);

  // 🔊 TTS: Play message
  const playText = (text, index) => {
    if (!window.speechSynthesis) {
      alert("Your browser does not support speech synthesis.");
      return;
    }

    stopSpeech(); // Always stop current speech first

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 1;
    utterance.pitch = 1;

    utterance.onend = () => {
      setSpeakingMsgIndex(null);
      setIsPaused(false);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
    setSpeakingMsgIndex(index);
    setIsPaused(false);
  };

  // ⏸️ Pause TTS
  const pauseSpeech = () => {
    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
      window.speechSynthesis.pause();
      setIsPaused(true);
    }
  };

  // 🔁 Resume TTS
  const resumeSpeech = () => {
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
    }
  };

  // ⏹️ Stop TTS
  const stopSpeech = () => {
    window.speechSynthesis.cancel();
    setSpeakingMsgIndex(null);
    setIsPaused(false);
  };

  // 📄 Fetch user documents
  const fetchDocuments = useCallback(async () => {
    try {
      const res = await api.get('/chatbot/documents/mydocs', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setDocuments(res.data);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load your documents. Please re-login.');
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages, aiTyping]);

  useEffect(() => {
    window.speechSynthesis.cancel(); // Cancel speech when messages update
  }, [messages]);

  // 💬 Fetch past chat history
  const fetchChatHistory = async (docName) => {
    try {
      const res = await api.get(`/chatbot/history/${docName}`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });

      const chatMsgs = res.data.flatMap(item => [
        { sender: 'user', text: item.question },
        { sender: 'ai', text: item.answer },
      ]);

      setMessages(chatMsgs);
    } catch (err) {
      console.error('Error loading chat history:', err);
      setMessages([]);
    }
  };

  const handleDocSelect = (e) => {
    const selected = Array.from(e.target.selectedOptions, opt => opt.value);
    setSelectedDocs(selected);
    setMessages([]);
    if (selected.length === 1) {
      fetchChatHistory(selected[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setAiTyping(true);

    const docName = selectedDocs[0];
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || !docName) {
      setError('Please enter a question and select a document.');
      setLoading(false);
      setAiTyping(false);
      return;
    }

    setMessages(prev => [...prev, { sender: 'user', text: trimmedQuestion }]);

    const formData = new FormData();
    formData.append('question', trimmedQuestion);
    selectedDocs.forEach(doc => formData.append('doc_names', doc));

    try {
      const res = await api.post('/chatbot/chat', formData, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });

      setMessages(prev => [...prev, { sender: 'ai', text: res.data.reply }]);
    } catch (err) {
      console.error('Chat error:', err);
      setError('Chatbot failed to respond.');
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
        <label><strong>Select Document(s):</strong></label>
        <select
          multiple
          size={Math.min(5, documents.length)}
          className="form-control"
          onChange={handleDocSelect}
          value={selectedDocs}
        >
          {documents.map((doc) => (
            <option key={doc.id} value={doc.name}>
              {doc.name} ({doc.domain})
            </option>
          ))}
        </select>
        <small className="form-text text-muted">
          You can select multiple documents.
        </small>
      </div>

      <div className="chat-window" ref={chatWindowRef}>
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.sender}`}>
              <div className="d-flex align-items-start gap-2">
                {msg.sender === 'ai' && (
                  <img src={logo} alt="AI" className="chat-logo" />
                )}
                <span>{msg.text}</span>
                {msg.sender === 'ai' && msg.text && (
                  <div className="d-flex gap-1 align-items-center">
                    <button
                      className="speaker-btn"
                      onClick={() => playText(msg.text, idx)}
                      title="Play"
                    >▶️</button>

                    {speakingMsgIndex === idx && (
                      <>
                        <button
                          className="speaker-btn"
                          onClick={pauseSpeech}
                          title="Pause"
                        >⏸️</button>
                        <button
                          className="speaker-btn"
                          onClick={resumeSpeech}
                          title="Resume"
                          disabled={!isPaused}
                        >🔁</button>
                        <button
                          className="speaker-btn"
                          onClick={stopSpeech}
                          title="Stop"
                        >⏹️</button>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {aiTyping && (
            <div className="chat-message ai">
              <div className="typing-indicator">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
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
