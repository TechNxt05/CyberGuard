"use client"
import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Send, LifeBuoy, CheckCircle, ChevronRight, HelpCircle, FileText } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { resolveIncident, solveDoubt, assistForm } from "@/lib/api"
import { cn } from "@/lib/utils"

interface Message {
    role: "user" | "assistant"
    content: string
    type?: "text" | "doubt_answer" | "form_guide"
}

export default function ResolvePage() {
    const [messages, setMessages] = useState<Message[]>([
        { role: "assistant", content: "I am CyberResolve. Describe your incident briefly (e.g., 'My Instagram was hacked')." }
    ])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const [caseState, setCaseState] = useState<any>(null)
    const [guide, setGuide] = useState<string | null>(null)
    const scrollRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [messages])

    const handleSend = async () => {
        if (!input.trim()) return
        const userMsg = input
        setInput("")
        setMessages(prev => [...prev, { role: "user", content: userMsg }])
        setLoading(true)

        try {
            if (!caseState) {
                // Initial Incident Report
                const data = await resolveIncident({ description: userMsg, user_context: { country: "India" } })
                setCaseState(data)
                // Extract initial guide from checking generic or if backend sent it (backend sends it via separate logic usually, but here we can rely on state)
                // NOTE: Our API client wrapper for resolveIncident only returns case_state, but we need the guide too.
                // Actually, the backend resolve_incident endpoint currently only returns CaseState.
                // I need to update the hook to fetch the guide or just use the plan from CaseState.

                // Let's assume the first step is the guide for now, or I'll fix the backend soon.
                // For MVP, simply extracting the first incomplete step from strategy
                if (data.strategy?.lifecycle_plan?.length > 0) {
                    setGuide(`Step 1: ${data.strategy.lifecycle_plan[0].action}\n${data.strategy.lifecycle_plan[0].description}`)
                }

                setMessages(prev => [...prev, {
                    role: "assistant",
                    content: `I've analyzed your situation. It looks like a ${data.dimensions.attack_type} attack. I have generated a ${data.strategy.lifecycle_plan.length}-step plan for you. Follow the guide on the right.`
                }])

            } else {
                // Interactive "Doubt" or standard chat
                // We assume generic chat is a doubt for now
                const data = await solveDoubt(caseState.incident_id, userMsg)
                setMessages(prev => [...prev, { role: "assistant", content: data.answer, type: "doubt_answer" }])
            }
        } catch (error) {
            console.error(error)
            setMessages(prev => [...prev, { role: "assistant", content: "I encountered an error connecting to the core. Please try again." }])
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-background p-4 md:p-6 flex flex-col">
            <header className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
                <Link href="/" className="text-xl font-bold flex items-center gap-2 text-white">
                    <LifeBuoy className="text-emerald-400" />
                    CyberResolve <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400">Beta</span>
                </Link>
            </header>

            <div className="flex-1 grid lg:grid-cols-3 gap-6 overflow-hidden">
                {/* Chat Area */}
                <div className="lg:col-span-2 flex flex-col h-[600px] lg:h-auto bg-white/5 rounded-xl border border-white/10 overflow-hidden">
                    <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                        {messages.map((m, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={cn(
                                    "max-w-[85%] p-4 rounded-xl text-sm leading-relaxed",
                                    m.role === "user" ? "bg-blue-600 text-white ml-auto" : "bg-white/10 text-gray-200 mr-auto"
                                )}
                            >
                                {m.content}
                            </motion.div>
                        ))}
                        {loading && (
                            <div className="bg-white/10 w-fit p-4 rounded-xl">
                                <div className="flex space-x-2">
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75" />
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150" />
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="p-4 bg-white/5 border-t border-white/10 flex gap-2">
                        <input
                            className="flex-1 bg-transparent border border-white/20 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-emerald-500 transition-colors placeholder:text-gray-600"
                            placeholder={caseState ? "Ask a doubt or next step..." : "Describe incident..."}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && handleSend()}
                        />
                        <Button onClick={handleSend} disabled={loading || !input} className="bg-emerald-600 hover:bg-emerald-700">
                            <Send size={18} />
                        </Button>
                    </div>
                </div>

                {/* Dynamic Guide Panel */}
                <div className="h-full overflow-y-auto space-y-4">
                    <AnimatePresence>
                        {caseState ? (
                            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">
                                <Card className="border-emerald-500/30 bg-emerald-500/5">
                                    <h3 className="text-emerald-400 font-semibold mb-2 flex items-center gap-2">
                                        <CheckCircle size={18} /> Current Priority
                                    </h3>
                                    <div className="text-white text-sm whitespace-pre-wrap">
                                        {guide || "Loading guide..."}
                                    </div>
                                </Card>

                                <div className="space-y-2">
                                    <h4 className="text-gray-500 text-xs uppercase tracking-wider font-semibold">Resolution Plan</h4>
                                    {caseState.strategy.lifecycle_plan.map((step: any, i: number) => (
                                        <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5 opacity-50 hover:opacity-100 transition-opacity">
                                            <span className="text-xs text-gray-400">{i + 1}</span>
                                            <p className="text-xs text-gray-300 line-clamp-1">{step.action}</p>
                                        </div>
                                    ))}
                                </div>

                                <div className="pt-4 border-t border-white/10">
                                    <h4 className="text-gray-500 text-xs uppercase tracking-wider font-semibold mb-3">Quick Tools</h4>
                                    <div className="grid grid-cols-2 gap-2">
                                        <Button variant="secondary" className="text-xs h-auto py-2 flex flex-col gap-1">
                                            <HelpCircle size={16} className="text-blue-400" />
                                            Legal Help
                                        </Button>
                                        <Button variant="secondary" className="text-xs h-auto py-2 flex flex-col gap-1" >
                                            <FileText size={16} className="text-purple-400" />
                                            Draft FIR
                                        </Button>
                                    </div>
                                </div>
                            </motion.div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-center text-gray-500 p-6 border border-white/10 rounded-xl bg-white/5">
                                <LifeBuoy size={48} className="mb-4 opacity-20" />
                                <p>Describe your incident to generate a custom recovery plan.</p>
                            </div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    )
}
