"use client";

import React from "react";
import { Terminal, Shield, Eye, BrainCircuit, Activity, Database, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export interface AgentActivity {
  id: string;
  agent: string;
  msg: string;
  status: "pending" | "loading" | "success" | "error";
  timestamp: string;
}

/** Shows progress events produced by the page while it calls the backend (newest first). */
export default function AgentActivityStream({ activities }: { activities: AgentActivity[] }) {
    const getAgentIcon = (agent: string) => {
        switch (agent.toLowerCase()) {
            case "understanding": return <Eye size={12} className="text-blue-400" />;
            case "evidence": return <Shield size={12} className="text-emerald-400" />;
            case "threat_intel": return <Activity size={12} className="text-red-400" />;
            case "strategy": return <BrainCircuit size={12} className="text-purple-400" />;
            case "memory": return <Database size={12} className="text-amber-400" />;
            case "recovery": return <Zap size={12} className="text-yellow-400" />;
            case "authority_mapper": return <Shield size={12} className="text-cyan-400" />;
            default: return <Terminal size={12} className="text-gray-400" />;
        }
    };

    return (
        <div className="flex flex-col bg-black/60 border-t border-white/5 h-32 overflow-hidden relative font-mono">
            <div className="absolute top-0 left-0 w-full h-4 bg-gradient-to-b from-black/60 to-transparent z-10 pointer-events-none" />
            
            <div className="p-3 overflow-y-auto custom-scrollbar space-y-1.5 z-0 flex flex-col-reverse h-full">
                <AnimatePresence>
                    {activities.map((act) => (
                        <motion.div 
                            key={act.id} 
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className={`flex items-start gap-3 text-[10px] ${act.status === 'error' ? 'text-red-400' : 'text-gray-400'}`}
                        >
                            <div className="mt-0.5 opacity-70">
                                {getAgentIcon(act.agent)}
                            </div>
                            <div className="flex-1">
                                <span className="font-bold text-gray-300">[{act.agent}]</span>
                                <span className="ml-2 leading-tight">{act.msg}</span>
                            </div>
                            <div className="text-[9px] text-gray-600 shrink-0">
                                {new Date(act.timestamp).toLocaleTimeString([], { hour12: false })}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
                
                {activities.length === 0 && (
                    <div className="flex items-center gap-2 text-[10px] text-gray-600 italic">
                        <Terminal size={10} /> No activity yet.
                    </div>
                )}
            </div>
            
            <div className="absolute bottom-0 left-0 w-full h-4 bg-gradient-to-t from-black/60 to-transparent z-10 pointer-events-none" />
        </div>
    );
}
