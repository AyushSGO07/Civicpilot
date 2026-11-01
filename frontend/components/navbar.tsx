"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield,
  Menu,
  X,
  Compass,
  FileCheck2,
  FolderLock,
  Sparkles,
  User,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "Home", href: "/", icon: Compass },
  { label: "Explore Services", href: "/services", icon: Compass },
  { label: "My Applications", href: "/applications", icon: FileCheck2 },
  { label: "Document Vault", href: "/documents", icon: FolderLock },
];

export function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  // Close mobile drawer on route navigation
  React.useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-navy-light/40 bg-navy text-white shadow-md backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo */}
        <div className="flex items-center gap-8">
          <Link
            href="/"
            className="group flex items-center gap-2.5 transition-opacity hover:opacity-95"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-civic-blue to-civic-cyan shadow-sm ring-1 ring-white/20 transition-transform group-hover:scale-105">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-black tracking-tight text-white">
                Civic<span className="text-civic-cyan">Pilot</span>
              </span>
              <span className="text-[10px] font-medium tracking-wider uppercase text-slate-300">
                Autonomous Citizen Services
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {NAV_ITEMS.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 rounded-lg px-3.5 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-white/10 text-white font-semibold"
                      : "text-slate-200 hover:bg-white/5 hover:text-white"
                  )}
                >
                  <item.icon className="h-4 w-4 opacity-70" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right Section: AI Status Badge & Profile/Auth */}
        <div className="hidden sm:flex items-center gap-3">
          {/* AI Copilot Active Indicator */}
          <div className="flex items-center gap-2 rounded-full border border-civic-cyan/30 bg-civic-cyan/10 px-3 py-1 text-xs font-semibold text-civic-cyan">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-civic-cyan opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-civic-cyan"></span>
            </span>
            <Sparkles className="h-3 w-3" />
            <span className="hidden lg:inline">AI Agent Ready</span>
            <span className="lg:hidden">Agent</span>
          </div>

          {/* Sign In CTA */}
          <Link href="/auth">
            <Button
              variant="cyan"
              size="sm"
              className="gap-1.5 font-semibold text-xs shadow-sm"
            >
              <User className="h-3.5 w-3.5" />
              Sign In
            </Button>
          </Link>
        </div>

        {/* Mobile Menu Hamburger Toggle */}
        <div className="flex sm:hidden items-center gap-2">
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="inline-flex items-center justify-center rounded-lg p-2 text-slate-200 hover:bg-white/10 hover:text-white focus:outline-none"
            aria-label="Toggle navigation menu"
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="sm:hidden border-t border-navy-light/50 bg-navy-dark px-4 pt-3 pb-6 shadow-xl transition-all animate-in slide-in-from-top-2">
          <div className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-base font-medium transition-colors",
                    isActive
                      ? "bg-civic-blue text-white"
                      : "text-slate-200 hover:bg-white/10 hover:text-white"
                  )}
                >
                  <item.icon className="h-5 w-5 opacity-80" />
                  {item.label}
                </Link>
              );
            })}
          </div>

          <div className="mt-4 pt-4 border-t border-white/10 flex flex-col gap-3">
            <div className="flex items-center justify-between px-2">
              <span className="text-xs text-slate-300">Agent Status</span>
              <div className="flex items-center gap-1.5 rounded-full border border-civic-cyan/30 bg-civic-cyan/10 px-2.5 py-0.5 text-xs text-civic-cyan font-medium">
                <span className="h-2 w-2 rounded-full bg-civic-cyan"></span>
                AI Ready
              </div>
            </div>

            <Link href="/auth" className="w-full">
              <Button
                variant="cyan"
                className="w-full justify-center gap-2 font-semibold"
              >
                Sign In / Citizen Portal
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
