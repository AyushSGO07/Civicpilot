"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from "react";
import { User, Session } from "@supabase/supabase-js";
import { supabase, isSupabaseConfigured } from "@/lib/supabase";
import { useRouter, usePathname } from "next/navigation";

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signInWithPassword: (
    email: string,
    password: string
  ) => Promise<{ error: Error | null }>;
  signUp: (
    email: string,
    password: string,
    fullName: string
  ) => Promise<{ error: Error | null }>;
  signOut: () => Promise<void>;
  loginAsDemoUser: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const LOCAL_STORAGE_KEY = "civicpilot_auth_session";

function createMockUser(email: string, fullName: string): User {
  return {
    id: "11111111-1111-1111-1111-111111111111",
    app_metadata: { provider: "email" },
    user_metadata: { full_name: fullName, name: fullName },
    aud: "authenticated",
    confirmation_sent_at: new Date().toISOString(),
    recovery_sent_at: "",
    email_change_sent_at: "",
    new_email: "",
    invited_at: "",
    action_link: "",
    email: email,
    phone: "",
    created_at: new Date().toISOString(),
    confirmed_at: new Date().toISOString(),
    email_confirmed_at: new Date().toISOString(),
    phone_confirmed_at: "",
    last_sign_in_at: new Date().toISOString(),
    role: "authenticated",
    updated_at: new Date().toISOString(),
    identities: [],
    factors: [],
  };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize session state on mount
  useEffect(() => {
    let mounted = true;

    async function initializeAuth() {
      if (isSupabaseConfigured) {
        try {
          const { data, error } = await supabase.auth.getSession();
          if (mounted) {
            if (!error && data.session) {
              setSession(data.session);
              setUser(data.session.user);
            }
            setLoading(false);
          }
        } catch {
          if (mounted) setLoading(false);
        }
      } else {
        // Offline / local development storage fallback
        try {
          const savedSession = localStorage.getItem(LOCAL_STORAGE_KEY);
          if (savedSession && mounted) {
            const parsed = JSON.parse(savedSession);
            setUser(parsed.user);
            setSession(parsed.session);
          }
        } catch {
          // ignore localStorage issues
        } finally {
          if (mounted) setLoading(false);
        }
      }
    }

    initializeAuth();

    if (isSupabaseConfigured) {
      const { data: authListener } = supabase.auth.onAuthStateChange(
        (_event, newSession) => {
          if (mounted) {
            setSession(newSession);
            setUser(newSession?.user ?? null);
            setLoading(false);
          }
        }
      );

      return () => {
        mounted = false;
        authListener.subscription.unsubscribe();
      };
    }

    return () => {
      mounted = false;
    };
  }, []);

  const signInWithPassword = useCallback(
    async (email: string, password: string): Promise<{ error: Error | null }> => {
      setLoading(true);
      if (isSupabaseConfigured) {
        try {
          const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password,
          });
          if (error) {
            setLoading(false);
            return { error };
          }
          setUser(data.user);
          setSession(data.session);
          setLoading(false);
          return { error: null };
        } catch (err: unknown) {
          setLoading(false);
          return { error: err as Error };
        }
      } else {
        // Offline / mock authentication
        if (!email || !password || password.length < 6) {
          setLoading(false);
          return {
            error: new Error("Password must be at least 6 characters"),
          };
        }
        const mockUser = createMockUser(email, email.split("@")[0] || "Citizen");
        const mockSession = {
          access_token: "civicpilot-offline-token",
          token_type: "bearer",
          expires_in: 3600,
          expires_at: Math.floor(Date.now() / 1000) + 3600,
          refresh_token: "mock-refresh",
          user: mockUser,
        } as Session;

        localStorage.setItem(
          LOCAL_STORAGE_KEY,
          JSON.stringify({ user: mockUser, session: mockSession })
        );
        setUser(mockUser);
        setSession(mockSession);
        setLoading(false);
        return { error: null };
      }
    },
    []
  );

  const signUp = useCallback(
    async (
      email: string,
      password: string,
      fullName: string
    ): Promise<{ error: Error | null }> => {
      setLoading(true);
      if (isSupabaseConfigured) {
        try {
          const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
              data: {
                full_name: fullName,
              },
            },
          });
          if (error) {
            setLoading(false);
            return { error };
          }
          setUser(data.user);
          setSession(data.session);
          setLoading(false);
          return { error: null };
        } catch (err: unknown) {
          setLoading(false);
          return { error: err as Error };
        }
      } else {
        // Offline / mock signup
        if (!email || !password || password.length < 6) {
          setLoading(false);
          return {
            error: new Error("Password must be at least 6 characters"),
          };
        }
        const mockUser = createMockUser(email, fullName || "Citizen");
        const mockSession = {
          access_token: "civicpilot-offline-token",
          token_type: "bearer",
          expires_in: 3600,
          expires_at: Math.floor(Date.now() / 1000) + 3600,
          refresh_token: "mock-refresh",
          user: mockUser,
        } as Session;

        localStorage.setItem(
          LOCAL_STORAGE_KEY,
          JSON.stringify({ user: mockUser, session: mockSession })
        );
        setUser(mockUser);
        setSession(mockSession);
        setLoading(false);
        return { error: null };
      }
    },
    []
  );

  const signOut = useCallback(async () => {
    setLoading(true);
    if (isSupabaseConfigured) {
      try {
        await supabase.auth.signOut();
      } catch {
        // proceed with local cleanup
      }
    }
    localStorage.removeItem(LOCAL_STORAGE_KEY);
    setUser(null);
    setSession(null);
    setLoading(false);
  }, []);

  const loginAsDemoUser = useCallback(() => {
    const demoUser = createMockUser("aarav.sharma@example.gov.in", "Aarav Sharma");
    const demoSession = {
      access_token: "civicpilot-offline-token",
      token_type: "bearer",
      expires_in: 86400,
      expires_at: Math.floor(Date.now() / 1000) + 86400,
      refresh_token: "mock-refresh",
      user: demoUser,
    } as Session;

    localStorage.setItem(
      LOCAL_STORAGE_KEY,
      JSON.stringify({ user: demoUser, session: demoSession })
    );
    setUser(demoUser);
    setSession(demoSession);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        loading,
        signInWithPassword,
        signUp,
        signOut,
        loginAsDemoUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export function useRequireAuth(redirectTo: string = "/auth") {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) {
      const returnUrl = encodeURIComponent(pathname || "/profile");
      router.push(`${redirectTo}?redirectTo=${returnUrl}`);
    }
  }, [user, loading, router, pathname, redirectTo]);

  return { user, loading, isAuthenticated: Boolean(user) };
}
