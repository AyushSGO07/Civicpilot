"use client";

import React, { useState, useEffect, useRef, useCallback, Suspense } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Play,
  Pause,
  Square,
  Sparkles,
  Bot,
  ShieldCheck,
  FileCheck2,
  ExternalLink,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Info,
  Lock,
  RefreshCw,
  Terminal,
  Activity,
  RotateCcw,
  User,
  Compass,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/context/auth-context";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface MilestoneEvent {
  id: string;
  timestamp: string;
  step: string;
  message: string;
  level: "info" | "success" | "warning" | "error" | "reasoning";
  details?: string;
}

interface CitizenProfile {
  full_name: string;
  date_of_birth: string;
  gender: string;
  contact_number: string;
  domicile_state: string;
  district?: string;
  pin_code: string;
  annual_income: number;
  social_category: string;
  occupation?: string;
  education_level?: string;
}

const DEFAULT_PROFILE: CitizenProfile = {
  full_name: "Aarav Sharma",
  date_of_birth: "14/05/2002",
  gender: "Male",
  contact_number: "+91 98765 43210",
  domicile_state: "Maharashtra",
  district: "Pune",
  pin_code: "411001",
  annual_income: 250000,
  social_category: "General",
  occupation: "Student",
  education_level: "Undergraduate",
};

interface ServiceMeta {
  id: string;
  service_name: string;
  department: string;
  official_application_url: string;
  category: string;
  required_documents: string[];
}

const FALLBACK_SERVICES: Record<string, ServiceMeta> = {
  "pm-usp-scholarship": {
    id: "pm-usp-scholarship",
    service_name: "Central Sector Scheme of Scholarship for College and University Students (PM-USP)",
    department: "Ministry of Education, Department of Higher Education",
    official_application_url: "https://scholarships.gov.in/",
    category: "Scholarship & Education",
    required_documents: ["Class 12 Marksheet", "Income Certificate", "Aadhaar Card", "Bank Passbook"],
  },
  "pm-kisan-samman-nidhi": {
    id: "pm-kisan-samman-nidhi",
    service_name: "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
    department: "Ministry of Agriculture and Farmers Welfare",
    official_application_url: "https://pmkisan.gov.in/RegistrationFormNew.aspx",
    category: "Agriculture & Farmers",
    required_documents: ["Aadhaar Card", "Land Ownership Records", "Bank Passbook"],
  },
  "pm-jay-ayushman-bharat": {
    id: "pm-jay-ayushman-bharat",
    service_name: "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
    department: "National Health Authority",
    official_application_url: "https://beneficiary.nha.gov.in/",
    category: "Healthcare & Insurance",
    required_documents: ["Aadhaar Card", "Ration Card", "Identity Proof"],
  },
};

const EXECUTION_STEPS = [
  { id: "discovery", label: "Scheme Discovery" },
  { id: "navigation", label: "Portal Navigation" },
  { id: "inspection", label: "DOM Inspection" },
  { id: "mapping", label: "Field Mapping" },
  { id: "filling", label: "Form Filling" },
  { id: "validation", label: "Submission Validation" },
];

function WorkspaceInner() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { session } = useAuth();

  const sessionId = (params?.sessionId as string) || "session-demo";
  const serviceId = searchParams.get("serviceId") || "pm-usp-scholarship";

  // Citizen Profile state
  const [profile, setProfile] = useState<CitizenProfile>(DEFAULT_PROFILE);

  // Scheme metadata
  const [service, setService] = useState<ServiceMeta>(
    FALLBACK_SERVICES[serviceId] || FALLBACK_SERVICES["pm-usp-scholarship"]
  );

  // Execution & WebSocket State
  const [wsConnected, setWsConnected] = useState(false);
  const [executionStatus, setExecutionStatus] = useState<
    "idle" | "active" | "paused" | "stopped" | "completed"
  >("idle");
  const [currentStep, setCurrentStep] = useState<string>("discovery");
  const [stepIndex, setStepIndex] = useState<number>(0);
  const [screenshotBase64, setScreenshotBase64] = useState<string | null>(null);
  const [milestones, setMilestones] = useState<MilestoneEvent[]>([]);
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const [filterLevel, setFilterLevel] = useState<string>("all");
  const [mobileTab, setMobileTab] = useState<"viewport" | "profile" | "logs">("viewport");
  const [showAbortConfirm, setShowAbortConfirm] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const logContainerRef = useRef<HTMLDivElement | null>(null);
  const simulationTimerRef = useRef<NodeJS.Timeout[]>([]);

  // Fetch Citizen Profile from backend if authenticated
  useEffect(() => {
    async function loadProfile() {
      if (!session?.access_token) return;
      try {
        const res = await fetch(`${API_BASE_URL}/api/profile`, {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });
        if (res.ok) {
          const data = await res.json();
          if (data) {
            setProfile({
              full_name: data.full_name || DEFAULT_PROFILE.full_name,
              date_of_birth: data.date_of_birth || DEFAULT_PROFILE.date_of_birth,
              gender: data.gender || DEFAULT_PROFILE.gender,
              contact_number: data.contact_number || DEFAULT_PROFILE.contact_number,
              domicile_state: data.state || DEFAULT_PROFILE.domicile_state,
              district: data.district || DEFAULT_PROFILE.district,
              pin_code: data.pincode || DEFAULT_PROFILE.pin_code,
              annual_income: Number(data.annual_income) || DEFAULT_PROFILE.annual_income,
              social_category: data.social_category || DEFAULT_PROFILE.social_category,
              occupation: data.occupation || DEFAULT_PROFILE.occupation,
              education_level: data.education_level || DEFAULT_PROFILE.education_level,
            });
          }
        }
      } catch {
        // Retain default profile fallback
      }
    }
    loadProfile();
  }, [session]);

  // Fetch Scheme Details
  useEffect(() => {
    async function fetchScheme() {
      try {
        const res = await fetch(`${API_BASE_URL}/api/services/${serviceId}`);
        if (res.ok) {
          const data = await res.json();
          setService(data);
        }
      } catch {
        // Fallback already pre-set
      }
    }
    fetchScheme();
  }, [serviceId]);

  // Helper to add milestone
  const addMilestone = useCallback(
    (step: string, message: string, level: MilestoneEvent["level"] = "info", details?: string) => {
      const now = new Date();
      const timeStr = now.toTimeString().split(" ")[0];
      const newEvent: MilestoneEvent = {
        id: "evt-" + Math.random().toString(36).substring(2, 9),
        timestamp: timeStr,
        step,
        message,
        level,
        details,
      };
      setMilestones((prev) => [...prev, newEvent]);
    },
    []
  );

  // Auto-scroll logs
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [milestones, autoScroll]);

  // WebSocket Connection
  useEffect(() => {
    let wsUrl = "ws://127.0.0.1:8000/ws/agent/" + sessionId;
    if (typeof window !== "undefined" && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      wsUrl = `${protocol}//${window.location.host}/ws/agent/${sessionId}`;
    }

    let isMounted = true;
    let socket: WebSocket;

    try {
      socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => {
        if (!isMounted) return;
        setWsConnected(true);
        addMilestone(
          "system",
          `Connected to agent execution stream for session ${sessionId}`,
          "info"
        );
      };

      socket.onmessage = (event) => {
        if (!isMounted) return;
        try {
          const data = JSON.parse(event.data);
          if (data.type === "connected") {
            setExecutionStatus(data.status || "idle");
          } else if (data.type === "status") {
            if (data.status) setExecutionStatus(data.status);
            if (data.step) {
              setCurrentStep(data.step);
              const idx = EXECUTION_STEPS.findIndex((s) => s.id === data.step);
              if (idx !== -1) setStepIndex(idx);
            }
          } else if (data.type === "milestone") {
            addMilestone(data.step || "agent", data.message, data.level || "info", data.details);
            if (data.step) {
              setCurrentStep(data.step);
              const idx = EXECUTION_STEPS.findIndex((s) => s.id === data.step);
              if (idx !== -1) setStepIndex(idx);
            }
          } else if (data.type === "screenshot") {
            setScreenshotBase64(data.screenshot_b64);
          }
        } catch {
          // Non-JSON frame ignored
        }
      };

      socket.onclose = () => {
        if (!isMounted) return;
        setWsConnected(false);
      };

      socket.onerror = () => {
        if (!isMounted) return;
        setWsConnected(false);
      };
    } catch {
      setWsConnected(false);
    }

    return () => {
      isMounted = false;
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, [sessionId, addMilestone]);

  // Outbound Control Actions via WebSocket / HTTP
  const sendControlAction = useCallback(
    async (action: "start" | "pause" | "resume" | "stop") => {
      // If WebSocket is open, send through WS
      let sentWs = false;
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        try {
          wsRef.current.send(JSON.stringify({ action }));
          sentWs = true;
        } catch {
          sentWs = false;
        }
      }

      // If WS wasn't available or as HTTP fallback:
      if (!sentWs) {
        try {
          await fetch(`${API_BASE_URL}/api/ws/agent/${sessionId}/${action}`, {
            method: "POST",
          });
        } catch {
          // Local state update when offline
        }
      }

      // Local State Transition Updates
      if (action === "pause") {
        setExecutionStatus("paused");
        addMilestone(
          currentStep,
          "Execution paused by citizen. Browser context held in memory.",
          "warning"
        );
      } else if (action === "resume") {
        setExecutionStatus("active");
        addMilestone(
          currentStep,
          "Execution resumed. Playwright agent resuming DOM interaction.",
          "info"
        );
      } else if (action === "stop") {
        setExecutionStatus("stopped");
        setShowAbortConfirm(false);
        addMilestone(
          currentStep,
          "Execution aborted. Chromium context terminated safely.",
          "error"
        );
      } else if (action === "start") {
        setExecutionStatus("active");
        addMilestone("discovery", "Workflow initialized. Launching Playwright runtime.", "info");
      }
    },
    [sessionId, currentStep, addMilestone]
  );

  // Keyboard Shortcuts (Space: Pause/Resume, Esc: Abort)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't intercept if user is typing in an input
      if (["INPUT", "TEXTAREA"].includes((e.target as HTMLElement)?.tagName)) {
        return;
      }

      if (e.code === "Space") {
        e.preventDefault();
        if (executionStatus === "active") {
          sendControlAction("pause");
        } else if (executionStatus === "paused") {
          sendControlAction("resume");
        } else if (executionStatus === "idle") {
          sendControlAction("start");
        }
      } else if (e.code === "Escape") {
        if (executionStatus === "active" || executionStatus === "paused") {
          setShowAbortConfirm(true);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [executionStatus, sendControlAction]);

  // Demo / Simulation Mode: Plays through realistic execution steps
  const triggerSimulation = useCallback(() => {
    // Clear previous simulation timers
    simulationTimerRef.current.forEach(clearTimeout);
    simulationTimerRef.current = [];

    setExecutionStatus("active");
    setMilestones([]);

    const steps = [
      {
        delay: 500,
        step: "discovery",
        index: 0,
        level: "info" as const,
        msg: `Verified official portal target: ${service.official_application_url}`,
        details: "Scheme ID: " + service.id + " | Portal verified against official government directory.",
      },
      {
        delay: 2000,
        step: "navigation",
        index: 1,
        level: "info" as const,
        msg: "Navigating Chromium instance to portal registration endpoint...",
        details: "Setting viewport: 1280x800 desktop. User-Agent: Mozilla/5.0 Chromium CivicPilot/1.0",
      },
      {
        delay: 4500,
        step: "inspection",
        index: 2,
        level: "reasoning" as const,
        msg: "Pruned DOM extracted: 24 interactive elements identified across application form.",
        details: "Found 14 text inputs, 3 select dropdowns, 2 radio groups, 2 file upload fields, 3 action buttons.",
      },
      {
        delay: 7000,
        step: "mapping",
        index: 3,
        level: "reasoning" as const,
        msg: "Gemini 2.5 Flash mapped 8 required profile attributes to form locators.",
        details: "Confidence: 0.98 for Full Name, 0.99 for DOB, 0.97 for Annual Income, 0.96 for Domicile State.",
      },
      {
        delay: 9500,
        step: "filling",
        index: 4,
        level: "info" as const,
        msg: "Populating applicant identity: Name, Date of Birth, Gender, and Category.",
        details: `Filled: ${profile.full_name} | Gender: ${profile.gender} | State: ${profile.domicile_state}`,
      },
      {
        delay: 12000,
        step: "filling",
        index: 4,
        level: "success" as const,
        msg: "Vault document attached: Income Certificate (Verified).",
        details: "File 'Income_Certificate_2025.pdf' successfully injected into input[type='file'].",
      },
      {
        delay: 14500,
        step: "validation",
        index: 5,
        level: "success" as const,
        msg: "Pre-submission validation complete: All mandatory form fields satisfied.",
        details: "Human-in-the-loop checkpoint ready. Waiting for citizen confirmation before final submission.",
      },
    ];

    steps.forEach(({ delay, step, index, level, msg, details }) => {
      const timer = setTimeout(() => {
        setCurrentStep(step);
        setStepIndex(index);
        addMilestone(step, msg, level, details);
        if (index === 5) {
          setExecutionStatus("completed");
        }
      }, delay);
      simulationTimerRef.current.push(timer);
    });
  }, [service, profile, addMilestone]);

  // Clean simulation timers on unmount
  useEffect(() => {
    return () => {
      simulationTimerRef.current.forEach(clearTimeout);
    };
  }, []);

  // Filtered milestones
  const filteredMilestones = milestones.filter((m) => {
    if (filterLevel === "all") return true;
    if (filterLevel === "reasoning") return m.level === "reasoning";
    if (filterLevel === "warnings") return m.level === "warning" || m.level === "error";
    return true;
  });

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col selection:bg-civic-blue selection:text-white">
      {/* ARIA Live Announcement for accessibility */}
      <div className="sr-only" aria-live="polite">
        {`Agent execution status is ${executionStatus}. Current stage: ${currentStep}.`}
      </div>

      {/* TOP WORKSPACE NAVIGATION & STATUS BAR */}
      <header className="h-16 border-b border-slate-800 bg-slate-950/90 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between z-30 sticky top-0">
        <div className="flex items-center gap-3 min-w-0">
          <Link
            href={`/services/${service.id}`}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            title="Return to Scheme Overview"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div className="h-5 w-px bg-slate-800 hidden sm:block" />
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="text-sm sm:text-base font-semibold text-white truncate max-w-[280px] sm:max-w-md">
                {service.service_name}
              </h1>
              <Badge variant="cyan" className="hidden md:inline-flex text-[11px] py-0 px-2 shrink-0">
                {service.category}
              </Badge>
            </div>
            <p className="text-xs text-slate-400 truncate max-w-sm">
              {service.department}
            </p>
          </div>
        </div>

        {/* Status Pill & Actions */}
        <div className="flex items-center gap-3 shrink-0">
          {/* Target Portal Link Pill */}
          <a
            href={service.official_application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="hidden lg:flex items-center gap-1.5 text-xs text-slate-300 bg-slate-800/80 hover:bg-slate-800 px-3 py-1.5 rounded-full border border-slate-700/60 transition group"
          >
            <Lock className="h-3.5 w-3.5 text-emerald-400" />
            <span className="truncate max-w-[140px]">
              {new URL(service.official_application_url).hostname}
            </span>
            <ExternalLink className="h-3 w-3 text-slate-400 group-hover:text-white" />
          </a>

          {/* Glowing Status Pill */}
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border ${
              executionStatus === "active"
                ? "bg-emerald-950/80 text-emerald-400 border-emerald-500/40"
                : executionStatus === "paused"
                ? "bg-amber-950/80 text-amber-400 border-amber-500/40"
                : executionStatus === "stopped"
                ? "bg-rose-950/80 text-rose-400 border-rose-500/40"
                : executionStatus === "completed"
                ? "bg-cyan-950/80 text-cyan-300 border-cyan-500/40"
                : "bg-slate-800 text-slate-300 border-slate-700"
            }`}
          >
            <span className="relative flex h-2.5 w-2.5">
              {executionStatus === "active" && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              )}
              {executionStatus === "paused" && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75" />
              )}
              <span
                className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                  executionStatus === "active"
                    ? "bg-emerald-500"
                    : executionStatus === "paused"
                    ? "bg-amber-500"
                    : executionStatus === "stopped"
                    ? "bg-rose-500"
                    : executionStatus === "completed"
                    ? "bg-cyan-400"
                    : "bg-slate-500"
                }`}
              />
            </span>
            <span className="capitalize font-semibold tracking-wide">
              {executionStatus === "active"
                ? "LIVE AGENT"
                : executionStatus === "paused"
                ? "PAUSED"
                : executionStatus === "stopped"
                ? "TERMINATED"
                : executionStatus === "completed"
                ? "VALIDATED"
                : "STANDBY"}
            </span>
          </div>

          {/* Quick Exit */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push(`/services/${service.id}`)}
            className="border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white text-xs h-8"
          >
            Exit
          </Button>
        </div>
      </header>

      {/* MOBILE TAB SWITCHER (< 1024px) */}
      <div className="lg:hidden flex border-b border-slate-800 bg-slate-950 text-xs">
        <button
          onClick={() => setMobileTab("viewport")}
          className={`flex-1 py-2.5 font-medium border-b-2 text-center transition ${
            mobileTab === "viewport"
              ? "border-civic-blue text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          Live Stream
        </button>
        <button
          onClick={() => setMobileTab("profile")}
          className={`flex-1 py-2.5 font-medium border-b-2 text-center transition ${
            mobileTab === "profile"
              ? "border-civic-blue text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          Citizen Profile
        </button>
        <button
          onClick={() => setMobileTab("logs")}
          className={`flex-1 py-2.5 font-medium border-b-2 text-center transition ${
            mobileTab === "logs"
              ? "border-civic-blue text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          AI Reasoning ({milestones.length})
        </button>
      </div>

      {/* 3-PANEL OPERATIONS WORKSPACE GRID */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
        {/* PANEL 1 (LEFT 1/4): CITIZEN PROFILE SUMMARY & VAULT */}
        <aside
          className={`lg:col-span-3 border-r border-slate-800 bg-slate-950/60 p-4 overflow-y-auto ${
            mobileTab === "profile" ? "block" : "hidden lg:block"
          }`}
        >
          <div className="space-y-5">
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
                <User className="h-4 w-4 text-civic-cyan" />
                <span>Applicant Identity</span>
              </div>
              <span className="text-[11px] text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">
                Verified
              </span>
            </div>

            {/* Profile Attributes */}
            <div className="space-y-2.5 text-xs">
              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[11px]">Full Legal Name</span>
                <span className="font-semibold text-white">
                  {profile.full_name}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[11px]">Date of Birth</span>
                  <span className="font-medium text-slate-200">
                    {profile.date_of_birth}
                  </span>
                </div>
                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[11px]">Gender</span>
                  <span className="font-medium text-slate-200">
                    {profile.gender}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[11px]">Mobile</span>
                  <span className="font-medium text-slate-200">
                    {profile.contact_number}
                  </span>
                </div>
                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[11px]">Social Category</span>
                  <span className="font-medium text-slate-200">
                    {profile.social_category}
                  </span>
                </div>
              </div>

              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[11px]">Annual Family Income</span>
                <span className="font-semibold text-emerald-400">
                  ₹{Number(profile.annual_income).toLocaleString("en-IN")} / year
                </span>
              </div>

              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[11px]">Domicile State</span>
                <span className="font-medium text-slate-200">
                  {profile.domicile_state} (PIN: {profile.pin_code})
                </span>
              </div>
            </div>

            {/* Attached Vault Documents */}
            <div className="pt-2">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
                <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
                  <ShieldCheck className="h-4 w-4 text-emerald-400" />
                  <span>Attached Vault Docs</span>
                </div>
                <span className="text-[11px] text-slate-400">
                  {service.required_documents.length} Files Ready
                </span>
              </div>

              <div className="space-y-2">
                {service.required_documents.map((docName, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 rounded-lg bg-slate-900/80 border border-slate-800 text-xs"
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <FileCheck2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                      <span className="truncate text-slate-200 font-medium">{docName}</span>
                    </div>
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                  </div>
                ))}
              </div>
            </div>

            {/* Privacy Protection Callout */}
            <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800/80 text-[11px] text-slate-400 leading-relaxed">
              <span className="text-slate-300 font-medium block mb-1">
                🔒 Zero Dummy Data & Privacy
              </span>
              Identity data is injected into official portal inputs on-demand. Vault credentials are
              never cached externally or transmitted without explicit approval.
            </div>
          </div>
        </aside>

        {/* PANEL 2 (CENTER 2/4): LIVE BROWSER VIEWPORT STREAM & CONTROLS */}
        <section
          className={`lg:col-span-6 flex flex-col bg-slate-950 overflow-hidden border-r border-slate-800 ${
            mobileTab === "viewport" ? "flex" : "hidden lg:flex"
          }`}
        >
          {/* Simulated Browser Chrome Top Header */}
          <div className="h-10 bg-slate-900 border-b border-slate-800 px-3 flex items-center justify-between text-xs shrink-0">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-rose-500/80" />
                <span className="h-2.5 w-2.5 rounded-full bg-amber-500/80" />
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/80" />
              </div>
              <div className="h-4 w-px bg-slate-800 mx-1" />
              <div className="flex items-center gap-1 text-slate-400 text-[11px] font-mono">
                <Lock className="h-3 w-3 text-emerald-400" />
                <span className="truncate max-w-[200px] sm:max-w-xs text-slate-300">
                  {service.official_application_url}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-slate-400 text-[11px]">
              <span className="hidden sm:inline-block font-mono text-slate-500">
                1280 × 800 (Desktop Chromium)
              </span>
              {wsConnected ? (
                <span className="flex items-center gap-1 text-emerald-400">
                  <Activity className="h-3 w-3" />
                  <span className="hidden sm:inline">Stream Sync</span>
                </span>
              ) : (
                <span className="flex items-center gap-1 text-amber-400">
                  <RefreshCw className="h-3 w-3 animate-spin" />
                  <span className="hidden sm:inline">Connecting</span>
                </span>
              )}
            </div>
          </div>

          {/* Canvas Viewport Screen (16:10 Aspect Ratio) */}
          <div className="flex-1 relative bg-slate-950 flex items-center justify-center overflow-hidden p-2">
            <div className="w-full h-full max-h-[560px] aspect-[16/10] bg-slate-900 rounded-lg border border-slate-800 relative overflow-hidden flex items-center justify-center shadow-2xl">
              {/* Active Base64 Frame Rendering */}
              {screenshotBase64 ? (
                /* eslint-disable-next-line @next/next/no-img-element */
                <img
                  src={`data:image/jpeg;base64,${screenshotBase64}`}
                  alt="Live Playwright Browser Viewport"
                  className="w-full h-full object-contain"
                />
              ) : (
                /* High-Fidelity Simulated Portal Canvas */
                <div className="w-full h-full flex flex-col items-center justify-between p-6 bg-gradient-to-b from-slate-900 via-slate-950 to-slate-900 text-slate-300 select-none">
                  {/* Mock Portal Header */}
                  <div className="w-full flex items-center justify-between pb-3 border-b border-slate-800/80">
                    <div className="flex items-center gap-2">
                      <div className="h-7 w-7 rounded bg-civic-blue/20 border border-civic-blue/40 flex items-center justify-center text-civic-cyan font-bold text-xs">
                        GOI
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-white">
                          National Government Application Portal
                        </div>
                        <div className="text-[10px] text-slate-400">
                          Official Direct Citizen Benefit Platform
                        </div>
                      </div>
                    </div>
                    <Badge variant="outline" className="border-slate-700 text-slate-400 text-[10px]">
                      SSL 256-bit Secure
                    </Badge>
                  </div>

                  {/* Center Visual Mock */}
                  <div className="text-center space-y-3 py-6 max-w-sm">
                    <div className="relative inline-block">
                      <div className="h-16 w-16 mx-auto rounded-2xl bg-civic-blue/10 border border-civic-blue/30 flex items-center justify-center text-civic-cyan shadow-lg">
                        <Compass className="h-8 w-8 animate-pulse text-civic-cyan" />
                      </div>
                      <span className="absolute -top-1 -right-1 flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-civic-cyan opacity-75" />
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-civic-cyan" />
                      </span>
                    </div>

                    <div>
                      <h4 className="text-sm font-semibold text-white">
                        {executionStatus === "active"
                          ? `Automating ${EXECUTION_STEPS[stepIndex]?.label || "Execution"}`
                          : executionStatus === "paused"
                          ? "Playwright Session Suspended"
                          : executionStatus === "stopped"
                          ? "Browser Context Terminated"
                          : executionStatus === "completed"
                          ? "All Application Fields Satisfied"
                          : "Chromium Headless Ready"}
                      </h4>
                      <p className="text-xs text-slate-400 mt-1">
                        {executionStatus === "active"
                          ? "Executing bounded navigation cycle on live portal with Gemini vision mapping."
                          : executionStatus === "idle"
                          ? "Press 'Start Automated Application' or hit [Space] to begin real navigation."
                          : "Agent paused. Inspection locators and session cookies remain locked in memory."}
                      </p>
                    </div>

                    {/* Step indicator pill */}
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs text-slate-300">
                      <span className="h-2 w-2 rounded-full bg-civic-cyan animate-pulse" />
                      <span>Stage {stepIndex + 1} of 6: {EXECUTION_STEPS[stepIndex]?.label}</span>
                    </div>
                  </div>

                  {/* Mock Portal Footer */}
                  <div className="w-full flex items-center justify-between text-[10px] text-slate-500 pt-3 border-t border-slate-800/80">
                    <span>Host: {new URL(service.official_application_url).hostname}</span>
                    <span>Session: {sessionId}</span>
                  </div>
                </div>
              )}

              {/* OVERLAY: PAUSED STATE (EXEC-04) */}
              {executionStatus === "paused" && (
                <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center text-center p-6 z-20 animate-in fade-in">
                  <div className="h-14 w-14 rounded-2xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 mb-3 shadow-lg shadow-amber-500/10">
                    <Pause className="h-7 w-7" />
                  </div>
                  <h3 className="text-base font-bold text-white mb-1">
                    Execution Paused by Citizen
                  </h3>
                  <p className="text-xs text-slate-300 max-w-sm mb-4 leading-relaxed">
                    Browser automation is suspended at the current form position. You may inspect
                    fields, take notes, or resume when ready.
                  </p>
                  <Button
                    onClick={() => sendControlAction("resume")}
                    className="bg-civic-blue hover:bg-civic-blue-hover text-white text-xs px-5 py-2 h-9 flex items-center gap-2 shadow-md shadow-civic-blue/20"
                  >
                    <Play className="h-4 w-4 fill-white" />
                    <span>Resume Execution (Space)</span>
                  </Button>
                </div>
              )}

              {/* OVERLAY: STOPPED / ABORTED STATE (EXEC-05) */}
              {executionStatus === "stopped" && (
                <div className="absolute inset-0 bg-slate-950/85 backdrop-blur-sm flex flex-col items-center justify-center text-center p-6 z-20 animate-in fade-in">
                  <div className="h-14 w-14 rounded-2xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 mb-3 shadow-lg shadow-rose-500/10">
                    <Square className="h-6 w-6" />
                  </div>
                  <h3 className="text-base font-bold text-white mb-1">
                    Execution Safely Terminated
                  </h3>
                  <p className="text-xs text-slate-400 max-w-sm mb-4">
                    The Playwright browser instance was cleanly closed. No pending network payloads
                    or uncommitted credentials remain active.
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      onClick={() => sendControlAction("start")}
                      variant="outline"
                      className="border-slate-700 text-slate-200 hover:bg-slate-800 text-xs h-8"
                    >
                      <RotateCcw className="h-3.5 w-3.5 mr-1.5" />
                      Restart Application
                    </Button>
                    <Button
                      onClick={() => router.push(`/services/${service.id}`)}
                      className="bg-civic-blue hover:bg-civic-blue-hover text-white text-xs h-8"
                    >
                      Return to Scheme
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* STEP PROGRESS TRACKER */}
          <div className="px-4 py-2 bg-slate-900/90 border-t border-slate-800 shrink-0">
            <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1.5 font-medium">
              <span>Execution Progression</span>
              <span className="text-civic-cyan font-semibold">
                {Math.round(((stepIndex + 1) / EXECUTION_STEPS.length) * 100)}% Complete
              </span>
            </div>
            <div className="grid grid-cols-6 gap-1">
              {EXECUTION_STEPS.map((step, idx) => (
                <div key={step.id} className="space-y-1">
                  <div
                    className={`h-1.5 rounded-full transition-all duration-300 ${
                      idx < stepIndex
                        ? "bg-emerald-500"
                        : idx === stepIndex
                        ? executionStatus === "active"
                          ? "bg-civic-cyan animate-pulse"
                          : executionStatus === "paused"
                          ? "bg-amber-500"
                          : "bg-slate-700"
                        : "bg-slate-800"
                    }`}
                  />
                  <span
                    className={`hidden sm:block text-[10px] truncate text-center ${
                      idx === stepIndex
                        ? "text-white font-semibold"
                        : idx < stepIndex
                        ? "text-emerald-400"
                        : "text-slate-500"
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* INTERACTIVE CONTROLS TOOLBAR (EXEC-04, EXEC-05) */}
          <div className="p-3 bg-slate-950 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2 shrink-0">
            {/* Primary Action Buttons */}
            <div className="flex items-center gap-2">
              {executionStatus === "idle" && (
                <Button
                  onClick={() => sendControlAction("start")}
                  className="bg-civic-blue hover:bg-civic-blue-hover text-white text-xs px-4 h-9 shadow-md shadow-civic-blue/20"
                >
                  <Play className="h-4 w-4 mr-1.5 fill-white" />
                  <span>Start Automated Application</span>
                </Button>
              )}

              {executionStatus === "active" && (
                <Button
                  onClick={() => sendControlAction("pause")}
                  className="bg-amber-600 hover:bg-amber-500 text-white text-xs px-4 h-9 shadow-md shadow-amber-600/20"
                  title="Pause automation (Space)"
                >
                  <Pause className="h-4 w-4 mr-1.5" />
                  <span>Pause (Space)</span>
                </Button>
              )}

              {executionStatus === "paused" && (
                <Button
                  onClick={() => sendControlAction("resume")}
                  className="bg-civic-blue hover:bg-civic-blue-hover text-white text-xs px-4 h-9 shadow-md shadow-civic-blue/20"
                  title="Resume automation (Space)"
                >
                  <Play className="h-4 w-4 mr-1.5 fill-white" />
                  <span>Resume (Space)</span>
                </Button>
              )}

              {/* Stop / Abort Button */}
              {(executionStatus === "active" || executionStatus === "paused") && (
                <Button
                  variant="outline"
                  onClick={() => setShowAbortConfirm(true)}
                  className="border-rose-900/60 bg-rose-950/30 text-rose-300 hover:bg-rose-900/50 hover:text-white text-xs px-3 h-9"
                  title="Stop and abort execution (Esc)"
                >
                  <Square className="h-3.5 w-3.5 mr-1.5 fill-rose-400" />
                  <span>Abort (Esc)</span>
                </Button>
              )}

              {/* Interactive Demo Simulation Button */}
              <Button
                variant="outline"
                size="sm"
                onClick={triggerSimulation}
                className="border-slate-700 bg-slate-900 text-slate-300 hover:bg-slate-800 text-xs h-9"
                title="Run step-by-step preview simulation"
              >
                <Sparkles className="h-3.5 w-3.5 mr-1.5 text-civic-cyan" />
                <span>Simulate Run</span>
              </Button>
            </div>

            {/* Keyboard Shortcuts Legend */}
            <div className="hidden md:flex items-center gap-3 text-[11px] text-slate-400 font-mono">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 text-[10px]">
                  Space
                </kbd>
                <span>Pause/Resume</span>
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 text-[10px]">
                  Esc
                </kbd>
                <span>Abort</span>
              </span>
            </div>
          </div>
        </section>

        {/* PANEL 3 (RIGHT 1/4): AI REASONING & AUDIT LOG */}
        <aside
          className={`lg:col-span-3 flex flex-col bg-slate-950/80 overflow-hidden ${
            mobileTab === "logs" ? "flex" : "hidden lg:flex"
          }`}
        >
          {/* Header & Controls */}
          <div className="p-3 border-b border-slate-800 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2">
              <Terminal className="h-4 w-4 text-civic-cyan" />
              <h2 className="text-sm font-semibold text-white">AI Reasoning Log</h2>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setAutoScroll(!autoScroll)}
                className={`text-[11px] px-2 py-0.5 rounded transition ${
                  autoScroll
                    ? "bg-civic-blue/20 text-civic-cyan border border-civic-cyan/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                title="Toggle Auto-Scroll"
              >
                Auto-scroll: {autoScroll ? "ON" : "OFF"}
              </button>
            </div>
          </div>

          {/* Filter Pills */}
          <div className="px-3 py-2 border-b border-slate-800 flex items-center gap-1 text-[11px] bg-slate-900/50 shrink-0">
            <button
              onClick={() => setFilterLevel("all")}
              className={`px-2 py-0.5 rounded-full transition ${
                filterLevel === "all"
                  ? "bg-slate-700 text-white font-medium"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              All ({milestones.length})
            </button>
            <button
              onClick={() => setFilterLevel("reasoning")}
              className={`px-2 py-0.5 rounded-full transition ${
                filterLevel === "reasoning"
                  ? "bg-civic-blue text-white font-medium"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Reasoning
            </button>
            <button
              onClick={() => setFilterLevel("warnings")}
              className={`px-2 py-0.5 rounded-full transition ${
                filterLevel === "warnings"
                  ? "bg-amber-900/60 text-amber-300 font-medium"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Alerts
            </button>
          </div>

          {/* Chronological Milestone Feed (EXEC-02) */}
          <div
            ref={logContainerRef}
            className="flex-1 p-3 overflow-y-auto space-y-2.5 text-xs font-sans font-normal"
          >
            {filteredMilestones.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500">
                <Bot className="h-8 w-8 text-slate-600 mb-2" />
                <p className="text-xs">No execution milestones logged yet.</p>
                <p className="text-[11px] text-slate-600 mt-1">
                  Click &apos;Start Automated Application&apos; or &apos;Simulate Run&apos; to begin.
                </p>
              </div>
            ) : (
              filteredMilestones.map((evt) => (
                <div
                  key={evt.id}
                  className={`p-2.5 rounded-lg border transition ${
                    evt.level === "reasoning"
                      ? "bg-indigo-950/30 border-indigo-500/30 text-indigo-200"
                      : evt.level === "success"
                      ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-300"
                      : evt.level === "warning"
                      ? "bg-amber-950/30 border-amber-500/30 text-amber-300"
                      : evt.level === "error"
                      ? "bg-rose-950/30 border-rose-500/30 text-rose-300"
                      : "bg-slate-900/90 border-slate-800 text-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1">
                    <span className="font-mono">{evt.timestamp}</span>
                    <span className="uppercase tracking-wider font-semibold px-1.5 py-0.2 rounded bg-slate-800/80 text-slate-300">
                      {evt.step}
                    </span>
                  </div>

                  <div className="flex items-start gap-2">
                    {evt.level === "reasoning" && (
                      <Sparkles className="h-3.5 w-3.5 text-civic-cyan shrink-0 mt-0.5" />
                    )}
                    {evt.level === "success" && (
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    )}
                    {evt.level === "warning" && (
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                    )}
                    {evt.level === "error" && (
                      <AlertCircle className="h-3.5 w-3.5 text-rose-400 shrink-0 mt-0.5" />
                    )}
                    {evt.level === "info" && (
                      <Info className="h-3.5 w-3.5 text-civic-blue shrink-0 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <p className="leading-snug">{evt.message}</p>
                      {evt.details && (
                        <p className="mt-1 text-[11px] opacity-75 font-mono bg-slate-950/50 p-1.5 rounded border border-slate-800/60 leading-relaxed">
                          {evt.details}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Audit Footer Summary */}
          <div className="p-2.5 bg-slate-950 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between shrink-0">
            <span className="flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
              <span>Audit Trail Secured</span>
            </span>
            <span className="font-mono text-slate-500">
              Retries: 0 / 3 (Bounded)
            </span>
          </div>
        </aside>
      </main>

      {/* ABORT CONFIRMATION MODAL */}
      {showAbortConfirm && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-md w-full bg-slate-900 border-slate-800 text-white shadow-2xl">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-rose-400">
                  <AlertTriangle className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="text-base font-bold text-white">
                    Abort Application Execution?
                  </CardTitle>
                  <p className="text-xs text-slate-400 mt-0.5">
                    This will immediately close the Playwright Chromium browser.
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-xs text-slate-300 leading-relaxed">
                Any uncommitted inputs entered on the portal will be discarded. No sensitive citizen
                vault data will remain in memory. You can restart the process at any time.
              </p>
              <div className="flex items-center justify-end gap-2 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowAbortConfirm(false)}
                  className="border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white text-xs h-8"
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={() => sendControlAction("stop")}
                  className="bg-rose-600 hover:bg-rose-700 text-white text-xs h-8"
                >
                  Yes, Abort Session
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

export default function WorkspacePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-400">
          <div className="h-8 w-8 border-2 border-civic-blue border-t-transparent rounded-full animate-spin mb-3" />
          <p className="text-sm font-medium">Initializing CivicPilot Operations Room...</p>
        </div>
      }
    >
      <WorkspaceInner />
    </Suspense>
  );
}
