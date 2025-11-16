"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "./AuthProvider";

export default function Navigation() {
  const pathname = usePathname();
  const { authed, user } = useAuth();

  if (!authed) return null;

  const navItems = [
    { href: "/dashboard", label: "Dashboard", icon: "📊" },
    { href: "/upload", label: "Upload", icon: "📤" },
    { href: "/batch-upload", label: "Batch Upload", icon: "📁" },
    { href: "/jobs", label: "Jobs", icon: "⚙️" },
    { href: "/search", label: "Search", icon: "🔍" },
    { href: "/analysis", label: "Analysis", icon: "📈" },
    { href: "/compare", label: "Compare", icon: "⚖️" },
    { href: "/chat", label: "Chat", icon: "💬" },
    { href: "/profile", label: "Profile", icon: "👤" },
  ];

  const isAdmin = (user?.role || "").toLowerCase() === "admin";
  if (isAdmin) {
    navItems.splice(1, 0, { href: "/admin/users", label: "Users", icon: "🛡️" });
  }

  return (
    <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex items-center gap-1 overflow-x-auto py-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors
                  ${
                    isActive
                      ? "bg-blue-100 text-blue-700"
                      : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                  }
                `}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
