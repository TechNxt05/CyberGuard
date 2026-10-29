"use client";

import { useEffect } from "react";

/** Root error boundary: a friendly fallback instead of a blank page when a component crashes. */
export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
    useEffect(() => {
        console.error("Unhandled UI error", error);
    }, [error]);

    return (
        <main className="min-h-screen bg-background flex flex-col items-center justify-center gap-4 text-white p-6 text-center">
            <h1 className="text-xl font-semibold">Something went wrong on this page.</h1>
            <p className="text-sm text-gray-400 max-w-md">
                Your data is safe. Try again, and if you are dealing with financial fraud right now, call 1930 immediately.
            </p>
            <button onClick={reset} className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-sm">Try again</button>
        </main>
    );
}
