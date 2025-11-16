"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import api from "../../../lib/api";
import formatError from "../../../lib/formatError";
import { useAuth } from "../../../components/AuthProvider";
import { useToasts } from "../../../components/ToastProvider";

interface UserItem {
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  disabled: boolean;
  created_at: string;
  organization?: string | null;
}

export default function AdminUsersPage() {
  const { authed, user } = useAuth();
  const router = useRouter();
  const toasts = useToasts();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [users, setUsers] = useState<UserItem[]>([]);

  const [creating, setCreating] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newFullName, setNewFullName] = useState("");
  const [newOrg, setNewOrg] = useState("");
  const [newRole, setNewRole] = useState("user");

  const isAdmin = useMemo(() => (user?.role || "").toLowerCase() === "admin", [user]);

  useEffect(() => {
    if (!authed) {
      router.replace("/login");
      return;
    }
    if (!isAdmin) {
      router.replace("/dashboard");
      return;
    }
    let mounted = true;
    api
      .apiFetch("/auth/admin/users")
      .then((data) => {
        if (!mounted) return;
        setUsers((data?.users || []) as UserItem[]);
      })
      .catch((err) => setError(formatError(err)))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [authed, isAdmin, router]);

  async function refresh() {
    const data = await api.apiFetch("/auth/admin/users");
    setUsers(data?.users || []);
  }

  async function toggleActive(u: UserItem, enable: boolean) {
    try {
      await api.apiFetch(`/auth/admin/users/${u.user_id}/${enable ? "enable" : "disable"}`, { method: "PUT" });
      toasts.push({ type: "success", message: enable ? "User enabled" : "User disabled" });
      await refresh();
    } catch (err: any) {
      toasts.push({ type: "error", message: formatError(err) });
    }
  }

  async function changeRole(u: UserItem, role: string) {
    try {
      await api.apiFetch(`/auth/admin/users/${u.user_id}/role?role=${encodeURIComponent(role)}`, { method: "PUT" });
      toasts.push({ type: "success", message: "Role updated" });
      await refresh();
    } catch (err: any) {
      toasts.push({ type: "error", message: formatError(err) });
    }
  }

  async function saveProfile(u: UserItem) {
    try {
      await api.apiFetch(`/auth/admin/users/${u.user_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ full_name: u.full_name, organization: u.organization }),
      });
      toasts.push({ type: "success", message: "User updated" });
      await refresh();
    } catch (err: any) {
      toasts.push({ type: "error", message: formatError(err) });
    }
  }

  async function createUser() {
    setCreating(true);
    setError(null);
    try {
      await api.apiFetch("/auth/admin/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: newEmail,
          password: newPassword,
          full_name: newFullName,
          organization: newOrg || undefined,
          role: newRole,
        }),
      });
      toasts.push({ type: "success", message: "User created" });
      setNewEmail("");
      setNewPassword("");
      setNewFullName("");
      setNewOrg("");
      setNewRole("user");
      await refresh();
    } catch (err: any) {
      setError(formatError(err));
    } finally {
      setCreating(false);
    }
  }

  if (loading) return <div className="p-6">Loading…</div>;

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <h1 className="text-2xl font-semibold mb-6">User Management</h1>

      <div className="mb-10 border rounded-lg p-4">
        <h2 className="text-lg font-medium mb-3">Create New User</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <input placeholder="Email" value={newEmail} onChange={(e) => setNewEmail(e.target.value)} className="rounded border px-3 py-2" />
          <input placeholder="Password" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} className="rounded border px-3 py-2" />
          <input placeholder="Full name" value={newFullName} onChange={(e) => setNewFullName(e.target.value)} className="rounded border px-3 py-2" />
          <input placeholder="Organization (optional)" value={newOrg} onChange={(e) => setNewOrg(e.target.value)} className="rounded border px-3 py-2" />
          <select value={newRole} onChange={(e) => setNewRole(e.target.value)} className="rounded border px-3 py-2">
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <div className="mt-3">
          <button onClick={createUser} disabled={creating} className="rounded bg-black text-white px-4 py-2">
            {creating ? "Creating…" : "Create user"}
          </button>
        </div>
        {error && <div className="mt-2 text-sm text-red-600">{error}</div>}
      </div>

      <div className="space-y-3">
        {users.map((u) => (
          <div key={u.user_id} className="p-4 border rounded-lg flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-3 items-center">
              <div>
                <div className="text-sm text-zinc-500">Email</div>
                <div className="font-medium">{u.email}</div>
              </div>
              <div>
                <div className="text-sm text-zinc-500">Full name</div>
                <input
                  className="mt-1 w-full rounded border px-3 py-2"
                  value={u.full_name}
                  onChange={(e) => setUsers((prev) => prev.map((x) => (x.user_id === u.user_id ? { ...x, full_name: e.target.value } : x)))}
                />
              </div>
              <div>
                <div className="text-sm text-zinc-500">Organization</div>
                <input
                  className="mt-1 w-full rounded border px-3 py-2"
                  value={u.organization || ""}
                  onChange={(e) => setUsers((prev) => prev.map((x) => (x.user_id === u.user_id ? { ...x, organization: e.target.value } : x)))}
                />
              </div>
              <div>
                <div className="text-sm text-zinc-500">Role</div>
                <select
                  className="mt-1 w-full rounded border px-3 py-2"
                  value={(u.role || "user").toLowerCase()}
                  onChange={(e) => changeRole(u, e.target.value)}
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => saveProfile(u)} className="rounded px-3 py-2 border">Save</button>
              {u.disabled ? (
                <button onClick={() => toggleActive(u, true)} className="rounded px-3 py-2 border text-green-700">Enable</button>
              ) : (
                <button onClick={() => toggleActive(u, false)} className="rounded px-3 py-2 border text-red-700">Disable</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
