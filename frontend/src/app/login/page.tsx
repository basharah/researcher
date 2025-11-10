"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import formatError from "../../lib/formatError";
import api from "../../lib/api";
import { useToasts } from "../../components/ToastProvider";
import { useAuth } from "../../components/AuthProvider";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const toasts = useToasts();
  const { checkAuth } = useAuth();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await api.apiFetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

        // With cookie-based auth the server should set secure HttpOnly cookies.
        // Verify the cookie-based session by calling /auth/me. Retry briefly
        // because some browsers may apply cookies a tiny moment after the
        // response is processed.
        let me = null;
        const maxAttempts = 3;
        for (let i = 0; i < maxAttempts; i++) {
          try {
            me = await api.apiFetch("/auth/me");
            break;
          } catch (err) {
            // small delay before retry
            await new Promise((r) => setTimeout(r, 200));
          }
        }

        if (!me) {
          // session cookie not present/accepted by browser
          setError("Signed in, but session cookie not detected. Check browser cookie settings or CORS allow-credentials.");
          return;
        }

        // Refresh global auth state
        await checkAuth();

        toasts.push({ type: "success", message: "Signed in" });
        router.push("/dashboard");
    } catch (err: any) {
      setError(formatError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-6 py-16">
      <h1 className="mb-6 text-2xl font-semibold">Sign in</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block">
          <div className="text-sm text-zinc-600">Email</div>
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded border px-3 py-2"
            type="email"
            required
          />
        </label>

        <label className="block">
          <div className="text-sm text-zinc-600">Password</div>
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded border px-3 py-2"
            type="password"
            required
          />
        </label>

        {error && <div className="text-sm text-red-600">{error}</div>}

        <div className="flex items-center justify-between">
          <button
            type="submit"
            disabled={loading}
            className="rounded bg-black px-4 py-2 text-white disabled:opacity-60"
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </div>
      </form>
    </div>
  );
}
