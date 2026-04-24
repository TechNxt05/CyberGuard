import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

interface ProbabilityMeterProps {
  score: number;
}

export function ProbabilityMeter({ score }: ProbabilityMeterProps) {
  const data = [
    { name: "Risk", value: score },
    { name: "Safe", value: 100 - score },
  ];
  
  const COLORS = ["#ef4444", "#334155"]; // Red for risk, slate for safe

  // If score is high, it's critical
  const isHighRisk = score > 70;
  const isMediumRisk = score > 40 && score <= 70;

  let labelColor = "text-emerald-400";
  let labelText = "SAFE";
  if (isHighRisk) { labelColor = "text-red-500 neon-text-red"; labelText = "CRITICAL RISK"; COLORS[0] = "#ef4444"; }
  else if (isMediumRisk) { labelColor = "text-yellow-500"; labelText = "SUSPICIOUS"; COLORS[0] = "#eab308"; }

  return (
    <div className="flex flex-col items-center justify-center p-4 glass-panel rounded-xl">
      <h3 className="text-gray-300 font-semibold mb-2">Threat Probability</h3>
      <div className="relative w-40 h-40">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={70}
              startAngle={180}
              endAngle={0}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center mt-6">
          <span className={`text-2xl font-bold ${labelColor}`}>{score}%</span>
          <span className={`text-xs font-semibold ${labelColor}`}>{labelText}</span>
        </div>
      </div>
    </div>
  );
}
