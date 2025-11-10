"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "../../components/AuthProvider";

interface Job {
  job_id: string;
  filename: string;
  status: string;
  progress: number;
  error_message?: string;
  created_at: string;
  completed_at?: string;
  batch_id?: string;
}

interface JobStep {
  step_name: string;
  status: string;
  message: string;
  duration_ms?: number;
  timestamp: string;
}

function JobsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { authed, loading } = useAuth();
  
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [jobSteps, setJobSteps] = useState<JobStep[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [loadingSteps, setLoadingSteps] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const batchFilter = searchParams?.get('batch');

  useEffect(() => {
    if (!loading && !authed) {
      router.replace("/login");
    }
  }, [authed, loading, router]);

  // Fetch jobs
  const fetchJobs = async () => {
    try {
      let url = 'http://localhost:8000/api/v1/jobs?limit=50';
      if (filterStatus !== 'all') {
        url += `&status=${filterStatus}`;
      }

      const response = await fetch(url, { credentials: 'include' });
      if (response.ok) {
        const data = await response.json();
        setJobs(data.jobs || []);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoadingJobs(false);
    }
  };

  // Fetch job steps
  const fetchJobSteps = async (jobId: string) => {
    setLoadingSteps(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/jobs/${jobId}`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setJobSteps(data.steps || []);
      }
    } catch (error) {
      console.error('Error fetching job steps:', error);
    } finally {
      setLoadingSteps(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [filterStatus]);

  // Auto-refresh every 5 seconds if enabled
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh, filterStatus]);

  // Load steps when job is selected
  useEffect(() => {
    if (selectedJob) {
      fetchJobSteps(selectedJob);
    }
  }, [selectedJob]);

  // Filter by batch if batch parameter is present
  const filteredJobs = batchFilter
    ? jobs.filter(job => job.batch_id === batchFilter)
    : jobs;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50';
      case 'failed': return 'text-red-600 bg-red-50';
      case 'processing': return 'text-blue-600 bg-blue-50';
      case 'pending': return 'text-yellow-600 bg-yellow-50';
      case 'cancelled': return 'text-zinc-600 bg-zinc-50';
      default: return 'text-zinc-600 bg-zinc-50';
    }
  };

  const getStepStatusIcon = (status: string) => {
    if (status === 'completed') {
      return <span className="text-green-600">✓</span>;
    } else if (status === 'failed') {
      return <span className="text-red-600">✗</span>;
    } else {
      return <span className="text-blue-600">●</span>;
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-12 text-center">
        <p className="text-zinc-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Processing Jobs</h1>
          <p className="text-zinc-600 mt-1">
            {batchFilter ? `Batch: ${batchFilter}` : 'Monitor document processing status'}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <label className="flex items-center text-sm">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="mr-2"
            />
            Auto-refresh
          </label>
          <button
            onClick={() => router.push('/dashboard')}
            className="text-sm text-zinc-600 hover:text-zinc-900"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex items-center space-x-4">
        <label className="text-sm font-medium">Filter by status:</label>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-1 border rounded text-sm"
        >
          <option value="all">All</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        
        <div className="flex-1"></div>
        
        <button
          onClick={fetchJobs}
          className="text-sm px-3 py-1 border rounded hover:bg-zinc-50"
        >
          ↻ Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Jobs List */}
        <div className="border rounded-lg">
          <div className="border-b p-4 bg-zinc-50">
            <h2 className="font-semibold">
              Jobs ({filteredJobs.length})
            </h2>
          </div>
          
          <div className="divide-y max-h-[600px] overflow-y-auto">
            {loadingJobs ? (
              <div className="p-8 text-center text-zinc-500">Loading jobs...</div>
            ) : filteredJobs.length === 0 ? (
              <div className="p-8 text-center text-zinc-500">No jobs found</div>
            ) : (
              filteredJobs.map(job => (
                <div
                  key={job.job_id}
                  className={`p-4 cursor-pointer hover:bg-zinc-50 transition-colors ${
                    selectedJob === job.job_id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                  }`}
                  onClick={() => setSelectedJob(job.job_id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <p className="font-medium text-sm truncate">{job.filename}</p>
                        <span className={`ml-2 px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(job.status)}`}>
                          {job.status}
                        </span>
                      </div>
                      <p className="text-xs text-zinc-500 mt-1">
                        ID: {job.job_id}
                      </p>
                      {job.batch_id && (
                        <p className="text-xs text-zinc-500">
                          Batch: {job.batch_id}
                        </p>
                      )}
                      
                      {/* Progress Bar */}
                      {(job.status === 'processing' || job.status === 'pending') && (
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-zinc-600">Progress</span>
                            <span className="text-zinc-600">{job.progress}%</span>
                          </div>
                          <div className="w-full bg-zinc-200 rounded-full h-1.5">
                            <div
                              className="bg-blue-600 h-1.5 rounded-full transition-all"
                              style={{ width: `${job.progress}%` }}
                            ></div>
                          </div>
                        </div>
                      )}

                      {job.error_message && (
                        <p className="text-xs text-red-600 mt-1">{job.error_message}</p>
                      )}

                      <p className="text-xs text-zinc-400 mt-1">
                        {new Date(job.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Job Details */}
        <div className="border rounded-lg">
          <div className="border-b p-4 bg-zinc-50">
            <h2 className="font-semibold">
              Processing Steps
            </h2>
          </div>
          
          <div className="p-4 max-h-[600px] overflow-y-auto">
            {!selectedJob ? (
              <div className="text-center text-zinc-500 py-12">
                Select a job to view processing steps
              </div>
            ) : loadingSteps ? (
              <div className="text-center text-zinc-500 py-12">Loading steps...</div>
            ) : jobSteps.length === 0 ? (
              <div className="text-center text-zinc-500 py-12">No steps recorded yet</div>
            ) : (
              <div className="space-y-3">
                {jobSteps.map((step, index) => (
                  <div key={index} className="border-l-2 border-zinc-200 pl-4 pb-4">
                    <div className="flex items-start">
                      <div className="mr-2 -ml-6 bg-white">
                        {getStepStatusIcon(step.status)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-sm">{step.step_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                          {step.duration_ms && (
                            <span className="text-xs text-zinc-500">{step.duration_ms}ms</span>
                          )}
                        </div>
                        <p className="text-sm text-zinc-600 mt-1">{step.message}</p>
                        <p className="text-xs text-zinc-400 mt-1">
                          {new Date(step.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="mt-8 grid grid-cols-2 md:grid-cols-5 gap-4">
        {['pending', 'processing', 'completed', 'failed', 'cancelled'].map(status => {
          const count = filteredJobs.filter(j => j.status === status).length;
          return (
            <div key={status} className="border rounded-lg p-4 text-center">
              <div className={`text-2xl font-bold ${getStatusColor(status)}`}>
                {count}
              </div>
              <div className="text-sm text-zinc-600 capitalize mt-1">{status}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function JobsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-zinc-50 py-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-zinc-600">Loading jobs...</p>
        </div>
      </div>
    }>
      <JobsContent />
    </Suspense>
  );
}
