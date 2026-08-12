import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VeriLens — Conversational Verification Engine",
  description:
    "Send a link, upload media, or ask VeriLens through social platforms. Get evidence-backed verdicts, not labels. The conversational verification layer for social media.",
  keywords: ["fact-check", "misinformation", "verification", "deepfake detection", "VeriLens"],
  openGraph: {
    title: "VeriLens — Verify what you see.",
    description:
      "Evidence-backed verdicts for suspicious content. Multimodal analysis, claim extraction, and conversational AI.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
