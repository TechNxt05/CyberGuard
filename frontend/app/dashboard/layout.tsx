import React from "react";
import { UserButton } from "@clerk/nextjs";
import Link from "next/link";
import { ShieldCheck, LayoutDashboard } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-50 selection:bg-blue-500/30">
      <header className="sticky top-0 z-50 w-full border-b border-white/5 glass-panel">
        <div className="flex h-16 items-center px-6 justify-between max-w-[1600px] mx-auto w-full">
          <Link href="/" className="flex items-center gap-2 font-bold text-lg hover:text-blue-400 transition-colors">
            <ShieldCheck className="text-blue-500" />
            <span>CyberGuardAI One X</span>
          </Link>
          
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="text-sm font-medium text-gray-300 hover:text-white flex items-center gap-2">
              <LayoutDashboard size={16} /> Cases
            </Link>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </header>

      <main className="flex-1 w-full relative overflow-hidden">
        {/* Ambient Backgrounds */}
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-emerald-900/10 rounded-full blur-[120px] pointer-events-none" />
        
        {children}
      </main>
    </div>
  );
}
