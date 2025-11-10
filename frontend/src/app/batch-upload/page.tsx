"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../components/AuthProvider";

interface UploadedFile {
  file: File;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  jobId?: string;
  error?: string;
}

export default function BatchUploadPage() {
  const router = useRouter();
  const { authed, loading } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [batchId, setBatchId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    if (!loading && !authed) {
      router.replace("/login");
    }
  }, [authed, loading, router]);

  // Handle file selection
  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return;

    const newFiles: UploadedFile[] = Array.from(selectedFiles)
      .filter(file => file.type === 'application/pdf')
      .map(file => ({
        file,
        status: 'pending',
        progress: 0
      }));

    if (newFiles.length < selectedFiles.length) {
      alert(`Only PDF files are allowed. ${selectedFiles.length - newFiles.length} file(s) were skipped.`);
    }

    setFiles(prev => [...prev, ...newFiles]);
  };

  // Handle drag and drop
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
    
    if (e.dataTransfer.files) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  // Remove file from list
  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Upload all files
  const handleBatchUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);

    try {
      const formData = new FormData();
      files.forEach(({ file }) => {
        formData.append('files', file);
      });

      // Update all files to uploading
      setFiles(prev => prev.map(f => ({ ...f, status: 'uploading' as const, progress: 30 })));

      const response = await fetch('http://localhost:8000/api/v1/batch-upload', {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      setBatchId(result.batch_id);

      // Update files to processing
      setFiles(prev => prev.map(f => ({ ...f, status: 'processing' as const, progress: 50 })));

      // Start polling for job status
      if (result.batch_id) {
        pollBatchStatus(result.batch_id);
      }

    } catch (error) {
      console.error('Batch upload failed:', error);
      setFiles(prev => prev.map(f => ({
        ...f,
        status: 'failed' as const,
        error: error instanceof Error ? error.message : 'Upload failed'
      })));
    } finally {
      setUploading(false);
    }
  };

  // Poll batch status
  const pollBatchStatus = async (batchId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/batches/${batchId}`, {
          credentials: 'include'
        });

        if (response.ok) {
          const batchData = await response.json();
          
          // Update file statuses based on jobs
          if (batchData.jobs && Array.isArray(batchData.jobs)) {
            setFiles(prev => prev.map((f, idx) => {
              const job = batchData.jobs[idx];
              if (!job) return f;

              return {
                ...f,
                jobId: job.job_id,
                status: job.status === 'completed' ? 'completed' :
                       job.status === 'failed' ? 'failed' :
                       job.status === 'processing' ? 'processing' : 'pending',
                progress: job.progress || 0,
                error: job.error_message
              };
            }));
          }

          // Stop polling if all completed or failed
          const allDone = batchData.jobs?.every((job: any) => 
            job.status === 'completed' || job.status === 'failed'
          );

          if (allDone) {
            clearInterval(pollInterval);
          }
        }
      } catch (error) {
        console.error('Error polling batch status:', error);
      }
    }, 2000); // Poll every 2 seconds

    // Stop polling after 5 minutes
    setTimeout(() => clearInterval(pollInterval), 5 * 60 * 1000);
  };

  // Clear all files
  const clearAll = () => {
    setFiles([]);
    setBatchId(null);
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-12 text-center">
        <p className="text-zinc-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Batch Upload</h1>
          <p className="text-zinc-600 mt-1">Upload multiple research papers at once</p>
        </div>
        <button
          onClick={() => router.push('/dashboard')}
          className="text-sm text-zinc-600 hover:text-zinc-900"
        >
          ← Back to Dashboard
        </button>
      </div>

      {/* Drag and Drop Zone */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-all ${
          dragActive ? 'border-blue-500 bg-blue-50' : 'border-zinc-300 hover:border-zinc-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <svg
          className="mx-auto h-12 w-12 text-zinc-400"
          stroke="currentColor"
          fill="none"
          viewBox="0 0 48 48"
        >
          <path
            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <p className="mt-4 text-sm text-zinc-600">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="font-semibold text-blue-600 hover:text-blue-500"
          >
            Click to upload
          </button>
          {' '}or drag and drop
        </p>
        <p className="mt-1 text-xs text-zinc-500">PDF files only</p>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf"
          onChange={(e) => handleFileSelect(e.target.files)}
          className="hidden"
        />
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">
              Selected Files ({files.length})
            </h2>
            <div className="space-x-2">
              <button
                onClick={clearAll}
                className="text-sm text-red-600 hover:text-red-700"
                disabled={uploading}
              >
                Clear All
              </button>
              <button
                onClick={handleBatchUpload}
                disabled={uploading || files.length === 0}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-zinc-300 disabled:cursor-not-allowed"
              >
                {uploading ? 'Uploading...' : `Upload ${files.length} File(s)`}
              </button>
            </div>
          </div>

          {/* Batch ID */}
          {batchId && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm">
              <span className="font-medium">Batch ID:</span> {batchId}
              <button
                onClick={() => router.push(`/jobs?batch=${batchId}`)}
                className="ml-4 text-blue-600 hover:text-blue-700"
              >
                View Details →
              </button>
            </div>
          )}

          {/* File Cards */}
          <div className="space-y-3">
            {files.map((fileData, index) => (
              <div
                key={index}
                className="border rounded-lg p-4 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      {/* Status Icon */}
                      <div className="mr-3">
                        {fileData.status === 'completed' && (
                          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                        {fileData.status === 'failed' && (
                          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                        {(fileData.status === 'uploading' || fileData.status === 'processing') && (
                          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                        )}
                        {fileData.status === 'pending' && (
                          <svg className="w-6 h-6 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          </svg>
                        )}
                      </div>

                      {/* File Info */}
                      <div className="flex-1">
                        <p className="font-medium text-sm">{fileData.file.name}</p>
                        <p className="text-xs text-zinc-500">
                          {(fileData.file.size / 1024 / 1024).toFixed(2)} MB
                          {fileData.jobId && ` • Job: ${fileData.jobId}`}
                        </p>
                        
                        {/* Progress Bar */}
                        {(fileData.status === 'uploading' || fileData.status === 'processing') && (
                          <div className="mt-2">
                            <div className="flex items-center justify-between text-xs mb-1">
                              <span className="text-zinc-600 capitalize">{fileData.status}</span>
                              <span className="text-zinc-600">{fileData.progress}%</span>
                            </div>
                            <div className="w-full bg-zinc-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full transition-all"
                                style={{ width: `${fileData.progress}%` }}
                              ></div>
                            </div>
                          </div>
                        )}

                        {/* Error Message */}
                        {fileData.error && (
                          <p className="mt-1 text-xs text-red-600">{fileData.error}</p>
                        )}

                        {/* Success Message */}
                        {fileData.status === 'completed' && (
                          <p className="mt-1 text-xs text-green-600">Processing completed successfully</p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Remove Button */}
                  {fileData.status === 'pending' && (
                    <button
                      onClick={() => removeFile(index)}
                      className="ml-4 text-zinc-400 hover:text-red-600"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Help Section */}
      {files.length === 0 && (
        <div className="mt-12 p-6 bg-zinc-50 rounded-lg">
          <h3 className="font-semibold mb-3">Batch Upload Benefits</h3>
          <ul className="space-y-2 text-sm text-zinc-700">
            <li className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              <span>Upload multiple papers simultaneously</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              <span>Real-time progress tracking for each file</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              <span>Automatic DOI extraction and OCR processing</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              <span>Background processing with detailed job monitoring</span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
