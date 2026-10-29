"use client";

import { CheckCircle2, Loader2 } from "lucide-react";
import type { ProgressStep } from "@/lib/api";

/** Live list of finished workflow steps, with a spinner for the one in progress. */
export function ProgressSteps({ steps, active }: { steps: ProgressStep[]; active: boolean }) {
    if (!steps.length && !active) return null;
    return (
        <ul className="space-y-1.5 text-xs text-gray-400" aria-live="polite">
            {steps.map((s, i) => (
                <li key={`${s.step}-${i}`} className="flex items-center gap-2">
                    <CheckCircle2 size={14} className="text-emerald-400 shrink-0" /> {s.label}
                </li>
            ))}
            {active && (
                <li className="flex items-center gap-2 text-gray-300">
                    <Loader2 size={14} className="animate-spin shrink-0" /> {steps.length ? "Working on the next step..." : "Starting analysis..."}
                </li>
            )}
        </ul>
    );
}
