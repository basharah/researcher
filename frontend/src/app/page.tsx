"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

export default function Home() {
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "error">("idle");
  const [payload, setPayload] = useState<any>(null);

  const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

  async function fetchHealth() {
    setStatus("loading");
    setPayload(null);
    try {
      const data = await apiFetch("/health", { cache: "no-store" });
      setStatus("ok");
      setPayload(data);
    } catch (err) {
      setStatus("error");
      setPayload({ error: String(err) });
    }
  }

  useEffect(() => {
    // run once on mount
    fetchHealth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-start py-12 px-6 bg-white dark:bg-black sm:items-start">
        <header className="w-full flex items-center justify-between pb-8">
          <div className="flex items-center gap-4">
            <Image className="dark:invert" src="/next.svg" alt="Next.js logo" width={72} height={18} priority />
            <h1 className="text-xl font-semibold">Researcher — Frontend</h1>
          </div>

          <div className="flex items-center gap-3">
            <div className="rounded-md border px-3 py-2 text-sm">
              <span className="font-medium">API:</span>{" "}
              <code className="text-xs">{base}</code>
            </div>
            <button
              onClick={fetchHealth}
              className="rounded-md bg-black px-3 py-2 text-sm text-white hover:opacity-90"
            >
              Refresh
            </button>
          </div>
        </header>

        <section className="w-full rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">API Gateway health</h2>
            <div>
              {status === "loading" && <span className="text-sm text-zinc-500">Checking…</span>}
              {status === "ok" && <span className="text-sm text-green-600">Healthy</span>}
              {status === "error" && <span className="text-sm text-red-600">Unhealthy</span>}
              {status === "idle" && <span className="text-sm text-zinc-500">—</span>}
            </div>
          </div>

          <div className="mt-4 max-h-48 overflow-auto rounded bg-zinc-50 p-3 text-sm">
            <pre className="whitespace-pre-wrap break-words">{JSON.stringify(payload, null, 2) || "No response yet"}</pre>
          </div>
        </section>

        <section className="mt-6 w-full text-sm text-zinc-700">
          <p>
            This page uses the env var <code>NEXT_PUBLIC_API_BASE</code> to build the health
            endpoint URL. To set it locally, create a <code>.env.local</code> file in the
            frontend folder with <code>NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1</code>.
          </p>
        </section>
      </main>
    </div>
  );
}
