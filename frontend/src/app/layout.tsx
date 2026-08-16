import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta-sans",
  weight: ["400", "500", "600", "700", "800"],
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["400", "500", "600", "700"],
});

const sometypeMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-sometype-mono",
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "Lucent — Evidence-Backed Content Verification",
  description:
    "Lucent is an independent verification layer that provides clear, evidence-backed explanations and structured verdicts for text claims, URLs, and media.",
  keywords: ["fact-check", "misinformation", "verification", "Lucent", "evidence", "news intelligence"],
  openGraph: {
    title: "Lucent — Evidence-Backed Content Verification",
    description:
      "Cross-examine suspicious claims, inspect primary evidence, and get plain-language truth.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${plusJakartaSans.variable} ${inter.variable} ${sometypeMono.variable}`}
    >
      <body>{children}</body>
    </html>
  );
}
