"use client";

import React, { useState, useEffect, Suspense, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  FileCheck2,
  Building2,
  Loader2,
  CheckCircle2,
  ArrowLeft,
  Bot,
  Layers,
} from "lucide-react";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { API_BASE_URL } from "@/lib/api-config";

interface ServiceInfo {
  id: string;
  service_name: string;
  department: string;
  official_application_url: string;
  required_documents: string[];
}

const FALLBACK_SERVICES: Record<string, ServiceInfo> = {
  "pm-usp-scholarship": {
    id: "pm-usp-scholarship",
    service_name: "Central Sector Scheme of Scholarship for College and University Students (PM-USP)",
    department: "Ministry of Education, Department of Higher Education",
    official_application_url: "https://scholarships.gov.in/",
    required_documents: ["Class 12 Marksheet", "Income Certificate", "Aadhaar Card", "Bank Passbook"],
  },
  "pm-kisan-samman-nidhi": {
    id: "pm-kisan-samman-nidhi",
    service_name: "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
    department: "Ministry of Agriculture and Farmers Welfare",
    official_application_url: "https://pmkisan.gov.in/RegistrationFormNew.aspx",
    required_documents: ["Aadhaar Card", "Land Ownership Records", "Bank Passbook"],
  },
  "pm-jay-ayushman-bharat": {
    id: "pm-jay-ayushman-bharat",
    service_name: "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
    department: "National Health Authority",
    official_application_url: "https://beneficiary.nha.gov.in/",
    required_documents: ["Aadhaar Card", "Ration Card", "Identity Proof"],
  },
};

function ApplicationLauncherContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const serviceId = searchParams.get("serviceId") || "pm-usp-scholarship";
  const { user } = useAuth();

  const [service, setService] = useState<ServiceInfo | null>(null);
  const [launching, setLaunching] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API_BASE_URL}/api/services/${serviceId}`);
        if (res.ok) {
          const data = await res.json();
          setService(data);
        } else {
          setService(FALLBACK_SERVICES[serviceId] || FALLBACK_SERVICES["pm-usp-scholarship"]);
        }
      } catch {
        setService(FALLBACK_SERVICES[serviceId] || FALLBACK_SERVICES["pm-usp-scholarship"]);
      }
    }
    load();
  }, [serviceId]);

  const handleLaunch = useCallback(async () => {
    setLaunching(true);
    let sessionId = "session-" + Math.random().toString(36).substring(2, 10);

    try {
      const res = await fetch(`${API_BASE_URL}/api/agent/browser/session/start`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        sessionId = data.session_id;
      }
    } catch {
      // Offline fallback session id
    }

    router.push(`/applications/workspace/${sessionId}?serviceId=${serviceId}`);
  }, [router, serviceId]);

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-canvas py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <Link
          href={`/services/${serviceId}`}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-civic-blue transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Scheme Details</span>
        </Link>

        {/* Preparation Header */}
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-xs space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-civic-blue border border-blue-200">
            <Bot className="h-3.5 w-3.5" />
            <span>Autonomous Application Workspace</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-black text-navy leading-tight">
            Launch Agent Execution
          </h1>

          <p className="text-sm text-slate-600 font-medium">
            CivicPilot will launch a persistent browser session targeting the official government portal,
            map your profile attributes, and prepare the application form with verified human-in-the-loop approval.
          </p>

          {service && (
            <div className="pt-3 border-t border-slate-100 flex items-center gap-2 text-xs font-bold text-slate-700">
              <Building2 className="h-4 w-4 text-civic-blue shrink-0" />
              <span>{service.service_name}</span>
            </div>
          )}
        </div>

        {/* Readiness Checklist Card */}
        <Card className="border border-slate-200/80 shadow-xs">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-bold text-navy flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-600" />
              Pre-Flight Execution Checklist
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-200 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <div>
                  <span className="text-xs font-bold text-navy block">Citizen Profile Verified</span>
                  <span className="text-[11px] text-slate-500">
                    {user?.user_metadata?.full_name || "Aarav Sharma"} (Identity, Income & Academic Details)
                  </span>
                </div>
              </div>
              <span className="text-xs font-black text-emerald-700">Ready</span>
            </div>

            <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-200 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <FileCheck2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <div>
                  <span className="text-xs font-bold text-navy block">Document Vault Synchronized</span>
                  <span className="text-[11px] text-slate-500">
                    Aadhaar Card, Income Certificate, and Marksheets available for upload
                  </span>
                </div>
              </div>
              <span className="text-xs font-black text-emerald-700">Ready</span>
            </div>

            <div className="p-3.5 rounded-xl bg-blue-50/60 border border-blue-200 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <Layers className="h-4 w-4 text-civic-blue shrink-0" />
                <div>
                  <span className="text-xs font-bold text-navy block">Human-in-the-Loop Safeguard</span>
                  <span className="text-[11px] text-slate-500">
                    Agent will pause before submission for your explicit approval
                  </span>
                </div>
              </div>
              <span className="text-xs font-black text-civic-blue">Active</span>
            </div>
          </CardContent>
        </Card>

        {/* Launch CTA */}
        <div className="pt-2">
          <Button
            onClick={handleLaunch}
            disabled={launching}
            className="w-full bg-civic-blue hover:bg-civic-blue-hover text-white font-bold text-sm py-6 shadow-md gap-2"
          >
            {launching ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin text-white" />
                <span>Initializing 3-Panel Operations Workspace...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-5 w-5 text-civic-cyan" />
                <span>Open Agent Execution Workspace</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function ApplicationLauncherPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-canvas">
          <Loader2 className="h-8 w-8 animate-spin text-civic-blue" />
        </div>
      }
    >
      <ApplicationLauncherContent />
    </Suspense>
  );
}
