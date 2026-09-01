import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "InterviewIQ AI | Interview intelligence", description: "Adaptive AI interview intelligence." };
export default function RootLayout({children}:{children:React.ReactNode}) { return <html lang="en"><body>{children}</body></html>; }
