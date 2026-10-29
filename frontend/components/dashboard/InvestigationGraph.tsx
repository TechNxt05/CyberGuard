"use client";

import React, { useEffect, useMemo } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Edge,
  Node,
} from '@xyflow/react';

import '@xyflow/react/dist/style.css';

import type { GraphData } from '@/lib/api';

interface InvestigationGraphProps {
  data: GraphData;
}

// First node in the centre, the rest on a circle around it.
const layout = (i: number, total: number) => {
  if (i === 0) return { x: 0, y: 0 };
  const angle = (2 * Math.PI * (i - 1)) / Math.max(1, total - 1);
  const radius = 160 + total * 12;
  return { x: Math.cos(angle) * radius, y: Math.sin(angle) * radius };
};

export default function InvestigationGraph({ data }: InvestigationGraphProps) {
  // Convert backend nodes to React Flow nodes
  const initialNodes: Node[] = useMemo(() => {
    return data.nodes.map((n, i) => {
      let bgColor = '#0f172a';
      let borderColor = '#334155';
      
      switch(n.type) {
        case 'victim': bgColor = '#1e293b'; borderColor = '#3b82f6'; break;
        case 'threat_actor': bgColor = '#2a0a12'; borderColor = '#ef4444'; break;
        case 'mule_account': bgColor = '#2d1b09'; borderColor = '#f59e0b'; break;
        case 'url': bgColor = '#0a192f'; borderColor = '#0ea5e9'; break;
        case 'wallet': bgColor = '#142013'; borderColor = '#10b981'; break;
        case 'ip': bgColor = '#1c1936'; borderColor = '#8b5cf6'; break;
        case 'email': bgColor = '#0f172a'; borderColor = '#64748b'; break;
        case 'phone': bgColor = '#1a1a2e'; borderColor = '#a855f7'; break;
        case 'scammer': bgColor = '#2a0a12'; borderColor = '#ef4444'; break;
        default: break;
      }

      return {
        id: n.id,
        type: 'default',
        position: layout(i, data.nodes.length),
        data: { label: n.label },
        style: { 
          background: bgColor,
          color: '#f1f5f9',
          border: `1px solid ${borderColor}`,
          borderRadius: '8px',
          padding: '10px',
          fontSize: '12px',
          fontWeight: 'bold',
          width: 150,
          boxShadow: `0 0 10px ${borderColor}33`
        }
      };
    });
  }, [data.nodes]);

  const initialEdges: Edge[] = useMemo(() => {
    return data.edges.map(e => ({
      id: e.id,
      source: e.source,
      target: e.target,
      label: e.label,
      animated: true,
      style: { stroke: '#334155' },
      labelStyle: { fill: '#94a3b8', fontSize: '10px', fontWeight: 'bold' }
    }));
  }, [data.edges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // useNodesState only reads its argument once; push later analysis results into the flow.
  useEffect(() => setNodes(initialNodes), [initialNodes, setNodes]);
  useEffect(() => setEdges(initialEdges), [initialEdges, setEdges]);

  return (
    <div className="w-full h-[400px] bg-slate-950/50 rounded-xl border border-white/5 overflow-hidden glass-panel relative">
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-blue-400">Cyber Investigation Graph</h3>
      </div>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        colorMode="dark"
      >
        <Controls showInteractive={false} />
        <MiniMap 
            nodeStrokeWidth={3} 
            maskColor="rgba(0, 0, 0, 0.5)" 
            style={{ background: '#020617' }} 
        />
        <Background color="#1e293b" gap={20} />
      </ReactFlow>
    </div>
  );
}
