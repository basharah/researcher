"use client";

import React, { createContext, useCallback, useContext, useState } from "react";

type Toast = { id: string; title?: string; message: string; type?: "info" | "success" | "error" };

const ToastContext = createContext<{
  toasts: Toast[];
  push: (t: Omit<Toast, "id">) => void;
  dismiss: (id: string) => void;
} | null>(null);

export function useToasts() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToasts must be used within ToastProvider");
  return ctx;
}

export default function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const push = useCallback((t: Omit<Toast, "id">) => {
    const id = Math.random().toString(36).slice(2, 9);
    const toast: Toast = { id, ...t };
    setToasts((s) => [...s, toast]);
    // auto dismiss
    setTimeout(() => setToasts((s) => s.filter((x) => x.id !== id)), 5000);
  }, []);

  const dismiss = useCallback((id: string) => setToasts((s) => s.filter((x) => x.id !== id)), []);

  return (
    <ToastContext.Provider value={{ toasts, push, dismiss }}>
      {children}

      <div className="fixed right-4 top-4 z-50 flex flex-col gap-3">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`max-w-sm rounded-md border px-4 py-3 shadow-md ${
              t.type === "success" ? "bg-green-50 border-green-200" : t.type === "error" ? "bg-red-50 border-red-200" : "bg-white border-zinc-200"
            }`}
          >
            {t.title && <div className="font-medium">{t.title}</div>}
            <div className="text-sm">{t.message}</div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
