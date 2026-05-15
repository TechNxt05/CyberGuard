"use client";

import React from "react";
import { motion } from "framer-motion";

interface ConfidenceMeterProps {
  label: string;
  value: number; // 0 to 1
  color: string;
}

export default function ConfidenceMeter({ label, value, color }: ConfidenceMeterProps) {
  const percentage = Math.round(value * 100);

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-center px-0.5">
        <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500">{label}</span>
        <span className="text-[10px] font-mono font-bold" style={{ color }}>{percentage}%</span>
      </div>
      <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="h-full rounded-full"
          style={{ 
            backgroundColor: color,
            boxShadow: `0 0 10px ${color}40`
          }}
        />
      </div>
    </div>
  );
}
