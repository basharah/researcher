"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { apiFetch } from "@/lib/api";

interface Document {
  id: number;
  filename: string;
  title?: string;
  upload_date: string;
}

interface ComparisonResult {
  document_ids: number[];
  comparison: string;
  model_used: string;
  provider_used: string;
  tokens_used?: number;
  processing_time_ms: number;
}

export default function ComparePage() {
  const router = useRouter();
  const { authed, loading: authLoading } = useAuth();
  
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocuments, setSelectedDocuments] = useState<number[]>([]);
  const [customAspects, setCustomAspects] = useState("");
  const [llmProvider, setLlmProvider] = useState("openai");
  
  const [loading, setLoading] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ComparisonResult | null>(null);

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
      setDocuments(data?.documents || []);
    } catch (err) {
      console.error("Failed to fetch documents:", err);
      setError("Failed to load documents");
    } finally {
      setLoadingDocs(false);
    }
  };

  const toggleDocument = (docId: number) => {
    setSelectedDocuments(prev => 
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (selectedDocuments.length < 2) {
      setError("Please select at least 2 documents to compare");
      return;
    }

    if (selectedDocuments.length > 5) {
      setError("Please select no more than 5 documents to compare");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const requestBody: any = {
        document_ids: selectedDocuments,
        llm_provider: llmProvider,
      };
      
      if (customAspects.trim()) {
        requestBody.comparison_aspects = customAspects
          .split(",")
          .map(a => a.trim())
          .filter(a => a.length > 0);
      }

      const data: ComparisonResult = await apiFetch("/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      setResult(data);
    } catch (err: any) {
      console.error("Comparison error:", err);
      setError(err.message || "Failed to perform comparison");
    } finally {
      setLoading(false);
    }
  };

  const formatComparisonText = (text?: string) => {
    const safe = typeof text === "string" ? text : "";
    return safe.split('\n').map((line, i) => {
      // Headers
      if (line.startsWith('###')) {
        return <h4 key={i} className="text-md font-semibold mt-4 mb-2 text-gray-800">{line.replace('###', '').trim()}</h4>;
      }
      if (line.startsWith('##')) {
        return <h3 key={i} className="text-lg font-semibold mt-4 mb-2 text-gray-900">{line.replace('##', '').trim()}</h3>;
      }
      if (line.startsWith('#')) {
        return <h2 key={i} className="text-xl font-bold mt-6 mb-3 text-gray-900">{line.replace('#', '').trim()}</h2>;
      }
      
      // Bold text
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

  const selectedDocs = documents.filter(d => selectedDocuments.includes(d.id));

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Compare Documents
          </h1>
          <p className="text-gray-600">
            Select 2-5 research papers to generate a comparative analysis using AI
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Selection & Settings */}
          <div className="lg:col-span-1 space-y-6">
            {/* Document Selection */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Select Documents</h2>
              
              {loadingDocs ? (
                <div className="text-sm text-gray-500">Loading documents...</div>
              ) : documents.length === 0 ? (
                <div className="text-sm text-gray-500">
                  No documents found. <a href="/upload" className="text-blue-600 hover:underline">Upload some</a>
                </div>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {documents.map((doc) => (
                    <label
                      key={doc.id}
                      className={`flex items-start p-3 rounded-lg border-2 cursor-pointer transition-colors ${
                        selectedDocuments.includes(doc.id)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedDocuments.includes(doc.id)}
                        onChange={() => toggleDocument(doc.id)}
                        className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <div className="ml-3 flex-1">
                        <div className="text-sm font-medium text-gray-900">
                          {doc.title || doc.filename}
                        </div>
                        <div className="text-xs text-gray-500">
                          ID: {doc.id}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              )}
              
              <div className="mt-4 text-sm text-gray-600">
                Selected: {selectedDocuments.length} document{selectedDocuments.length !== 1 ? 's' : ''}
                {selectedDocuments.length > 0 && selectedDocuments.length < 2 && (
                  <span className="text-orange-600"> (need at least 2)</span>
                )}
                {selectedDocuments.length > 5 && (
                  <span className="text-red-600"> (max 5)</span>
                )}
              </div>
            </div>

            {/* Comparison Settings */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Settings</h2>
              
              <form onSubmit={handleCompare} className="space-y-4">
                {/* Custom Aspects */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Focus Areas (optional)
                  </label>
                  <textarea
                    value={customAspects}
                    onChange={(e) => setCustomAspects(e.target.value)}
                    placeholder="e.g., methodology, results, limitations (comma-separated)"
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Leave blank for general comparison
                  </p>
                </div>

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

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading || loadingDocs || selectedDocuments.length < 2 || selectedDocuments.length > 5}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Comparing...
                    </span>
                  ) : (
                    "Compare Documents"
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
                      Comparative Analysis
                    </h2>
                    {result.processing_time_ms && (
                      <span className="text-sm text-gray-500">
                        {(result.processing_time_ms / 1000).toFixed(2)}s
                      </span>
                    )}
                  </div>
                  <div className="mt-2">
                    <p className="text-sm text-gray-600">
                      Model: {result.model_used} ({result.provider_used})
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      Comparing {selectedDocs.length} documents:
                    </p>
                    <ul className="mt-2 space-y-1">
                      {selectedDocs.map((doc) => (
                        <li key={doc.id} className="text-sm text-gray-700 ml-4">
                          • {doc.title || doc.filename}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Comparison Content */}
                <div className="prose max-w-none">
                  {formatComparisonText(result.comparison)}
                </div>

                {/* Actions */}
                <div className="mt-6 pt-4 border-t border-gray-200 flex gap-3">
                  <button
                    onClick={() => {
                      const blob = new Blob([result.comparison || ""], { type: 'text/plain' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `comparison-${selectedDocuments.join('-')}-${new Date().toISOString()}.txt`;
                      a.click();
                    }}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium text-sm"
                  >
                    Download as Text
                  </button>
                  <button
                    onClick={() => navigator.clipboard.writeText(result.comparison || "")}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium text-sm"
                  >
                    Copy to Clipboard
                  </button>
                  <button
                    onClick={() => {
                      setResult(null);
                      setError(null);
                    }}
                    className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 font-medium text-sm ml-auto"
                  >
                    New Comparison
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Comparison Yet
                </h3>
                <p className="text-gray-600 mb-4">
                  Select 2-5 documents and click "Compare Documents" to get started
                </p>
                
                <div className="mt-6 bg-blue-50 rounded-lg p-4 text-left">
                  <h4 className="text-sm font-semibold text-blue-900 mb-2">
                    What gets compared?
                  </h4>
                  <ul className="space-y-1 text-sm text-blue-800">
                    <li className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>Research objectives and questions</span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>Methodological approaches</span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>Key findings and results</span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>Similarities and differences</span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>Complementary or contradictory conclusions</span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>Relative strengths and limitations</span>
                    </li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
