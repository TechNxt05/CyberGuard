"use client";

import React from "react";
import { motion } from "framer-motion";
import { ShieldAlert, AlertTriangle, CheckCircle2 } from "lucide-react";

interface PriorityAction {
    action: string;
    deadline: string;
    impact: string;
}

interface ConfidenceData {
    scamLikelihood: number;
    attackSophistication: string;
    sophisticationScore: number;
    recoveryProbability: number;
    urgencyLevel: string;
    urgencyReason: string;
    timeToAct: string;
    priorityActions: PriorityAction[];
}

export default function ConfidencePanel({ data }: { data: ConfidenceData }) {
    
    const getScamColor = (val: number) => {
        if (val >= 80) return "bg-red-500";
        if (val >= 50) return "bg-amber-500";
        return "bg-emerald-500";
    };

    const getRecoveryColor = (val: number) => {
        if (val >= 70) return "bg-emerald-500";
        if (val >= 40) return "bg-amber-500";
        return "bg-red-500";
    };

    return (
        <div className="flex flex-col gap-4 p-5 rounded-2xl glass-card bg-black/40 border border-white/5 backdrop-blur-xl">
            <div className="flex items-center gap-2 mb-2">
                <ShieldAlert className="text-blue-500" size={18} />
                <h2 className="text-sm font-bold tracking-widest uppercase text-white">Threat Confidence</h2>
            </div>

            {/* Scam Likelihood */}
            <div className="space-y-1.5">
                <div className="flex justify-between items-center text-xs font-bold text-gray-300">
                    <span>Scam Likelihood</span>
                    <span>{data.scamLikelihood}%</span>
                </div>
                <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${data.scamLikelihood}%` }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className={`h-full rounded-full ${getScamColor(data.scamLikelihood)}`}
                    />
                </div>
            </div>

            {/* Recovery Probability */}
            <div className="space-y-1.5">
                <div className="flex justify-between items-center text-xs font-bold text-gray-300">
                    <span>Recovery Probability</span>
                    <span>{data.recoveryProbability}%</span>
                </div>
                <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${data.recoveryProbability}%` }}
                        transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
                        className={`h-full rounded-full ${getRecoveryColor(data.recoveryProbability)}`}
                    />
                </div>
            </div>

            {/* Attack Sophistication */}
            <div className="flex justify-between items-center bg-white/5 p-3 rounded-lg border border-white/5 mt-2">
                <span className="text-xs text-gray-400 font-medium">Attack Sophistication</span>
                <span className="text-xs font-bold text-white flex items-center gap-1">
                    <span className={`w-2 h-2 rounded-full ${data.attackSophistication === 'CRITICAL' || data.attackSophistication === 'HIGH' ? 'bg-red-500' : 'bg-amber-500'}`}></span>
                    {data.attackSophistication}
                </span>
            </div>

            {/* Urgency */}
            <div className={`p-4 rounded-lg border mt-2 ${data.urgencyLevel === 'CRITICAL' ? 'bg-red-500/10 border-red-500/30' : 'bg-amber-500/10 border-amber-500/30'}`}>
                <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle size={14} className={data.urgencyLevel === 'CRITICAL' ? 'text-red-400' : 'text-amber-400'} />
                    <span className={`text-xs font-bold uppercase tracking-wider ${data.urgencyLevel === 'CRITICAL' ? 'text-red-400' : 'text-amber-400'}`}>
                        URGENCY: {data.urgencyLevel}
                    </span>
                </div>
                <p className="text-[10px] text-gray-300 mt-1 leading-relaxed">
                    {data.urgencyReason}
                </p>
                <div className="mt-2 text-[10px] font-bold text-white">
                    {data.timeToAct}
                </div>
            </div>

            {/* Priority Actions */}
            <div className="mt-2">
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Priority Actions</h3>
                <div className="space-y-2">
                    {data.priorityActions.map((act, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs p-2 bg-white/5 rounded-md border border-white/5">
                            <CheckCircle2 size={14} className="text-blue-400 mt-0.5 shrink-0" />
                            <div>
                                <p className="text-gray-200 font-medium leading-tight mb-1">{act.action}</p>
                                <div className="flex gap-2 text-[9px] uppercase tracking-wider font-bold">
                                    <span className="text-gray-500">By: {act.deadline}</span>
                                    <span className={act.impact === 'CRITICAL' ? 'text-red-400' : 'text-amber-400'}>
                                        Impact: {act.impact}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
