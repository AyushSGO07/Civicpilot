import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "CivicPilot | Autonomous Public Service Platform",
  description:
    "AI-powered citizen service portal for discovering government schemes, evaluating eligibility, and navigating applications.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-canvas text-navy antialiased selection:bg-civic-blue selection:text-white">
        {children}
      </body>
    </html>
  );
}
