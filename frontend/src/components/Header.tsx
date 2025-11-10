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
          <Link href="/" className="font-semibold">
            Researcher
          </Link>
          <nav className="hidden gap-3 sm:flex">
            <Link href="/dashboard" className="text-sm text-zinc-600 hover:underline">
              Dashboard
            </Link>
            {authed && (
              <>
                <Link href="/upload" className="text-sm text-zinc-600 hover:underline">
                  Upload
                </Link>
                <Link href="/profile" className="text-sm text-zinc-600 hover:underline">
                  Profile
                </Link>
              </>
            )}
            {!authed && enableRegistration && (
              <Link href="/register" className="text-sm text-zinc-600 hover:underline">
                Register
              </Link>
            )}
          </nav>
        </div>

        <div>
          {!authed ? (
            <Link href="/login" className="rounded-md bg-black px-3 py-2 text-sm text-white">
              Sign in
            </Link>
          ) : (
            <button onClick={handleLogout} className="rounded-md border px-3 py-2 text-sm">
              Sign out
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
