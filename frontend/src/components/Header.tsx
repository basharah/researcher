"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import api from "../lib/api";
import { useToasts } from "./ToastProvider";
import { useAuth } from "./AuthProvider";

export default function Header() {
  const { authed, checkAuth } = useAuth();
  const router = useRouter();
  const toasts = useToasts();

  function handleLogout() {
    api.apiFetch("/auth/logout", { method: "POST" })
      .catch(() => {})
      .finally(() => {
        checkAuth(); // Refresh auth state
        toasts.push({ type: "info", message: "Signed out" });
        router.push("/login");
      });
  }

  const enableRegistration = process.env.NEXT_PUBLIC_ENABLE_REGISTRATION === "true";

  return (
    <header className="w-full border-b bg-white/50 py-3 px-6">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/" className="text-xl font-bold text-blue-600">
            📚 Researcher
          </Link>
        </div>

        <div>
          {!authed ? (
            <div className="flex items-center gap-3">
              {enableRegistration && (
                <Link href="/register" className="text-sm text-zinc-600 hover:underline">
                  Register
                </Link>
              )}
              <Link href="/login" className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
                Sign in
              </Link>
            </div>
          ) : (
            <button onClick={handleLogout} className="rounded-md border px-4 py-2 text-sm hover:bg-zinc-50">
              Sign out
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
