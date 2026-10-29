"use client";

import type { Lang } from "@/lib/i18n";

export function LanguageToggle({ lang, onChange }: { lang: Lang; onChange: (l: Lang) => void }) {
    return (
        <div className="inline-flex rounded-lg border border-white/10 overflow-hidden text-xs" role="group" aria-label="Language">
            {(["en", "hi"] as const).map(l => (
                <button
                    key={l}
                    onClick={() => onChange(l)}
                    aria-pressed={lang === l}
                    className={`px-3 py-1.5 ${lang === l ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"}`}
                >
                    {l === "en" ? "English" : "हिंदी"}
                </button>
            ))}
        </div>
    );
}
