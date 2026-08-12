import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Inter({
  subsets: ["latin"],
  variable: "--font-geistsans",
  weight: ["400", "500", "600", "700"],
});

const geistMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-geistmono",
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Lucent — Midnight AI Verification Console",
  description:
    "A midnight developer console for social media verification — supporting Instagram Reels, X posts, YouTube Shorts, WhatsApp, and Web.",
  keywords: ["fact-check", "misinformation", "verification", "deepfake detection", "Lucent", "AI verification"],
  openGraph: {
    title: "Lucent — Midnight AI Verification Console",
    description:
      "Evidence-backed verdicts, multimodal analysis, and claim extraction in a midnight developer console.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
