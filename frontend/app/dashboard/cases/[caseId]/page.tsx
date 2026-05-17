"use client";

import React, { useState, useRef } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { demoCases } from "@/data/demo-cases";
import { motion } from "framer-motion";
import { Send, Image as ImageIcon, FileText, UploadCloud, Download, ShieldAlert } from "lucide-react";
import { ProbabilityMeter } from "@/components/ProbabilityMeter";
import { EntityCards } from "@/components/EntityCards";
import { InteractiveTimeline } from "@/components/InteractiveTimeline";
import { Button } from "@/components/ui/button";

import InvestigationGraph from "@/components/dashboard/InvestigationGraph";
import IncidentTimeline from "@/components/dashboard/IncidentTimeline";
import ConfidencePanel from "@/components/ConfidencePanel";
import AgentActivityStream from "@/components/dashboard/AgentActivityStream";
import ThreatIntelFeed from "@/components/dashboard/ThreatIntelFeed";
import ThreatMap from "@/components/dashboard/ThreatMap";
import { Activity, GitBranch, Clock, Terminal, AlertTriangle, ShieldCheck } from "lucide-react";
import jsPDF from "jspdf";
import { runInvestigation, getConfidence, getTimeline, getGraph } from "@/lib/api";

export default function CaseInvestigationPage() {
  const { caseId } = useParams();
  const searchParams = useSearchParams();
  const isDemo = searchParams.get('demo') === 'true';
  const [messages, setMessages] = useState<{role: string, content: string}[]>([{ role: "agent", content: "Hello. I am CyberGuard AI Investigator. I've initiated the autonomous investigation pipeline. Please upload any evidence (screenshots, phishing emails, bank transactions) or describe the incident." }]);
  const [input, setInput] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState<"graph" | "timeline">("graph");
  
  // Advanced Dashboard State
  const [confidenceData, setConfidenceData] = useState<any>(null);
  
  const [graphData, setGraphData] = useState({
    nodes: [
        { id: 'n_victim', type: 'victim', label: 'Victim (You)' },
        { id: 'n_threat', type: 'threat_actor', label: 'Attacker' }
    ],
    edges: [
        { id: 'e1', source: 'n_victim', target: 'n_threat', label: 'targeted_by' }
    ]
  });

  const [timeline, setTimeline] = useState<any[]>([
    { id: 't1', timestamp: new Date().toISOString(), eventType: "reconnaissance", description: "Case initialized in CyberGuard OS.", relativeTime: "T+0" }
  ]);

  const [agentActivity, setAgentActivity] = useState<any[]>([
    { id: 'a1', agent: "understanding", msg: "Awaiting evidence ingestion...", status: "pending", timestamp: new Date().toISOString() }
  ]);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = async (forcedInput?: string) => {
    const messageContent = forcedInput || input;
    if (!messageContent.trim() && !fileInputRef.current?.files?.length) return;
    
    setMessages(prev => [...prev, { role: "user", content: messageContent || "Uploaded evidence screenshot." }]);
    setInput("");
    setIsAnalyzing(true);
    
    // Generate session ID
    const sessionIdStr = caseId && caseId !== "new" ? (caseId as string) : `session-${Date.now()}`;

    // Demo Mode Logic
    if (isDemo && forcedInput) {
        setAgentActivity(prev => [{ id: Math.random().toString(), agent: "evidence", msg: "Analyzing visual patterns and OCR...", status: "loading", timestamp: new Date().toISOString() }, ...prev]);
        setTimeout(() => {
          setAgentActivity(prev => [{ id: Math.random().toString(), agent: "threat_intel", msg: "Cross-referencing Reddit & Twitter for similar scam patterns...", status: "loading", timestamp: new Date().toISOString() }, ...prev]);
          setConfidenceData({
            scamLikelihood: 92,
            attackSophistication: "HIGH",
            sophisticationScore: 85,
            recoveryProbability: 45,
            urgencyLevel: "CRITICAL",
            urgencyReason: "Financial transactions within last 48 hours — reversal window still open",
            timeToAct: "Act within 6 hours for best recovery outcome",
            priorityActions: [
              { action: "File cybercrime complaint at cybercrime.gov.in", deadline: "Immediately", impact: "HIGH" },
              { action: "Contact bank fraud helpline 1930", deadline: "Within 2 hours", impact: "CRITICAL" }
            ],
            riskFactors: ["Recent transaction"],
            mitigatingFactors: ["Within 48hr window"]
          });
          setGraphData(prev => ({
            nodes: [
                ...prev.nodes,
                { id: 'n_upi', type: 'wallet', label: 'UPI: scammer@ybl' },
                { id: 'n_url', type: 'url', label: 'http://login-sbi-update.xyz' }
            ],
            edges: [
                ...prev.edges,
                { id: 'e2', source: 'n_threat', target: 'n_upi', label: 'receives_funds' },
                { id: 'e3', source: 'n_threat', target: 'n_url', label: 'operates' }
            ]
          }));
          setTimeline(prev => [
            ...prev,
            { id: 't2', timestamp: new Date().toISOString(), eventType: "exfiltration", description: "Extracted fraudulent UPI handle and phishing URL.", relativeTime: "T+3 mins", impact: "High risk of fund loss" }
          ]);
          setMessages(prev => [...prev, { role: "agent", content: "Investigation complete. I've mapped the attack chain. This is a highly sophisticated phishing attempt targeting bank credentials. Recovery workflows have been generated." }]);
          setIsAnalyzing(false);
          setAgentActivity(prev => [{ id: Math.random().toString(), agent: "strategy", msg: "Response plan generated. Immediate bank notification required.", status: "success", timestamp: new Date().toISOString() }, ...prev]);
        }, 3000);
        return;
    }

    // LIVE AI MODE
    setAgentActivity([{ id: 'init', agent: "understanding", msg: "Initiating live parallel investigation...", status: "loading", timestamp: new Date().toISOString() }]);
    
    try {
        // Run main investigation
        const result = await runInvestigation({
            message: messageContent,
            sessionId: sessionIdStr
        });

        // Trigger parallel detailed analyses
        const [confRes, timelineRes, graphRes] = await Promise.all([
            getConfidence(sessionIdStr, messageContent).catch(() => null),
            getTimeline(sessionIdStr, messageContent).catch(() => null),
            getGraph(sessionIdStr, messageContent).catch(() => null)
        ]);

        if (confRes) setConfidenceData(confRes);
        if (timelineRes?.events) setTimeline(timelineRes.events);
        if (graphRes?.nodes) setGraphData(graphRes);
        
        setMessages(prev => [...prev, { role: "agent", content: "Live investigation complete. The swarm has mapped out the threat vectors and updated the dashboard." }]);
    } catch (err) {
        console.error(err);
        setMessages(prev => [...prev, { role: "agent", content: "Investigation encountered an error connecting to the AI models." }]);
    } finally {
        setIsAnalyzing(false);
    }
  };

  const handleExportPDF = () => {
    const doc = new jsPDF();
    
    doc.setFontSize(22);
    doc.setTextColor(59, 130, 246);
    doc.text("CyberGuardAI OS - Official Evidence Report", 20, 20);
    
    doc.setFontSize(12);
    doc.setTextColor(50, 50, 50);
    doc.text(`Case ID: ${caseId}`, 20, 35);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 42);
    
    if (confidenceData) {
        doc.setFontSize(16);
        doc.setTextColor(0, 0, 0);
        doc.text("Threat Assessment", 20, 60);
        
        doc.setFontSize(11);
        doc.text(`Scam Likelihood: ${confidenceData.scamLikelihood}%`, 20, 70);
        doc.text(`Urgency Level: ${confidenceData.urgencyLevel}`, 20, 77);
        doc.text(`Attack Sophistication: ${confidenceData.attackSophistication}`, 20, 84);
        doc.text(`Recovery Probability: ${confidenceData.recoveryProbability}%`, 20, 91);
        
        doc.setFontSize(14);
        doc.text("Priority Actions", 20, 110);
        confidenceData.priorityActions.forEach((act: any, idx: number) => {
            doc.setFontSize(10);
            doc.text(`${idx + 1}. ${act.action} (Deadline: ${act.deadline}) - Impact: ${act.impact}`, 20, 120 + (idx * 8));
        });
    }
    
    doc.setFontSize(16);
    doc.text("Investigation Timeline", 20, 150);
    timeline.forEach((ev: any, idx: number) => {
        doc.setFontSize(10);
        doc.text(`[${new Date(ev.timestamp).toLocaleTimeString()}] ${ev.eventType.toUpperCase()} - ${ev.description}`, 20, 160 + (idx * 8));
    });
    
    doc.save(`CyberGuard_Evidence_${caseId}.pdf`);
  };

  useEffect(() => {
    if (isDemo) {
        const demoData = demoCases.find(c => c.id === caseId);
        if (demoData) {
            setTimeout(() => {
                handleSend(demoData.summary);
            }, 500);
        }
    }
  }, [isDemo, caseId]);

  return (
    <div className="flex h-[calc(100vh-64px)] w-full max-w-[1800px] mx-auto p-4 gap-4 bg-[#020617] overflow-hidden">
      {/* FAR LEFT PANEL: Threat Feed */}
      <div className="hidden lg:flex w-72 flex-col">
          <ThreatIntelFeed />
      </div>

      {/* CENTER PANEL: Chat & Investigation Console */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex-[1.2] flex flex-col glass-card rounded-2xl overflow-hidden border border-white/5 bg-black/40 backdrop-blur-xl h-full"
      >
        <div className="p-4 border-b border-white/5 bg-slate-900/30 flex justify-between items-center relative">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            <h2 className="font-bold text-sm tracking-widest uppercase flex items-center gap-2">Investigation Console</h2>
          </div>
          <div className="flex items-center gap-3">
              {isDemo && (
                  <span className="bg-amber-500/20 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest animate-pulse">
                      Demo Mode
                  </span>
              )}
              <span className="text-[10px] text-gray-500 font-mono">NODE: OS-ALPHA-7 // {caseId}</span>
          </div>
        </div>
        
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-sm shadow-lg shadow-blue-500/20' : 'bg-slate-900/80 border border-white/10 text-gray-200 rounded-tl-sm'}`}>
                {msg.content}
              </div>
            </div>
          ))}
          {isAnalyzing && (
            <div className="flex justify-start">
              <div className="bg-slate-900/80 border border-white/10 text-blue-400 rounded-2xl rounded-tl-sm p-4 flex items-center gap-3 shadow-lg shadow-blue-500/10">
                <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '200ms' }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '400ms' }} />
                </div>
                <span className="text-xs font-bold uppercase tracking-widest">Multi-Agent Ingress...</span>
              </div>
            </div>
          )}
        </div>
        
        {/* Agent Activity Mini-Stream */}
        <AgentActivityStream sessionId={caseId as string} fallbackActivities={agentActivity} />

        {/* Input Area */}
        <div className="p-4 bg-black/60 border-t border-white/5 backdrop-blur-md">
          <div className="flex items-center gap-2 bg-slate-950/50 rounded-xl border border-white/5 p-2 pr-4 focus-within:border-blue-500/50 transition-all shadow-inner">
            <button className="p-2 text-gray-500 hover:text-blue-400 transition-colors" onClick={() => fileInputRef.current?.click()}>
              <ImageIcon size={20} />
            </button>
            <input type="file" className="hidden" ref={fileInputRef} />
            <input 
              type="text" 
              className="flex-1 bg-transparent border-none outline-none text-white text-sm px-2"
              placeholder="Describe incident or upload evidence..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button 
              className="p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all flex items-center justify-center shadow-lg shadow-blue-500/30"
              onClick={() => handleSend()}
              disabled={isAnalyzing}
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </motion.div>

      {/* RIGHT PANEL: Mission Control Dashboard */}
      <motion.div 
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex-[1.8] flex flex-col gap-6 overflow-y-auto pr-2 custom-scrollbar h-full"
      >
        {/* Intelligence Panel */}
        {confidenceData ? (
            <ConfidencePanel data={confidenceData} />
        ) : (
            <div className="flex flex-col gap-4 p-5 rounded-2xl glass-card bg-black/40 border border-white/5 animate-pulse min-h-[300px]">
                <div className="h-4 bg-white/10 rounded w-1/3 mb-4"></div>
                <div className="h-8 bg-white/5 rounded w-full mb-2"></div>
                <div className="h-8 bg-white/5 rounded w-full mb-2"></div>
                <div className="h-16 bg-white/5 rounded w-full mt-4"></div>
            </div>
        )}

        {/* Graph / Timeline Tabs */}
        <div className="flex-1 flex flex-col min-h-[500px]">
             <div className="flex gap-1 p-1 bg-black/40 rounded-lg border border-white/5 self-start mb-4">
                <button 
                    onClick={() => setActiveTab("graph")}
                    className={`px-4 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-widest transition-all ${activeTab === 'graph' ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-gray-500 hover:text-gray-300'}`}
                >
                    <GitBranch size={12} className="inline mr-2" />
                    Investigation Graph
                </button>
                <button 
                    onClick={() => setActiveTab("timeline")}
                    className={`px-4 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-widest transition-all ${activeTab === 'timeline' ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-gray-500 hover:text-gray-300'}`}
                >
                    <Clock size={12} className="inline mr-2" />
                    Incident Timeline
                </button>
            </div>

            <div className="flex-1">
                {activeTab === 'graph' ? (
                    <InvestigationGraph data={graphData} />
                ) : (
                    <div className="glass-card rounded-2xl p-6 border border-white/5 bg-black/20 backdrop-blur-md min-h-[400px]">
                        <IncidentTimeline events={timeline} />
                    </div>
                )}
            </div>
        </div>

        {/* Recovery Actions (Simplified Placeholder) */}
        <div className="glass-card rounded-2xl p-5 border border-white/5 bg-blue-500/5 backdrop-blur-md mb-6">
             <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-4">
                <div className="flex items-center gap-2">
                    <ShieldCheck size={18} className="text-blue-500" />
                    <h3 className="text-xs font-bold uppercase tracking-widest text-blue-400">Recovery Workflow</h3>
                </div>
                <Button 
                    onClick={handleExportPDF}
                    className="h-8 text-[10px] font-bold uppercase tracking-widest bg-blue-600 hover:bg-blue-500"
                >
                    <Download size={14} className="mr-2" /> Export Legal Evidence
                </Button>
             </div>
             <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                 {["Freeze Bank Account", "Report to Portal", "Generate FIR Draft", "Notify Contacts"].map((action, i) => (
                     <div key={i} className="p-3 rounded-lg border border-white/5 bg-white/[0.02] flex items-center justify-between hover:bg-white/[0.05] cursor-pointer transition-colors group">
                        <span className="text-xs font-medium text-gray-300">{action}</span>
                        <div className="w-4 h-4 rounded border border-blue-500/30 group-hover:bg-blue-500/20 transition-colors" />
                     </div>
                 ))}
             </div>
        </div>

        {/* GEOSPATIAL THREAT MAP */}
        <ThreatMap />
        
      </motion.div>
    </div>
  );
}
