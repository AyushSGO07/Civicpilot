"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  GraduationCap,
  FileText,
  Car,
  Sprout,
  HeartPulse,
  Building2,
  Banknote,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export const CATEGORIES = [
  { id: "all", label: "All Services", icon: Sparkles },
  { id: "scholarships", label: "Scholarships & Education", icon: GraduationCap },
  { id: "agriculture", label: "Agriculture & Farmers", icon: Sprout },
  { id: "healthcare", label: "Healthcare", icon: HeartPulse },
  { id: "transport", label: "Transport & Licences", icon: Car },
  { id: "business-msme", label: "Business & MSME", icon: Building2 },
  { id: "financial-assistance", label: "Financial Assistance", icon: Banknote },
  { id: "identity-docs", label: "Identity & Documents", icon: FileText },
];

export const QUERY_CHIPS = [
  "Find scholarships for engineering students",
  "Renew driving licence",
  "Small business MSME subsidy",
  "Subsidies for farmers in Bihar",
];

export function HeroSearch() {
  const router = useRouter();
  const [query, setQuery] = React.useState("");
  const [activeCategory, setActiveCategory] = React.useState<string>("all");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    const params = new URLSearchParams();
    if (trimmed) params.set("q", trimmed);
    if (activeCategory && activeCategory !== "all") params.set("category", activeCategory);

    router.push(`/services${params.toString() ? `?${params.toString()}` : ""}`);
  };

  const handleChipClick = (suggestion: string) => {
    setQuery(suggestion);
    router.push(`/services?q=${encodeURIComponent(suggestion)}`);
  };

  const handleCategorySelect = (categoryId: string) => {
    setActiveCategory(categoryId);
    const trimmed = query.trim();
    if (categoryId !== "all") {
      const params = new URLSearchParams();
      if (trimmed) params.set("q", trimmed);
      params.set("category", categoryId);
      router.push(`/services?${params.toString()}`);
    } else if (trimmed) {
      router.push(`/services?q=${encodeURIComponent(trimmed)}`);
    } else {
      router.push(`/services`);
    }
  };

  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-navy via-navy to-[#15233d] pt-12 pb-24 text-white sm:pt-16 sm:pb-32">
      {/* Background Decorative Glow */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-civic-blue/20 blur-3xl" />
        <div className="absolute top-1/2 -left-40 h-96 w-96 rounded-full bg-civic-cyan/15 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        {/* Main Title & Subtitle */}
        <div className="text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-1.5 text-xs font-semibold text-civic-cyan backdrop-blur-md mb-6">
            <Sparkles className="h-3.5 w-3.5 text-civic-cyan" />
            <span>Autonomous Bureaucratic Execution • Zero Dummy Data</span>
          </div>

          <h1 className="text-3xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl text-white">
            Your Government Work,{" "}
            <span className="bg-gradient-to-r from-civic-cyan via-[#60d5eb] to-white bg-clip-text text-transparent">
              Simplified.
            </span>
          </h1>

          <p className="mx-auto mt-4 max-w-2xl text-base text-slate-300 sm:text-lg sm:leading-relaxed">
            Discover services, check eligibility, and let AI handle the paperwork.
          </p>
        </div>

        {/* Elevated MakeMyTrip Discovery Card */}
        <div className="mt-10 rounded-2xl bg-white p-4 shadow-2xl ring-1 ring-slate-900/5 sm:p-6 text-navy">
          {/* 8 Category Tabs Bar */}
          <div className="border-b border-slate-200 pb-3">
            <div className="flex space-x-1 overflow-x-auto no-scrollbar scroll-smooth pb-1">
              {CATEGORIES.map((cat) => {
                const Icon = cat.icon;
                const isActive = activeCategory === cat.id;

                return (
                  <button
                    key={cat.id}
                    type="button"
                    onClick={() => handleCategorySelect(cat.id)}
                    className={cn(
                      "relative flex shrink-0 items-center gap-2 rounded-lg px-3.5 py-2.5 text-xs sm:text-sm font-semibold transition-all cursor-pointer",
                      isActive
                        ? "bg-civic-blue text-white shadow-sm"
                        : "text-slate-600 hover:bg-slate-100 hover:text-navy"
                    )}
                  >
                    <Icon
                      className={cn(
                        "h-4 w-4",
                        isActive ? "text-white" : "text-slate-500"
                      )}
                    />
                    <span>{cat.label}</span>
                    {isActive && (
                      <span className="absolute -bottom-[13px] left-1/2 hidden sm:block h-1 w-6 -translate-x-1/2 rounded-full bg-civic-blue" />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Search Input Box */}
          <form onSubmit={handleSearch} className="mt-5">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search schemes, subsidies, licences (e.g., student scholarships, PM Kisan)..."
                  className="w-full rounded-xl border border-slate-300 bg-slate-50/70 py-3.5 pl-12 pr-4 text-sm text-navy placeholder:text-slate-400 focus:border-civic-blue focus:bg-white focus:outline-none focus:ring-2 focus:ring-civic-blue/20 transition-all font-medium"
                />
              </div>

              <Button
                type="submit"
                size="lg"
                className="gap-2 font-bold tracking-wide shadow-md hover:shadow-lg sm:w-auto"
              >
                <span>Search Services</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </form>

          {/* Clickable Query Suggestion Chips */}
          <div className="mt-4 flex flex-wrap items-center gap-2 pt-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mr-1">
              Popular:
            </span>
            {QUERY_CHIPS.map((chip) => (
              <button
                key={chip}
                type="button"
                onClick={() => handleChipClick(chip)}
                className="group inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50/90 px-3 py-1 text-xs font-medium text-slate-600 transition-all hover:border-civic-blue/50 hover:bg-civic-blue-light hover:text-civic-blue cursor-pointer"
              >
                <span>{chip}</span>
                <ArrowRight className="h-3 w-3 opacity-0 transition-opacity group-hover:opacity-100 text-civic-blue" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
