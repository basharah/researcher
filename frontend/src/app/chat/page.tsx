"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../components/AuthProvider";
import { apiFetch } from "../../lib/api";

interface Document {
  id: number;
  title: string;
  filename: string;
  upload_date: string;
  doi?: string;
  authors?: string[];
}

interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

interface ChatSource {
  document_id: number;
  text: string;
  section: string;
  similarity: number;
}

interface ChatResponse {
  message: string;
  model_used: string;
  provider_used: string;
  tokens_used?: number;
  processing_time_ms: number;
  sources?: ChatSource[];
}

export default function ChatPage() {
  const router = useRouter();
  const { authed, loading } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocs, setSelectedDocs] = useState<number[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [useRAG, setUseRAG] = useState(true);
  const [llmProvider, setLlmProvider] = useState<"openai" | "anthropic">("openai");
  const [showSources, setShowSources] = useState(false);
  const [currentSources, setCurrentSources] = useState<ChatSource[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!loading && !authed) {
      router.replace("/login");
    }
  }, [authed, loading, router]);

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadDocuments = async () => {
    try {
      const data = await apiFetch("/documents");
      setDocuments(data.documents || []);
    } catch (error) {
      console.error("Failed to load documents:", error);
    }
  };

  const toggleDocument = (docId: number) => {
    setSelectedDocs((prev) =>
      prev.includes(docId)
        ? prev.filter((id) => id !== docId)
        : [...prev, docId]
    );
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: input.trim(),
    };

    // Add user message to chat
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const requestData = {
        messages: [...messages, userMessage],
        document_context: selectedDocs.length > 0 ? selectedDocs : null,
        use_rag: useRAG && selectedDocs.length > 0,
        llm_provider: llmProvider,
      };

      const response: ChatResponse = await apiFetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.message,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Store sources if available
      if (response.sources && response.sources.length > 0) {
        setCurrentSources(response.sources);
      }
    } catch (error: any) {
      console.error("Chat error:", error);
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: `Error: ${error.message || "Failed to get response"}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setCurrentSources([]);
  };

  const exportChat = () => {
    const chatText = messages
      .map((msg) => `${msg.role.toUpperCase()}: ${msg.content}`)
      .join("\n\n");

    const blob = new Blob([chatText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `chat-export-${new Date().toISOString()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatMessageContent = (content: string) => {
    // Basic markdown-like formatting
    const lines = content.split("\n");
    return lines.map((line, idx) => {
      // Headers
      if (line.startsWith("## ")) {
        return (
          <h3 key={idx} className="text-lg font-bold mt-3 mb-2">
            {line.substring(3)}
          </h3>
        );
      }
      if (line.startsWith("# ")) {
        return (
          <h2 key={idx} className="text-xl font-bold mt-4 mb-2">
            {line.substring(2)}
          </h2>
        );
      }

      // Bold text
      const boldRegex = /\*\*(.*?)\*\*/g;
      let processedLine = line;
      const boldMatches = [...line.matchAll(boldRegex)];
      if (boldMatches.length > 0) {
        const parts = [];
        let lastIndex = 0;
        boldMatches.forEach((match, i) => {
          parts.push(processedLine.substring(lastIndex, match.index));
          parts.push(
            <strong key={`bold-${idx}-${i}`}>{match[1]}</strong>
          );
          lastIndex = (match.index || 0) + match[0].length;
        });
        parts.push(processedLine.substring(lastIndex));
        return <p key={idx} className="mb-2">{parts}</p>;
      }

      // Bullet points
      if (line.trim().startsWith("- ") || line.trim().startsWith("• ")) {
        return (
          <li key={idx} className="ml-4 mb-1">
            {line.trim().substring(2)}
          </li>
        );
      }

      // Regular paragraph
      if (line.trim()) {
        return (
          <p key={idx} className="mb-2">
            {line}
          </p>
        );
      }

      // Empty line
      return <div key={idx} className="h-2"></div>;
    });
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl px-6 py-12 text-center">
        <p className="text-zinc-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Interactive Q&A Chat</h1>
        <p className="text-zinc-600">
          Ask questions about your research papers with AI-powered responses
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar - Document Selection & Settings */}
        <div className="lg:col-span-1 space-y-4">
          {/* Document Context */}
          <div className="border rounded-lg p-4 bg-white">
            <h3 className="font-semibold mb-3 flex items-center">
              <svg
                className="w-5 h-5 mr-2 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              Document Context
            </h3>
            <p className="text-xs text-zinc-500 mb-3">
              Select documents to provide context for your questions
            </p>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {documents.length === 0 ? (
                <p className="text-sm text-zinc-400">No documents available</p>
              ) : (
                documents.map((doc) => (
                  <label
                    key={doc.id}
                    className="flex items-start space-x-2 cursor-pointer hover:bg-zinc-50 p-2 rounded"
                  >
                    <input
                      type="checkbox"
                      checked={selectedDocs.includes(doc.id)}
                      onChange={() => toggleDocument(doc.id)}
                      className="mt-1"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {doc.title || doc.filename}
                      </p>
                      <p className="text-xs text-zinc-500">ID: {doc.id}</p>
                    </div>
                  </label>
                ))
              )}
            </div>
            <div className="mt-3 pt-3 border-t text-xs text-zinc-600">
              {selectedDocs.length} document{selectedDocs.length !== 1 && "s"} selected
            </div>
          </div>

          {/* Settings */}
          <div className="border rounded-lg p-4 bg-white">
            <h3 className="font-semibold mb-3">Settings</h3>
            
            {/* RAG Toggle */}
            <label className="flex items-center space-x-2 mb-3 cursor-pointer">
              <input
                type="checkbox"
                checked={useRAG}
                onChange={(e) => setUseRAG(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm">Use RAG (Semantic Search)</span>
            </label>

            {/* LLM Provider */}
            <div className="mb-3">
              <label className="block text-sm font-medium mb-1">
                LLM Provider
              </label>
              <select
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value as "openai" | "anthropic")}
                className="w-full border rounded px-3 py-2 text-sm"
              >
                <option value="openai">OpenAI (GPT-4)</option>
                <option value="anthropic">Anthropic (Claude)</option>
              </select>
            </div>

            {/* Show Sources Toggle */}
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showSources}
                onChange={(e) => setShowSources(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm">Show Sources</span>
            </label>
          </div>

          {/* Actions */}
          <div className="border rounded-lg p-4 bg-white space-y-2">
            <button
              onClick={clearChat}
              className="w-full px-4 py-2 text-sm border rounded hover:bg-zinc-50 transition-colors"
              disabled={messages.length === 0}
            >
              Clear Chat
            </button>
            <button
              onClick={exportChat}
              className="w-full px-4 py-2 text-sm border rounded hover:bg-zinc-50 transition-colors"
              disabled={messages.length === 0}
            >
              Export Chat
            </button>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="lg:col-span-3 flex flex-col" style={{ height: "calc(100vh - 200px)" }}>
          {/* Messages Container */}
          <div className="flex-1 border rounded-lg bg-white overflow-y-auto p-4 mb-4">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center text-center">
                <div>
                  <svg
                    className="w-16 h-16 mx-auto mb-4 text-zinc-300"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                  <h3 className="text-lg font-semibold mb-2">Start a Conversation</h3>
                  <p className="text-zinc-500 text-sm max-w-md mx-auto">
                    Select documents from the sidebar and ask questions about your research papers.
                    The AI will provide detailed answers with context.
                  </p>
                  <div className="mt-6 space-y-2 text-left max-w-md mx-auto">
                    <p className="text-sm text-zinc-600">
                      <strong>Example questions:</strong>
                    </p>
                    <ul className="text-sm text-zinc-500 space-y-1">
                      <li>• What is the main contribution of this paper?</li>
                      <li>• Explain the methodology used in the experiments</li>
                      <li>• What are the key findings and limitations?</li>
                      <li>• How does this compare to previous work?</li>
                    </ul>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${
                      msg.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg px-4 py-3 ${
                        msg.role === "user"
                          ? "bg-blue-600 text-white"
                          : "bg-zinc-100 text-zinc-900"
                      }`}
                    >
                      <div className="flex items-center mb-1">
                        {msg.role === "user" ? (
                          <svg
                            className="w-4 h-4 mr-2"
                            fill="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                          </svg>
                        ) : (
                          <svg
                            className="w-4 h-4 mr-2"
                            fill="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" />
                          </svg>
                        )}
                        <span className="text-xs font-semibold opacity-75">
                          {msg.role === "user" ? "You" : "AI Assistant"}
                        </span>
                      </div>
                      <div className="text-sm whitespace-pre-wrap">
                        {formatMessageContent(msg.content)}
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-zinc-100 rounded-lg px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                        <div className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                        <div className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Sources Display */}
          {showSources && currentSources.length > 0 && (
            <div className="mb-4 p-4 border rounded-lg bg-yellow-50">
              <h4 className="font-semibold text-sm mb-2">Sources Used:</h4>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {currentSources.map((source, idx) => (
                  <div key={idx} className="text-xs bg-white p-2 rounded border">
                    <div className="flex justify-between mb-1">
                      <span className="font-medium">Doc ID: {source.document_id}</span>
                      <span className="text-zinc-500">
                        Similarity: {(source.similarity * 100).toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-zinc-600 line-clamp-2">{source.text}</p>
                    {source.section && (
                      <p className="text-zinc-500 mt-1">Section: {source.section}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="border rounded-lg bg-white p-4">
            <div className="flex space-x-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about your documents..."
                className="flex-1 border rounded-lg px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-zinc-300 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? (
                  <svg
                    className="w-5 h-5 animate-spin"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                ) : (
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                  </svg>
                )}
              </button>
            </div>
            <div className="mt-2 text-xs text-zinc-500 flex justify-between">
              <span>Press Enter to send, Shift+Enter for new line</span>
              {selectedDocs.length > 0 && useRAG && (
                <span className="text-green-600 font-medium">
                  ✓ RAG enabled with {selectedDocs.length} document{selectedDocs.length !== 1 && "s"}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
