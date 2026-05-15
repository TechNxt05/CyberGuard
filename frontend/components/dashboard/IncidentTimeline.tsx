"use client";

import React from "react";
import { motion } from "framer-motion";
import { Clock, ShieldCheck, FileText, AlertTriangle } from "lucide-react";

interface TimelineEvent {
  id: string;
  timestamp: string;
  eventType: string;
  description: string;
  impact?: string;
  relativeTime?: string;
}

interface IncidentTimelineProps {
  events: TimelineEvent[];
}

export default function IncidentTimeline({ events }: IncidentTimelineProps) {
  
  const getEventColor = (type: string) => {
      switch (type) {
          case 'reconnaissance': return 'bg-blue-500/10 text-blue-400';
          case 'initial_access': return 'bg-amber-500/10 text-amber-400';
          case 'execution': return 'bg-purple-500/10 text-purple-400';
          case 'exfiltration': return 'bg-red-500/10 text-red-400';
          case 'impact': return 'bg-red-600/10 text-red-500';
          default: return 'bg-gray-500/10 text-gray-400';
      }
  };

  return (
    <div className="space-y-4 relative">
      {/* Vertical Line */}
      <div className="absolute left-4 top-2 bottom-2 w-px bg-white/5" />

      {events.map((event, i) => (
        <motion.div
          key={event.id}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.1 }}
          className="relative pl-10 group"
        >
          {/* Dot */}
          <div className="absolute left-[13px] top-1.5 w-2 h-2 rounded-full bg-blue-500 ring-4 ring-blue-500/10 group-hover:scale-125 transition-transform" />
          
          <div className="p-3 rounded-lg border border-white/5 bg-white/[0.02] group-hover:bg-white/[0.04] transition-all relative">
            
            {/* Relative Time Badge */}
            {event.relativeTime && (
                <div className="absolute -top-3 right-2 bg-blue-600 text-white text-[9px] font-bold px-2 py-0.5 rounded shadow-lg">
                    {event.relativeTime}
                </div>
            )}

            <div className="flex justify-between items-start mb-1 mt-1">
              <span className="text-[10px] font-mono text-gray-500">
                {new Date(event.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
              </span>
              <span className={`text-[8px] px-1.5 py-0.5 rounded uppercase font-bold tracking-tighter ${getEventColor(event.eventType)}`}>
                {event.eventType.replace('_', ' ')}
              </span>
            </div>
            <p className="text-xs text-gray-300 font-medium">{event.description}</p>
            {event.impact && (
              <div className="mt-2 flex items-center gap-1.5">
                <span className="text-[9px] text-gray-500 uppercase tracking-widest font-bold">Impact:</span>
                <span className="text-[9px] text-red-400 font-bold">{event.impact}</span>
              </div>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
