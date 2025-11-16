"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../components/AuthProvider";
import api from "../../lib/api";

interface Stats {
  total_documents: number;
  total_chunks: number;
  recent_documents: Array<{
    id: number;
    title: string;
    upload_date: string;
    page_count: number;
  }>;
}

export default function DashboardPage() {
  const router = useRouter();
  const { authed, loading } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    if (!loading && !authed) {
      router.replace("/login");
    }
  }, [authed, loading, router]);

  useEffect(() => {
    if (authed) {
      // Fetch dashboard statistics
      Promise.all([
        api.apiFetch("/documents").catch(() => ({ documents: [] })),
        api.apiFetch("/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: "", max_results: 1 }),
        }).catch(() => ({ results_count: 0 })),
      ])
        .then(([docsResponse, searchResponse]) => {
          const documents = docsResponse.documents || [];
          setStats({
            total_documents: documents.length,
            total_chunks: searchResponse.results_count || 0,
            recent_documents: documents
              .sort((a: any, b: any) => 
                new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime()
              )
              .slice(0, 5),
          });
        })
        .finally(() => setLoadingStats(false));
    }
  }, [authed]);

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-12 text-center">
        <p className="text-zinc-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
      <p className="text-zinc-600 mb-8">
        Overview of your research paper collection
      </p>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="p-6 border rounded-lg bg-gradient-to-br from-blue-50 to-white">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-zinc-600">Total Papers</h3>
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          {loadingStats ? (
            <p className="text-2xl font-bold text-zinc-400">...</p>
          ) : (
            <p className="text-3xl font-bold text-blue-600">{stats?.total_documents || 0}</p>
          )}
        </div>

        <div className="p-6 border rounded-lg bg-gradient-to-br from-green-50 to-white">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-zinc-600">Total Pages</h3>
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          </div>
          {loadingStats ? (
            <p className="text-2xl font-bold text-zinc-400">...</p>
          ) : (
            <p className="text-3xl font-bold text-green-600">
              {stats?.recent_documents.reduce((sum, doc) => sum + (doc.page_count || 0), 0) || 0}
            </p>
          )}
        </div>

        <div className="p-6 border rounded-lg bg-gradient-to-br from-purple-50 to-white">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-zinc-600">Text Chunks</h3>
            <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </div>
          {loadingStats ? (
            <p className="text-2xl font-bold text-zinc-400">...</p>
          ) : (
            <p className="text-3xl font-bold text-purple-600">{stats?.total_chunks || 0}</p>
          )}
        </div>
      </div>

      {/* Recent Papers */}
      <div className="border rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Recent Papers</h2>
        {loadingStats ? (
          <p className="text-zinc-600">Loading recent papers...</p>
        ) : stats?.recent_documents && stats.recent_documents.length > 0 ? (
          <div className="space-y-3">
            {stats.recent_documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-start justify-between p-4 border rounded hover:border-blue-500 hover:shadow-sm transition-all"
              >
                <div className="flex-1">
                  <h3 className="font-medium text-zinc-900 mb-1">
                    {doc.title || `Document ${doc.id}`}
                  </h3>
                  <div className="flex items-center gap-4 text-sm text-zinc-500">
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {new Date(doc.upload_date).toLocaleDateString()}
                    </span>
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                      {doc.page_count || 0} pages
                    </span>
                  </div>
                </div>
                <div className="ml-4 flex gap-2">
                  <button
                    onClick={() => router.push(`/analysis?document_id=${doc.id}`)}
                    className="px-3 py-1 text-blue-600 hover:bg-blue-50 rounded text-sm font-medium transition-colors"
                    title="Analyze this paper"
                  >
                    Analyze
                  </button>
                  <button
                    onClick={() => router.push(`/chat?document_id=${doc.id}`)}
                    className="px-3 py-1 text-green-600 hover:bg-green-50 rounded text-sm font-medium transition-colors"
                    title="Chat about this paper"
                  >
                    Chat
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <svg className="w-16 h-16 mx-auto text-zinc-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-zinc-600 mb-4">No papers uploaded yet</p>
            <button
              onClick={() => router.push("/upload")}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Upload Your First Paper
            </button>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <button
          onClick={() => router.push("/upload")}
          className="p-4 border rounded-lg hover:border-blue-500 hover:shadow-sm transition-all text-center"
        >
          <div className="text-2xl mb-2">📤</div>
          <div className="text-sm font-medium">Upload Paper</div>
        </button>
        <button
          onClick={() => router.push("/search")}
          className="p-4 border rounded-lg hover:border-blue-500 hover:shadow-sm transition-all text-center"
        >
          <div className="text-2xl mb-2">🔍</div>
          <div className="text-sm font-medium">Search</div>
        </button>
        <button
          onClick={() => router.push("/chat")}
          className="p-4 border rounded-lg hover:border-blue-500 hover:shadow-sm transition-all text-center"
        >
          <div className="text-2xl mb-2">💬</div>
          <div className="text-sm font-medium">Ask AI</div>
        </button>
        <button
          onClick={() => router.push("/compare")}
          className="p-4 border rounded-lg hover:border-blue-500 hover:shadow-sm transition-all text-center"
        >
          <div className="text-2xl mb-2">⚖️</div>
          <div className="text-sm font-medium">Compare</div>
        </button>
      </div>
    </div>
  );
}
