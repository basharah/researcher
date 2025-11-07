import React from 'react';
import type { Document } from '../services/documents.service';

interface DocumentListProps {
  documents: Document[];
  onSelectDocument: (document: Document) => void;
  onRefresh: () => void;
}

const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  onSelectDocument,
  onRefresh,
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">
          My Documents ({documents.length})
        </h2>
        <button
          onClick={onRefresh}
          className="btn-secondary"
        >
          <svg className="w-5 h-5 mr-2 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="card text-center py-12">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No documents yet</h3>
          <p className="mt-2 text-gray-600">Upload your first research paper to get started</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="card hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => onSelectDocument(doc)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 truncate mb-2">
                    {doc.title || doc.filename}
                  </h3>
                  
                  {doc.authors && (
                    <p className="text-sm text-gray-600 mb-1 line-clamp-1">
                      {doc.authors}
                    </p>
                  )}
                  
                  {doc.abstract && (
                    <p className="text-sm text-gray-500 line-clamp-2 mb-3">
                      {doc.abstract}
                    </p>
                  )}
                  
                  <div className="flex items-center text-xs text-gray-500 space-x-4">
                    <span>{formatDate(doc.upload_date)}</span>
                    {doc.page_count && (
                      <span>{doc.page_count} pages</span>
                    )}
                    {doc.file_size && (
                      <span>{formatFileSize(doc.file_size)}</span>
                    )}
                  </div>
                </div>
                
                <svg
                  className="h-5 w-5 text-gray-400 flex-shrink-0 ml-2"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentList;
