"use client";

import Link from "next/link";
import { ArrowLeft, Server, Database, Brain, Globe, Shield, Activity, Users, FileText, ArrowRight, Zap, Lock, Search } from "lucide-react";
import { Card } from "@/components/ui/card";

export default function AboutPage() {
    return (
        <div className="min-h-screen bg-black text-white p-6 md:p-12 font-sans selection:bg-blue-500/30">

            {/* Header */}
            <header className="max-w-7xl mx-auto mb-16 flex items-center gap-6">
                <Link href="/dashboard" className="p-2 rounded-full hover:bg-white/10 transition-colors">
                    <ArrowLeft className="text-gray-400 hover:text-white" />
                </Link>
                <div>
                    <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                        System Architecture
                    </h1>
                    <p className="text-gray-400 mt-2 text-lg">
                        Under the hood of CyberGuardAI One.
                    </p>
                </div>
            </header>

            <div className="max-w-7xl mx-auto space-y-24">

                {/* SECTION 1: High-Level Architecture */}
                <section>
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400"><Server size={24} /></div>
                        <h2 className="text-2xl font-bold">Platform Architecture</h2>
                    </div>

                    <div className="relative p-8 md:p-12 rounded-3xl border border-white/10 bg-white/5 overflow-hidden">
                        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />

                        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8 md:gap-4">

                            {/* Frontend Node */}
                            <div className="flex flex-col items-center gap-4 group">
                                <div className="w-40 h-40 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-white/10 flex flex-col items-center justify-center shadow-2xl group-hover:border-blue-500/50 transition-all">
                                    <Globe className="text-blue-400 mb-2" size={32} />
                                    <span className="font-bold text-lg">Next.js Frontend</span>
                                    <span className="text-xs text-gray-500 px-4 text-center mt-1">Client Interface & Auth</span>
                                </div>
                            </div>

                            {/* Arrow */}
                            <Arrow />

                            {/* Backend Node */}
                            <div className="flex flex-col items-center gap-4 group">
                                <div className="w-40 h-40 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-white/10 flex flex-col items-center justify-center shadow-2xl group-hover:border-emerald-500/50 transition-all">
                                    <Server className="text-emerald-400 mb-2" size={32} />
                                    <span className="font-bold text-lg">FastAPI Backend</span>
                                    <span className="text-xs text-gray-500 px-4 text-center mt-1">Orchestration Layer</span>
                                </div>
                            </div>

                            {/* Arrow */}
                            <Arrow />

                            {/* MCP Node */}
                            <div className="flex flex-col items-center gap-4 group">
                                <div className="w-48 h-48 rounded-2xl bg-gradient-to-br from-purple-900/50 to-slate-900 border border-purple-500/30 flex flex-col items-center justify-center shadow-2xl relative overflow-hidden">
                                    <div className="absolute inset-0 bg-purple-500/10 animate-pulse" />
                                    <Brain className="text-purple-400 mb-2 relative z-10" size={40} />
                                    <span className="font-bold text-lg relative z-10">MCP Router</span>
                                    <span className="text-xs text-purple-300 px-4 text-center mt-1 relative z-10">LangGraph Agents</span>
                                </div>
                            </div>

                            {/* Arrow */}
                            <Arrow />

                            {/* External Services */}
                            <div className="flex flex-col gap-4">
                                <div className="w-40 h-16 rounded-xl bg-slate-900 border border-white/10 flex items-center px-4 gap-3 shadow-lg">
                                    <Database className="text-yellow-500" size={20} />
                                    <div className="flex flex-col">
                                        <span className="text-sm font-bold">MongoDB</span>
                                        <span className="text-[10px] text-gray-500">Atlas Vector Store</span>
                                    </div>
                                </div>
                                <div className="w-40 h-16 rounded-xl bg-slate-900 border border-white/10 flex items-center px-4 gap-3 shadow-lg">
                                    <Zap className="text-orange-500" size={20} />
                                    <div className="flex flex-col">
                                        <span className="text-sm font-bold">LLM Provider</span>
                                        <span className="text-[10px] text-gray-500">Gemini / Groq</span>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </div>
                </section>

                {/* SECTION 2: ScamShield Workflow */}
                <section>
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 bg-red-500/10 rounded-lg text-red-400"><Shield size={24} /></div>
                        <div>
                            <h2 className="text-2xl font-bold">ScamShield Analysis Pipeline</h2>
                            <p className="text-gray-500 text-sm">Deep forensic analysis of text and images.</p>
                        </div>
                    </div>

                    <div className="relative p-10 rounded-3xl border border-white/10 bg-gradient-to-b from-red-500/5 to-transparent">
                        <div className="flex flex-wrap md:flex-nowrap items-center justify-center gap-4 md:gap-6">

                            <StepBox icon={FileText} title="User Input" desc="Message / Image" color="gray" />
                            <ArrowRight className="text-gray-600 hidden md:block" />
                            <StepBox icon={Users} title="Profiler Agent" desc="Analyzes User Context" color="blue" />
                            <ArrowRight className="text-gray-600 hidden md:block" />
                            <StepBox icon={Search} title="Scam Detector" desc="Pattern Matching" color="red" />
                            <ArrowRight className="text-gray-600 hidden md:block" />
                            <StepBox icon={Brain} title="Explainer" desc="Generates Logic & Tips" color="purple" />
                            <ArrowRight className="text-gray-600 hidden md:block" />
                            <StepBox icon={Shield} title="Final Report" desc="Severity & Action Plan" color="emerald" />

                        </div>
                    </div>
                </section>

                {/* SECTION 3: CyberResolve Workflow */}
                <section>
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400"><Activity size={24} /></div>
                        <div>
                            <h2 className="text-2xl font-bold">CyberResolve Resolution Pipeline</h2>
                            <p className="text-gray-500 text-sm">Automated incident response and guidance system.</p>
                        </div>
                    </div>

                    <div className="relative p-10 rounded-3xl border border-white/10 bg-gradient-to-b from-blue-500/5 to-transparent">
                        <div className="flex flex-col items-center gap-8">

                            {/* Row 1 */}
                            <div className="flex flex-col md:flex-row items-center gap-8">
                                <StepBox icon={Activity} title="Incident Report" desc="User Chat / Evidence" color="gray" />
                                <ArrowRight className="text-gray-600 hidden md:block" />
                                <ArrowDown className="md:hidden" />
                                <StepBox icon={Brain} title="Understanding Node" desc="Extracts Dimensions" color="blue" />
                                <ArrowRight className="text-gray-600 hidden md:block" />
                                <ArrowDown className="md:hidden" />
                                <StepBox icon={Search} title="Research Agent" desc="Live Web/Reddit/Twitter" color="red" />
                            </div>

                            <ArrowDown />

                            {/* Branching Logic Visual */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-4xl px-4 relative">
                                {/* Connecting Lines */}
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-4/5 h-[2px] bg-blue-500/20 hidden md:block -mt-4"></div>
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[2px] h-4 bg-blue-500/20 hidden md:block -mt-4"></div>
                                <div className="absolute top-0 left-[18%] w-[2px] h-4 bg-blue-500/20 hidden md:block -mt-4"></div>
                                <div className="absolute top-0 right-[18%] w-[2px] h-4 bg-blue-500/20 hidden md:block -mt-4"></div>

                                <StepBox icon={Activity} title="Strategy Node" desc="Generates Lifecycle Plan" color="emerald" />
                                <StepBox icon={Users} title="Authority Mapper" desc="Identifies Jurisdictions" color="amber" />
                                <StepBox icon={Globe} title="Guide Node" desc="Step-by-Step Navigation" color="cyan" />
                            </div>

                            <ArrowDown />

                            <div className="flex items-center gap-8">
                                <StepBox icon={Database} title="Memory Persistence" desc="Saves State to Atlas" color="purple" />
                            </div>

                        </div>
                    </div>
                </section>

                {/* SECTION 4: Agent Roster */}
                <section>
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400"><Users size={24} /></div>
                        <h2 className="text-2xl font-bold">Agent Roster</h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <AgentCard
                            name="Incident Understanding Agent"
                            role="Forensic Analyst"
                            desc="Extracts structured data (assets, attack vectors) from unstructured user stories."
                            icon={Search}
                        />
                        <AgentCard
                            name="Authenticity Researcher"
                            role="Investigator"
                            desc="Scours the open web, Reddit, and social media for real-time recovery steps and latest scam trends."
                            icon={Globe}
                        />
                        <AgentCard
                            name="Resolution Strategy Agent"
                            role="Tactical Planner"
                            desc="Generates a multi-step lifecycle plan (Containment -> Recovery) based on attack type."
                            icon={Activity}
                        />
                        <AgentCard
                            name="Authority Mapper Agent"
                            role="Legal Liaison"
                            desc="Identifies relevant authorities (Banks, Social Platforms, Cyber Cells) for reporting."
                            icon={Lock}
                        />
                        <AgentCard
                            name="Website Guidance Agent"
                            role="Navigator"
                            desc="Provides click-by-click navigation instructions for official portals."
                            icon={Globe}
                        />
                        <AgentCard
                            name="Scam Detection Agent"
                            role="Threat Hunter"
                            desc="Compares input against a knowledge base of known scam patterns and logical fallacies."
                            icon={Shield}
                        />
                        <AgentCard
                            name="Memory Manager"
                            role="Archivist"
                            desc="Handles state persistence, ensuring context survives sessions and reloads."
                            icon={Database}
                        />
                    </div>
                </section>

            </div>
        </div>
    );
}

// Visual Components

function Arrow() {
    return <div className="hidden md:block w-16 h-[2px] bg-white/10 relative">
        <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 border-t-2 border-r-2 border-white/20 rotate-45"></div>
    </div>
}

function ArrowDown() {
    return <div className="h-8 w-[2px] bg-white/10 relative">
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-2 h-2 border-b-2 border-r-2 border-white/20 rotate-45"></div>
    </div>
}

function StepBox({ icon: Icon, title, desc, color }: { icon: any, title: string, desc: string, color: string }) {
    const colorClasses: Record<string, string> = {
        gray: "bg-gray-500/10 border-gray-500/20 text-gray-400",
        blue: "bg-blue-500/10 border-blue-500/20 text-blue-400",
        red: "bg-red-500/10 border-red-500/20 text-red-400",
        purple: "bg-purple-500/10 border-purple-500/20 text-purple-400",
        emerald: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400",
        amber: "bg-amber-500/10 border-amber-500/20 text-amber-400",
        cyan: "bg-cyan-500/10 border-cyan-500/20 text-cyan-400",
    };

    return (
        <div className={`p-4 rounded-xl border flex flex-col items-center text-center w-full md:w-48 ${colorClasses[color] || colorClasses['gray']}`}>
            <Icon size={24} className="mb-2 opacity-80" />
            <h4 className="font-bold text-sm text-white">{title}</h4>
            <p className="text-[10px] opacity-70 mt-1">{desc}</p>
        </div>
    );
}

function AgentCard({ name, role, desc, icon: Icon }: any) {
    return (
        <div className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all hover:bg-white/10 group">
            <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-black/40 rounded-xl group-hover:scale-110 transition-transform">
                    <Icon size={20} className="text-gray-300" />
                </div>
                <div>
                    <h3 className="font-bold text-white leading-none">{name}</h3>
                    <span className="text-xs text-blue-400 font-mono mt-1 block">{role}</span>
                </div>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">
                {desc}
            </p>
        </div>
    )
}
