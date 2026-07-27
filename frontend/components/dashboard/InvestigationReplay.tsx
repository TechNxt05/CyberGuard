'use client';

import React, { useState } from 'react';
import { Play, Pause, RotateCcw, ChevronRight, CheckCircle2, AlertTriangle, Terminal } from 'lucide-react';

interface TrajectoryStep {
  step_index: number;
  agent_name: string;
  reasoning: string;
  tool_calls: { tool_name: string; output: string }[];
  retries: number;
  errors: string[];
  timestamp: string;
}

const sampleTrajectory: TrajectoryStep[] = [
  {
    step_index: 1,
    agent_name: 'UnderstandingAgent',
    reasoning: 'Parsed incoming incident report. Extracted indicators: UPI ID pay.refund8821@ybl, Phone +919876543210.',
    tool_calls: [{ tool_name: 'regex_entity_extractor', output: 'Extracted 2 indicators' }],
    retries: 0,
    errors: [],
    timestamp: '00:00.12'
  },
  {
    step_index: 2,
    agent_name: 'EvidenceAgent',
    reasoning: 'Ran Vision OCR on payment screenshot. Detected fake HDFC/YBL refund banner.',
    tool_calls: [{ tool_name: 'vision_ocr_engine', output: 'OCR confidence 95%' }],
    retries: 0,
    errors: [],
    timestamp: '00:00.85'
  },
  {
    step_index: 3,
    agent_name: 'ThreatIntelAgent',
    reasoning: 'Queried longitudinal threat memory. Match found: UPI ID pay.refund8821@ybl seen in 3 prior cases. CONFIRMED THREAT (Risk score 0.75).',
    tool_calls: [{ tool_name: 'memory_service_check', output: 'Found 3 prior occurrences' }],
    retries: 0,
    errors: [],
    timestamp: '00:02.05'
  },
  {
    step_index: 4,
    agent_name: 'StrategyAgent',
    reasoning: 'Formulated 4-phase containment plan: 1. Freeze UPI handle, 2. File Cybercrime report, 3. Notify HDFC Bank helpline.',
    tool_calls: [{ tool_name: 'strategy_planner', output: 'Generated 4 lifecycle steps' }],
    retries: 0,
    errors: [],
    timestamp: '00:02.75'
  },
  {
    step_index: 5,
    agent_name: 'RecoveryAgent',
    reasoning: 'Generated immediate step-by-step victim guide for 1930 Cybercell reporting.',
    tool_calls: [{ tool_name: 'recovery_guide_builder', output: 'Guide ready' }],
    retries: 0,
    errors: [],
    timestamp: '00:03.25'
  },
  {
    step_index: 6,
    agent_name: 'AuthorityMapperAgent',
    reasoning: 'Mapped HDFC Bank cyber fraud desk and Mumbai Cyber Crime Cell jurisdiction.',
    tool_calls: [{ tool_name: 'authority_mapper', output: 'Mapped 2 authorities' }],
    retries: 0,
    errors: [],
    timestamp: '00:03.65'
  },
  {
    step_index: 7,
    agent_name: 'PreventionAgent',
    reasoning: 'Generated 3 actionable security recommendations and updated longitudinal threat ledger.',
    tool_calls: [{ tool_name: 'prevention_generator', output: 'Insights finalized' }],
    retries: 0,
    errors: [],
    timestamp: '00:04.10'
  }
];

export const InvestigationReplay: React.FC = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  const currentStep = sampleTrajectory[currentStepIndex];

  const handleNext = () => {
    if (currentStepIndex < sampleTrajectory.length - 1) {
      setCurrentStepIndex((prev) => prev + 1);
    }
  };

  const handleReset = () => {
    setCurrentStepIndex(0);
    setIsPlaying(false);
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur-md border border-cyan-500/20 rounded-xl p-6 shadow-2xl text-slate-100 font-sans">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-cyan-500/20">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-cyan-500/10 rounded-lg border border-cyan-500/30 text-cyan-400">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-cyan-400">AuditAI Investigation Trajectory Replay</h3>
            <p className="text-xs text-slate-400">Step-by-step playback of agent reasoning, tool calls, and state transitions</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleReset}
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 border border-slate-700 text-xs flex items-center"
          >
            <RotateCcw className="w-3.5 h-3.5 mr-1" /> Reset
          </button>
          <button
            onClick={handleNext}
            disabled={currentStepIndex >= sampleTrajectory.length - 1}
            className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold flex items-center disabled:opacity-50"
          >
            Next Step <ChevronRight className="w-3.5 h-3.5 ml-1" />
          </button>
        </div>
      </div>

      {/* Progress Timeline */}
      <div className="flex items-center justify-between mb-6 px-2">
        {sampleTrajectory.map((step, idx) => (
          <button
            key={step.step_index}
            onClick={() => setCurrentStepIndex(idx)}
            className={`flex flex-col items-center group transition-all ${
              idx === currentStepIndex ? 'scale-110' : 'opacity-70'
            }`}
          >
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold font-mono border ${
                idx === currentStepIndex
                  ? 'bg-cyan-500 text-slate-950 border-cyan-300 ring-2 ring-cyan-500/50'
                  : idx < currentStepIndex
                  ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                  : 'bg-slate-800 text-slate-400 border-slate-700'
              }`}
            >
              {step.step_index}
            </div>
            <span className="text-[10px] text-slate-400 mt-1 hidden md:block max-w-[80px] truncate">{step.agent_name}</span>
          </button>
        ))}
      </div>

      {/* Current Step Card */}
      {currentStep && (
        <div className="bg-slate-850/90 border border-slate-700/80 rounded-lg p-5">
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm font-bold text-cyan-300 font-mono">
              Step #{currentStep.step_index}: {currentStep.agent_name}
            </span>
            <span className="text-xs text-slate-400 font-mono">{currentStep.timestamp}</span>
          </div>

          <div className="mb-4">
            <h4 className="text-xs uppercase font-semibold text-slate-400 mb-1">Reasoning Trajectory</h4>
            <p className="text-sm text-slate-200 leading-relaxed bg-slate-900/60 p-3 rounded border border-slate-800">
              {currentStep.reasoning}
            </p>
          </div>

          <div>
            <h4 className="text-xs uppercase font-semibold text-slate-400 mb-1">Executed Tool Calls</h4>
            <div className="space-y-1.5">
              {currentStep.tool_calls.map((tool, tIdx) => (
                <div key={tIdx} className="flex items-center justify-between bg-slate-950 p-2.5 rounded text-xs font-mono border border-slate-800">
                  <span className="text-cyan-400">{tool.tool_name}</span>
                  <span className="text-slate-400">{tool.output}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
