"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { Flag } from "lucide-react";
import { ApiError, apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const TYPES = [
    { value: "phone_number", label: "Phone number" },
    { value: "upi_id", label: "UPI ID" },
    { value: "url", label: "Website / link" },
    { value: "email", label: "Email" },
    { value: "wallet_address", label: "Crypto wallet" },
] as const;

interface MyReport {
    _id: string;
    entity_type: string;
    value: string;
    status: "pending" | "approved" | "rejected";
    created_at: string;
}

/** Lets signed-in users report a scam contact; reports are moderated before they affect anyone. */
export function ReportIndicator() {
    const { getToken } = useAuth();
    const [entityType, setEntityType] = useState<string>("phone_number");
    const [value, setValue] = useState("");
    const [description, setDescription] = useState("");
    const [message, setMessage] = useState<string | null>(null);
    const [busy, setBusy] = useState(false);
    const [mine, setMine] = useState<MyReport[]>([]);

    const loadMine = async () => {
        try {
            setMine(await apiFetch<MyReport[]>("/api/community/reports/mine", { token: await getToken() }));
        } catch { /* list is optional */ }
    };

    useEffect(() => {
        loadMine();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const submit = async () => {
        if (!value.trim()) return;
        setBusy(true);
        setMessage(null);
        try {
            await apiFetch("/api/community/reports", {
                method: "POST",
                body: { entity_type: entityType, value, description },
                token: await getToken(),
            });
            setValue("");
            setDescription("");
            setMessage("Thanks - your report will be reviewed before it is shared with other users.");
            loadMine();
        } catch (err) {
            setMessage(err instanceof ApiError ? err.message : "Could not submit the report.");
        } finally {
            setBusy(false);
        }
    };

    return (
        <Card className="p-5 mt-10 bg-white/5 border-white/10">
            <h3 className="text-white font-semibold flex items-center gap-2 mb-1"><Flag size={16} className="text-red-400" /> Report a scam contact</h3>
            <p className="text-xs text-gray-400 mb-4">Help warn others. Reports are reviewed by a moderator, and a contact is only marked as a confirmed threat after several people report it.</p>
            <div className="grid sm:grid-cols-[160px_1fr] gap-2">
                <select value={entityType} onChange={e => setEntityType(e.target.value)} className="bg-black/30 border border-white/10 rounded p-2 text-sm text-white">
                    {TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
                <input value={value} onChange={e => setValue(e.target.value)} placeholder="e.g. 9876543210 or fraud@ybl" className="bg-black/30 border border-white/10 rounded p-2 text-sm text-white" />
            </div>
            <textarea value={description} onChange={e => setDescription(e.target.value)} maxLength={1000} placeholder="What happened? (optional)" className="w-full mt-2 bg-black/30 border border-white/10 rounded p-2 text-sm text-white h-20" />
            <div className="flex items-center gap-3 mt-2 flex-wrap">
                <Button onClick={submit} disabled={busy || !value.trim()} className="bg-red-600 hover:bg-red-500">{busy ? "Submitting..." : "Submit report"}</Button>
                {message && <span className="text-xs text-gray-300">{message}</span>}
            </div>
            {mine.length > 0 && (
                <ul className="mt-4 space-y-1 text-xs text-gray-400">
                    {mine.slice(0, 10).map(r => (
                        <li key={r._id} className="flex justify-between gap-2">
                            <span className="font-mono break-all">{r.value}</span>
                            <span className={r.status === "approved" ? "text-emerald-400" : r.status === "rejected" ? "text-gray-500" : "text-amber-300"}>{r.status}</span>
                        </li>
                    ))}
                </ul>
            )}
        </Card>
    );
}
