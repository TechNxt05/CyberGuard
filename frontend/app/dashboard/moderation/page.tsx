"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";

interface PendingReport {
    _id: string;
    entity_type: string;
    value: string;
    crime_type: string;
    description: string;
    created_at: string;
}

export default function ModerationPage() {
    const { getToken, isLoaded } = useAuth();
    const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
    const [reports, setReports] = useState<PendingReport[]>([]);

    const load = useCallback(async () => {
        const token = await getToken();
        const role = await apiFetch<{ is_admin: boolean }>("/me/role", { token }).catch(() => ({ is_admin: false }));
        setIsAdmin(role.is_admin);
        if (role.is_admin) setReports(await apiFetch<PendingReport[]>("/api/admin/reports", { token }));
    }, [getToken]);

    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        if (isLoaded) load();
    }, [isLoaded, load]);

    const decide = async (id: string, action: "approve" | "reject") => {
        await apiFetch(`/api/admin/reports/${id}/${action}`, { method: "POST", body: { note: "" }, token: await getToken() });
        setReports(prev => prev.filter(r => r._id !== id));
    };

    if (isAdmin === null) return <div className="p-6 text-gray-400">Loading...</div>;
    if (!isAdmin) return <div className="p-6 text-gray-400">This page is for moderators. <Link href="/dashboard" className="text-blue-400">Back</Link></div>;

    return (
        <div className="max-w-4xl mx-auto p-4 sm:p-6">
            <h1 className="text-2xl font-bold text-white mb-1">Report moderation</h1>
            <p className="text-sm text-gray-400 mb-6">Approve only reports that clearly describe a scam. Approved contacts enter threat memory; they become &quot;confirmed&quot; only after several independent reports.</p>
            {reports.length === 0 ? (
                <p className="text-gray-500 text-sm">No pending reports.</p>
            ) : (
                <ul className="space-y-3">
                    {reports.map(r => (
                        <li key={r._id} className="p-4 rounded-lg border border-white/10 bg-white/5">
                            <div className="flex justify-between gap-3 flex-wrap">
                                <div>
                                    <p className="font-mono text-white break-all">{r.value}</p>
                                    <p className="text-xs text-gray-500 uppercase mt-1">{r.entity_type.replace("_", " ")} · {r.crime_type} · {new Date(r.created_at).toLocaleString()}</p>
                                </div>
                                <div className="flex gap-2">
                                    <Button onClick={() => decide(r._id, "approve")} className="bg-emerald-600 hover:bg-emerald-500 h-8 text-xs">Approve</Button>
                                    <Button onClick={() => decide(r._id, "reject")} variant="ghost" className="h-8 text-xs text-gray-300">Reject</Button>
                                </div>
                            </div>
                            {r.description && <p className="text-sm text-gray-300 mt-2 whitespace-pre-wrap">{r.description}</p>}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
