import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import documentsService from '../services/documents.service';
import type { Document } from '../services/documents.service';
import DocumentUpload from '../components/DocumentUpload';
import DocumentList from '../components/DocumentList';
import ChatInterface from '../components/ChatInterface';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const docs = await documentsService.getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadComplete = (document: Document) => {
    setDocuments([document, ...documents]);
    setShowUpload(false);
    setSelectedDocument(document);
  };

  const handleLogout = async () => {
    await logout();
  };

  if (selectedDocument) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <ChatInterface
            document={selectedDocument}
            onBack={() => setSelectedDocument(null)}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Research Paper Analyst
              </h1>
              <p className="text-sm text-gray-600">
                Welcome back, {user?.full_name}!
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowUpload(!showUpload)}
                className="btn-primary"
              >
                {showUpload ? 'View Documents' : '+ Upload Paper'}
              </button>
              <button
                onClick={handleLogout}
                className="btn-secondary"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : showUpload ? (
          <DocumentUpload onUploadComplete={handleUploadComplete} />
        ) : (
          <DocumentList
            documents={documents}
            onSelectDocument={setSelectedDocument}
            onRefresh={loadDocuments}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="text-center text-sm text-gray-600">
            <p>
              Powered by AI · Phase 5 Complete · {documents.length} documents analyzed
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
