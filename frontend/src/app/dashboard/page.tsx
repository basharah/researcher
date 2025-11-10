"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "../../components/AuthProvider";

export default function DashboardPage() {
  const router = useRouter();
  const { authed, loading } = useAuth();

  useEffect(() => {
    if (!loading && !authed) {
      // Not authenticated - redirect to login
      router.replace("/login");
    }
  }, [authed, loading, router]);

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-12 text-center">
        <p className="text-zinc-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="text-3xl font-bold mb-2">Research Paper Analysis</h1>
      <p className="text-zinc-600 mb-8">
        Upload, analyze, and search through your research papers
      </p>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {/* Single Upload */}
        <Link
          href="/upload"
          className="block p-6 border rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
        >
          <div className="flex items-center mb-3">
            <svg className="w-8 h-8 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <h2 className="text-xl font-semibold">Upload Paper</h2>
          </div>
          <p className="text-sm text-zinc-600">
            Upload a single PDF research paper for analysis
          </p>
        </Link>

        {/* Batch Upload */}
        <Link
          href="/batch-upload"
          className="block p-6 border rounded-lg hover:border-green-500 hover:shadow-md transition-all"
        >
          <div className="flex items-center mb-3">
            <svg className="w-8 h-8 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h2 className="text-xl font-semibold">Batch Upload</h2>
          </div>
          <p className="text-sm text-zinc-600">
            Upload multiple papers at once with progress tracking
          </p>
        </Link>

        {/* Processing Jobs */}
        <Link
          href="/jobs"
          className="block p-6 border rounded-lg hover:border-purple-500 hover:shadow-md transition-all"
        >
          <div className="flex items-center mb-3">
            <svg className="w-8 h-8 text-purple-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            <h2 className="text-xl font-semibold">Processing Jobs</h2>
          </div>
          <p className="text-sm text-zinc-600">
            Monitor document processing status and history
          </p>
        </Link>

        {/* Search */}
        <Link
          href="/search"
          className="block p-6 border rounded-lg hover:border-orange-500 hover:shadow-md transition-all"
        >
          <div className="flex items-center mb-3">
            <svg className="w-8 h-8 text-orange-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h2 className="text-xl font-semibold">Search Papers</h2>
          </div>
          <p className="text-sm text-zinc-600">
            Semantic search across all uploaded documents
          </p>
        </Link>

        {/* Analysis */}
        <Link
          href="/analysis"
          className="block p-6 border rounded-lg hover:border-red-500 hover:shadow-md transition-all"
        >
          <div className="flex items-center mb-3">
            <svg className="w-8 h-8 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h2 className="text-xl font-semibold">AI Analysis</h2>
          </div>
          <p className="text-sm text-zinc-600">
            Get AI-powered insights and summaries
          </p>
        </Link>

        {/* Profile */}
        <Link
          href="/profile"
          className="block p-6 border rounded-lg hover:border-zinc-500 hover:shadow-md transition-all"
        >
          <div className="flex items-center mb-3">
            <svg className="w-8 h-8 text-zinc-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <h2 className="text-xl font-semibold">Profile</h2>
          </div>
          <p className="text-sm text-zinc-600">
            View and manage your account settings
          </p>
        </Link>
      </div>

      {/* Features Section */}
      <section className="mt-12 rounded-lg border bg-gradient-to-r from-blue-50 to-indigo-50 p-8">
        <h2 className="text-2xl font-bold mb-4">Platform Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-lg mb-2 flex items-center">
              <span className="text-blue-600 mr-2">✓</span>
              Advanced Processing
            </h3>
            <ul className="text-sm text-zinc-700 space-y-1 ml-6">
              <li>• Automatic DOI extraction and validation</li>
              <li>• OCR support for scanned PDFs</li>
              <li>• Table and figure extraction</li>
              <li>• Reference parsing</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-lg mb-2 flex items-center">
              <span className="text-green-600 mr-2">✓</span>
              Smart Search & Analysis
            </h3>
            <ul className="text-sm text-zinc-700 space-y-1 ml-6">
              <li>• Semantic search with vector embeddings</li>
              <li>• AI-powered summaries and insights</li>
              <li>• Document comparison</li>
              <li>• Interactive Q&A chat</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}
