"use client"
import { useAuth, UserButton } from "@clerk/nextjs";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Plus, MessageSquare, Clock, ShieldAlert, Info } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MemoryStats, MemoryStatsData } from "@/components/MemoryStats";
import { apiFetch } from "@/lib/api";

interface Case {
    _id: string;
    title: string;
    incident_summary: string;
    status: string;
    updated_at: string;
}

export default function Dashboard() {
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const [cases, setCases] = useState<Case[]>([]);
    const [loading, setLoading] = useState(true);
    const [casesError, setCasesError] = useState(false);

    // Persistent memory stats state
    const [stats, setStats] = useState<MemoryStatsData | null>(null);
    const [statsLoading, setStatsLoading] = useState(true);

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newCaseTitle, setNewCaseTitle] = useState("");
    const [creating, setCreating] = useState(false);
    const router = useRouter();

    useEffect(() => {
        const fetchCasesAndStats = async () => {
            if (!isSignedIn) return;
            const token = await getToken();
            await Promise.all([
                apiFetch<Case[]>("/cases", { token })
                    .then(setCases)
                    .catch(() => setCasesError(true))
                    .finally(() => setLoading(false)),
                apiFetch<MemoryStatsData>("/api/memory/stats")
                    .then(setStats)
                    .catch(() => setStats(null))
                    .finally(() => setStatsLoading(false)),
            ]);
        };

        if (isLoaded) fetchCasesAndStats();
    }, [isLoaded, isSignedIn, getToken]);

    const handleCreateCase = async () => {
        if (!newCaseTitle) return;
        setCreating(true);
        try {
            const data = await apiFetch<{ case_id: string }>("/cases", {
                method: "POST",
                body: { title: newCaseTitle, summary: "Pending analysis..." },
                token: await getToken(),
            });
            router.push(`/cases/${data.case_id}`);
        } catch {
            alert("Could not create the case. Please try again.");
        } finally {
            setCreating(false);
            setIsModalOpen(false);
        }
    };

    if (!isLoaded || !isSignedIn) {
        return <div className="min-h-screen bg-background flex items-center justify-center text-white">Loading...</div>;
    }

    return (
        <div className="min-h-screen bg-background p-6 relative">
            {/* Create Case Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                    <Card className="w-full max-w-md p-6 bg-slate-900 border-slate-700">
                        <h2 className="text-xl font-bold text-white mb-4">Report New Incident</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="text-sm text-gray-400 mb-1 block">Incident Title</label>
                                <input
                                    className="w-full bg-black/20 border border-white/10 rounded p-2 text-white"
                                    placeholder="e.g. Unauthorized UPI Transaction"
                                    value={newCaseTitle}
                                    onChange={e => setNewCaseTitle(e.target.value)}
                                />
                            </div>
                            <div className="flex justify-end gap-3 mt-4">
                                <Button variant="ghost" onClick={() => setIsModalOpen(false)} className="text-gray-400">Cancel</Button>
                                <Button onClick={handleCreateCase} disabled={creating} className="bg-blue-600 hover:bg-blue-700">
                                    {creating ? "Creating..." : "Start Resolution"}
                                </Button>
                            </div>
                        </div>
                    </Card>
                </div>
            )}

            <header className="flex justify-between items-center mb-10 max-w-6xl mx-auto">
                <div className="flex items-center gap-3">
                    <ShieldAlert className="text-blue-500" size={32} />
                    <h1 className="text-2xl font-bold text-white">CyberGuard Dashboard</h1>
                </div>
                <div className="flex items-center gap-4">
                    <Link href="/about">
                        <Button variant="ghost" className="text-gray-400 hover:text-white flex items-center gap-2">
                            <Info size={16} /> <span className="hidden md:inline">System Architecture</span>
                        </Button>
                    </Link>
                    <Link href="/">
                        <Button variant="ghost" className="text-gray-400 hover:text-white">Home</Button>
                    </Link>
                    <UserButton afterSignOutUrl="/" />
                </div>
            </header>

            <main className="max-w-6xl mx-auto">
                {/* Persistent Memory Layer Stats Widget */}
                <MemoryStats stats={stats} loading={statsLoading} />

                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-white">Your Cases</h2>
                    <Button onClick={() => setIsModalOpen(true)} className="bg-blue-600 hover:bg-blue-700">
                        <Plus size={16} className="mr-2" /> New Case
                    </Button>
                </div>

                {loading ? (
                    <div className="text-gray-400">Loading cases...</div>
                ) : casesError ? (
                    <div className="text-amber-400 text-sm">Could not load your cases. The server may be waking up — refresh in a moment.</div>
                ) : cases.length === 0 ? (
                    <div className="text-center py-20 border border-dashed border-gray-800 rounded-xl bg-white/5">
                        <p className="text-gray-400 mb-4">No active cases found.</p>
                        <Button onClick={() => setIsModalOpen(true)} variant="secondary" className="border-blue-500/50 text-blue-400">
                            Report an Incident
                        </Button>
                    </div>
                ) : (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {cases.map((c) => (
                            <Link href={`/cases/${c._id}`} key={c._id}>
                                <Card className="p-6 bg-white/5 hover:bg-white/10 border-white/10 transition-all cursor-pointer group h-full">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className={`px-2 py-1 rounded text-xs font-bold uppercase ${c.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                                            {c.status}
                                        </div>
                                        <Clock size={14} className="text-gray-500" />
                                    </div>
                                    <h3 className="text-lg font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">{c.title}</h3>
                                    <p className="text-sm text-gray-400 line-clamp-2 mb-4">{c.incident_summary}</p>
                                    <div className="flex items-center text-xs text-gray-500 mt-auto">
                                        <MessageSquare size={12} className="mr-1" /> Open Chat
                                    </div>
                                </Card>
                            </Link>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
