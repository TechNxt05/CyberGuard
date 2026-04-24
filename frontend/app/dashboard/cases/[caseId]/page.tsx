"use client";

import React, { useState, useRef } from "react";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import { Send, Image as ImageIcon, FileText, UploadCloud, Download, ShieldAlert } from "lucide-react";
import { ProbabilityMeter } from "@/components/ProbabilityMeter";
import { EntityCards } from "@/components/EntityCards";
import { InteractiveTimeline } from "@/components/InteractiveTimeline";
import { Button } from "@/components/ui/button";

export default function CaseInvestigationPage() {
  const { caseId } = useParams();
  const [messages, setMessages] = useState<{role: string, content: string}[]>([{ role: "agent", content: "Hello. I am CyberGuard One X. Please upload any evidence (screenshots, audio) or describe the incident." }]);
  const [input, setInput] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // Dashboard State
  const [riskScore, setRiskScore] = useState(10);
  const [entities, setEntities] = useState({});
  const [timeline, setTimeline] = useState([{ time: new Date().toLocaleTimeString(), description: "Case opened." }]);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    if (!input.trim() && !fileInputRef.current?.files?.length) return;
    
    // Simulate adding user message
    setMessages(prev => [...prev, { role: "user", content: input || "Uploaded evidence." }]);
    setInput("");
    setIsAnalyzing(true);
    
    // Simulate API call to FastAPI Vision/Analysis Engine
    setTimeout(() => {
      setRiskScore(85); // High risk for demo
      setEntities({
        upi_ids: ["scammer@ybl", "fakebank@sbi"],
        urls: ["http://login-sbi-update.xyz"],
        phones: ["+91 9876543210"]
      });
      setTimeline(prev => [...prev, { time: new Date().toLocaleTimeString(), description: "Extracted phishing URLs and UPI IDs from uploaded evidence." }]);
      
      setMessages(prev => [...prev, { role: "agent", content: "I've analyzed the evidence. This appears to be a high-risk phishing attempt. I've extracted the fraudulent entities to your Evidence Locker." }]);
      setIsAnalyzing(false);
    }, 2500);
  };

  return (
    <div className="flex h-[calc(100vh-64px)] w-full max-w-[1600px] mx-auto p-4 gap-4">
      {/* LEFT PANEL: Chat & Investigation Input */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-1/2 flex flex-col glass-card rounded-2xl overflow-hidden border border-white/10"
      >
        <div className="p-4 border-b border-white/10 bg-slate-900/50 flex justify-between items-center">
          <h2 className="font-bold text-lg flex items-center gap-2"><ShieldAlert className="text-blue-500"/> Investigation Agent</h2>
          <span className="text-xs text-gray-400 font-mono">CASE ID: {caseId}</span>
        </div>
        
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-sm' : 'bg-slate-800/80 border border-white/5 text-gray-200 rounded-tl-sm'}`}>
                {msg.content}
              </div>
            </div>
          ))}
          {isAnalyzing && (
            <div className="flex justify-start">
              <div className="bg-slate-800/80 border border-white/5 text-gray-400 rounded-2xl rounded-tl-sm p-4 flex items-center gap-2">
                <span className="animate-pulse">Analyzing evidence via Vision Engine...</span>
              </div>
            </div>
          )}
        </div>
        
        {/* Input Area */}
        <div className="p-4 bg-slate-900/80 border-t border-white/10">
          <div className="flex items-center gap-2 bg-slate-950 rounded-xl border border-white/10 p-2 pr-4 focus-within:border-blue-500/50 transition-colors">
            <button className="p-2 text-gray-400 hover:text-blue-400 transition-colors" onClick={() => fileInputRef.current?.click()}>
              <UploadCloud size={20} />
            </button>
            <input type="file" className="hidden" ref={fileInputRef} />
            <input 
              type="text" 
              className="flex-1 bg-transparent border-none outline-none text-white text-sm"
              placeholder="Describe the incident or upload screenshots/audio..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button 
              className="p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors flex items-center justify-center"
              onClick={handleSend}
              disabled={isAnalyzing}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </motion.div>

      {/* RIGHT PANEL: Dashboard & Evidence Locker */}
      <motion.div 
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-1/2 flex flex-col gap-4 overflow-y-auto pr-2 custom-scrollbar"
      >
        {/* Threat Level */}
        <div className="glass-card rounded-2xl p-6 border border-white/10">
          <div className="flex justify-between items-start mb-4">
            <h2 className="font-bold text-lg">Threat Analysis</h2>
            <Button variant="ghost" className="border border-blue-500/50 hover:bg-blue-500/20 text-blue-400 text-xs h-8">
              <Download size={14} className="mr-2" /> Export PDF
            </Button>
          </div>
          <ProbabilityMeter score={riskScore} />
        </div>

        {/* Evidence Locker */}
        <div className="glass-card rounded-2xl p-6 border border-white/10">
          <h2 className="font-bold text-lg mb-4 flex items-center gap-2"><FileText className="text-emerald-500" size={20}/> Evidence Locker (Extracted)</h2>
          <EntityCards entities={entities} />
        </div>

        {/* Investigation Timeline */}
        <div className="glass-card rounded-2xl p-6 border border-white/10 flex-1">
          <h2 className="font-bold text-lg mb-4">Investigation Timeline</h2>
          <InteractiveTimeline events={timeline} />
        </div>
      </motion.div>
    </div>
  );
}
