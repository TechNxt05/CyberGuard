import React from "react";
import { motion, Variants } from "framer-motion";
import { ShieldAlert, Database, Skull, Zap, Radio } from "lucide-react";

export interface MemoryStatsData {
  total_tracked_entities: number;
  confirmed_threats: number;
  high_risk_entities: number;
  type_breakdown: { type: string; count: number }[];
}

interface Props {
  stats: MemoryStatsData | null;
  loading: boolean;
}

export const MemoryStats = ({ stats, loading }: Props) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="h-28 rounded-2xl glass-card bg-black/40 border border-white/5 animate-pulse flex flex-col justify-between p-4"
          >
            <div className="h-4 bg-white/10 rounded w-1/3"></div>
            <div className="h-8 bg-white/5 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!stats) return null;

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.1,
        duration: 0.4,
        ease: "easeOut",
      },
    }),
  };

  return (
    <div className="mb-8">
      {/* Title block */}
      <div className="flex items-center gap-2 mb-4 justify-between">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          <h3 className="text-xs font-bold uppercase tracking-widest text-blue-400 font-mono flex items-center gap-1.5">
            <Radio size={12} className="animate-pulse" /> Longitudinal Threat Intelligence Network
          </h3>
        </div>
        <span className="text-[9px] text-gray-500 font-mono">STATUS: SYNCED & SECURED</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Total Tracked Card */}
        <motion.div
          custom={0}
          initial="hidden"
          animate="visible"
          variants={cardVariants as Variants}
          className="relative overflow-hidden rounded-2xl border border-white/5 bg-slate-950/40 backdrop-blur-xl p-5 hover:border-blue-500/30 transition-all duration-300 group"
        >
          <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-full blur-2xl group-hover:bg-blue-500/10 transition-all duration-500" />
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400 font-mono">Tracked Indicators</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Database size={16} />
            </div>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-3xl font-extrabold tracking-tight text-white font-mono bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
              {stats.total_tracked_entities}
            </span>
          </div>
          <p className="text-[9px] text-gray-500 font-mono mt-1">Cross-case unique identifiers</p>
        </motion.div>

        {/* Confirmed Threat Actors Card */}
        <motion.div
          custom={1}
          initial="hidden"
          animate="visible"
          variants={cardVariants as Variants}
          className="relative overflow-hidden rounded-2xl border border-white/5 bg-slate-950/40 backdrop-blur-xl p-5 hover:border-red-500/30 transition-all duration-300 group"
        >
          <div className="absolute top-0 right-0 w-24 h-24 bg-red-500/5 rounded-full blur-2xl group-hover:bg-red-500/10 transition-all duration-500" />
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400 font-mono">Confirmed Offenders</span>
            <div className="p-2 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20">
              <Skull size={16} />
            </div>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-3xl font-extrabold tracking-tight text-white font-mono bg-gradient-to-r from-white to-red-200 bg-clip-text text-transparent">
              {stats.confirmed_threats}
            </span>
          </div>
          <p className="text-[9px] text-red-400/50 font-mono mt-1">Flagged in 3+ investigations</p>
        </motion.div>

        {/* High Risk Card */}
        <motion.div
          custom={2}
          initial="hidden"
          animate="visible"
          variants={cardVariants as Variants}
          className="relative overflow-hidden rounded-2xl border border-white/5 bg-slate-950/40 backdrop-blur-xl p-5 hover:border-amber-500/30 transition-all duration-300 group"
        >
          <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-full blur-2xl group-hover:bg-amber-500/10 transition-all duration-500" />
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400 font-mono">Critical Markers</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <ShieldAlert size={16} />
            </div>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-3xl font-extrabold tracking-tight text-white font-mono bg-gradient-to-r from-white to-amber-200 bg-clip-text text-transparent">
              {stats.high_risk_entities}
            </span>
          </div>
          <p className="text-[9px] text-amber-400/50 font-mono mt-1">Risk probability &ge; 70%</p>
        </motion.div>

        {/* Breakdown Card */}
        <motion.div
          custom={3}
          initial="hidden"
          animate="visible"
          variants={cardVariants as Variants}
          className="relative overflow-hidden rounded-2xl border border-white/5 bg-slate-950/40 backdrop-blur-xl p-4 hover:border-purple-500/30 transition-all duration-300 group flex flex-col justify-center"
        >
          <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/5 rounded-full blur-2xl group-hover:bg-purple-500/10 transition-all duration-500" />
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400 font-mono">Vector Distribution</span>
            <Zap size={14} className="text-purple-400" />
          </div>
          <div className="space-y-1.5 max-h-[56px] overflow-y-auto pr-1 scrollbar-hide">
            {stats.type_breakdown.length === 0 ? (
              <span className="text-[10px] text-gray-500 font-mono italic">No threat vectors recorded</span>
            ) : (
              stats.type_breakdown.slice(0, 3).map((item, idx) => (
                <div key={idx} className="flex justify-between items-center text-[10px] font-mono">
                  <span className="text-gray-400 uppercase truncate max-w-[80px]">
                    {item.type.replace("_", " ")}
                  </span>
                  <div className="flex items-center gap-1.5">
                    <div className="w-12 h-1 bg-white/5 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-purple-500/80 rounded-full" 
                        style={{ width: `${Math.min(100, (item.count / (stats.total_tracked_entities || 1)) * 100)}%` }}
                      />
                    </div>
                    <span className="text-white font-bold">{item.count}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};
