import React, { useState, useRef } from 'react';
import type { Document } from '../services/documents.service';
import documentsService from '../services/documents.service';

interface DocumentUploadProps {
  onUploadComplete: (document: Document) => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    setError('');
    
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a PDF file');
      return;
    }

    if (file.size > 20 * 1024 * 1024) { // 20MB limit
      setError('File size must be less than 20MB');
      return;
    }

    setUploading(true);

    try {
      const document = await documentsService.uploadDocument(file);
      onUploadComplete(document);
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="card max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Upload Research Paper
      </h2>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <div
        className={`relative border-2 border-dashed rounded-lg p-12 text-center ${
          dragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf"
          onChange={handleChange}
          disabled={uploading}
        />

        {uploading ? (
          <div className="space-y-4">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="text-gray-600">Uploading and processing document...</p>
          </div>
        ) : (
          <div className="space-y-4">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            
            <div>
              <button
                type="button"
                onClick={onButtonClick}
                className="btn-primary"
              >
                Select PDF File
              </button>
              <p className="mt-2 text-sm text-gray-600">
                or drag and drop
              </p>
            </div>
            
            <p className="text-xs text-gray-500">
              PDF up to 20MB
            </p>
          </div>
        )}
      </div>

      <div className="mt-6 text-sm text-gray-600 space-y-2">
        <p className="font-medium">What happens after upload:</p>
        <ul className="list-disc list-inside space-y-1 ml-2">
          <li>Text extraction from PDF</li>
          <li>Semantic chunking and vector embeddings</li>
          <li>Metadata extraction (title, authors, abstract)</li>
          <li>Ready for AI-powered analysis</li>
        </ul>
      </div>
    </div>
  );
};

export default DocumentUpload;
