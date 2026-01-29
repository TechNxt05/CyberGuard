"use client"
import { useState, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ArrowLeft, AlertTriangle, ShieldCheck, ShieldAlert, Search, Loader2, Upload, FileText, X, Brain } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { checkScam } from "@/lib/api"
import { cn } from "@/lib/utils"
import { SCAM_TYPES } from "@/lib/knowledge"

export default function ScamShieldPage() {
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<any>(null)
    const [imageBase64, setImageBase64] = useState<string | null>(null)
    const [fileName, setFileName] = useState<string | null>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const handleAnalyze = async () => {
        if (!input.trim() && !imageBase64) return
        setLoading(true)
        setResult(null)
        try {
            const data = await checkScam({
                message: input,
                image_base64: imageBase64 || undefined,
                source: "user_input"
            })
            setResult(data)
        } catch (error) {
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        setFileName(file.name)

        // Text File
        if (file.type === "text/plain") {
            const reader = new FileReader()
            reader.onload = (e) => {
                const text = e.target?.result as string
                setInput(text)
                setImageBase64(null)
            }
            reader.readAsText(file)
        }
        // Image File
        else if (file.type.startsWith("image/")) {
            const reader = new FileReader()
            reader.onload = (e) => {
                const base64 = (e.target?.result as string).split(",")[1] // Remove data:image/... prefix
                setImageBase64(base64)
                setInput("") // Clear text if image is primary, or keep it? Let's clear to avoid confusion or allow both.
                // For UI feedback, let's show the user an image is selected
            }
            reader.readAsDataURL(file)
        }
        else {
            alert("Please upload .txt or image files (.png, .jpg)")
        }
    }

    return (
        <div className="min-h-screen bg-background p-6">
            <Link href="/" className="inline-flex items-center text-gray-400 hover:text-white mb-8 transition-colors">
                <ArrowLeft size={20} className="mr-2" /> Back to Home
            </Link>

            <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 mb-20">
                <div className="space-y-6">
                    <div className="space-y-2">
                        <h1 className="text-3xl font-bold text-white">ScamShield Detector</h1>
                        <p className="text-gray-400">Paste any suspicious message, email, or UPI ID below.</p>
                    </div>

                    <Card className="p-0 border-blue-500/20 overflow-hidden relative group">
                        <textarea
                            className="w-full h-80 bg-transparent p-6 text-white resize-none focus:outline-none placeholder:text-gray-600 font-mono text-sm leading-relaxed"
                            placeholder="e.g. 'Dear customer, your electricity will be cut at 9PM. Call this number...'"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                        />

                        {/* Action Bar */}
                        <div className="absolute bottom-4 right-4 flex gap-2 items-center">
                            {fileName && <span className="text-xs text-blue-300 bg-blue-500/10 px-2 py-1 rounded">{fileName}</span>}
                            <input
                                type="file"
                                ref={fileInputRef}
                                className="hidden"
                                accept=".txt,.png,.jpg,.jpeg"
                                onChange={handleFileUpload}
                            />
                            <Button
                                variant="secondary"
                                className="bg-white/5 hover:bg-white/10"
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <Upload size={16} className="mr-2" /> Upload
                            </Button>
                            <Button onClick={handleAnalyze} disabled={loading || (!input && !imageBase64)}>
                                {loading ? <Loader2 className="animate-spin mr-2" /> : <Search className="mr-2" size={16} />}
                                Analyze Risk
                            </Button>
                        </div>
                        {(input || imageBase64) && (
                            <button
                                onClick={() => { setInput(""); setImageBase64(null); setFileName(null); }}
                                className="absolute top-4 right-4 text-gray-500 hover:text-white"
                            >
                                <X size={16} />
                            </button>
                        )}
                    </Card>
                </div>

                {/* Results Section */}
                <div>
                    <AnimatePresence>
                        {result && (
                            <motion.div
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="w-full"
                            >
                                <Card className={`p-6 border-l-4 ${result.scout_report.risk_score > 70 ? 'border-red-500 bg-red-500/10' :
                                    result.scout_report.risk_score > 40 ? 'border-orange-500 bg-orange-500/10' :
                                        'border-green-500 bg-green-500/10'
                                    }`}>
                                    <div className="flex justify-between items-start mb-6">
                                        <div className="flex items-center gap-3">
                                            {result.scout_report.risk_score > 70 ? <ShieldAlert size={32} className="text-red-500" /> : <ShieldCheck size={32} className="text-green-500" />}
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <h3 className="font-bold text-2xl text-white">{result.scout_report.risk_score}/100</h3>
                                                    <span className={`text-xs px-2 py-0.5 rounded-full border ${result.scout_report.risk_score > 70 ? 'border-red-500 text-red-400' : 'border-green-500 text-green-400'
                                                        }`}>
                                                        RISK SCORE
                                                    </span>
                                                </div>
                                                <p className={`text-sm font-medium ${result.scout_report.risk_score > 70 ? 'text-red-400' : 'text-green-400'}`}>
                                                    {result.scout_report.severity ? result.scout_report.severity.toUpperCase() : "ANALYZED"}
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Analysis Content */}
                                    <div className="space-y-6">

                                        {/* Extracted Entities */}
                                        {result.scout_report.extracted_entities && Object.keys(result.scout_report.extracted_entities).length > 0 && (
                                            <div className="bg-black/40 rounded-lg p-4 border border-white/5">
                                                <h4 className="text-xs font-semibold text-gray-400 mb-3 uppercase tracking-wider">Extracted Details</h4>
                                                <div className="grid grid-cols-2 gap-4">
                                                    {Object.entries(result.scout_report.extracted_entities).map(([key, value]) => (
                                                        <div key={key}>
                                                            <span className="text-xs text-gray-500 block capitalize">{key.replace(/_/g, " ")}</span>
                                                            <span className="text-sm text-white font-mono">{String(value)}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        <div className="space-y-4">
                                            <div className="flex gap-3 items-start">
                                                <Brain className="text-blue-400 mt-1 shrink-0" size={18} />
                                                <div>
                                                    <h4 className="font-semibold text-blue-200 mb-1">Mechanism (Logic)</h4>
                                                    <p className="text-gray-300 text-sm leading-relaxed">{result.scout_report.scam_logic || result.scout_report.analysis}</p>
                                                </div>
                                            </div>

                                            <div className="flex gap-3 items-start">
                                                <AlertTriangle className="text-orange-400 mt-1 shrink-0" size={18} />
                                                <div>
                                                    <h4 className="font-semibold text-orange-200 mb-1">Consequences</h4>
                                                    <p className="text-gray-300 text-sm leading-relaxed">{result.scout_report.consequences || "Potential financial or data loss."}</p>
                                                </div>
                                            </div>

                                            <div className="flex gap-3 items-start">
                                                <ShieldCheck className="text-green-400 mt-1 shrink-0" size={18} />
                                                <div>
                                                    <h4 className="font-semibold text-green-200 mb-1">Recommendation</h4>
                                                    <p className="text-gray-300 text-sm leading-relaxed">{result.scout_report.recommendation}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </Card>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    )
}
