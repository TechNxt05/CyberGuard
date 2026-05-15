"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, ShieldAlert, Radio } from "lucide-react";

interface ThreatFeedItem {
  id: string;
  timestamp: string;
  type: 'UPI_FRAUD' | 'PHISHING' | 'SEXTORTION' | 'INVESTMENT_FRAUD' | 'VISHING' | 'COURIER_FRAUD';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  detail: string;
  affectedPlatform: string;
  reportCount: number;
  region: string;
}

export default function ThreatIntelFeed() {
  const [threats, setThreats] = useState<ThreatFeedItem[]>([]);
  const [lastUpdated, setLastUpdated] = useState<string>("Live");

  useEffect(() => {
    const fetchFeed = async () => {
      try {
        const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_BASE}/api/threat-feed`);
        if (res.ok) {
          const data = await res.json();
          setThreats(data.threats || []);
          setLastUpdated(data.lastUpdated || "Live");
        }
      } catch (e) {
        console.error("Failed to fetch threat feed:", e);
      }
    };

    fetchFeed();
    const interval = setInterval(fetchFeed, 30000); // 30s auto-refresh
    return () => clearInterval(interval);
  }, []);

  const getSeverityStyle = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'border-red-500/50 bg-red-950/30 text-red-400';
      case 'HIGH': return 'border-amber-500/50 bg-amber-950/30 text-amber-400';
      case 'MEDIUM': return 'border-blue-500/50 bg-blue-950/30 text-blue-400';
      default: return 'border-gray-500/50 bg-gray-950/30 text-gray-400';
    }
  };

  return (
    <div className="flex flex-col h-full bg-black/40 border border-white/5 rounded-2xl overflow-hidden glass-panel">
      <div className="p-4 border-b border-white/5 flex items-center justify-between bg-black/60">
        <div className="flex items-center gap-2">
          <Radio size={16} className="text-red-500 animate-pulse" />
          <h3 className="text-xs font-bold uppercase tracking-widest text-white">Live Threat Intel</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-gray-500">Updated {lastUpdated}</span>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-3 relative">
        <AnimatePresence>
          {threats.map((t, i) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`p-3 rounded-xl border ${getSeverityStyle(t.severity)} flex flex-col gap-2 relative overflow-hidden`}
            >
              <div className="flex items-start justify-between mb-1">
                <span className="text-[10px] font-bold tracking-widest uppercase px-1.5 py-0.5 rounded bg-black/50">
                  [{t.severity}] {t.type.replace('_', ' ')}
                </span>
                <span className="text-[9px] text-gray-400 font-mono">{t.timestamp}</span>
              </div>
              <p className="text-xs font-bold text-gray-200">{t.title}</p>
              <p className="text-[10px] text-gray-400 leading-relaxed">{t.detail}</p>
              
              <div className="flex items-center gap-3 mt-1 pt-2 border-t border-white/10 text-[9px] font-medium text-gray-500 uppercase">
                <span>{t.reportCount} reports</span>
                <span>•</span>
                <span className="truncate">{t.region}</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {threats.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-600 gap-2">
            <ShieldAlert size={24} />
            <span className="text-xs">Initializing intelligence feed...</span>
          </div>
        )}
      </div>
    </div>
  );
}
