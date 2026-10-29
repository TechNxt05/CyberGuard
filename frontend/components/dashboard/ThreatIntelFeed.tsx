"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ShieldAlert, BookOpen, Fingerprint } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface Indicator {
  entity_type: string;
  entity_value: string;
  occurrence_count: number;
  last_seen: string;
  crime_types: string[];
  risk_score: number;
  is_confirmed_threat: boolean;
}

interface Advisory {
  id: string;
  type: string;
  title: string;
  detail: string;
  affectedPlatform: string;
}

interface FeedResponse {
  indicators: Indicator[];
  advisories: Advisory[];
  generatedAt: string;
}

const REFRESH_MS = 5 * 60 * 1000;

export default function ThreatIntelFeed() {
  const [feed, setFeed] = useState<FeedResponse | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const load = () =>
      apiFetch<FeedResponse>("/api/threat-feed")
        .then(data => { setFeed(data); setError(false); })
        .catch(() => setError(true));
    load();
    const interval = setInterval(load, REFRESH_MS);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-full bg-black/40 border border-white/5 rounded-2xl overflow-hidden glass-panel">
      <div className="p-4 border-b border-white/5 flex items-center justify-between bg-black/60">
        <h3 className="text-xs font-bold uppercase tracking-widest text-white">Threat Intel</h3>
        {feed && <span className="text-[10px] text-gray-500">Updated {new Date(feed.generatedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>}
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-4">
        {error && !feed && (
          <div className="flex flex-col items-center justify-center py-10 text-gray-600 gap-2">
            <ShieldAlert size={24} />
            <span className="text-xs">Feed unavailable.</span>
          </div>
        )}

        {feed && (
          <section>
            <h4 className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-red-400 mb-2">
              <Fingerprint size={12} /> Reported in multiple cases
            </h4>
            {feed.indicators.length === 0 ? (
              <p className="text-[10px] text-gray-500 leading-relaxed">No indicator has appeared in more than one investigation yet.</p>
            ) : (
              <div className="space-y-2">
                {feed.indicators.map(ind => (
                  <div key={`${ind.entity_type}:${ind.entity_value}`} className="p-2.5 rounded-lg border border-red-500/30 bg-red-950/20">
                    <p className="text-[11px] font-mono text-gray-200 break-all">{ind.entity_value}</p>
                    <p className="text-[9px] text-gray-500 uppercase mt-1">
                      {ind.entity_type.replace("_", " ")} · {ind.occurrence_count} reports · last {new Date(ind.last_seen).toLocaleDateString()}
                      {ind.is_confirmed_threat && <span className="text-red-400"> · confirmed</span>}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {feed && (
          <section>
            <h4 className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-blue-400 mb-2">
              <BookOpen size={12} /> Common scam advisories
            </h4>
            <div className="space-y-2">
              {feed.advisories.map((a, i) => (
                <motion.div
                  key={a.id}
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="p-3 rounded-xl border border-white/10 bg-white/[0.02] flex flex-col gap-1.5"
                >
                  <span className="text-[9px] font-bold tracking-widest uppercase text-gray-500">{a.type.replace("_", " ")} · {a.affectedPlatform}</span>
                  <p className="text-xs font-bold text-gray-200">{a.title}</p>
                  <p className="text-[10px] text-gray-400 leading-relaxed">{a.detail}</p>
                </motion.div>
              ))}
            </div>
            <p className="text-[9px] text-gray-600 mt-2">Advisories are curated reference material, not live detections.</p>
          </section>
        )}
      </div>
    </div>
  );
}
