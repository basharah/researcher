import React, { useState, useRef, useEffect } from 'react';
import type { Document } from '../services/documents.service';
import documentsService from '../services/documents.service';

interface ChatInterfaceProps {
  document: Document;
  onBack: () => void;
}

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ document, onBack }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Welcome message
    addMessage('system', `Document loaded: ${document.title || document.filename}. Ask me anything about this paper!`);
  }, [document]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessage = (type: Message['type'], content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    addMessage('user', userMessage);
    setLoading(true);

    try {
      const response = await documentsService.askQuestion(document.id, userMessage);
      addMessage('assistant', response.answer);
    } catch (error: any) {
      addMessage('system', `Error: ${error.response?.data?.detail || 'Failed to get response'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAnalysis = async (analysisType: 'summary' | 'methodology' | 'findings' | 'gaps') => {
    setSelectedAnalysis(analysisType);
    setLoading(true);
    
    const prompts = {
      summary: 'Provide a comprehensive summary of this paper',
      methodology: 'Explain the methodology used in this research',
      findings: 'What are the key findings and contributions?',
      gaps: 'What research gaps or limitations are identified?',
    };

    addMessage('user', prompts[analysisType]);

    try {
      const response = await documentsService.analyzeDocument(document.id, analysisType);
      addMessage('assistant', response.result);
    } catch (error: any) {
      addMessage('system', `Error: ${error.response?.data?.detail || 'Analysis failed'}`);
    } finally {
      setLoading(false);
      setSelectedAnalysis('');
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-16rem)]">
      {/* Header */}
      <div className="card mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={onBack}
              className="btn-secondary"
            >
              ← Back
            </button>
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {document.title || document.filename}
              </h2>
              {document.authors && (
                <p className="text-sm text-gray-600">{document.authors}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Analysis Buttons */}
      <div className="card mb-4">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Analysis</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => handleQuickAnalysis('summary')}
            disabled={loading}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedAnalysis === 'summary'
                ? 'bg-primary-600 text-white'
                : 'bg-primary-50 text-primary-700 hover:bg-primary-100'
            }`}
          >
            Summary
          </button>
          <button
            onClick={() => handleQuickAnalysis('methodology')}
            disabled={loading}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedAnalysis === 'methodology'
                ? 'bg-primary-600 text-white'
                : 'bg-primary-50 text-primary-700 hover:bg-primary-100'
            }`}
          >
            Methodology
          </button>
          <button
            onClick={() => handleQuickAnalysis('findings')}
            disabled={loading}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedAnalysis === 'findings'
                ? 'bg-primary-600 text-white'
                : 'bg-primary-50 text-primary-700 hover:bg-primary-100'
            }`}
          >
            Key Findings
          </button>
          <button
            onClick={() => handleQuickAnalysis('gaps')}
            disabled={loading}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedAnalysis === 'gaps'
                ? 'bg-primary-600 text-white'
                : 'bg-primary-50 text-primary-700 hover:bg-primary-100'
            }`}
          >
            Research Gaps
          </button>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 card overflow-y-auto mb-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.type === 'user'
                    ? 'bg-primary-600 text-white'
                    : message.type === 'assistant'
                    ? 'bg-gray-100 text-gray-900'
                    : 'bg-yellow-50 text-yellow-900 border border-yellow-200'
                }`}
              >
                <div className="whitespace-pre-wrap break-words">{message.content}</div>
                <div
                  className={`text-xs mt-1 ${
                    message.type === 'user'
                      ? 'text-primary-100'
                      : 'text-gray-500'
                  }`}
                >
                  {formatTime(message.timestamp)}
                </div>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="card">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask a question about this paper..."
            className="input-field flex-1"
            disabled={loading}
          />
          <button
            onClick={handleSendMessage}
            disabled={loading || !input.trim()}
            className="btn-primary"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
