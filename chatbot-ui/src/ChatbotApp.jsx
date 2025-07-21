import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { FaTrash } from 'react-icons/fa';

function ChatbotApp() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [sessionName, setSessionName] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (currentSession) {
      setMessages([{ sender: 'bot', text: 'New conversation started.' }]);
    }
  }, [currentSession]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchSessions = async () => {
    try {
      const res = await fetch('http://127.0.0.1:9999/sessions');
      const data = await res.json();
      setSessions(data.sessions || []);
    } catch {
      setSessions([]);
    }
  };

  const startSession = async (e) => {
    e.preventDefault();
    if (!sessionName.trim()) return;
    try {
      const res = await fetch('http://127.0.0.1:9999/new_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_name: sessionName })
      });
      const data = await res.json();
      setCurrentSession(data.session_id);
      setMessages([{ sender: 'bot', text: `Session "${sessionName}" started.` }]);
      setSessionName('');
      fetchSessions();
    } catch {
      alert('Failed to start new session');
    }
  };

  const selectSession = async (sid) => {
    setCurrentSession(sid);
    try {
      const res = await fetch(`http://127.0.0.1:9999/session_history?session_id=${sid}`);
      const data = await res.json();
      if (Array.isArray(data.history) && data.history.length > 0) {
        setMessages(data.history);
      } else {
        setMessages([{ sender: 'bot', text: 'No previous messages in this session.' }]);
      }
    } catch {
      setMessages([{ sender: 'bot', text: 'Error loading previous session.' }]);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !currentSession) return;
    setMessages((msgs) => [...msgs, { sender: 'user', text: input }]);
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:9999/ChatHome', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, session_id: currentSession })
      });
      const data = await response.json();
      setMessages((msgs) => [...msgs, { sender: 'bot', text: data.reply || 'No response' }]);
    } catch {
      setMessages((msgs) => [...msgs, { sender: 'bot', text: 'Error connecting to server.' }]);
    }
    setInput('');
    setLoading(false);
  };

  const deleteSession = async (sid) => {
    if (!window.confirm(`Delete session "${sid}"? This cannot be undone.`)) return;
    try {
      await fetch('http://127.0.0.1:9999/delete_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sid })
      });
      if (sid === currentSession) {
        setCurrentSession(null);
        setMessages([]);
      }
      fetchSessions();
    } catch {
      alert('Failed to delete session');
    }
  };

  return (
    <div className="app-container">
        {/* Sidebar for sessions */}
        <aside className="sidebar">
            <div className="sidebar-header">Chats</div>
            <form onSubmit={startSession} className="session-input-row">
                <input
                    type="text"
                    className="session-input"
                    value={sessionName}
                    onChange={e => setSessionName(e.target.value)}
                    placeholder="New session name"
                    disabled={loading}
                />
                <button type="submit" className="session-start-btn" disabled={loading || !sessionName.trim()}>
                    Start
                </button>
            </form>
            <div className="session-list">
                {sessions.map(sid => (
                    <div key={sid} style={{ display: 'flex', alignItems: 'center' }}>
                        <button
                            className={`session-btn${sid === currentSession ? ' active' : ''}`}
                            onClick={() => selectSession(sid)}
                            disabled={sid === currentSession}
                            style={{ flex: 1 }}
                        >
                            {sid}
                        </button>
                        <button
                            className="delete-session-btn"
                            title="Delete session"
                            onClick={() => deleteSession(sid)}
                            style={{ background: 'none', border: 'none', color: '#c00', cursor: 'pointer', marginLeft: 4 }}
                            disabled={loading}
                        >
                            <FaTrash size={14} />
                        </button>
                    </div>
                ))}
            </div>
        </aside>
        {/* Main chat area */}
        <main className="main">
            <div className="header">ChatBot Assistant</div>
            {messages.length === 0 ? (
                <h3 className="no-messages">Start a conversation by selecting a session or creating a new one.</h3>
            ) : (
                <div className="chat-window">
                {messages.map((msg, idx) => (
                    <div key={idx} className="message-row">
                        <div className={`message-bubble ${msg.sender}`}>{msg.text}</div>
                    </div>
                ))}
                {loading && (
                    <div className="message-row">
                        <div className={`message-bubble bot`}>Loading Response....</div>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>
            )}
            
            <form
                className="input-row"
                onSubmit={e => {
                    sendMessage(e);
                    setInput('');
                }}
            >
                <textarea
                    className="input-box"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    placeholder={currentSession ? "Ask anything" : "Start a conversation first"}
                    disabled={loading || !currentSession}
                    rows={2}
                    onKeyDown={e => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            if (!loading && input.trim() && currentSession) {
                                sendMessage(e);
                                setInput('');
                            }
                        }
                    }}
                />
                <button type="submit" className="send-btn" disabled={loading || !input.trim() || !currentSession}>
                    {loading ? 'Sending...' : 'Send'}
                </button>
            </form>
        </main>
    </div>
);
}

export default ChatbotApp;
