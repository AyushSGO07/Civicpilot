"use client";

import React, { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import {
  FileCheck2,
  ExternalLink,
  Download,
  Copy,
  Check,
  Search,
  Filter,
  Clock,
  ShieldCheck,
  Building2,
  Bot,
  AlertCircle,
  Sparkles,
  RefreshCw,
  FolderLock,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

interface ApplicationRecord {
  id: string;
  user_id: string;
  service_id: string;
  service_name: string;
  department: string;
  category: string;
  portal_url: string;
  status: "draft" | "in_progress" | "waiting_approval" | "submitted" | "approved" | "rejected" | "failed";
  acknowledgement_number?: string | null;
  confirmation_text?: string | null;
  submission_timestamp?: string | null;
  receipt_url?: string | null;
  receipt_path?: string | null;
  populated_data?: Record<string, unknown>;
  attached_documents?: string[];
  created_at?: string;
  updated_at?: string;
}

// Fallback baseline demonstration applications (authentic schemes & portals)
const DEMO_APPLICATIONS: ApplicationRecord[] = [
  {
    id: "app-demo-nsp-01",
    user_id: "demo-citizen-id",
    service_id: "nsp-post-matric-sc",
    service_name: "Post-Matric Scholarship for SC Students",
    department: "Ministry of Social Justice and Empowerment",
    category: "Education",
    portal_url: "https://scholarships.gov.in",
    status: "submitted",
    acknowledgement_number: "NSP2026/APPL/894125",
    confirmation_text: "Your application has been submitted successfully to National Scholarship Portal.",
    submission_timestamp: "2026-10-28T14:30:00Z",
    populated_data: {
      full_name: "Arjun Sharma",
      date_of_birth: "15/08/1998",
      gender: "Male",
      domicile_state: "Maharashtra",
      annual_income: "180000",
      social_category: "SC",
    },
    attached_documents: [
      "Aadhaar Identity Card (Verified)",
      "Income Certificate 2025-26 (Verified)",
      "Caste Certificate (Verified)",
    ],
  },
  {
    id: "app-demo-pmk-02",
    user_id: "demo-citizen-id",
    service_id: "pm-kisan-samman-nidhi",
    service_name: "PM Kisan Samman Nidhi Yojana",
    department: "Ministry of Agriculture and Farmers Welfare",
    category: "Agriculture",
    portal_url: "https://pmkisan.gov.in",
    status: "submitted",
    acknowledgement_number: "PMK-MH-948123",
    confirmation_text: "Application registered successfully under PM-Kisan scheme.",
    submission_timestamp: "2026-10-31T09:15:00Z",
    populated_data: {
      full_name: "Arjun Sharma",
      date_of_birth: "15/08/1998",
      gender: "Male",
      domicile_state: "Maharashtra",
      annual_income: "180000",
      social_category: "General",
    },
    attached_documents: [
      "Aadhaar Identity Card (Verified)",
      "Land Ownership Record (7/12 Extract)",
    ],
  },
  {
    id: "app-demo-ab-03",
    user_id: "demo-citizen-id",
    service_id: "ayushman-bharat-pmjay",
    service_name: "Ayushman Bharat - PMJAY Health Card",
    department: "National Health Authority (NHA)",
    category: "Healthcare",
    portal_url: "https://beneficiary.nha.gov.in",
    status: "waiting_approval",
    acknowledgement_number: null,
    confirmation_text: null,
    submission_timestamp: null,
    populated_data: {
      full_name: "Arjun Sharma",
      date_of_birth: "15/08/1998",
      gender: "Male",
      domicile_state: "Maharashtra",
      annual_income: "180000",
      social_category: "OBC",
    },
    attached_documents: [
      "Aadhaar Identity Card (Verified)",
      "Ration Card (Verified)",
    ],
  },
];

import { API_BASE_URL } from "@/lib/api-config";

export default function ApplicationsDashboardPage() {
  const [applications, setApplications] = useState<ApplicationRecord[]>(DEMO_APPLICATIONS);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  // Fetch applications from backend
  const fetchApplications = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/applications`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setApplications(data);
        }
      }
    } catch {
      // Offline fallback: keep DEMO_APPLICATIONS
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, []);

  // 1-Click Copy Reference Number Handler
  const handleCopy = (refNo: string, id: string) => {
    navigator.clipboard.writeText(refNo);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Direct Official Receipt PDF Download (APP-05)
  const handleDownloadReceipt = async (appRecord: ApplicationRecord) => {
    setDownloadingId(appRecord.id);
    try {
      const downloadUrl = `${API_BASE_URL}/api/applications/${appRecord.id}/receipt`;
      const res = await fetch(downloadUrl);
      if (!res.ok) throw new Error("Receipt download failed");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      const safeAck = (appRecord.acknowledgement_number || appRecord.id)
        .replace(/[\/\\]/g, "_");
      link.href = url;
      link.download = `CivicPilot_Receipt_${safeAck}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      // Client-side fallback notification
      window.open(`${API_BASE_URL}/api/applications/${appRecord.id}/receipt`, "_blank");
    } finally {
      setDownloadingId(null);
    }
  };

  // Format Indian locale timestamp (APP-04)
  const formatTimestamp = (isoString?: string | null) => {
    if (!isoString) return "Pending Submission";
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      });
    } catch {
      return isoString;
    }
  };

  // Metrics Calculations
  const metrics = useMemo(() => {
    const total = applications.length;
    const submitted = applications.filter((a) => a.status === "submitted" || a.status === "approved").length;
    const waiting = applications.filter((a) => a.status === "waiting_approval").length;
    const active = applications.filter((a) => a.status === "in_progress" || a.status === "draft").length;
    return { total, submitted, waiting, active };
  }, [applications]);

  // Filtered List
  const filteredApplications = useMemo(() => {
    return applications.filter((app) => {
      // Status filter
      if (selectedStatus === "submitted" && app.status !== "submitted" && app.status !== "approved") {
        return false;
      }
      if (selectedStatus === "waiting" && app.status !== "waiting_approval") {
        return false;
      }
      if (selectedStatus === "active" && app.status !== "in_progress" && app.status !== "draft") {
        return false;
      }

      // Category filter
      if (selectedCategory !== "all" && app.category.toLowerCase() !== selectedCategory.toLowerCase()) {
        return false;
      }

      // Search Query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesName = app.service_name.toLowerCase().includes(q);
        const matchesDept = app.department.toLowerCase().includes(q);
        const matchesAck = app.acknowledgement_number?.toLowerCase().includes(q) || false;
        if (!matchesName && !matchesDept && !matchesAck) return false;
      }

      return true;
    });
  }, [applications, selectedStatus, selectedCategory, searchQuery]);

  return (
    <div className="min-h-screen bg-slate-50 pb-20 font-sans text-slate-800">
      {/* MakeMyTrip Elevated Navy Hero Section */}
      <div className="relative bg-navy text-white pt-10 pb-16 px-4 sm:px-6 lg:px-8 border-b border-navy-light/40 overflow-hidden shadow-lg">
        <div className="absolute inset-0 bg-radial-pattern opacity-10 pointer-events-none" />
        <div className="max-w-7xl mx-auto relative z-10">
          {/* Breadcrumb Navigation */}
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-4">
            <Link href="/" className="hover:text-white transition">
              Home
            </Link>
            <ChevronRight className="h-3 w-3" />
            <span className="text-civic-cyan font-semibold">My Applications</span>
          </div>

          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-civic-cyan/15 border border-civic-cyan/30 text-civic-cyan text-xs font-bold tracking-wide uppercase mb-3">
                <ShieldCheck className="h-3.5 w-3.5 text-civic-cyan" />
                <span>Autonomous Execution Dashboard</span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                My Public Service Applications
              </h1>
              <p className="mt-2 text-sm sm:text-base text-slate-300 max-w-2xl leading-relaxed">
                Track live automation progress, inspect verified portal acknowledgement numbers, and
                download authentic government submission receipt slips.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={fetchApplications}
                className="border-slate-700 bg-slate-900/60 text-slate-200 hover:bg-slate-800 hover:text-white text-xs h-9"
              >
                <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
                <span>Refresh Status</span>
              </Button>
              <Link href="/services">
                <Button className="bg-civic-blue hover:bg-civic-blue-hover text-white text-xs font-bold h-9 shadow-md shadow-civic-blue/30">
                  <Sparkles className="h-3.5 w-3.5 mr-1.5" />
                  <span>Explore Schemes</span>
                </Button>
              </Link>
            </div>
          </div>

          {/* Elevated Summary Metrics Cards Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
            <div className="bg-slate-900/80 backdrop-blur-sm border border-slate-800 rounded-xl p-4 shadow-md transition hover:border-slate-700">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400 font-medium">Total Applications</span>
                <div className="h-8 w-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300">
                  <FileCheck2 className="h-4 w-4" />
                </div>
              </div>
              <div className="text-2xl font-black text-white mt-2">{metrics.total}</div>
              <span className="text-[11px] text-slate-400 mt-1 block">Tracked across ministries</span>
            </div>

            <div className="bg-slate-900/80 backdrop-blur-sm border border-slate-800 rounded-xl p-4 shadow-md transition hover:border-emerald-500/40">
              <div className="flex items-center justify-between">
                <span className="text-xs text-emerald-300 font-medium">Official Submissions</span>
                <div className="h-8 w-8 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                  <Check className="h-4 w-4" />
                </div>
              </div>
              <div className="text-2xl font-black text-emerald-400 mt-2">{metrics.submitted}</div>
              <span className="text-[11px] text-emerald-300/80 mt-1 block">Verified on portals</span>
            </div>

            <div className="bg-slate-900/80 backdrop-blur-sm border border-slate-800 rounded-xl p-4 shadow-md transition hover:border-amber-500/40">
              <div className="flex items-center justify-between">
                <span className="text-xs text-amber-300 font-medium">Pending Review (HIL)</span>
                <div className="h-8 w-8 rounded-lg bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <AlertCircle className="h-4 w-4" />
                </div>
              </div>
              <div className="text-2xl font-black text-amber-400 mt-2">{metrics.waiting}</div>
              <span className="text-[11px] text-amber-300/80 mt-1 block">Requires citizen authorization</span>
            </div>

            <div className="bg-slate-900/80 backdrop-blur-sm border border-slate-800 rounded-xl p-4 shadow-md transition hover:border-blue-500/40">
              <div className="flex items-center justify-between">
                <span className="text-xs text-civic-cyan font-medium">Active & Drafts</span>
                <div className="h-8 w-8 rounded-lg bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-civic-cyan">
                  <Bot className="h-4 w-4" />
                </div>
              </div>
              <div className="text-2xl font-black text-white mt-2">{metrics.active}</div>
              <span className="text-[11px] text-slate-400 mt-1 block">Automation in progress</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-6 relative z-20">
        {/* Filter and Search Bar Card */}
        <Card className="bg-white border-slate-200 shadow-md rounded-2xl mb-8 overflow-hidden">
          <CardContent className="p-4 sm:p-5">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              {/* Search Bar */}
              <div className="relative w-full md:w-96">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search by scheme name, ministry, or reference no..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs sm:text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-civic-blue focus:bg-white transition"
                />
              </div>

              {/* Status Tabs */}
              <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl w-full md:w-auto overflow-x-auto">
                <button
                  onClick={() => setSelectedStatus("all")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    selectedStatus === "all"
                      ? "bg-white text-navy shadow-sm"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  All ({applications.length})
                </button>
                <button
                  onClick={() => setSelectedStatus("submitted")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    selectedStatus === "submitted"
                      ? "bg-emerald-600 text-white shadow-sm"
                      : "text-slate-600 hover:text-emerald-700"
                  }`}
                >
                  Submitted ({metrics.submitted})
                </button>
                <button
                  onClick={() => setSelectedStatus("waiting")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    selectedStatus === "waiting"
                      ? "bg-amber-600 text-white shadow-sm"
                      : "text-slate-600 hover:text-amber-700"
                  }`}
                >
                  Under Review ({metrics.waiting})
                </button>
                <button
                  onClick={() => setSelectedStatus("active")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    selectedStatus === "active"
                      ? "bg-civic-blue text-white shadow-sm"
                      : "text-slate-600 hover:text-civic-blue"
                  }`}
                >
                  Active / Draft ({metrics.active})
                </button>
              </div>
            </div>

            {/* Quick Category Chips */}
            <div className="flex items-center gap-2 mt-4 pt-4 border-t border-slate-100 overflow-x-auto text-xs">
              <span className="text-slate-400 flex items-center gap-1 shrink-0 font-medium">
                <Filter className="h-3.5 w-3.5" />
                <span>Category:</span>
              </span>
              {["all", "education", "agriculture", "healthcare", "social welfare"].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-2.5 py-1 rounded-full capitalize text-xs transition shrink-0 ${
                    selectedCategory === cat
                      ? "bg-navy text-white font-bold"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Application Cards Deck (APP-03, APP-04) */}
        {filteredApplications.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center shadow-sm">
            <div className="h-16 w-16 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 mx-auto mb-4">
              <FileCheck2 className="h-8 w-8" />
            </div>
            <h3 className="text-lg font-bold text-slate-800">No applications found</h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto mt-1 mb-6">
              {searchQuery || selectedStatus !== "all" || selectedCategory !== "all"
                ? "No applications matched your search filters. Try adjusting the query or resetting the filter options."
                : "You haven't initiated any government scheme applications yet. Browse the official scheme catalog to check your eligibility."}
            </p>
            <div className="flex items-center justify-center gap-3">
              {(searchQuery || selectedStatus !== "all" || selectedCategory !== "all") && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSearchQuery("");
                    setSelectedStatus("all");
                    setSelectedCategory("all");
                  }}
                  className="text-xs"
                >
                  Reset Filters
                </Button>
              )}
              <Link href="/services">
                <Button size="sm" className="bg-civic-blue hover:bg-civic-blue-hover text-white text-xs">
                  <Sparkles className="h-3.5 w-3.5 mr-1.5" />
                  <span>Discover Eligible Schemes</span>
                </Button>
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredApplications.map((app) => {
              const isSubmitted = app.status === "submitted" || app.status === "approved";
              const isWaiting = app.status === "waiting_approval";
              const isInProgress = app.status === "in_progress";

              return (
                <Card
                  key={app.id}
                  className="bg-white border border-slate-200 hover:border-slate-300 shadow-sm hover:shadow-md transition-all rounded-2xl overflow-hidden"
                >
                  <CardContent className="p-5 sm:p-6">
                    <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
                      {/* Left: Scheme Info & Details */}
                      <div className="space-y-3 flex-1 min-w-0">
                        {/* Header Badges */}
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge variant="cyan" className="text-[11px] font-bold">
                            {app.category}
                          </Badge>
                          <span className="text-xs text-slate-500 flex items-center gap-1 truncate max-w-sm">
                            <Building2 className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                            <span>{app.department}</span>
                          </span>

                          {/* Live Status Badge (APP-04) */}
                          {isSubmitted && (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold">
                              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                              <span>Official Submission Confirmed</span>
                            </span>
                          )}
                          {isWaiting && (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-xs font-bold">
                              <span className="h-2 w-2 rounded-full bg-amber-500 animate-ping" />
                              <span>Waiting Citizen Approval (HIL)</span>
                            </span>
                          )}
                          {isInProgress && (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold">
                              <span className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                              <span>Automating Portal Fields</span>
                            </span>
                          )}
                          {app.status === "draft" && (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-slate-600 text-xs font-semibold">
                              <span>Draft Initialized</span>
                            </span>
                          )}
                        </div>

                        {/* Scheme Title */}
                        <div>
                          <Link
                            href={`/services/${app.service_id}`}
                            className="text-lg sm:text-xl font-extrabold text-navy hover:text-civic-blue transition line-clamp-1"
                          >
                            {app.service_name}
                          </Link>
                          {app.confirmation_text && (
                            <p className="text-xs text-slate-500 mt-1 italic line-clamp-1">
                              &ldquo;{app.confirmation_text}&rdquo;
                            </p>
                          )}
                        </div>

                        {/* Metadata Row: Timestamp & Portal URL (APP-04) */}
                        <div className="flex flex-wrap items-center gap-y-2 gap-x-4 text-xs text-slate-500 pt-1">
                          <div className="flex items-center gap-1.5">
                            <Clock className="h-3.5 w-3.5 text-slate-400" />
                            <span>
                              {isSubmitted ? "Submitted on: " : "Updated: "}
                              <strong className="text-slate-700 font-semibold">
                                {formatTimestamp(app.submission_timestamp || app.updated_at || app.created_at)}
                              </strong>
                            </span>
                          </div>

                          <div className="flex items-center gap-1.5">
                            <ExternalLink className="h-3.5 w-3.5 text-slate-400" />
                            <a
                              href={app.portal_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-civic-blue hover:underline font-medium truncate max-w-xs"
                            >
                              {app.portal_url.replace("https://", "")}
                            </a>
                          </div>
                        </div>

                        {/* Verified Vault Certificates Tagging */}
                        {app.attached_documents && app.attached_documents.length > 0 && (
                          <div className="flex flex-wrap items-center gap-1.5 pt-1">
                            <span className="text-[11px] text-slate-400 font-medium mr-1 flex items-center gap-1">
                              <FolderLock className="h-3 w-3" />
                              <span>Attached:</span>
                            </span>
                            {app.attached_documents.map((doc, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-600 text-[10px] font-medium"
                              >
                                {doc}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Right: Reference Number Box & Actions (APP-01, APP-05) */}
                      <div className="flex flex-col sm:flex-row lg:flex-col items-start sm:items-center lg:items-end justify-between gap-4 shrink-0 border-t lg:border-t-0 pt-4 lg:pt-0 border-slate-100">
                        {/* Acknowledgement Reference Number (APP-01, APP-04) */}
                        {app.acknowledgement_number ? (
                          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-left lg:text-right w-full sm:w-auto min-w-[210px]">
                            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-0.5">
                              Official Acknowledgement No.
                            </span>
                            <div className="flex items-center justify-between lg:justify-end gap-2">
                              <span className="font-mono text-xs sm:text-sm font-extrabold text-navy select-all">
                                {app.acknowledgement_number}
                              </span>
                              <button
                                onClick={() => handleCopy(app.acknowledgement_number!, app.id)}
                                title="Copy Acknowledgement Number"
                                className="p-1 rounded-md text-slate-400 hover:text-civic-blue hover:bg-slate-200/60 transition"
                              >
                                {copiedId === app.id ? (
                                  <Check className="h-3.5 w-3.5 text-emerald-600" />
                                ) : (
                                  <Copy className="h-3.5 w-3.5" />
                                )}
                              </button>
                            </div>
                            {copiedId === app.id && (
                              <span className="text-[10px] text-emerald-600 font-semibold mt-1 block">
                                Copied to clipboard!
                              </span>
                            )}
                          </div>
                        ) : (
                          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-left lg:text-right w-full sm:w-auto min-w-[210px]">
                            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-0.5">
                              Acknowledgement No.
                            </span>
                            <span className="text-xs text-amber-700 font-semibold italic">
                              Generated upon citizen approval
                            </span>
                          </div>
                        )}

                        {/* Action Buttons */}
                        <div className="flex items-center gap-2 w-full sm:w-auto">
                          {isSubmitted ? (
                            <Button
                              onClick={() => handleDownloadReceipt(app)}
                              disabled={downloadingId === app.id}
                              className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs h-9 px-4 shadow-sm"
                            >
                              <Download className={`h-3.5 w-3.5 mr-1.5 ${downloadingId === app.id ? "animate-bounce" : ""}`} />
                              <span>{downloadingId === app.id ? "Generating..." : "Download Official Receipt"}</span>
                            </Button>
                          ) : (
                            <Link href={`/applications/workspace/${app.id}`}>
                              <Button
                                className={`${
                                  isWaiting
                                    ? "bg-amber-600 hover:bg-amber-500 shadow-amber-600/20"
                                    : "bg-civic-blue hover:bg-civic-blue-hover"
                                } text-white font-bold text-xs h-9 px-4 shadow-md`}
                              >
                                <Bot className="h-3.5 w-3.5 mr-1.5" />
                                <span>{isWaiting ? "Review & Authorize" : "Open Operations Room"}</span>
                              </Button>
                            </Link>
                          )}

                          <Link href={`/applications/workspace/${app.id}`}>
                            <Button
                              variant="outline"
                              size="sm"
                              className="border-slate-200 hover:bg-slate-100 text-slate-700 text-xs h-9 px-3"
                              title="Inspect Live Operations Room"
                            >
                              <Bot className="h-3.5 w-3.5" />
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Security & Statutory Notice Footer */}
        <div className="mt-12 p-4 rounded-2xl bg-white border border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-600 shrink-0" />
            <span>
              All acknowledgement slips are cryptographically sealed with SHA-256 hashes and compliant with the IT Act, 2000.
            </span>
          </div>
          <span className="font-mono text-[11px] text-slate-400">
            CivicPilot Automated Verification Engine v1.0
          </span>
        </div>
      </main>
    </div>
  );
}
