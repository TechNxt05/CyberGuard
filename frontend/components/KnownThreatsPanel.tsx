import React from "react";
import { motion } from "framer-motion";

export interface KnownThreat {
  entity_type: string;
  entity_value: string;
  occurrence_count: number;
  first_seen: string;
  last_seen: string;
  crime_types: string[];
  risk_score: number;
  is_confirmed_threat: boolean;
  case_count: number;
}

interface Props {
  threats: KnownThreat[];
}

export const KnownThreatsPanel = ({ threats }: Props) => {
  if (!threats || threats.length === 0) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="border border-red-500/30 bg-red-950/20 rounded-xl p-4 mb-6 shadow-lg shadow-red-900/10 backdrop-blur-md"
    >
      <div className="flex items-center gap-2 mb-3">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"></span>
        </span>
        <h3 className="text-xs font-bold uppercase tracking-widest text-red-400 flex items-center gap-1.5 font-mono">
          ⚠️ REPEAT OFFENDER INTELLIGENCE — {threats.length} known threat{threats.length > 1 ? 's' : ''} detected
        </h3>
      </div>

      <div className="space-y-3">
        {threats.map((threat, i) => (
          <div key={i} className="bg-red-950/30 border border-red-500/20 rounded-lg p-3 hover:bg-red-950/40 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono text-red-200 select-all font-semibold break-all mr-2">{threat.entity_value}</span>
              <span className={`text-[9px] px-2 py-0.5 rounded font-mono font-bold tracking-wider shrink-0 ${
                threat.is_confirmed_threat
                  ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                  : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
              }`}>
                {threat.is_confirmed_threat ? '🔴 CONFIRMED THREAT' : '🟡 SUSPECTED'}
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1.5 text-[10px] text-gray-400 font-mono">
              <div>
                TYPE: <span className="text-gray-200 uppercase font-semibold">{threat.entity_type.replace('_', ' ')}</span>
              </div>
              <div>
                RISK SCORE: <span className="text-red-400 font-bold">{Math.round(threat.risk_score * 100)}%</span>
              </div>
              <div>
                REPORTS: <span className="text-red-300 font-semibold">{threat.occurrence_count} time{threat.occurrence_count > 1 ? 's' : ''}</span>
              </div>
              <div>
                CASES: <span className="text-red-300 font-semibold">{threat.case_count} incident{threat.case_count > 1 ? 's' : ''}</span>
              </div>
              <div className="sm:col-span-2">
                CRIME PATTERNS: <span className="text-gray-200 font-semibold uppercase">{threat.crime_types.join(', ')}</span>
              </div>
              <div className="sm:col-span-2 text-[9px] text-gray-500">
                FIRST SEEN: {new Date(threat.first_seen).toLocaleString()} // LAST SEEN: {new Date(threat.last_seen).toLocaleString()}
              </div>
            </div>
          </div>
        ))}
      </div>

      <p className="text-[10px] text-red-400/50 mt-3 font-mono leading-relaxed">
        Note: These entities have been flagged in previous CyberGuardAI OS case files. Double-check all transaction history and alert local banking nodes immediately.
      </p>
    </motion.div>
  );
};
