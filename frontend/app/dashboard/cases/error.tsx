"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Investigation System Offline:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center h-[calc(100vh-64px)] w-full text-slate-300 bg-[#020617]">
      <div className="glass-card p-8 rounded-2xl border border-white/10 flex flex-col items-center max-w-md text-center bg-black/40 backdrop-blur-xl">
        <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mb-6 border border-red-500/20">
          <AlertTriangle className="text-red-500" size={32} />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2 tracking-wide uppercase">Investigation System Offline</h2>
        <p className="text-sm text-slate-400 mb-8 leading-relaxed">
          The CyberGuard backend is currently unreachable. If the system is starting from a cold state, please wait 30 seconds and try again.
        </p>
        <button
          onClick={() => reset()}
          className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold uppercase tracking-widest text-xs transition-colors shadow-lg shadow-blue-500/20"
        >
          <RefreshCw size={14} />
          Retry Connection
        </button>
      </div>
    </div>
  );
}
