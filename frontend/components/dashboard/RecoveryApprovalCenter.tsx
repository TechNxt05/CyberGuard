'use client';

import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, XCircle, Play, Lock, FileText } from 'lucide-react';

interface RecoveryActionItem {
  id: string;
  type: string;
  title: string;
  description: string;
  recommendedBy: string;
  status: 'PROPOSED' | 'APPROVED' | 'REJECTED' | 'EXECUTED';
}

const initialActions: RecoveryActionItem[] = [
  {
    id: 'act_001',
    type: 'bank_freeze',
    title: 'Freeze Collect Request at HDFC Fraud Desk',
    description: 'Issue urgent freeze directive for UPI handle pay.refund8821@ybl to prevent asset dissipation.',
    recommendedBy: 'RecoveryAgent',
    status: 'PROPOSED'
  },
  {
    id: 'act_002',
    type: 'police_report',
    title: 'Generate National Cybercrime Reporting Portal (1930) FIR Package',
    description: 'Prepare C6 Legal Evidence Package with digital signature and SHA-256 evidence manifest.',
    recommendedBy: 'AuthorityMapperAgent',
    status: 'PROPOSED'
  }
];

export const RecoveryApprovalCenter: React.FC = () => {
  const [actions, setActions] = useState<RecoveryActionItem[]>(initialActions);

  const handleApprove = (id: string) => {
    setActions((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'APPROVED' } : a))
    );
  };

  const handleReject = (id: string) => {
    setActions((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'REJECTED' } : a))
    );
  };

  const handleExecute = (id: string) => {
    setActions((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'EXECUTED' } : a))
    );
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur-md border border-cyan-500/30 rounded-xl p-6 shadow-2xl text-slate-100 font-sans">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-cyan-500/20">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-amber-500/10 rounded-lg border border-amber-500/30 text-amber-400">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-amber-300">Human-in-the-Loop Recovery Approval Gates</h3>
            <p className="text-xs text-slate-400">High-impact recovery actions require explicit investigator approval before execution</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {actions.map((act) => (
          <div key={act.id} className="bg-slate-800/60 p-4 rounded-lg border border-slate-700">
            <div className="flex justify-between items-start mb-2">
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-bold text-slate-100">{act.title}</h4>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold border ${
                      act.status === 'PROPOSED'
                        ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                        : act.status === 'APPROVED'
                        ? 'bg-blue-500/20 text-blue-400 border-blue-500/30'
                        : act.status === 'EXECUTED'
                        ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                        : 'bg-red-500/20 text-red-400 border-red-500/30'
                    }`}
                  >
                    {act.status}
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-1">{act.description}</p>
                <p className="text-[11px] text-slate-500 mt-1">Recommended by: <span className="text-cyan-400">{act.recommendedBy}</span></p>
              </div>

              <div className="flex items-center space-x-2">
                {act.status === 'PROPOSED' && (
                  <>
                    <button
                      onClick={() => handleApprove(act.id)}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-semibold flex items-center"
                    >
                      <CheckCircle className="w-3.5 h-3.5 mr-1" /> Approve
                    </button>
                    <button
                      onClick={() => handleReject(act.id)}
                      className="px-3 py-1.5 bg-red-600/30 hover:bg-red-600/50 text-red-300 rounded text-xs font-semibold flex items-center border border-red-500/40"
                    >
                      <XCircle className="w-3.5 h-3.5 mr-1" /> Reject
                    </button>
                  </>
                )}
                {act.status === 'APPROVED' && (
                  <button
                    onClick={() => handleExecute(act.id)}
                    className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-semibold flex items-center animate-pulse"
                  >
                    <Play className="w-3.5 h-3.5 mr-1" /> Execute Action
                  </button>
                )}
                {act.status === 'EXECUTED' && (
                  <span className="text-xs text-emerald-400 font-mono flex items-center">
                    <CheckCircle className="w-4 h-4 mr-1" /> Executed & Logged
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
