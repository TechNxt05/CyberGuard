'use client';

import React from 'react';
import { ShieldCheck, Target, AlertOctagon, TrendingUp, Layers, CheckCircle2, Clock } from 'lucide-react';

interface CaseCommandCenterProps {
  caseId?: string;
  title?: string;
  status?: string;
  priority?: string;
  severity?: string;
  financialImpact?: number;
  currentObjective?: string;
}

export const CaseCommandCenter: React.FC<CaseCommandCenterProps> = ({
  caseId = "case_investigation_001",
  title = "Investigation: UPI Phishing & Financial Fraud",
  status = "INVESTIGATING",
  priority = "HIGH",
  severity = "CRITICAL",
  financialImpact = 15000,
  currentObjective = "Entity Resolution & Multi-Hop Attack Path Traversal"
}) => {
  return (
    <div className="bg-slate-900/80 backdrop-blur-md border border-cyan-500/30 rounded-xl p-6 shadow-2xl text-slate-100 font-sans">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-cyan-500/20">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-cyan-500/10 rounded-lg border border-cyan-500/30 text-cyan-400">
            <ShieldCheck className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xl font-bold text-cyan-300">{title}</h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
                {status}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">Case ID: <span className="font-mono text-slate-300">{caseId}</span></p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className="px-3 py-1 bg-red-500/10 text-red-400 border border-red-500/30 text-xs font-bold rounded-lg flex items-center">
            <AlertOctagon className="w-3.5 h-3.5 mr-1" /> {severity} SEVERITY
          </span>
          <span className="px-3 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-bold rounded-lg">
            {priority} PRIORITY
          </span>
        </div>
      </div>

      {/* Case Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-slate-800/60 p-4 rounded-lg border border-slate-700">
          <div className="flex items-center text-xs text-slate-400 mb-1">
            <TrendingUp className="w-4 h-4 mr-1 text-emerald-400" /> Financial Loss at Risk
          </div>
          <div className="text-2xl font-mono font-bold text-emerald-400">₹{financialImpact.toLocaleString()}</div>
        </div>
        <div className="bg-slate-800/60 p-4 rounded-lg border border-slate-700">
          <div className="flex items-center text-xs text-slate-400 mb-1">
            <Target className="w-4 h-4 mr-1 text-cyan-400" /> Active Objective
          </div>
          <div className="text-xs font-semibold text-slate-200 truncate">{currentObjective}</div>
        </div>
        <div className="bg-slate-800/60 p-4 rounded-lg border border-slate-700">
          <div className="flex items-center text-xs text-slate-400 mb-1">
            <Layers className="w-4 h-4 mr-1 text-purple-400" /> Investigation Phase
          </div>
          <div className="text-sm font-mono font-bold text-purple-300 flex items-center">
            <Clock className="w-3.5 h-3.5 mr-1" /> PHASE D: COMPETING HYPOTHESIS
          </div>
        </div>
      </div>
    </div>
  );
};
