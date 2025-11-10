"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "../../lib/api";
import formatError from "../../lib/formatError";
import { useToasts } from "../../components/ToastProvider";
import { useAuth } from "../../components/AuthProvider";

export default function ProfilePage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [organization, setOrganization] = useState<string | null>(null);
  const router = useRouter();
  const toasts = useToasts();
  const { authed } = useAuth();

  useEffect(() => {
    let mounted = true;
    api.apiFetch("/auth/me")
      .then((data) => {
        if (!mounted) return;
        setEmail(data?.email || "");
        setName(data?.full_name || "");
        setOrganization(data?.organization || "");
      })
      .catch((err) => {
        // If unauthorized, redirect to login
        if (err?.status === 401) router.push("/login");
        else setError(formatError(err));
      })
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [router]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setFieldErrors({});
    setSaving(true);
    try {
      const payload = { full_name: name, organization };
      const res = await api.apiFetch("/auth/me", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      // show success toast and refresh
      toasts.push({ type: "success", message: "Profile updated" });
      router.replace("/profile");
    } catch (err: any) {
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
        // focus first invalid field
        const firstField = Object.keys(flattened)[0];
        if (firstField) {
          const el = document.querySelector(`[name="${firstField}"]`) as HTMLElement | null;
          if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "center" });
            try { el.focus(); } catch {};
          }
        }
      } else {
        setError(formatError(err));
      }
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="p-6">Loading…</div>;

  return (
    <div className="mx-auto max-w-2xl px-6 py-12">
      <h1 className="text-2xl font-semibold">Profile</h1>
      <form className="mt-6 space-y-4" onSubmit={handleSave}>
        <div>
          <label className="block text-sm text-zinc-600">Email</label>
          <input name="email" value={email} disabled className="mt-1 w-full rounded border px-3 py-2 bg-zinc-50" />
          {fieldErrors.email && <div className="mt-1 text-sm text-red-600">{fieldErrors.email}</div>}
        </div>

        <div>
          <label className="block text-sm text-zinc-600">Full name</label>
          <input
            name="name"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              setFieldErrors((p) => ({ ...p, name: "" }));
            }}
            className="mt-1 w-full rounded border px-3 py-2"
          />
          {fieldErrors.name && <div className="mt-1 text-sm text-red-600">{fieldErrors.name}</div>}
        </div>

        <div>
          <label className="block text-sm text-zinc-600">Organization</label>
          <input
            name="organization"
            value={organization || ""}
            onChange={(e) => {
              setOrganization(e.target.value);
              setFieldErrors((p) => ({ ...p, organization: "" }));
            }}
            className="mt-1 w-full rounded border px-3 py-2"
          />
          {fieldErrors.organization && <div className="mt-1 text-sm text-red-600">{fieldErrors.organization}</div>}
        </div>

        {error && <div className="text-sm text-red-600">{error}</div>}

        <div>
          <button disabled={saving} className="rounded bg-black px-4 py-2 text-white">
            {saving ? "Saving…" : "Save changes"}
          </button>
        </div>
      </form>
    </div>
  );
}
