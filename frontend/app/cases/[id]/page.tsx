"use client"
import { useAuth } from "@clerk/nextjs";
import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Send, ArrowLeft, CheckCircle, Circle, Clock, AlertTriangle, Upload, X, Loader2, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface Message {
    sender: "user" | "agent";
    content: string;
    timestamp: string;
}

interface Task {
    label: string;
    status: "pending" | "completed";
    action_link?: string;
    action_type?: "link" | "call" | "info";
}

interface CaseDetails {
    title: string;
    status: string;
    incident_summary: string;
    attack_type?: string;
    incident_logic?: string;
    prevention_tips?: string[];
}

export default function CaseChatPage() {
    const { id } = useParams();
    const { getToken } = useAuth();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [caseDetails, setCaseDetails] = useState<CaseDetails | null>(null);
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);

    // New Image State
    const [imageBase64, setImageBase64] = useState<string | null>(null);
    const [fileName, setFileName] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const scrollRef = useRef<HTMLDivElement>(null);

    // Fetch Case Data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = await getToken();
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/cases/${id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setCaseDetails(data.case);
                    setMessages(data.history || []);
                    setTasks(data.tasks || []);
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id, getToken]);

    // Auto-scroll
    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        if (file.type.startsWith("image/")) {
            setFileName(file.name);
            const reader = new FileReader();
            reader.onload = (e) => {
                // remove data:image/... base64 prefix
                const base64 = (e.target?.result as string).split(",")[1];
                setImageBase64(base64);
            };
            reader.readAsDataURL(file);
        } else {
            alert("Please select an image file.");
        }
    };

    const sendMessage = async () => {
        if ((!input.trim() && !imageBase64) || sending) return;
        setSending(true);

        // Optimistic Update
        let displayContent = input;
        if (fileName) {
            displayContent += `\n[Uploaded Image: ${fileName}]`;
        }

        const newMsg: Message = { sender: "user", content: displayContent, timestamp: new Date().toISOString() };
        setMessages(prev => [...prev, newMsg]);

        const payload = {
            message: input,
            image_base64: imageBase64
        };

        // Clear input immediately
        setInput("");
        setImageBase64(null);
        setFileName(null);
        if (fileInputRef.current) fileInputRef.current.value = "";

        try {
            const token = await getToken();
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/cases/${id}/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            console.log("DEBUG: Chat response received", data);

            setMessages(prev => [...prev, {
                sender: "agent",
                content: data.reply,
                timestamp: new Date().toISOString()
            }]);

            if (data.tasks) {
                console.log("DEBUG: Updating tasks", data.tasks);
                setTasks(data.tasks);
            }

            if (data.case_details) {
                console.log("DEBUG: Updating case details", data.case_details);
                setCaseDetails(data.case_details);
            }
        } catch (err) {
            console.error("Failed to send", err);
        } finally {
            setSending(false);
        }
    };

    if (loading) return <div className="min-h-screen bg-background flex items-center justify-center text-white">Loading Case...</div>;

    return (
        <div className="flex h-screen bg-background overflow-hidden relative">
            {/* LEFT: Chat Area */}
            <div className="flex-1 flex flex-col min-w-0">
                <header className="h-16 border-b border-white/10 flex items-center px-6 gap-4 bg-white/5">
                    <Link href="/dashboard" className="text-gray-400 hover:text-white">
                        <ArrowLeft size={20} />
                    </Link>
                    <div>
                        <h1 className="text-white font-bold truncate">{caseDetails?.title}</h1>
                        <p className="text-xs text-blue-400 flex items-center gap-1">
                            <Clock size={10} /> Status: {caseDetails?.status}
                        </p>
                    </div>
                </header>

                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.length === 0 && (
                        <div className="text-center text-gray-500 mt-20">
                            <p>Start the conversation to resolve this incident.</p>
                        </div>
                    )}

                    {messages.map((m, i) => (
                        <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] p-4 rounded-xl ${m.sender === 'user'
                                ? 'bg-blue-600 text-white rounded-tr-none'
                                : 'bg-white/10 text-gray-200 rounded-tl-none border border-white/5'
                                }`}>
                                <p className="whitespace-pre-wrap">{m.content}</p>
                                <span className="text-[10px] opacity-50 block mt-2 text-right">
                                    {new Date(m.timestamp).toLocaleTimeString()}
                                </span>
                            </div>
                        </div>
                    ))}
                    <div ref={scrollRef} />
                </div>

                <div className="p-4 border-t border-white/10 bg-white/5">
                    {/* Image Preview */}
                    {fileName && (
                        <div className="flex items-center gap-2 mb-2 px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-lg max-w-fit">
                            <span className="text-xs text-blue-300">File: {fileName}</span>
                            <button onClick={() => { setImageBase64(null); setFileName(null); if (fileInputRef.current) fileInputRef.current.value = ""; }} className="text-blue-400 hover:text-white">
                                <X size={14} />
                            </button>
                        </div>
                    )}

                    <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex gap-2 max-w-4xl mx-auto items-center">
                        <input
                            type="file"
                            ref={fileInputRef}
                            className="hidden"
                            accept="image/*"
                            onChange={handleFileSelect}
                        />
                        <Button
                            type="button"
                            variant="ghost"
                            className="text-gray-400 hover:text-white w-9 h-9 p-0"
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <Upload size={20} />
                        </Button>

                        <input
                            className="flex-1 bg-black/20 border border-white/10 rounded-full px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                            placeholder="Type a message or upload screenshot..."
                            value={input}
                            onChange={e => setInput(e.target.value)}
                        />
                        <Button type="submit" disabled={sending} className="rounded-full w-12 h-12 p-0 bg-blue-600 hover:bg-blue-500">
                            {sending ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
                        </Button>
                    </form>
                </div>
            </div>

            {/* RIGHT: Sidebar (Tasks & Context) */}
            <div className="w-80 border-l border-white/10 bg-black/20 hidden md:flex flex-col h-full overflow-hidden">
                <div className="p-6 border-b border-white/10 h-1/2 overflow-y-auto">
                    <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Case Tasks</h2>
                    <div className="space-y-3">
                        {tasks.length === 0 ? (
                            <p className="text-sm text-gray-600 italic">No tasks generated yet.</p>
                        ) : (
                            tasks.map((t, i) => (
                                <div
                                    key={i}
                                    onClick={async () => {
                                        // Optimistic Update
                                        const newStatus = t.status === 'completed' ? 'pending' : 'completed';
                                        setTasks(prev => prev.map(pt => pt.label === t.label ? { ...pt, status: newStatus } : pt));

                                        // API Call
                                        try {
                                            const token = await getToken();
                                            await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/cases/${id}/tasks/${encodeURIComponent(t.label)}?status=${newStatus}`, {
                                                method: "PUT",
                                                headers: { Authorization: `Bearer ${token}` }
                                            });
                                        } catch (e) {
                                            console.error("Task update failed", e);
                                        }
                                    }}
                                    className={`flex items-start gap-3 p-3 rounded-lg border transition-all cursor-pointer group hover:bg-white/5 ${t.status === 'completed'
                                        ? 'bg-emerald-500/5 border-emerald-500/20'
                                        : 'border-white/5 bg-black/20'
                                        }`}
                                >
                                    <div className={`mt-0.5 shrink-0 flex items-center justify-center w-5 h-5 rounded-full border text-[10px] ${t.status === 'completed'
                                        ? 'bg-emerald-500 text-black border-emerald-500'
                                        : 'border-white/20 text-gray-400 group-hover:border-white/40 group-hover:text-white'
                                        }`}>
                                        {t.status === 'completed' ? <CheckCircle size={12} /> : <span>{i + 1}</span>}
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        <h4 className={`text-sm font-medium leading-tight truncate ${t.status === 'completed' ? 'text-gray-500 line-through' : 'text-gray-300'}`}>
                                            {t.label}
                                        </h4>
                                        <p className="text-[10px] text-gray-500 truncate mt-1">Check to mark done</p>

                                        {t.action_link && t.status !== 'completed' && (
                                            <a
                                                href={t.action_link}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                onClick={(e) => e.stopPropagation()}
                                                className={`mt-2 text-xs py-1.5 px-3 rounded inline-flex items-center gap-2 transition-colors font-medium border ${t.action_type === 'call'
                                                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20'
                                                    : 'bg-blue-600/10 text-blue-400 border-blue-600/20 hover:bg-blue-600/20'
                                                    }`}
                                            >
                                                {t.action_type === 'call' ? '📞 Call' : '🔗 Open'}
                                            </a>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                <div className="p-6 bg-black/40 border-t border-white/10 h-1/2 overflow-y-auto">
                    <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Case Analysis</h2>
                    <div className="space-y-4">
                        <Card className="p-4 bg-yellow-500/5 border-yellow-500/20">
                            <div className="flex gap-2 mb-2 text-yellow-500">
                                <AlertTriangle size={16} />
                                <span className="text-xs font-bold">What Happened</span>
                            </div>
                            <p className="text-xs text-gray-400 leading-relaxed">
                                {caseDetails?.incident_summary || "Pending analysis..."}
                            </p>
                        </Card>

                        {caseDetails?.attack_type && (
                            <div>
                                <h3 className="text-xs font-bold text-gray-500 mb-2 uppercase">Category</h3>
                                <span className="text-xs font-mono bg-blue-500/10 text-blue-400 px-2 py-1 rounded border border-blue-500/20">
                                    {caseDetails.attack_type.replace(/_/g, " ").toUpperCase()}
                                </span>
                            </div>
                        )}

                        {caseDetails?.incident_logic && (
                            <Card className="p-4 bg-blue-500/5 border-blue-500/20">
                                <h3 className="text-xs font-bold text-blue-400 mb-2 uppercase">Mechanism</h3>
                                <p className="text-xs text-gray-400 leading-relaxed">
                                    {caseDetails.incident_logic}
                                </p>
                            </Card>
                        )}

                        {caseDetails?.prevention_tips && caseDetails.prevention_tips.length > 0 && (
                            <div className="p-4 rounded-lg border border-green-500/20 bg-green-500/5">
                                <h3 className="text-xs font-bold text-green-400 mb-2 uppercase flex items-center gap-2">
                                    <ShieldCheck size={14} /> Prevention
                                </h3>
                                <ul className="list-disc list-inside space-y-1">
                                    {caseDetails.prevention_tips.map((tip, i) => (
                                        <li key={i} className="text-[10px] text-gray-400 leading-snug">
                                            {tip}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
