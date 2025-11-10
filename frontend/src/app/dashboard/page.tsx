"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../components/AuthProvider";

export default function DashboardPage() {
  const router = useRouter();
  const { authed, loading } = useAuth();

  useEffect(() => {
    if (!loading && !authed) {
      // Not authenticated - redirect to login
      router.replace("/login");
    }
  }, [authed, loading, router]);

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-12 text-center">
        <p className="text-zinc-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-2xl font-semibold">Welcome to your dashboard</h1>
      <p className="mt-4 text-zinc-700">
        This is the landing page after login. Replace this with your application
        landing components — e.g., recent documents, search box, or quick actions.
      </p>

      <section className="mt-8 rounded border p-4">
        <h2 className="font-medium">Quick links</h2>
        <ul className="mt-2 ml-4 list-disc text-sm text-zinc-700">
          <li>Search documents</li>
          <li>Upload paper</li>
          <li>Start analysis</li>
        </ul>
      </section>
    </div>
  );
}
