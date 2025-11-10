"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";

interface SearchResult {
  chunk_id: number;
  document_id: number;
  document_title: string;
  section: string;
  text: string;
  similarity_score: number;
  page_number?: number;
}

interface SearchResponse {
  query: string;
  results_count: number;
  search_time_ms: number;
  chunks: SearchResult[];
}

export default function SearchPage() {
  const router = useRouter();
  const { authed, loading: authLoading } = useAuth();
  
  const [query, setQuery] = useState("");
  const [maxResults, setMaxResults] = useState(10);
  const [documentFilter, setDocumentFilter] = useState<number | null>(null);
  const [sectionFilter, setSectionFilter] = useState<string>("");
  
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [documents, setDocuments] = useState<any[]>([]);

  useEffect(() => {
    if (!authLoading && !authed) {
      router.push("/login");
      return;
    }
    
    if (authed) {
      // Fetch available documents for filter dropdown
      fetchDocuments();
    }
  }, [authed, authLoading, router]);

  const fetchDocuments = async () => {
    try {
      const response = await fetch("/api/v1/documents?limit=100", {
        credentials: "include",
      });
      
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      }
    } catch (err) {
      console.error("Failed to fetch documents:", err);
    }
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    
    if (!query.trim()) {
      setError("Please enter a search query");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const requestBody: any = {
        query: query.trim(),
        max_results: maxResults,
      };
      
      if (documentFilter) {
        requestBody.document_id = documentFilter;
      }
      
      if (sectionFilter) {
        requestBody.section = sectionFilter;
      }

      const response = await fetch("/api/v1/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Search failed");
      }

      const data: SearchResponse = await response.json();
      setResults(data);
    } catch (err: any) {
      console.error("Search error:", err);
      setError(err.message || "Failed to perform search");
    } finally {
      setLoading(false);
    }
  };

  const highlightText = (text: string, query: string) => {
    if (!query) return text;
    
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, i) => 
      part.toLowerCase() === query.toLowerCase() ? 
        <mark key={i} className="bg-yellow-200 px-1 rounded">{part}</mark> : 
        part
    );
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 0.8) return "text-green-600";
    if (score >= 0.6) return "text-blue-600";
    if (score >= 0.4) return "text-orange-600";
    return "text-gray-600";
  };

  const getSectionBadgeColor = (section: string) => {
    const colors: { [key: string]: string } = {
      abstract: "bg-purple-100 text-purple-700",
      introduction: "bg-blue-100 text-blue-700",
      methodology: "bg-green-100 text-green-700",
      results: "bg-yellow-100 text-yellow-700",
      conclusion: "bg-red-100 text-red-700",
      references: "bg-gray-100 text-gray-700",
    };
    return colors[section.toLowerCase()] || "bg-gray-100 text-gray-700";
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Search Papers
          </h1>
          <p className="text-gray-600">
            Semantic search across all your research papers using AI-powered embeddings
          </p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <form onSubmit={handleSearch}>
            {/* Search Input */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Query
              </label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., machine learning algorithms for image classification"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              {/* Document Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Filter by Document
                </label>
                <select
                  value={documentFilter || ""}
                  onChange={(e) => setDocumentFilter(e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Documents</option>
                  {documents.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      {doc.title || doc.filename}
                    </option>
                  ))}
                </select>
              </div>

              {/* Section Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Filter by Section
                </label>
                <select
                  value={sectionFilter}
                  onChange={(e) => setSectionFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Sections</option>
                  <option value="abstract">Abstract</option>
                  <option value="introduction">Introduction</option>
                  <option value="methodology">Methodology</option>
                  <option value="results">Results</option>
                  <option value="conclusion">Conclusion</option>
                </select>
              </div>

              {/* Max Results */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Results
                </label>
                <select
                  value={maxResults}
                  onChange={(e) => setMaxResults(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="5">5</option>
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                </select>
              </div>
            </div>

            {/* Search Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Searching...
                </span>
              ) : (
                "Search"
              )}
            </button>
          </form>

          {/* Error Display */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Search Results */}
        {results && (
          <div className="bg-white rounded-lg shadow-md p-6">
            {/* Results Header */}
            <div className="mb-6 pb-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    Search Results
                  </h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Found {results.results_count} results in {results.search_time_ms.toFixed(2)}ms
                  </p>
                </div>
                <div className="text-sm text-gray-500">
                  Query: <span className="font-medium">&quot;{results.query}&quot;</span>
                </div>
              </div>
            </div>

            {/* Results List */}
            {results.chunks.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No results found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try adjusting your search query or filters
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {results.chunks.map((result, index) => (
                  <div
                    key={result.chunk_id}
                    className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all"
                  >
                    {/* Result Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium text-gray-900">
                            #{index + 1}
                          </span>
                          <h3 className="text-lg font-semibold text-blue-600 hover:text-blue-700 cursor-pointer">
                            {result.document_title}
                          </h3>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSectionBadgeColor(result.section)}`}>
                            {result.section}
                          </span>
                          {result.page_number && (
                            <span className="text-xs text-gray-500">
                              Page {result.page_number}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${getSimilarityColor(result.similarity_score)}`}>
                          {(result.similarity_score * 100).toFixed(1)}%
                        </div>
                        <div className="text-xs text-gray-500">similarity</div>
                      </div>
                    </div>

                    {/* Result Text */}
                    <p className="text-gray-700 leading-relaxed">
                      {highlightText(result.text, query)}
                    </p>

                    {/* Actions */}
                    <div className="mt-3 pt-3 border-t border-gray-100 flex gap-2">
                      <button
                        onClick={() => router.push(`/documents/${result.document_id}`)}
                        className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                      >
                        View Document →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Help Section */}
        {!results && !loading && (
          <div className="bg-blue-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">
              Search Tips
            </h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Use natural language queries like &quot;What are the main findings about neural networks?&quot;</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Filter by specific documents or sections to narrow results</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Semantic search understands meaning, not just keywords</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Higher similarity scores indicate more relevant results</span>
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
