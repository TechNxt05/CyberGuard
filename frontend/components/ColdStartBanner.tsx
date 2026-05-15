"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function ColdStartBanner() {
    const [showBanner, setShowBanner] = useState(false);
    const [isWarming, setIsWarming] = useState(true);

    useEffect(() => {
        let isMounted = true;
        const startTime = Date.now();
        let slowPingTimeout: NodeJS.Timeout;

        const checkHealth = async () => {
            try {
                // If it takes more than 3 seconds, show the banner
                slowPingTimeout = setTimeout(() => {
                    if (isMounted && isWarming) {
                        setShowBanner(true);
                    }
                }, 3000);

                const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const res = await fetch(`${API_URL}/health`);
                
                if (res.ok) {
                    if (isMounted) {
                        setIsWarming(false);
                        setShowBanner(false);
                    }
                }
            } catch (error) {
                // If backend is completely offline, maybe don't show the warming banner, or show offline
                console.error("Backend health check failed", error);
            } finally {
                clearTimeout(slowPingTimeout);
            }
        };

        checkHealth();

        return () => {
            isMounted = false;
            clearTimeout(slowPingTimeout);
        };
    }, []);

    return (
        <AnimatePresence>
            {showBanner && (
                <motion.div 
                    initial={{ y: -50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: -50, opacity: 0 }}
                    className="fixed top-0 left-0 w-full z-50 bg-amber-500 text-amber-950 px-4 py-2 text-sm font-bold flex justify-between items-center shadow-md"
                >
                    <p>Backend warming up — first response may take 15s. Subsequent responses are fast.</p>
                    <button 
                        onClick={() => setShowBanner(false)}
                        className="p-1 hover:bg-amber-600 rounded transition-colors text-amber-900"
                    >
                        Dismiss
                    </button>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
