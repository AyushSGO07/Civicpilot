import * as React from "react";
import Link from "next/link";
import {
  Lock,
  ArrowRight,
  Sparkles,
  Bot,
  ExternalLink,
  ShieldCheck,
} from "lucide-react";
import { HeroSearch } from "@/components/hero-search";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const FEATURES = [
  {
    icon: Sparkles,
    badge: "Discovery",
    title: "1-Click Scheme Matcher",
    description:
      "Intelligently evaluates age, income, caste, state, and occupation rules to match your exact citizen entitlements.",
  },
  {
    icon: Bot,
    badge: "Automation",
    title: "Autonomous Portal Agent",
    description:
      "Playwright-powered browser automation that navigates complex government forms and uploads verified documents.",
  },
  {
    icon: ShieldCheck,
    badge: "Security",
    title: "Human-in-the-Loop Gate",
    description:
      "Zero blind submissions. You review every pre-filled field and provide OTP/CAPTCHA verification before final submission.",
  },
  {
    icon: Lock,
    badge: "Vault",
    title: "Encrypted Document Vault",
    description:
      "Store Aadhaar, Income Certificates, and Passports with field-level redaction and strict AES encryption.",
  },
];

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-canvas">
      {/* Hero Search Section */}
      <HeroSearch />

      {/* Trust & Stats Bar */}
      <section className="border-y border-slate-200/80 bg-white py-6">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-4 text-center sm:grid-cols-4 sm:gap-8">
            <div className="p-2">
              <p className="text-2xl sm:text-3xl font-black text-navy">2,400+</p>
              <p className="text-xs sm:text-sm font-medium text-slate-500">Government Schemes</p>
            </div>
            <div className="p-2">
              <p className="text-2xl sm:text-3xl font-black text-civic-blue">100%</p>
              <p className="text-xs sm:text-sm font-medium text-slate-500">Official Portals Only</p>
            </div>
            <div className="p-2">
              <p className="text-2xl sm:text-3xl font-black text-navy">Zero</p>
              <p className="text-xs sm:text-sm font-medium text-slate-500">Dummy Data Policy</p>
            </div>
            <div className="p-2">
              <p className="text-2xl sm:text-3xl font-black text-emerald-600">Strict</p>
              <p className="text-xs sm:text-sm font-medium text-slate-500">Human Approval Gate</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Grid */}
      <section className="py-16 sm:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <Badge variant="cyan" className="mb-3">
              Autonomous Citizen Portal
            </Badge>
            <h2 className="text-2xl sm:text-4xl font-bold tracking-tight text-navy">
              Bureaucratic Execution, Not Another Chatbot
            </h2>
            <p className="mt-3 text-sm sm:text-base text-slate-600">
              CivicPilot bridges the gap between searching for a scheme and successfully submitting an application on real government portals.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <Card
                  key={idx}
                  className="group relative flex flex-col justify-between transition-all duration-200 hover:-translate-y-1 hover:border-civic-blue/40"
                >
                  <CardHeader>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-civic-blue-light text-civic-blue transition-colors group-hover:bg-civic-blue group-hover:text-white">
                        <Icon className="h-6 w-6" />
                      </div>
                      <Badge variant="secondary" className="text-[11px]">
                        {feature.badge}
                      </Badge>
                    </div>
                    <CardTitle className="text-base sm:text-lg">
                      {feature.title}
                    </CardTitle>
                    <CardDescription className="text-xs sm:text-sm mt-2 leading-relaxed">
                      {feature.description}
                    </CardDescription>
                  </CardHeader>

                  <CardContent className="pt-0">
                    <div className="flex items-center text-xs font-semibold text-civic-blue group-hover:underline">
                      <span>Learn more</span>
                      <ArrowRight className="ml-1 h-3.5 w-3.5" />
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Live Service Guarantee Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-8 text-slate-600">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-semibold text-navy">CivicPilot Engine v1.0.0</span>
            <span>— Connected to National Portal Directories</span>
          </div>

          <div className="flex items-center gap-6">
            <Link href="/services" className="hover:text-civic-blue hover:underline">
              All Schemes
            </Link>
            <Link href="/applications" className="hover:text-civic-blue hover:underline">
              Application Tracker
            </Link>
            <Link href="/documents" className="hover:text-civic-blue hover:underline">
              Document Vault
            </Link>
            <a
              href="https://myscheme.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-slate-500 hover:text-navy"
            >
              <span>MyScheme Official</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
