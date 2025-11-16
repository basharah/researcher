"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import api from "../lib/api";

interface UserInfo {
  user_id: string;
  email: string;
  full_name: string;
  organization?: string | null;
  role: string;
  disabled?: boolean;
}

interface AuthContextType {
  authed: boolean;
  loading: boolean;
  user?: UserInfo | null;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  authed: false,
  loading: true,
  user: null,
  checkAuth: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authed, setAuthed] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [user, setUser] = useState<UserInfo | null>(null);

  const checkAuth = async () => {
    try {
      const me = await api.apiFetch("/auth/me");
      setUser(me || null);
      setAuthed(true);
    } catch {
      setUser(null);
      setAuthed(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ authed, loading, user, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
