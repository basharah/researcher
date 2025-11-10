"use client";

import { useState } from "react";
import api from "../../lib/api";
import formatError from "../../lib/formatError";
import { useToasts } from "../../components/ToastProvider";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const toasts = useToasts();

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    setError(null);
    const f = e.target.files?.[0] || null;
    setFile(f);
  }

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return setError("Please choose a file to upload.");
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const fd = new FormData();
      fd.append("file", file);
      setProgress(0);
      const data = await api.uploadWithProgress("/upload", fd, (p) => setProgress(p));
  setResult(data);
  toasts.push({ type: "success", message: "Upload completed" });
      setError(null);
    } catch (err: any) {
      setError(formatError(err));
      setResult(null);
    } finally {
      setLoading(false);
      setProgress(0);
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="text-2xl font-semibold">Upload Document</h1>

      <form onSubmit={handleUpload} className="mt-6 space-y-4">
        <div>
          <label className="block text-sm text-zinc-600">PDF file</label>
          <input type="file" accept="application/pdf" onChange={handleFile} className="mt-2" />
        </div>

        {error && <div className="text-sm text-red-600">{error}</div>}

        {progress > 0 && (
          <div className="w-full rounded bg-zinc-100">
            <div
              className="h-2 rounded bg-black"
              style={{ width: `${progress}%`, transition: "width 150ms linear" }}
            />
            <div className="mt-1 text-xs text-zinc-600">{progress}%</div>
          </div>
        )}

        <div>
          <button disabled={loading} className="rounded bg-black px-4 py-2 text-white">
            {loading ? "Uploading…" : "Upload"}
          </button>
        </div>
      </form>

      {result && (
        <section className="mt-6 rounded border p-4 bg-zinc-50">
          <h2 className="font-medium">Upload result</h2>
          <pre className="mt-2 max-h-64 overflow-auto text-sm">{JSON.stringify(result, null, 2)}</pre>
        </section>
      )}
    </div>
  );
}
