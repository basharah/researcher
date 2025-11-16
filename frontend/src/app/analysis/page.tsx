"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { apiFetch } from "@/lib/api";

interface Document {
  id: number;
  filename: string;
  title?: string;
  upload_date: string;
}

interface AnalysisResult {
  document_id?: number;
  analysis_type: string;
  result: string;
  model_used?: string;
  provider_used?: string;
  tokens_used?: number;
  processing_time_ms?: number;
  sources_used?: any[];
}

export default function AnalysisPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { authed, loading: authLoading } = useAuth();
  
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(null);
  const [analysisType, setAnalysisType] = useState("summary");
  const [customPrompt, setCustomPrompt] = useState("");
  const [useRAG, setUseRAG] = useState(true);
  const [llmProvider, setLlmProvider] = useState("openai");
  
  const [loading, setLoading] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    if (!authLoading && !authed) {
      router.push("/login");
      return;
    }
    
    if (authed) {
      fetchDocuments();
    }
  }, [authed, authLoading, router]);

  const fetchDocuments = async () => {
    setLoadingDocs(true);
    try {
      const data = await apiFetch("/documents?limit=100");
      const docs = data?.documents || [];
      setDocuments(docs);
      
      // Auto-select document from URL parameter
      const docIdParam = searchParams.get('document_id');
      if (docIdParam) {
        const docId = parseInt(docIdParam, 10);
        if (!isNaN(docId) && docs.some((d: Document) => d.id === docId)) {
          setSelectedDocumentId(docId);
        }
      }
    } catch (err) {
      console.error("Failed to fetch documents:", err);
      setError("Failed to load documents");
    } finally {
      setLoadingDocs(false);
    }
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedDocumentId) {
      setError("Please select a document");
      return;
    }

    if (analysisType === "custom" && !customPrompt.trim()) {
      setError("Please enter a custom prompt");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const requestBody: any = {
        document_id: selectedDocumentId,
        analysis_type: analysisType,
        use_rag: useRAG,
        llm_provider: llmProvider,
      };
      
      if (analysisType === "custom" && customPrompt.trim()) {
        requestBody.custom_prompt = customPrompt.trim();
      }

      const data: AnalysisResult = await apiFetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      setResult(data as AnalysisResult);
    } catch (err: any) {
      console.error("Analysis error:", err);
      setError(err.message || "Failed to perform analysis");
    } finally {
      setLoading(false);
    }
  };

  const analysisTypes = [
    { value: "summary", label: "Summary", description: "Comprehensive overview of the paper" },
    { value: "key_findings", label: "Key Findings", description: "Main discoveries and results" },
    { value: "methodology", label: "Methodology", description: "Research methods and approach" },
    { value: "literature_review", label: "Literature Review", description: "Related work analysis" },
    { value: "results_analysis", label: "Results Analysis", description: "Deep dive into results" },
    { value: "limitations", label: "Limitations", description: "Study limitations and constraints" },
    { value: "future_work", label: "Future Work", description: "Potential next steps" },
    { value: "custom", label: "Custom Analysis", description: "Your own analysis prompt" },
  ];

  const formatAnalysisText = (text?: string) => {
    // Simple markdown-like formatting
    const safe = typeof text === "string" ? text : "";
    return safe.split('\n').map((line, i) => {
      // Headers (lines starting with #)
      if (line.startsWith('###')) {
        return <h4 key={i} className="text-md font-semibold mt-4 mb-2 text-gray-800">{line.replace('###', '').trim()}</h4>;
      }
      if (line.startsWith('##')) {
        return <h3 key={i} className="text-lg font-semibold mt-4 mb-2 text-gray-900">{line.replace('##', '').trim()}</h3>;
      }
      if (line.startsWith('#')) {
        return <h2 key={i} className="text-xl font-bold mt-6 mb-3 text-gray-900">{line.replace('#', '').trim()}</h2>;
      }
      
      // Bold text (**text**)
      if (line.includes('**')) {
        const parts = line.split(/(\*\*.*?\*\*)/g);
        return (
          <p key={i} className="mb-2 leading-relaxed text-gray-700">
            {parts.map((part, j) => 
              part.startsWith('**') && part.endsWith('**') ? 
                <strong key={j}>{part.slice(2, -2)}</strong> : 
                part
            )}
          </p>
        );
      }
      
      // Bullet points
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        return <li key={i} className="ml-6 mb-1 text-gray-700">{line.replace(/^[\-\*]\s/, '')}</li>;
      }
      
      // Empty lines
      if (!line.trim()) {
        return <br key={i} />;
      }
      
      // Regular paragraphs
      return <p key={i} className="mb-2 leading-relaxed text-gray-700">{line}</p>;
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Analysis
          </h1>
          <p className="text-gray-600">
            Analyze your research papers using advanced AI models
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Analysis Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-6">
              <h2 className="text-xl font-semibold mb-4">Analysis Settings</h2>
              
              <form onSubmit={handleAnalyze} className="space-y-4">
                {/* Document Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Document *
                  </label>
                  {loadingDocs ? (
                    <div className="text-sm text-gray-500">Loading documents...</div>
                  ) : documents.length === 0 ? (
                    <div className="text-sm text-gray-500">
                      No documents found. <a href="/upload" className="text-blue-600 hover:underline">Upload one</a>
                    </div>
                  ) : (
                    <select
                      value={selectedDocumentId || ""}
                      onChange={(e) => setSelectedDocumentId(e.target.value ? parseInt(e.target.value) : null)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    >
                      <option value="">Choose a document...</option>
                      {documents.map((doc) => (
                        <option key={doc.id} value={doc.id}>
                          {doc.title || doc.filename}
                        </option>
                      ))}
                    </select>
                  )}
                </div>

                {/* Analysis Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Analysis Type *
                  </label>
                  <select
                    value={analysisType}
                    onChange={(e) => setAnalysisType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {analysisTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-xs text-gray-500">
                    {analysisTypes.find(t => t.value === analysisType)?.description}
                  </p>
                </div>

                {/* Custom Prompt (only for custom type) */}
                {analysisType === "custom" && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Custom Prompt *
                    </label>
                    <textarea
                      value={customPrompt}
                      onChange={(e) => setCustomPrompt(e.target.value)}
                      placeholder="e.g., What are the ethical implications discussed in this paper?"
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                )}

                {/* LLM Provider */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    LLM Provider
                  </label>
                  <select
                    value={llmProvider}
                    onChange={(e) => setLlmProvider(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="openai">OpenAI (GPT-4)</option>
                    <option value="anthropic">Anthropic (Claude)</option>
                  </select>
                </div>

                {/* Use RAG Toggle */}
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="use-rag"
                    checked={useRAG}
                    onChange={(e) => setUseRAG(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="use-rag" className="ml-2 block text-sm text-gray-700">
                    Use RAG (Retrieval Augmented Generation)
                  </label>
                </div>
                <p className="text-xs text-gray-500 -mt-2">
                  Recommended: Uses semantic search for more accurate analysis
                </p>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading || loadingDocs}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing...
                    </span>
                  ) : (
                    "Analyze Document"
                  )}
                </button>
              </form>

              {/* Error Display */}
              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2">
            {result ? (
              <div className="bg-white rounded-lg shadow-md p-6">
                {/* Results Header */}
                <div className="mb-6 pb-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-gray-900">
                      {analysisTypes.find(t => t.value === result.analysis_type)?.label || "Analysis Results"}
                    </h2>
                    {result.processing_time_ms && (
                      <span className="text-sm text-gray-500">
                        {(result.processing_time_ms / 1000).toFixed(2)}s
                      </span>
                    )}
                  </div>
                  {result.model_used && (
                    <p className="text-sm text-gray-600 mt-1">
                      Model: {result.model_used}
                    </p>
                  )}
                </div>

                {/* Analysis Content */}
                <div className="prose max-w-none">
                  {formatAnalysisText(result.result)}
                </div>

                {/* Actions */}
                <div className="mt-6 pt-4 border-t border-gray-200 flex gap-3">
                  <button
                    onClick={() => {
                      const blob = new Blob([result.result || ""], { type: 'text/plain' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `analysis-${result.analysis_type}-${new Date().toISOString()}.txt`;
                      a.click();
                    }}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium text-sm"
                  >
                    Download as Text
                  </button>
                  <button
                    onClick={() => navigator.clipboard.writeText(result.result || "")}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium text-sm"
                  >
                    Copy to Clipboard
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Analysis Yet
                </h3>
                <p className="text-gray-600">
                  Select a document and analysis type to get started
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Info Section */}
        {!result && (
          <div className="mt-8 bg-blue-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">
              Analysis Types Explained
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
              {analysisTypes.filter(t => t.value !== 'custom').map((type) => (
                <div key={type.value} className="flex items-start">
                  <span className="mr-2 font-semibold">•</span>
                  <div>
                    <strong>{type.label}:</strong> {type.description}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
