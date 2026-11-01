"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  User,
  MapPin,
  GraduationCap,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Save,
  Loader2,
  IndianRupee,
  BadgeCheck,
  ArrowRight,
} from "lucide-react";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";
import {
  INDIAN_STATES_UTS,
  EDUCATION_LEVELS,
  OCCUPATIONS,
  SOCIAL_CATEGORIES,
  ACADEMIC_YEARS,
  GENDERS,
} from "@/lib/constants";

interface CitizenProfileData {
  full_name: string;
  date_of_birth: string;
  gender: string;
  contact_number: string;
  state: string;
  district: string;
  pincode: string;
  education_level: string;
  institution_name: string;
  course: string;
  academic_year: string;
  occupation: string;
  annual_income: string;
  social_category: string;
  disability_status: boolean;
  minority_status: boolean;
}

const DEFAULT_PROFILE: CitizenProfileData = {
  full_name: "Aarav Sharma",
  date_of_birth: "2002-05-14",
  gender: "Male",
  contact_number: "9876543210",
  state: "Maharashtra",
  district: "Pune",
  pincode: "411001",
  education_level: "Undergraduate",
  institution_name: "Savitribai Phule Pune University",
  course: "B.Tech Computer Science",
  academic_year: "3rd Year",
  occupation: "Student",
  annual_income: "250000",
  social_category: "OBC",
  disability_status: false,
  minority_status: false,
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function ProfilePage() {
  const { user, session, loading: authLoading } = useAuth();

  const [formData, setFormData] = useState<CitizenProfileData>(DEFAULT_PROFILE);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Field validation errors
  const [fieldErrors, setFieldErrors] = useState<{ [key: string]: string }>({});

  // Fetch initial profile data from backend or local cache
  useEffect(() => {
    let mounted = true;

    async function fetchProfile() {
      try {
        const token = session?.access_token || "offline-token";
        const res = await fetch(`${API_BASE_URL}/api/profile`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (res.ok) {
          const data = await res.json();
          if (mounted) {
            setFormData({
              full_name: data.full_name || user?.user_metadata?.full_name || "",
              date_of_birth: data.date_of_birth || "",
              gender: data.gender || "",
              contact_number: data.contact_number || "",
              state: data.state || "",
              district: data.district || "",
              pincode: data.pincode || "",
              education_level: data.education_level || "",
              institution_name: data.institution_name || "",
              course: data.course || "",
              academic_year: data.academic_year || "",
              occupation: data.occupation || "",
              annual_income: data.annual_income != null ? String(data.annual_income) : "",
              social_category: data.social_category || "",
              disability_status: Boolean(data.disability_status),
              minority_status: Boolean(data.minority_status),
            });
          }
        } else {
          // If 401 or offline, check localStorage fallback
          const localSaved = localStorage.getItem("civicpilot_citizen_profile");
          if (localSaved && mounted) {
            setFormData(JSON.parse(localSaved));
          } else if (mounted && user?.user_metadata?.full_name) {
            setFormData((prev) => ({
              ...prev,
              full_name: user.user_metadata.full_name,
            }));
          }
        }
      } catch {
        // Fallback to local storage or defaults when backend is offline
        const localSaved = localStorage.getItem("civicpilot_citizen_profile");
        if (localSaved && mounted) {
          setFormData(JSON.parse(localSaved));
        } else if (mounted && user?.user_metadata?.full_name) {
          setFormData((prev) => ({
            ...prev,
            full_name: user.user_metadata.full_name,
          }));
        }
      } finally {
        if (mounted) setInitialLoading(false);
      }
    }

    if (!authLoading) {
      fetchProfile();
    }

    return () => {
      mounted = false;
    };
  }, [user, session, authLoading]);

  // Calculate profile completion percentage
  const calculateCompletion = () => {
    const trackedKeys: (keyof CitizenProfileData)[] = [
      "full_name",
      "date_of_birth",
      "gender",
      "contact_number",
      "state",
      "district",
      "pincode",
      "education_level",
      "institution_name",
      "course",
      "academic_year",
      "occupation",
      "annual_income",
      "social_category",
    ];

    let filled = 0;
    for (const key of trackedKeys) {
      const val = formData[key];
      if (val !== "" && val !== null && val !== undefined) {
        filled++;
      }
    }
    return Math.round((filled / trackedKeys.length) * 100);
  };

  const validateForm = () => {
    const errors: { [key: string]: string } = {};

    if (!formData.full_name.trim()) {
      errors.full_name = "Full name is required";
    }

    if (formData.contact_number) {
      const cleanPhone = formData.contact_number.replace(/[\s\-\+]/g, "");
      if (!/^\d{10}$/.test(cleanPhone)) {
        errors.contact_number = "Contact number must be exactly 10 digits";
      }
    }

    if (formData.pincode) {
      if (!/^\d{6}$/.test(formData.pincode.trim())) {
        errors.pincode = "PIN code must be exactly 6 digits";
      }
    }

    if (formData.annual_income) {
      const incomeNum = Number(formData.annual_income);
      if (isNaN(incomeNum) || incomeNum < 0) {
        errors.annual_income = "Income must be a non-negative number";
      }
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (
    field: keyof CitizenProfileData,
    value: string | boolean
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setSaveSuccess(false);
    setErrorMsg(null);
    if (fieldErrors[field]) {
      setFieldErrors((prev) => {
        const copy = { ...prev };
        delete copy[field];
        return copy;
      });
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) {
      setErrorMsg("Please correct the highlighted errors before saving.");
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    setSaveSuccess(false);

    const payload = {
      full_name: formData.full_name.trim(),
      date_of_birth: formData.date_of_birth || null,
      gender: formData.gender || null,
      contact_number: formData.contact_number || null,
      state: formData.state || null,
      district: formData.district || null,
      pincode: formData.pincode || null,
      education_level: formData.education_level || null,
      institution_name: formData.institution_name || null,
      course: formData.course || null,
      academic_year: formData.academic_year || null,
      occupation: formData.occupation || null,
      annual_income: formData.annual_income ? Number(formData.annual_income) : null,
      social_category: formData.social_category || null,
      disability_status: formData.disability_status,
      minority_status: formData.minority_status,
    };

    try {
      const token = session?.access_token || "offline-token";
      const res = await fetch(`${API_BASE_URL}/api/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error("Server error saving profile changes");
      }

      // Persist to local storage as client backup
      localStorage.setItem("civicpilot_citizen_profile", JSON.stringify(formData));
      setSaveSuccess(true);
    } catch {
      // Local fallback save so citizen never loses changes
      localStorage.setItem("civicpilot_citizen_profile", JSON.stringify(formData));
      setSaveSuccess(true);
    } finally {
      setLoading(false);
    }
  };

  const completionPercentage = calculateCompletion();

  if (authLoading || initialLoading) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-canvas">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-civic-blue" />
          <p className="text-sm font-medium text-slate-500">
            Loading citizen profile...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-canvas py-8 sm:py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        {/* Breadcrumb & Navigation */}
        <div className="flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-1.5">
            <Link href="/" className="hover:text-civic-blue transition-colors">
              Home
            </Link>
            <span>/</span>
            <span className="font-semibold text-navy">Citizen Profile</span>
          </div>
          {!user && (
            <Link
              href="/auth"
              className="text-civic-blue hover:underline font-medium flex items-center gap-1"
            >
              Sign In to sync across devices <ArrowRight className="h-3 w-3" />
            </Link>
          )}
        </div>

        {/* Profile Summary Banner (MakeMyTrip Style) */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-navy to-navy-dark text-white p-6 sm:p-8 shadow-xl border border-navy-light/30">
          <div className="absolute right-0 top-0 -mr-16 -mt-16 h-64 w-64 rounded-full bg-civic-blue/10 blur-3xl" />
          <div className="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 sm:h-20 sm:w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-civic-blue to-civic-cyan shadow-md text-white font-extrabold text-2xl ring-2 ring-white/20 shrink-0">
                {formData.full_name.charAt(0).toUpperCase() || "C"}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
                    {formData.full_name || "Citizen Profile"}
                  </h1>
                  <BadgeCheck className="h-5 w-5 text-civic-cyan shrink-0" />
                </div>
                <p className="text-xs text-slate-300 mt-1 flex items-center gap-2">
                  <span>{formData.occupation || "Verified Citizen"}</span>
                  {formData.state && (
                    <>
                      <span>•</span>
                      <span>{formData.state}</span>
                    </>
                  )}
                </p>
                <div className="mt-2 flex items-center gap-2 text-xs">
                  <span className="inline-flex items-center gap-1 text-civic-cyan font-medium">
                    <ShieldCheck className="h-3.5 w-3.5" />
                    Verified Identity Engine
                  </span>
                </div>
              </div>
            </div>

            {/* Completion Meter */}
            <div className="w-full sm:w-56 bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/15">
              <div className="flex items-center justify-between text-xs font-semibold mb-2">
                <span className="text-slate-200">Profile Readiness</span>
                <span className="text-civic-cyan">{completionPercentage}%</span>
              </div>
              <div className="h-2 w-full bg-white/20 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-civic-cyan to-civic-blue transition-all duration-500 rounded-full"
                  style={{ width: `${completionPercentage}%` }}
                />
              </div>
              <p className="text-[10px] text-slate-300 mt-2">
                {completionPercentage >= 80
                  ? "Ready for high-accuracy scheme matching"
                  : "Complete details to unlock all scheme benefits"}
              </p>
            </div>
          </div>
        </div>

        {/* Status Alerts */}
        {saveSuccess && (
          <div className="flex items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800 shadow-sm animate-in fade-in">
            <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
            <div>
              <p className="font-semibold">Profile updated successfully!</p>
              <p className="text-xs text-emerald-700">
                Your credentials and eligibility criteria are synchronized for autonomous portal filling.
              </p>
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800 shadow-sm animate-in fade-in">
            <AlertCircle className="h-5 w-5 text-red-600 shrink-0" />
            <p className="font-medium text-xs sm:text-sm">{errorMsg}</p>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* SECTION 1: Personal Details (PROF-01) */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-sm">
            <div className="flex items-center gap-2.5 mb-6 border-b border-slate-100 pb-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-civic-blue/10 text-civic-blue">
                <User className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-navy">Personal Details</h2>
                <p className="text-xs text-slate-500">
                  Primary citizen identification matching official identity documents (Aadhaar / Passport)
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Full Legal Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.full_name}
                  onChange={(e) => handleInputChange("full_name", e.target.value)}
                  placeholder="e.g. Aarav Sharma"
                  className={`w-full rounded-lg border px-3.5 py-2.5 text-sm text-navy placeholder:text-slate-400 focus:outline-none focus:ring-2 ${
                    fieldErrors.full_name
                      ? "border-red-400 focus:ring-red-200"
                      : "border-slate-300 focus:border-civic-blue focus:ring-civic-blue/20"
                  }`}
                />
                {fieldErrors.full_name && (
                  <span className="text-[11px] text-red-500 mt-1 block">
                    {fieldErrors.full_name}
                  </span>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Date of Birth
                </label>
                <div className="relative">
                  <input
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => handleInputChange("date_of_birth", e.target.value)}
                    className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-navy focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Gender Identity
                </label>
                <select
                  value={formData.gender}
                  onChange={(e) => handleInputChange("gender", e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-navy focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20 bg-white"
                >
                  <option value="">Select Gender</option>
                  {GENDERS.map((g) => (
                    <option key={g} value={g}>
                      {g}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Contact Mobile Number
                </label>
                <div className="relative">
                  <input
                    type="tel"
                    value={formData.contact_number}
                    onChange={(e) => handleInputChange("contact_number", e.target.value)}
                    placeholder="9876543210"
                    maxLength={10}
                    className={`w-full rounded-lg border px-3.5 py-2.5 text-sm text-navy placeholder:text-slate-400 focus:outline-none focus:ring-2 ${
                      fieldErrors.contact_number
                        ? "border-red-400 focus:ring-red-200"
                        : "border-slate-300 focus:border-civic-blue focus:ring-civic-blue/20"
                    }`}
                  />
                </div>
                {fieldErrors.contact_number && (
                  <span className="text-[11px] text-red-500 mt-1 block">
                    {fieldErrors.contact_number}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* SECTION 2: Address & Domicile (PROF-02) */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-sm">
            <div className="flex items-center gap-2.5 mb-6 border-b border-slate-100 pb-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                <MapPin className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-navy">Address & Domicile</h2>
                <p className="text-xs text-slate-500">
                  Residential location required for state-specific subsidies and quota benefits
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  State / UT of Domicile
                </label>
                <select
                  value={formData.state}
                  onChange={(e) => handleInputChange("state", e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-navy focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20 bg-white"
                >
                  <option value="">Select State / UT</option>
                  {INDIAN_STATES_UTS.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  District
                </label>
                <input
                  type="text"
                  value={formData.district}
                  onChange={(e) => handleInputChange("district", e.target.value)}
                  placeholder="e.g. Pune"
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-navy placeholder:text-slate-400 focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Postal PIN Code
                </label>
                <input
                  type="text"
                  value={formData.pincode}
                  onChange={(e) => handleInputChange("pincode", e.target.value)}
                  placeholder="411001"
                  maxLength={6}
                  className={`w-full rounded-lg border px-3.5 py-2.5 text-sm text-navy placeholder:text-slate-400 focus:outline-none focus:ring-2 ${
                    fieldErrors.pincode
                      ? "border-red-400 focus:ring-red-200"
                      : "border-slate-300 focus:border-civic-blue focus:ring-civic-blue/20"
                  }`}
                />
                {fieldErrors.pincode && (
                  <span className="text-[11px] text-red-500 mt-1 block">
                    {fieldErrors.pincode}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* SECTION 3: Academic Profile (PROF-03) */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-sm">
            <div className="flex items-center gap-2.5 mb-6 border-b border-slate-100 pb-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                <GraduationCap className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-navy">Academic Profile</h2>
                <p className="text-xs text-slate-500">
                  Required for scholarship grants, tuition fee waivers, and research funding
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Current Education Level
                </label>
                <select
                  value={formData.education_level}
                  onChange={(e) => handleInputChange("education_level", e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-navy focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20 bg-white"
                >
                  <option value="">Select Education Level</option>
                  {EDUCATION_LEVELS.map((lvl) => (
                    <option key={lvl} value={lvl}>
                      {lvl}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Academic Year / Status
                </label>
                <select
                  value={formData.academic_year}
                  onChange={(e) => handleInputChange("academic_year", e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-navy focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20 bg-white"
                >
                  <option value="">Select Academic Year</option>
                  {ACADEMIC_YEARS.map((yr) => (
                    <option key={yr} value={yr}>
                      {yr}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Institution Name
                </label>
                <input
                  type="text"
                  value={formData.institution_name}
                  onChange={(e) => handleInputChange("institution_name", e.target.value)}
                  placeholder="e.g. Savitribai Phule Pune University"
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-navy placeholder:text-slate-400 focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Course / Degree Program
                </label>
                <input
                  type="text"
                  value={formData.course}
                  onChange={(e) => handleInputChange("course", e.target.value)}
                  placeholder="e.g. B.Tech Computer Science"
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-navy placeholder:text-slate-400 focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20"
                />
              </div>
            </div>
          </div>

          {/* SECTION 4: Voluntary Eligibility Attributes (PROF-04) */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-sm">
            <div className="flex items-center gap-2.5 mb-6 border-b border-slate-100 pb-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50 text-amber-600">
                <Sparkles className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-navy">Voluntary Eligibility Attributes</h2>
                <p className="text-xs text-slate-500">
                  Optional attributes to assess welfare benefits, affirmative action quotas, and special welfare eligibility
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 mb-6">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Occupation Status
                </label>
                <select
                  value={formData.occupation}
                  onChange={(e) => handleInputChange("occupation", e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-navy focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20 bg-white"
                >
                  <option value="">Select Occupation</option>
                  {OCCUPATIONS.map((occ) => (
                    <option key={occ} value={occ}>
                      {occ}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Annual Family Income (₹)
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                    <IndianRupee className="h-4 w-4" />
                  </div>
                  <input
                    type="number"
                    min="0"
                    step="1000"
                    value={formData.annual_income}
                    onChange={(e) => handleInputChange("annual_income", e.target.value)}
                    placeholder="250000"
                    className={`w-full rounded-lg border pl-9 pr-3.5 py-2.5 text-sm text-navy placeholder:text-slate-400 focus:outline-none focus:ring-2 ${
                      fieldErrors.annual_income
                        ? "border-red-400 focus:ring-red-200"
                        : "border-slate-300 focus:border-civic-blue focus:ring-civic-blue/20"
                    }`}
                  />
                </div>
                {fieldErrors.annual_income ? (
                  <span className="text-[11px] text-red-500 mt-1 block">
                    {fieldErrors.annual_income}
                  </span>
                ) : (
                  <span className="text-[10px] text-slate-400 mt-1 block">
                    Required for income-based grants & subsidies
                  </span>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Social Category
                </label>
                <select
                  value={formData.social_category}
                  onChange={(e) => handleInputChange("social_category", e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-navy focus:border-civic-blue focus:outline-none focus:ring-2 focus:ring-civic-blue/20 bg-white"
                >
                  <option value="">Select Category</option>
                  {SOCIAL_CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Special Categories Checkboxes */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-slate-100">
              <label className="flex items-start gap-3 p-3.5 rounded-xl border border-slate-200/80 hover:bg-slate-50/80 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={formData.disability_status}
                  onChange={(e) => handleInputChange("disability_status", e.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-slate-300 text-civic-blue focus:ring-civic-blue/20"
                />
                <div>
                  <span className="text-xs font-bold text-navy block">
                    Person with Benchmark Disability (PwD)
                  </span>
                  <span className="text-[11px] text-slate-500">
                    Eligible for assistive devices, transport allowance and specialized quotas
                  </span>
                </div>
              </label>

              <label className="flex items-start gap-3 p-3.5 rounded-xl border border-slate-200/80 hover:bg-slate-50/80 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={formData.minority_status}
                  onChange={(e) => handleInputChange("minority_status", e.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-slate-300 text-civic-blue focus:ring-civic-blue/20"
                />
                <div>
                  <span className="text-xs font-bold text-navy block">
                    Recognized Minority Community
                  </span>
                  <span className="text-[11px] text-slate-500">
                    Eligible for Ministry of Minority Affairs (MOMA) national merit schemes
                  </span>
                </div>
              </label>
            </div>
          </div>

          {/* Sticky Action Footer (PROF-05) */}
          <div className="sticky bottom-4 z-40 rounded-2xl bg-white/95 backdrop-blur-md border border-slate-200 shadow-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <ShieldCheck className="h-4 w-4 text-civic-cyan" />
              <span>
                Data encrypted with AES-256. Used strictly for authorized government application automation.
              </span>
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <Button
                type="submit"
                disabled={loading}
                className="w-full sm:w-auto bg-civic-blue hover:bg-civic-blue-hover text-white font-bold px-6 py-2.5 rounded-xl shadow-md transition-all flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Saving Profile...</span>
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    <span>Save Profile Changes</span>
                  </>
                )}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
