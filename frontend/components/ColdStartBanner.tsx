"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { checkHealth } from "@/lib/api";

const SHOW_AFTER_MS = 3000;
const POLL_MS = 5000;
const GIVE_UP_MS = 120_000;

/**
 * Render's free tier sleeps after 15 idle minutes and takes ~30-60s to wake.
 * Ping /health on load (which also starts the wake-up) and tell the user while we wait.
 */
export default function ColdStartBanner() {
    const [state, setState] = useState<"checking" | "waking" | "ready" | "offline">("checking");
    const [dismissed, setDismissed] = useState(false);
    const [elapsed, setElapsed] = useState(0);

    useEffect(() => {
        let cancelled = false;
        const started = Date.now();
        const showTimer = setTimeout(() => !cancelled && setState(s => (s === "checking" ? "waking" : s)), SHOW_AFTER_MS);
        const tick = setInterval(() => setElapsed(Math.round((Date.now() - started) / 1000)), 1000);

        const poll = async () => {
            while (!cancelled) {
                if (await checkHealth()) {
                    if (!cancelled) setState("ready");
                    return;
                }
                if (Date.now() - started > GIVE_UP_MS) {
                    if (!cancelled) setState("offline");
                    return;
                }
                await new Promise(r => setTimeout(r, POLL_MS));
            }
        };
        poll().finally(() => clearInterval(tick));

        return () => {
            cancelled = true;
            clearTimeout(showTimer);
            clearInterval(tick);
        };
    }, []);

    const visible = !dismissed && (state === "waking" || state === "offline");

    return (
        <AnimatePresence>
            {visible && (
                <motion.div
                    initial={{ y: -50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: -50, opacity: 0 }}
                    role="status"
                    className="fixed top-0 left-0 w-full z-50 bg-amber-500 text-amber-950 px-4 py-2 text-sm font-bold flex justify-between items-center shadow-md"
                >
                    <p>
                        {state === "waking"
                            ? `Waking up the server (free hosting sleeps when idle) - this can take up to a minute... ${elapsed}s`
                            : "The server isn't responding right now. Please try again in a few minutes."}
                    </p>
                    <button onClick={() => setDismissed(true)} className="p-1 hover:bg-amber-600 rounded transition-colors text-amber-900">
                        Dismiss
                    </button>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
