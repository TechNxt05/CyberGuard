"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { motion } from "framer-motion";
import { Send, Image as ImageIcon, Download, ShieldCheck, GitBranch, Clock, X } from "lucide-react";
import jsPDF from "jspdf";

import { demoCases, DemoCase } from "@/data/demo-cases";
import { Button } from "@/components/ui/button";
import InvestigationGraph from "@/components/dashboard/InvestigationGraph";
import IncidentTimeline from "@/components/dashboard/IncidentTimeline";
import ConfidencePanel from "@/components/ConfidencePanel";
import AgentActivityStream, { AgentActivity } from "@/components/dashboard/AgentActivityStream";
import ThreatIntelFeed from "@/components/dashboard/ThreatIntelFeed";
import ThreatMap from "@/components/dashboard/ThreatMap";
import { KnownThreatsPanel } from "@/components/KnownThreatsPanel";
import {
  ApiError, ConfidenceData, GraphData, KnownThreat, MAX_IMAGE_BYTES, TimelineEventData,
  checkKnownEntities, fileToBase64, getConfidence, getGraph, getTimeline, runInvestigation,
} from "@/lib/api";

const EMPTY_GRAPH: GraphData = {
  nodes: [{ id: "n_victim", type: "victim", label: "Victim (You)" }],
  edges: [],
};

const now = () => new Date().toISOString();
let activitySeq = 0;
const activity = (agent: string, msg: string, status: AgentActivity["status"]): AgentActivity => ({
  id: `act-${++activitySeq}`, agent, msg, status, timestamp: now(),
});

/** Sample results for a demo case, derived only from that case's fixture. */
function buildDemoResults(demo: DemoCase) {
  const confidence: ConfidenceData = {
    scamLikelihood: 95,
    attackSophistication: demo.urgency === "CRITICAL" ? "HIGH" : "MEDIUM",
    sophisticationScore: demo.urgency === "CRITICAL" ? 80 : 60,
    recoveryProbability: demo.recoveryProbability,
    urgencyLevel: demo.urgency,
    urgencyReason: demo.evidence.description,
    timeToAct: demo.type === "financial_fraud" ? "Call 1930 within the first hours for the best chance of freezing funds" : "Act today",
    priorityActions: [
      { action: "Report at cybercrime.gov.in or call 1930", deadline: "Immediately", impact: "CRITICAL" },
      { action: "Preserve screenshots, messages and transaction IDs", deadline: "Today", impact: "HIGH" },
    ],
    riskFactors: demo.attackChain,
    mitigatingFactors: [],
  };
  const nodes: GraphData["nodes"] = [
    { id: "n_victim", type: "victim", label: "Victim (You)" },
    { id: "n_threat", type: "threat_actor", label: "Attacker" },
  ];
  const edges: GraphData["edges"] = [{ id: "e_target", source: "n_threat", target: "n_victim", label: "targeted" }];
  const nodeType: Record<string, string> = { upi_id: "wallet", wallet_address: "wallet", url: "url", email: "email", phone_number: "phone" };
  Object.entries(demo.indicators).forEach(([type, values]) =>
    values.forEach((value, i) => {
      const id = `n_${type}_${i}`;
      nodes.push({ id, type: nodeType[type] || "default", label: value });
      edges.push({ id: `e_${id}`, source: "n_threat", target: id, label: type === "url" ? "operates" : "uses" });
    }),
  );
  const timeline: TimelineEventData[] = demo.attackChain.map((step, i) => ({
    id: `demo-t${i}`,
    timestamp: "",
    eventType: ["initial_access", "execution", "exfiltration", "impact"][Math.min(i, 3)],
    description: step,
    relativeTime: `Step ${i + 1}`,
  }));
  return { confidence, graph: { nodes, edges }, timeline };
}

export default function CaseInvestigationPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const searchParams = useSearchParams();
  const { getToken, isSignedIn } = useAuth();
  const demo = searchParams.get("demo") === "true" ? demoCases.find(c => c.id === caseId) : undefined;
  const isDemo = Boolean(demo);

  const [messages, setMessages] = useState<{ role: string; content: string }[]>([{
    role: "agent",
    content: isDemo
      ? "Demo mode: this walkthrough uses sample data for the selected case. Sign in to investigate your own incident."
      : "Describe the incident and attach any screenshot (phishing SMS, payment page, chat). I'll extract indicators, check them against past reports and map the attack.",
  }]);
  const [input, setInput] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState<"graph" | "timeline">("graph");
  const [confidenceData, setConfidenceData] = useState<ConfidenceData | null>(null);
  const [knownThreats, setKnownThreats] = useState<KnownThreat[]>([]);
  const [graphData, setGraphData] = useState<GraphData>(EMPTY_GRAPH);
  const [timeline, setTimeline] = useState<TimelineEventData[]>([]);
  const [agentActivity, setAgentActivity] = useState<AgentActivity[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const demoStarted = useRef(false);

  const log = useCallback((a: AgentActivity) => setAgentActivity(prev => [a, ...prev].slice(0, 50)), []);
  const say = (content: string) => setMessages(prev => [...prev, { role: "agent", content }]);

  // ---- Demo: sample data only, plus a read-only lookup against real threat memory ----
  useEffect(() => {
    if (!demo || demoStarted.current) return;
    demoStarted.current = true;
    setMessages(prev => [...prev, { role: "user", content: demo.summary }]);
    const results = buildDemoResults(demo);
    setConfidenceData(results.confidence);
    setGraphData(results.graph);
    setTimeline(results.timeline);
    log(activity("evidence", "Loaded sample evidence for this demo case.", "success"));
    checkKnownEntities(demo.indicators)
      .then(setKnownThreats)
      .catch(() => log(activity("memory", "Threat memory lookup unavailable.", "error")));
    say("Sample analysis loaded. The graph, timeline and assessment on the right are illustrative data for this demo case.");
  }, [demo, log]);

  const handleSelectImage = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) return alert("Please choose an image file.");
    if (file.size > MAX_IMAGE_BYTES) return alert("Image is too large (max 5 MB).");
    setImage(file);
  };

  const clearImage = () => {
    setImage(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // ---- Live investigation: real authenticated calls ----
  const handleSend = async () => {
    const text = input.trim();
    if ((!text && !image) || isAnalyzing) return;
    if (!isSignedIn) return say("Please sign in to run a live investigation.");

    setMessages(prev => [...prev, { role: "user", content: text + (image ? `\n[Attached: ${image.name}]` : "") }]);
    setInput("");
    setIsAnalyzing(true);
    const attached = image;
    clearImage();

    try {
      const token = await getToken();
      log(activity("evidence", attached ? "Reading screenshot and extracting indicators..." : "Extracting indicators...", "loading"));
      const result = await runInvestigation({
        message: text,
        sessionId: caseId,
        ...(attached ? { imageBase64: await fileToBase64(attached), imageMimeType: attached.type } : {}),
      }, token);
      const found = Object.values(result.extracted_entities).flat().length;
      log(activity("evidence", `Found ${found} indicator(s).`, "success"));
      setKnownThreats(result.known_threats);
      if (result.known_threats.length) log(activity("memory", `${result.known_threats.length} indicator(s) seen in earlier reports.`, "success"));

      const description = [text, result.image_text].filter(Boolean).join("\n\n");
      log(activity("threat_intel", "Assessing threat, timeline and relationships...", "loading"));
      const [conf, tl, graph] = await Promise.allSettled([
        getConfidence(description, result.extracted_entities, token),
        getTimeline(description, token),
        getGraph(description, result.extracted_entities, token),
      ]);
      if (conf.status === "fulfilled") setConfidenceData(conf.value);
      if (tl.status === "fulfilled") setTimeline(tl.value.events);
      if (graph.status === "fulfilled" && graph.value.nodes.length) setGraphData(graph.value);

      const failed = [conf, tl, graph].filter(r => r.status === "rejected").length;
      log(activity("strategy", failed ? `${3 - failed}/3 analyses completed (the AI service may be busy).` : "Analysis complete.", failed ? "error" : "success"));
      say(failed
        ? "Partial results are on the right. Some analyses failed - please retry in a minute."
        : "Analysis complete. Review the assessment, priority actions, graph and timeline on the right.");
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Could not reach the server.";
      log(activity("understanding", msg, "error"));
      say(`Investigation failed: ${msg}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleExportPDF = () => {
    const doc = new jsPDF();
    const pageHeight = doc.internal.pageSize.getHeight();
    const width = doc.internal.pageSize.getWidth() - 40;
    let y = 20;
    const write = (text: string, size = 10, gap = 2) => {
      doc.setFontSize(size);
      // jsPDF's built-in fonts can't render ₹ and similar glyphs.
      const lines = doc.splitTextToSize(text.replace(/₹/g, "Rs. ").replace(/[^\x00-\xFF]/g, "?"), width);
      lines.forEach((line: string) => {
        if (y > pageHeight - 15) { doc.addPage(); y = 20; }
        doc.text(line, 20, y);
        y += size * 0.5;
      });
      y += gap;
    };

    write("CyberGuard Investigation Summary", 18, 4);
    write(`Case: ${caseId}${isDemo ? " (DEMO - sample data)" : ""}`);
    write(`Generated: ${new Date().toLocaleString()}`, 10, 6);
    if (confidenceData) {
      write("Threat Assessment", 14);
      write(`Scam likelihood: ${confidenceData.scamLikelihood}%  |  Urgency: ${confidenceData.urgencyLevel}  |  Sophistication: ${confidenceData.attackSophistication}`);
      write(`Recovery probability (estimate): ${confidenceData.recoveryProbability}%`, 10, 4);
      write("Priority Actions", 14);
      (confidenceData.priorityActions || []).forEach((a, i) => write(`${i + 1}. ${a.action} (Deadline: ${a.deadline}, Impact: ${a.impact})`));
      y += 4;
    }
    if (knownThreats.length) {
      write("Indicators Seen in Earlier Reports", 14);
      knownThreats.forEach(t => write(`- ${t.entity_type}: ${t.entity_value} (${t.case_count} case(s), risk ${Math.round(t.risk_score * 100)}%)`));
      y += 4;
    }
    if (timeline.length) {
      write("Incident Timeline", 14);
      timeline.forEach(ev => write(`[${ev.relativeTime || ev.timestamp || "-"}] ${ev.eventType.toUpperCase()} - ${ev.description}`));
    }
    doc.save(`CyberGuard_Investigation_${caseId}.pdf`);
  };

  const priorityActions = confidenceData?.priorityActions || [];

  return (
    <div className="flex h-[calc(100vh-64px)] w-full max-w-[1800px] mx-auto p-4 gap-4 bg-[#020617] overflow-hidden">
      <div className="hidden lg:flex w-72 flex-col">
        <ThreatIntelFeed />
      </div>

      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex-[1.2] flex flex-col glass-card rounded-2xl overflow-hidden border border-white/5 bg-black/40 backdrop-blur-xl h-full"
      >
        <div className="p-4 border-b border-white/5 bg-slate-900/30 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-500" />
            <h2 className="font-bold text-sm tracking-widest uppercase">Investigation Console</h2>
          </div>
          {isDemo && (
            <span className="bg-amber-500/20 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest">
              Demo · sample data
            </span>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed whitespace-pre-wrap ${msg.role === "user" ? "bg-blue-600 text-white rounded-tr-sm" : "bg-slate-900/80 border border-white/10 text-gray-200 rounded-tl-sm"}`}>
                {msg.content}
              </div>
            </div>
          ))}
          {isAnalyzing && (
            <div className="flex justify-start">
              <div className="bg-slate-900/80 border border-white/10 text-blue-400 rounded-2xl rounded-tl-sm p-4 text-xs font-bold uppercase tracking-widest">
                Analyzing...
              </div>
            </div>
          )}
          {isDemo && (
            <div className="text-center pt-2">
              <Link href="/dashboard" className="text-xs text-blue-400 hover:underline">Sign in to investigate your own incident →</Link>
            </div>
          )}
        </div>

        <AgentActivityStream activities={agentActivity} />

        {!isDemo && (
          <div className="p-4 bg-black/60 border-t border-white/5 backdrop-blur-md">
            {image && (
              <div className="flex items-center gap-2 mb-2 text-xs text-gray-300">
                <ImageIcon size={14} /> {image.name}
                <button onClick={clearImage} aria-label="Remove attachment" className="text-gray-500 hover:text-white"><X size={14} /></button>
              </div>
            )}
            <div className="flex items-center gap-2 bg-slate-950/50 rounded-xl border border-white/5 p-2 pr-4 focus-within:border-blue-500/50 transition-all">
              <button className="p-2 text-gray-500 hover:text-blue-400 transition-colors" onClick={() => fileInputRef.current?.click()} aria-label="Attach screenshot">
                <ImageIcon size={20} />
              </button>
              <input type="file" accept="image/*" className="hidden" ref={fileInputRef} onChange={handleSelectImage} />
              <input
                type="text"
                className="flex-1 bg-transparent border-none outline-none text-white text-sm px-2"
                placeholder="Describe the incident or attach a screenshot..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
              />
              <button
                className="p-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg transition-all"
                onClick={handleSend}
                disabled={isAnalyzing}
                aria-label="Send"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        )}
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex-[1.8] flex flex-col gap-6 overflow-y-auto pr-2 custom-scrollbar h-full"
      >
        <KnownThreatsPanel threats={knownThreats} />

        {confidenceData ? (
          <ConfidencePanel data={confidenceData} />
        ) : (
          <div className="flex items-center justify-center p-5 rounded-2xl bg-black/40 border border-white/5 min-h-[160px] text-xs text-gray-500">
            The threat assessment appears here after an investigation.
          </div>
        )}

        <div className="flex-1 flex flex-col min-h-[500px]">
          <div className="flex gap-1 p-1 bg-black/40 rounded-lg border border-white/5 self-start mb-4">
            {(["graph", "timeline"] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-widest transition-all ${activeTab === tab ? "bg-blue-600 text-white" : "text-gray-500 hover:text-gray-300"}`}
              >
                {tab === "graph" ? <GitBranch size={12} className="inline mr-2" /> : <Clock size={12} className="inline mr-2" />}
                {tab === "graph" ? "Investigation Graph" : "Incident Timeline"}
              </button>
            ))}
          </div>
          <div className="flex-1">
            {activeTab === "graph" ? (
              <InvestigationGraph data={graphData} />
            ) : (
              <div className="glass-card rounded-2xl p-6 border border-white/5 bg-black/20 min-h-[400px]">
                {timeline.length ? <IncidentTimeline events={timeline} /> : <p className="text-xs text-gray-500">No timeline yet.</p>}
              </div>
            )}
          </div>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-white/5 bg-blue-500/5 mb-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-4">
            <div className="flex items-center gap-2">
              <ShieldCheck size={18} className="text-blue-500" />
              <h3 className="text-xs font-bold uppercase tracking-widest text-blue-400">Priority Actions</h3>
            </div>
            <Button onClick={handleExportPDF} disabled={!confidenceData && !timeline.length} className="h-8 text-[10px] font-bold uppercase tracking-widest bg-blue-600 hover:bg-blue-500">
              <Download size={14} className="mr-2" /> Export Summary PDF
            </Button>
          </div>
          {priorityActions.length ? (
            <ol className="space-y-2">
              {priorityActions.map((a, i) => (
                <li key={i} className="p-3 rounded-lg border border-white/5 bg-white/[0.02] text-xs text-gray-300 flex justify-between gap-3">
                  <span>{i + 1}. {a.action}</span>
                  <span className="text-gray-500 shrink-0">{a.deadline}</span>
                </li>
              ))}
            </ol>
          ) : (
            <p className="text-xs text-gray-500">
              Run an investigation to get prioritised actions. For financial fraud in India, call <a href="tel:1930" className="text-blue-400">1930</a> immediately and report at{" "}
              <a href="https://cybercrime.gov.in" target="_blank" rel="noopener noreferrer" className="text-blue-400">cybercrime.gov.in</a>.
            </p>
          )}
        </div>

        <ThreatMap />
      </motion.div>
    </div>
  );
}
