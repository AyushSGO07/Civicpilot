"use client";

import React, { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  ShieldCheck,
  Lock,
  Mail,
  User,
  Eye,
  EyeOff,
  ArrowRight,
  Loader2,
  AlertCircle,
  Sparkles,
  CheckCircle2,
} from "lucide-react";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";

function AuthForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirectTo") || "/profile";

  const { user, signInWithPassword, signUp, loginAsDemoUser } = useAuth();
  const [tab, setTab] = useState<"signin" | "signup">("signin");

  // Form states
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  // Status feedback
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // If already authenticated, redirect safely
  React.useEffect(() => {
    if (user) {
      // Validate local redirect path to prevent open redirect
      const safeRedirect = redirectTo.startsWith("/") ? redirectTo : "/profile";
      router.push(safeRedirect);
    }
  }, [user, router, redirectTo]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    // Client-side validation
    if (!email || !email.includes("@")) {
      setErrorMessage("Please enter a valid email address.");
      return;
    }

    if (!password || password.length < 6) {
      setErrorMessage("Password must be at least 6 characters long.");
      return;
    }

    if (tab === "signup" && !fullName.trim()) {
      setErrorMessage("Please enter your legal full name.");
      return;
    }

    setLoading(true);

    try {
      if (tab === "signin") {
        const { error } = await signInWithPassword(email, password);
        if (error) {
          setErrorMessage(error.message || "Failed to sign in. Please verify your credentials.");
          setLoading(false);
          return;
        }
        setSuccessMessage("Signed in successfully. Redirecting...");
      } else {
        const { error } = await signUp(email, password, fullName.trim());
        if (error) {
          setErrorMessage(error.message || "Could not complete account creation.");
          setLoading(false);
          return;
        }
        setSuccessMessage("Account created successfully! Redirecting...");
      }

      // Safe client redirect
      const safeRedirect = redirectTo.startsWith("/") ? redirectTo : "/profile";
      setTimeout(() => {
        router.push(safeRedirect);
      }, 400);
    } catch {
      setErrorMessage("An unexpected authentication error occurred.");
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    loginAsDemoUser();
    const safeRedirect = redirectTo.startsWith("/") ? redirectTo : "/profile";
    router.push(safeRedirect);
  };

  return (
    <div className="w-full max-w-md mx-auto">
      {/* Brand Header */}
      <div className="text-center mb-6">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-civic-blue to-civic-cyan shadow-md text-white mb-3">
          <ShieldCheck className="h-6 w-6" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-navy">
          {tab === "signin" ? "Sign In to CivicPilot" : "Create Citizen Account"}
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          {tab === "signin"
            ? "Access your eligibility profile & tracked applications"
            : "Begin autonomous discovery and government scheme execution"}
        </p>
      </div>

      {/* Main Elevated Card */}
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200/80 p-6 sm:p-8 transition-all">
        {/* Segmented Tab Switcher */}
        <div className="flex rounded-xl bg-slate-100 p-1 mb-6">
          <button
            type="button"
            onClick={() => {
              setTab("signin");
              setErrorMessage(null);
            }}
            className={`flex-1 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all ${
              tab === "signin"
                ? "bg-white text-civic-blue shadow-sm"
                : "text-slate-600 hover:text-navy"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setTab("signup");
              setErrorMessage(null);
            }}
            className={`flex-1 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all ${
              tab === "signup"
                ? "bg-white text-civic-blue shadow-sm"
                : "text-slate-600 hover:text-navy"
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="mb-4 flex items-center gap-2.5 rounded-lg border border-red-200 bg-red-50 p-3 text-xs text-red-700">
            <AlertCircle className="h-4 w-4 shrink-0 text-red-600" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Success Alert */}
        {successMessage && (
          <div className="mb-4 flex items-center gap-2.5 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Auth Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {tab === "signup" && (
            <div>
              <label
                htmlFor="fullName"
                className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1"
              >
                Full Legal Name
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <User className="h-4 w-4" />
                </div>
                <input
                  id="fullName"
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Aarav Sharma"
                  className="w-full rounded-lg border border-slate-300 pl-10 pr-3 py-2 text-sm text-navy placeholder:text-slate-400 focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20"
                />
              </div>
            </div>
          )}

          <div>
            <label
              htmlFor="email"
              className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1"
            >
              Email Address
            </label>
            <div className="relative">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                <Mail className="h-4 w-4" />
              </div>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="citizen@example.gov.in"
                className="w-full rounded-lg border border-slate-300 pl-10 pr-3 py-2 text-sm text-navy placeholder:text-slate-400 focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1"
            >
              Password
            </label>
            <div className="relative">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                <Lock className="h-4 w-4" />
              </div>
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                autoComplete={tab === "signin" ? "current-password" : "new-password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-lg border border-slate-300 pl-10 pr-10 py-2 text-sm text-navy placeholder:text-slate-400 focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600 focus:outline-none"
                aria-label="Toggle password visibility"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {tab === "signup" && (
              <span className="text-[11px] text-slate-500 mt-1 block">
                Must be at least 6 characters.
              </span>
            )}
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full bg-civic-blue hover:bg-civic-blue-hover text-white font-semibold py-2.5 rounded-lg shadow-sm transition-all flex items-center justify-center gap-2 mt-2"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Processing...</span>
              </>
            ) : tab === "signin" ? (
              <>
                <span>Sign In to CivicPilot</span>
                <ArrowRight className="h-4 w-4" />
              </>
            ) : (
              <>
                <span>Create Citizen Account</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </Button>
        </form>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-200" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-white px-3 text-slate-400 font-medium">Or quick demo</span>
          </div>
        </div>

        {/* 1-Click Demo Citizen Login */}
        <Button
          type="button"
          variant="outline"
          onClick={handleDemoLogin}
          className="w-full border-dashed border-civic-cyan/60 text-navy hover:bg-civic-blue/5 flex items-center justify-center gap-2 font-medium text-xs"
        >
          <Sparkles className="h-3.5 w-3.5 text-civic-cyan" />
          Continue as Demo Citizen (Aarav Sharma)
        </Button>

        {/* Security Assurance Footer */}
        <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-center gap-2 text-[11px] text-slate-400 text-center">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
          <span>Protected by 256-bit AES encryption • Zero plain text storage</span>
        </div>
      </div>

      <div className="mt-4 text-center">
        <Link href="/" className="text-xs text-slate-500 hover:text-civic-blue underline">
          ← Back to CivicPilot Home
        </Link>
      </div>
    </div>
  );
}

export default function AuthPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8 bg-canvas">
      <Suspense
        fallback={
          <div className="flex items-center justify-center py-20 text-slate-500">
            <Loader2 className="h-6 w-6 animate-spin text-civic-blue mr-2" />
            Loading authentication...
          </div>
        }
      >
        <AuthForm />
      </Suspense>
    </div>
  );
}
