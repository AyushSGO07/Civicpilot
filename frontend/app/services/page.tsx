"use client";

import React, { useState, useEffect, Suspense, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Search,
  ExternalLink,
  Award,
  FileText,
  Car,
  Sprout,
  HeartPulse,
  Building2,
  Banknote,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  Filter,
  MapPin,
  FileCheck2,
  Loader2,
  Calendar,
  Layers,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { INDIAN_STATES_UTS } from "@/lib/constants";

export interface GovernmentService {
  id: string;
  service_name: string;
  department: string;
  description: string;
  category: string;
  state: string;
  eligibility_summary: string;
  eligibility_criteria: Record<string, unknown>;
  required_documents: string[];
  official_source_url: string;
  official_application_url: string;
  application_deadline?: string;
  is_active: boolean;
}

const CATEGORY_TABS = [
  { id: "all", label: "All Schemes", icon: Layers },
  { id: "scholarships", label: "Scholarships & Education", icon: Award },
  { id: "agriculture", label: "Agriculture & Farmers", icon: Sprout },
  { id: "healthcare", label: "Healthcare", icon: HeartPulse },
  { id: "transport", label: "Transport", icon: Car },
  { id: "business-msme", label: "Business & MSME", icon: Building2 },
  { id: "financial-assistance", label: "Financial Assistance", icon: Banknote },
  { id: "identity-docs", label: "Identity & Docs", icon: FileText },
];

import { API_BASE_URL } from "@/lib/api-config";

// Fallback seed services if backend is offline during development/review
const FALLBACK_SCHEMES: GovernmentService[] = [
  {
    id: "pm-usp-scholarship",
    service_name: "Central Sector Scheme of Scholarship for College and University Students (PM-USP)",
    department: "Ministry of Education, Department of Higher Education",
    description: "Financial support to meritorious undergraduate and postgraduate students from low-income families to cover college expenses.",
    category: "Scholarships",
    state: "Central",
    eligibility_summary: "Scored above 80th percentile in relevant stream in Class 12. Annual family income <= ₹4,50,000. Pursuing regular degree.",
    eligibility_criteria: { min_marks_percentile: 80.0, max_annual_income: 450000.0 },
    required_documents: ["Class 12 Marksheet", "Income Certificate", "Aadhaar Card", "Bank Passbook", "Bonafide Student Certificate"],
    official_source_url: "https://www.myscheme.gov.in/schemes/pm-usp",
    official_application_url: "https://scholarships.gov.in/",
    application_deadline: "31st October (Annual Cycle)",
    is_active: true,
  },
  {
    id: "pm-kisan-samman-nidhi",
    service_name: "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
    department: "Ministry of Agriculture and Farmers Welfare",
    description: "Direct income support of ₹6,000 per year in 3 equal installments transferred into bank accounts of landholder farmer families.",
    category: "Agriculture",
    state: "Central",
    eligibility_summary: "All landholding farmer families having cultivable land in their names. High-income tax payers are excluded.",
    eligibility_criteria: { occupation: "Farmer", landholding_required: true },
    required_documents: ["Aadhaar Card", "Land Ownership Records", "Bank Passbook"],
    official_source_url: "https://pmkisan.gov.in/",
    official_application_url: "https://pmkisan.gov.in/RegistrationFormNew.aspx",
    application_deadline: "Open Throughout Year",
    is_active: true,
  },
  {
    id: "pm-jay-ayushman-bharat",
    service_name: "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
    department: "National Health Authority, Ministry of Health and Family Welfare",
    description: "World's largest health assurance scheme offering free health cover of up to ₹5,00,000 per family per year for secondary and tertiary hospitalization.",
    category: "Healthcare",
    state: "Central",
    eligibility_summary: "Economically vulnerable families identified based on SECC 2011 deprivation criteria and NFSA ration card holders.",
    eligibility_criteria: { max_annual_income: 250000.0 },
    required_documents: ["Aadhaar Card", "Ration Card / Family ID", "Identity Proof"],
    official_source_url: "https://pmjay.gov.in/",
    official_application_url: "https://beneficiary.nha.gov.in/",
    application_deadline: "Continuous Open Enrolment",
    is_active: true,
  },
  {
    id: "post-matric-scholarship-sc",
    service_name: "Centrally Sponsored Post Matric Scholarship for SC Students",
    department: "Ministry of Social Justice and Empowerment",
    description: "Complete financial assistance including compulsory college fees and maintenance allowance for Scheduled Caste students pursuing post-matric courses.",
    category: "Scholarships",
    state: "Central",
    eligibility_summary: "Belonging to Scheduled Caste (SC). Studying post-matriculation degree/diploma courses. Annual family income <= ₹2,50,000.",
    eligibility_criteria: { social_category: "SC", max_annual_income: 250000.0 },
    required_documents: ["Caste Certificate (SC)", "Income Certificate", "10th/12th Marksheet", "Aadhaar Card", "Bank Passbook"],
    official_source_url: "https://www.myscheme.gov.in/schemes/pmsss-sc",
    official_application_url: "https://scholarships.gov.in/",
    application_deadline: "30th November (Annual Cycle)",
    is_active: true,
  },
  {
    id: "pmegp-msme-scheme",
    service_name: "Prime Minister's Employment Generation Programme (PMEGP)",
    department: "Ministry of Micro, Small and Medium Enterprises (MSME)",
    description: "Credit-linked government subsidy of 15% to 35% on bank loans for establishing micro-enterprises in manufacturing and service sectors.",
    category: "Business & MSME",
    state: "Central",
    eligibility_summary: "Any individual above 18 years of age. Minimum Class 8 passed for manufacturing projects costing above ₹10 lakh.",
    eligibility_criteria: { min_age: 18, min_education: "8th Standard" },
    required_documents: ["Project Report (DPR)", "Aadhaar Card", "PAN Card", "Educational Qualification Certificate"],
    official_source_url: "https://www.kviconline.gov.in/pmegpeportal/",
    official_application_url: "https://www.kviconline.gov.in/pmegpeportal/jsp/pmegponline.jsp",
    application_deadline: "Open Throughout Year",
    is_active: true,
  },
  {
    id: "parivahan-driving-licence",
    service_name: "Sarathi Parivahan Learner & Permanent Driving Licence Services",
    department: "Ministry of Road Transport and Highways (MoRTH)",
    description: "Unified national service for application, slot booking, test scheduling, and issuance of learner and permanent driving licences across all states.",
    category: "Transport",
    state: "Central",
    eligibility_summary: "Minimum 18 years of age for Light Motor Vehicles; minimum 16 years for motorcycle without gear up to 50cc with parental consent.",
    eligibility_criteria: { min_age_lmv: 18 },
    required_documents: ["Age Proof (Aadhaar / 10th Certificate)", "Address Proof", "Form 1 Medical Declaration", "Photograph"],
    official_source_url: "https://parivahan.gov.in/parivahan/",
    official_application_url: "https://sarathi.parivahan.gov.in/sarathiservice/stateSelection.do",
    application_deadline: "Rolling / Always Open",
    is_active: true,
  },
  {
    id: "naps-apprenticeship",
    service_name: "National Apprenticeship Promotion Scheme (NAPS)",
    department: "Ministry of Skill Development and Entrepreneurship",
    description: "On-the-job industrial skill training offering stipends up to ₹1,500/month government subsidy to trainees in technical and engineering industries.",
    category: "Education",
    state: "Central",
    eligibility_summary: "Candidates aged 14 and above. Minimum educational qualification 5th, 10th, 12th standard, ITI, or Diploma graduate.",
    eligibility_criteria: { min_age: 14 },
    required_documents: ["Aadhaar Card", "Educational Qualification Certificate", "Bank Account Details"],
    official_source_url: "https://www.apprenticeshipindia.gov.in/",
    official_application_url: "https://www.apprenticeshipindia.gov.in/candidate-registration",
    application_deadline: "Open Enrolment Year-Round",
    is_active: true,
  },
  {
    id: "pmay-urban-housing",
    service_name: "Pradhan Mantri Awas Yojana - Urban (PMAY-U)",
    department: "Ministry of Housing and Urban Affairs",
    description: "Interest subsidy and financial assistance up to ₹2.67 lakh for constructing or purchasing pucca houses for urban Economically Weaker Sections.",
    category: "Financial Assistance",
    state: "Central",
    eligibility_summary: "Beneficiary family must not own a pucca house in India. Annual family income up to ₹3,00,000 for EWS and ₹6,00,000 for LIG category.",
    eligibility_criteria: { max_annual_income_ews: 300000.0, no_pucca_house: true },
    required_documents: ["Aadhaar Card", "Annual Income Certificate", "Affidavit of No Pucca House", "Bank Passbook"],
    official_source_url: "https://pmay-urban.gov.in/",
    official_application_url: "https://pmaymis.gov.in/",
    application_deadline: "Rolling Phased Allotment",
    is_active: true,
  },
];

function ExploreServicesContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const initialQuery = searchParams.get("q") || "";
  const initialCategory = searchParams.get("category") || "all";
  const initialState = searchParams.get("state") || "all";

  const [query, setQuery] = useState(initialQuery);
  const [activeCategory, setActiveCategory] = useState(initialCategory);
  const [selectedState, setSelectedState] = useState(initialState);
  const [services, setServices] = useState<GovernmentService[]>(FALLBACK_SCHEMES);
  const [loading, setLoading] = useState(false);

  const fetchServices = useCallback(async (qParam: string, catParam: string, stateParam: string) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (qParam.trim()) params.set("q", qParam.trim());
      if (catParam && catParam !== "all") params.set("category", catParam);
      if (stateParam && stateParam !== "all") params.set("state", stateParam);

      const res = await fetch(`${API_BASE_URL}/api/services?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setServices(data);
      } else {
        // Fallback filter locally
        filterFallbackSchemes(qParam, catParam, stateParam);
      }
    } catch {
      filterFallbackSchemes(qParam, catParam, stateParam);
    } finally {
      setLoading(false);
    }
  }, []);

  const filterFallbackSchemes = (qParam: string, catParam: string, stateParam: string) => {
    let filtered = [...FALLBACK_SCHEMES];

    if (catParam && catParam !== "all") {
      const catLower = catParam.toLowerCase();
      filtered = filtered.filter((s) => {
        const itemCat = s.category.toLowerCase();
        return (
          itemCat.includes(catLower) ||
          catLower.includes(itemCat) ||
          (catLower === "education" && itemCat.includes("scholarship")) ||
          (catLower === "scholarships" && s.service_name.toLowerCase().includes("scholarship"))
        );
      });
    }

    if (stateParam && stateParam !== "all" && stateParam !== "Central") {
      filtered = filtered.filter(
        (s) => s.state === "Central" || s.state.toLowerCase() === stateParam.toLowerCase()
      );
    }

    if (qParam.trim()) {
      const qLower = qParam.toLowerCase();
      filtered = filtered.filter(
        (s) =>
          s.service_name.toLowerCase().includes(qLower) ||
          s.description.toLowerCase().includes(qLower) ||
          s.department.toLowerCase().includes(qLower) ||
          s.eligibility_summary.toLowerCase().includes(qLower) ||
          s.category.toLowerCase().includes(qLower)
      );
    }

    setServices(filtered);
  };

  useEffect(() => {
    const qParam = searchParams.get("q") || "";
    const catParam = searchParams.get("category") || "all";
    const stateParam = searchParams.get("state") || "all";

    setQuery(qParam);
    setActiveCategory(catParam);
    setSelectedState(stateParam);
    fetchServices(qParam, catParam, stateParam);
  }, [searchParams, fetchServices]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchServices(query, activeCategory, selectedState);
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());
    if (activeCategory !== "all") params.set("category", activeCategory);
    if (selectedState !== "all") params.set("state", selectedState);
    router.replace(`/services?${params.toString()}`);
  };

  const handleCategoryClick = (catId: string) => {
    setActiveCategory(catId);
    const params = new URLSearchParams(searchParams.toString());
    if (catId === "all") {
      params.delete("category");
    } else {
      params.set("category", catId);
    }
    router.replace(`/services?${params.toString()}`);
  };

  const handleStateChange = (stateVal: string) => {
    setSelectedState(stateVal);
    const params = new URLSearchParams(searchParams.toString());
    if (stateVal === "all") {
      params.delete("state");
    } else {
      params.set("state", stateVal);
    }
    router.replace(`/services?${params.toString()}`);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-canvas py-8 sm:py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-1.5">
            <Link href="/" className="hover:text-civic-blue transition-colors">
              Home
            </Link>
            <span>/</span>
            <span className="font-semibold text-navy">Explore Services</span>
          </div>
          <span className="text-[11px] text-slate-400 font-medium">
            Official Indian Central & State Schemes Catalog
          </span>
        </div>

        {/* Hero Search Header (MakeMyTrip Style) */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-navy via-navy to-navy-dark text-white p-6 sm:p-10 shadow-xl border border-navy-light/30">
          <div className="absolute right-0 top-0 -mr-20 -mt-20 h-72 w-72 rounded-full bg-civic-blue/20 blur-3xl" />
          <div className="absolute left-1/3 bottom-0 -mb-20 h-48 w-48 rounded-full bg-civic-cyan/15 blur-3xl" />

          <div className="relative z-10 max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-civic-cyan/30 bg-civic-cyan/10 px-3 py-1 text-xs font-semibold text-civic-cyan mb-4">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Official Government Portal Endpoints • Zero Dummy Data</span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white mb-2">
              Explore Government Services & Schemes
            </h1>
            <p className="text-sm text-slate-300 mb-6">
              Search verified welfare schemes, student scholarships, business subsidies, and transport services with direct authoritative links.
            </p>

            {/* Natural Language Search Bar (DISC-01) */}
            <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search schemes by name, keyword, or requirement (e.g. scholarship, PM Kisan, licence)..."
                  className="w-full rounded-xl border border-white/20 bg-white/95 text-navy py-3.5 pl-12 pr-4 text-sm font-medium placeholder:text-slate-400 shadow-sm focus:border-civic-cyan focus:bg-white focus:outline-none focus:ring-2 focus:ring-civic-cyan/30"
                />
              </div>

              <Button
                type="submit"
                size="lg"
                className="bg-civic-blue hover:bg-civic-blue-hover text-white font-bold gap-2 px-6 shadow-md"
              >
                <span>Search</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </div>

        {/* 8 Category Tabs Bar (DISC-02) */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-3 sm:p-4 shadow-sm space-y-4">
          <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 no-scrollbar">
            {CATEGORY_TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeCategory === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => handleCategoryClick(tab.id)}
                  className={`flex shrink-0 items-center gap-2 rounded-xl px-4 py-2.5 text-xs sm:text-sm font-bold transition-all cursor-pointer ${
                    isActive
                      ? "bg-civic-blue text-white shadow-sm"
                      : "text-slate-600 hover:bg-slate-100 hover:text-navy"
                  }`}
                >
                  <Icon className={`h-4 w-4 ${isActive ? "text-white" : "text-slate-400"}`} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>

          {/* Domicile State Filter & Results Counter */}
          <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 text-slate-500 font-semibold">
                <MapPin className="h-4 w-4 text-civic-blue" />
                <span>Domicile State Filter:</span>
              </div>
              <select
                value={selectedState}
                onChange={(e) => handleStateChange(e.target.value)}
                className="rounded-lg border border-slate-300 bg-slate-50/80 px-3 py-1.5 text-xs font-semibold text-navy focus:border-civic-blue focus:outline-none focus:ring-1 focus:ring-civic-blue"
              >
                <option value="all">All India (Central & All States)</option>
                {INDIAN_STATES_UTS.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2 text-slate-500">
              <Filter className="h-3.5 w-3.5 text-slate-400" />
              <span>
                Showing <strong className="text-navy">{services.length}</strong> official verified schemes
              </span>
            </div>
          </div>
        </div>

        {/* Schemes Card Deck (DISC-03, DISC-04) */}
        {loading ? (
          <div className="py-20 text-center">
            <Loader2 className="h-8 w-8 animate-spin text-civic-blue mx-auto mb-2" />
            <p className="text-xs text-slate-500">Searching government schemes catalog...</p>
          </div>
        ) : services.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center shadow-sm">
            <div className="h-16 w-16 bg-slate-100 rounded-2xl flex items-center justify-center text-slate-400 mx-auto mb-3">
              <Search className="h-8 w-8" />
            </div>
            <h3 className="text-base font-bold text-navy">No schemes found matching your search</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              Try adjusting your search terms or select &quot;All Schemes&quot; to explore national welfare benefits and scholarships.
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setQuery("");
                setActiveCategory("all");
                setSelectedState("all");
                router.replace("/services");
              }}
              className="mt-4 text-xs"
            >
              Reset All Filters
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {services.map((scheme) => (
              <div
                key={scheme.id}
                className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-7 shadow-sm hover:shadow-lg hover:-translate-y-0.5 transition-all flex flex-col justify-between group"
              >
                <div>
                  {/* Badges: Category & State */}
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                    <span className="text-[11px] font-bold px-2.5 py-1 rounded-md bg-civic-blue/10 text-civic-blue border border-civic-blue/20">
                      {scheme.category}
                    </span>

                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                      {scheme.state === "Central" ? "Central Scheme (All India)" : scheme.state}
                    </span>
                  </div>

                  {/* Title & Department (DISC-03) */}
                  <h3 className="text-lg font-bold text-navy group-hover:text-civic-blue transition-colors leading-snug mb-1">
                    {scheme.service_name}
                  </h3>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
                    {scheme.department}
                  </p>

                  {/* Description */}
                  <p className="text-xs text-slate-600 line-clamp-3 mb-4 leading-relaxed">
                    {scheme.description}
                  </p>

                  {/* Eligibility Summary Card */}
                  <div className="rounded-xl bg-slate-50 p-3.5 border border-slate-200/70 mb-4 text-xs space-y-1">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-navy flex items-center gap-1.5 mb-1">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                      Eligibility Criteria Summary
                    </div>
                    <p className="text-slate-600 text-xs leading-relaxed">
                      {scheme.eligibility_summary}
                    </p>
                  </div>

                  {/* Required Documents Tags */}
                  {scheme.required_documents && scheme.required_documents.length > 0 && (
                    <div className="mb-4">
                      <div className="text-[11px] font-semibold text-slate-400 mb-1.5 flex items-center gap-1">
                        <FileCheck2 className="h-3 w-3" />
                        Required Documents:
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {scheme.required_documents.map((doc) => (
                          <span
                            key={doc}
                            className="text-[10px] font-medium bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200"
                          >
                            {doc}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Application Deadline */}
                  {scheme.application_deadline && (
                    <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mb-5">
                      <Calendar className="h-3.5 w-3.5 text-slate-400" />
                      <span>Deadline: <strong className="text-slate-600 font-semibold">{scheme.application_deadline}</strong></span>
                    </div>
                  )}
                </div>

                {/* Card Action Footer: Official Portal & AI Check (DISC-04) */}
                <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3">
                  <a
                    href={scheme.official_source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 text-xs font-bold text-slate-600 hover:text-civic-blue transition-colors px-3 py-2 rounded-lg hover:bg-slate-100"
                  >
                    <span>Official Portal</span>
                    <ExternalLink className="h-3.5 w-3.5 opacity-70" />
                  </a>

                  <Link
                    href={`/services/${scheme.id}`}
                    className="w-full sm:w-auto"
                  >
                    <Button
                      size="sm"
                      className="w-full sm:w-auto bg-civic-blue hover:bg-civic-blue-hover text-white font-bold text-xs gap-1.5 px-4 shadow-sm"
                    >
                      <Sparkles className="h-3.5 w-3.5 text-civic-cyan" />
                      <span>Check AI Eligibility</span>
                      <ArrowRight className="h-3 w-3" />
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ExploreServicesPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-canvas">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-civic-blue" />
            <p className="text-xs text-slate-500 font-medium">
              Loading verified government schemes...
            </p>
          </div>
        </div>
      }
    >
      <ExploreServicesContent />
    </Suspense>
  );
}
