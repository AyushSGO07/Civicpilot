/**
 * Centralized API configuration for CivicPilot frontend.
 * Dynamically resolves API base URL across local development and Vercel deployments.
 */

export const getApiBaseUrl = (): string => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/+$/, "");
  }
  if (typeof window !== "undefined") {
    // If developing locally on localhost/127.0.0.1 without custom env var
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
      return "http://127.0.0.1:8000";
    }
    // Deployed production domain (Vercel) -> use same-origin relative path
    return "";
  }
  return process.env.NODE_ENV === "production" ? "" : "http://127.0.0.1:8000";
};

export const API_BASE_URL = getApiBaseUrl();
