"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import formatError from "../../lib/formatError";
import api from "../../lib/api";
import { useToasts } from "../../components/ToastProvider";
import { useAuth } from "../../components/AuthProvider";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [organization, setOrganization] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const router = useRouter();
  const toasts = useToasts();
  const { checkAuth } = useAuth();

  const enabled = process.env.NEXT_PUBLIC_ENABLE_REGISTRATION === "true";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
  setError(null);
  setFieldErrors({});
    if (!enabled) {
      setError("Registration is disabled");
      return;
    }
    setLoading(true);

    const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

    try {
      const data = await api.apiFetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: name, organization }),
      });

      // Refresh global auth state after registration
      await checkAuth();

      // If server sets cookie, we're authenticated; otherwise redirect to login
      toasts.push({ type: "success", message: "Account created" });
      router.push("/dashboard");
    } catch (err: any) {
      // Handle validation errors (FastAPI/Pydantic style)
      if (err?.status === 422 && Array.isArray(err?.detail)) {
        const map: Record<string, string[]> = {};
        for (const it of err.detail) {
          const loc = Array.isArray(it.loc) ? it.loc : it?.loc || [];
          const fieldRaw = loc.slice(-1)[0] || "_";
          const field = fieldRaw === "full_name" ? "name" : fieldRaw;
          map[field] = map[field] || [];
          map[field].push(it.msg || JSON.stringify(it));
        }
        const flattened: Record<string, string> = {};
        for (const k of Object.keys(map)) flattened[k] = map[k].join("; ");
        setFieldErrors(flattened);
        setError("Please fix the highlighted fields.");
        // focus & scroll to first invalid field
        const firstField = Object.keys(flattened)[0];
        if (firstField) {
          const el = document.querySelector(`[name="${firstField}"]`) as HTMLElement | null;
          if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "center" });
            try {
              (el as HTMLElement).focus();
            } catch (e) {
              // ignore
            }
          }
        }
      } else {
        setError(formatError(err));
      }
    } finally {
      setLoading(false);
    }
  }

  if (!enabled) {
    return (
      <div className="mx-auto max-w-md px-6 py-16">
        <h1 className="mb-4 text-2xl font-semibold">Register</h1>
        <p className="text-sm text-zinc-600">Registration is currently disabled. Contact an administrator to create an account.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md px-6 py-16">
      <h1 className="mb-6 text-2xl font-semibold">Create an account</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block">
          <div className="text-sm text-zinc-600">Full name</div>
          <input
            name="name"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              setFieldErrors((p) => ({ ...p, name: "" }));
            }}
            className="mt-1 w-full rounded border px-3 py-2"
            type="text"
            required
          />
          {fieldErrors.name && <div className="mt-1 text-sm text-red-600">{fieldErrors.name}</div>}
        </label>

        <label className="block">
          <div className="text-sm text-zinc-600">Organization (optional)</div>
          <input
            name="organization"
            value={organization}
            onChange={(e) => {
              setOrganization(e.target.value);
              setFieldErrors((p) => ({ ...p, organization: "" }));
            }}
            className="mt-1 w-full rounded border px-3 py-2"
            type="text"
          />
          {fieldErrors.organization && <div className="mt-1 text-sm text-red-600">{fieldErrors.organization}</div>}
        </label>

        <label className="block">
          <div className="text-sm text-zinc-600">Email</div>
          <input
            name="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              setFieldErrors((p) => ({ ...p, email: "" }));
            }}
            className="mt-1 w-full rounded border px-3 py-2"
            type="email"
            required
          />
          {fieldErrors.email && <div className="mt-1 text-sm text-red-600">{fieldErrors.email}</div>}
        </label>

        <label className="block">
          <div className="text-sm text-zinc-600">Password</div>
          <input
            name="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setFieldErrors((p) => ({ ...p, password: "" }));
            }}
            className="mt-1 w-full rounded border px-3 py-2"
            type="password"
            required
          />
          {fieldErrors.password && <div className="mt-1 text-sm text-red-600">{fieldErrors.password}</div>}
        </label>

        {error && <div className="text-sm text-red-600">{error}</div>}

        <div className="flex items-center justify-between">
          <button
            type="submit"
            disabled={loading}
            className="rounded bg-black px-4 py-2 text-white disabled:opacity-60"
          >
            {loading ? "Creating…" : "Create account"}
          </button>
        </div>
      </form>
    </div>
  );
}
