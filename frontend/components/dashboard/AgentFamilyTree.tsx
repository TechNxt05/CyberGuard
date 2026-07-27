'use client';

import React from 'react';
import { GitBranch, User, ArrowDownRight, CornerDownRight } from 'lucide-react';

interface TreeNode {
  id: string;
  name: string;
  role: string;
  status: string;
  children?: TreeNode[];
}

const defaultTree: TreeNode = {
  id: 'understanding',
  name: 'UnderstandingAgent',
  role: 'Incident Intake & Profile Extractor',
  status: 'complete',
  children: [
    {
      id: 'evidence',
      name: 'EvidenceAgent',
      role: 'Multimodal OCR & Entity Intelligence',
      status: 'complete',
      children: [
        {
          id: 'strategy',
          name: 'StrategyAgent',
          role: 'Resolution Lifecycle Planner',
          status: 'complete',
          children: [
            { id: 'recovery', name: 'RecoveryAgent', role: 'Immediate Victim Action Guide', status: 'complete' },
            { id: 'authority', name: 'AuthorityMapperAgent', role: 'Cybercell & Police Mapping', status: 'complete' },
            { id: 'prevention', name: 'PreventionAgent', role: 'Long-term Hardening & Tips', status: 'complete' },
          ]
        }
      ]
    },
    {
      id: 'threat_intel',
      name: 'ThreatIntelAgent',
      role: 'OSINT & Longitudinal Memory Lookup',
      status: 'complete',
    }
  ]
};

export const AgentFamilyTree: React.FC<{ data?: TreeNode }> = ({ data = defaultTree }) => {
  const renderNode = (node: TreeNode, depth: number = 0) => {
    return (
      <div key={node.id} className="my-2 transition-all duration-300">
        <div
          className={`flex items-center justify-between p-3 rounded-lg border backdrop-blur-sm ${
            depth === 0
              ? 'bg-cyan-950/40 border-cyan-500/40 shadow-lg shadow-cyan-950/50'
              : depth === 1
              ? 'bg-slate-800/60 border-slate-700 ml-6'
              : depth === 2
              ? 'bg-slate-900/60 border-slate-700/80 ml-12'
              : 'bg-slate-950/80 border-slate-800 ml-16'
          }`}
        >
          <div className="flex items-center space-x-3">
            {depth > 0 && <CornerDownRight className="w-4 h-4 text-cyan-400/70" />}
            <div className="p-1.5 bg-slate-800 rounded border border-slate-700 text-cyan-400">
              <User className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-sm text-slate-100">{node.name}</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  {node.status}
                </span>
              </div>
              <p className="text-xs text-slate-400">{node.role}</p>
            </div>
          </div>
          <span className="text-[11px] font-mono text-slate-500">Depth: {depth}</span>
        </div>

        {node.children && (
          <div className="relative pl-2 border-l border-cyan-500/20 ml-4 mt-1 space-y-1">
            {node.children.map((child) => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur-md border border-cyan-500/20 rounded-xl p-6 shadow-2xl text-slate-100">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-cyan-500/20">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-cyan-500/10 rounded-lg border border-cyan-500/30 text-cyan-400">
            <GitBranch className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-cyan-400">Tree-Shaped Agent Family Delegation</h3>
            <p className="text-xs text-slate-400">Non-linear span hierarchy ("Who instantiated whom")</p>
          </div>
        </div>
      </div>
      <div className="overflow-x-auto">{renderNode(data)}</div>
    </div>
  );
};
