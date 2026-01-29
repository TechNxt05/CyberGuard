"use client"
import { motion } from "framer-motion"
import { ShieldCheck, LifeBuoy, ArrowRight, LayoutDashboard, LogIn } from "lucide-react"
import { Card } from "@/components/ui/card"
import Link from "next/link"
import { CYBER_CRIMES } from "@/lib/knowledge"
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";
import { Button } from "@/components/ui/button"

export default function Home() {
    return (
        <main className="flex min-h-screen flex-col items-center p-6 relative overflow-x-hidden">
            {/* Hero Section */}
            <div className="w-full max-w-5xl mx-auto pt-20 pb-16 text-center z-10">
                <div className="flex justify-end absolute top-6 right-6 gap-4">
                    <SignedIn>
                        <Link href="/dashboard">
                            <Button variant="secondary" className="border-blue-500/50 text-blue-400 hover:bg-blue-500/10">
                                <LayoutDashboard className="mr-2" size={16} /> Dashboard
                            </Button>
                        </Link>
                        <UserButton afterSignOutUrl="/" />
                    </SignedIn>
                    <SignedOut>
                        <SignInButton mode="modal">
                            <Button className="bg-blue-600 hover:bg-blue-700">
                                <LogIn className="mr-2" size={16} /> Sign In
                            </Button>
                        </SignInButton>
                    </SignedOut>
                </div>

                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-sm mb-8">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                    </span>
                    CyberGuardAI One Online
                </div>

                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6"
                >
                    Your Personal <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-300 to-emerald-400">
                        Digital Bodyguard
                    </span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto mb-12"
                >
                    Protect yourself from scams, fraud, and cyber threats with enterprise-grade AI.
                    Real-time detection and expert resolution guidance.
                </motion.p>

                {/* Modules */}
                <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                    <Link href="/scamshield" className="group">
                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                            <Card className="h-full border-blue-500/30 bg-gradient-to-br from-blue-500/10 to-transparent hover:border-blue-500/50 p-8 text-left transition-all">
                                <div className="p-4 rounded-xl bg-blue-500/20 w-fit mb-6 text-blue-400 group-hover:text-blue-300 group-hover:shadow-[0_0_20px_rgba(59,130,246,0.5)] transition-all">
                                    <ShieldCheck size={32} />
                                </div>
                                <h2 className="text-2xl font-bold text-white mb-3">ScamShield Detector</h2>
                                <p className="text-gray-400 mb-6">
                                    Paste any message, link, or UPI ID. Our agents analyze detection patterns instantly.
                                </p>
                                <div className="flex items-center text-blue-400 font-medium text-sm group-hover:translate-x-1 transition-transform">
                                    Start Scan <ArrowRight size={16} className="ml-2" />
                                </div>
                            </Card>
                        </motion.div>
                    </Link>

                    <SignedIn>
                        <Link href="/dashboard" className="group">
                            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                                <Card className="h-full border-emerald-500/30 bg-gradient-to-br from-emerald-500/10 to-transparent hover:border-emerald-500/50 p-8 text-left transition-all">
                                    <div className="p-4 rounded-xl bg-emerald-500/20 w-fit mb-6 text-emerald-400 group-hover:text-emerald-300 group-hover:shadow-[0_0_20px_rgba(16,185,129,0.5)] transition-all">
                                        <LayoutDashboard size={32} />
                                    </div>
                                    <h2 className="text-2xl font-bold text-white mb-3">CyberResolve Dashboard</h2>
                                    <p className="text-gray-400 mb-6">
                                        Manage your incidents, track recovery tasks, and chat with AI legal experts.
                                    </p>
                                    <div className="flex items-center text-emerald-400 font-medium text-sm group-hover:translate-x-1 transition-transform">
                                        Go to Dashboard <ArrowRight size={16} className="ml-2" />
                                    </div>
                                </Card>
                            </motion.div>
                        </Link>
                    </SignedIn>

                    <SignedOut>
                        <div className="group cursor-not-allowed opacity-75">
                            <Card className="h-full border-gray-700 bg-gradient-to-br from-gray-800/10 to-transparent p-8 text-left">
                                <div className="p-4 rounded-xl bg-gray-700/20 w-fit mb-6 text-gray-400">
                                    <LifeBuoy size={32} />
                                </div>
                                <h2 className="text-2xl font-bold text-gray-300 mb-3">CyberResolve Engine</h2>
                                <p className="text-gray-500 mb-6">
                                    Victim of a hack or fraud? Sign in to create a case and get a custom recovery plan.
                                </p>
                                <div className="flex items-center text-gray-500 font-medium text-sm">
                                    Sign In to Access
                                </div>
                            </Card>
                        </div>
                    </SignedOut>
                </div>
            </div>

            {/* Cyber Crime Knowledge Section */}
            <div className="w-full max-w-6xl mx-auto mt-20 border-t border-white/5 pt-20">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold text-white mb-4">Understanding Cyber Threats</h2>
                    <p className="text-gray-400">Stay informed about the latest digital dangers targeting users.</p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {CYBER_CRIMES.map((crime, i) => (
                        <Card key={i} className="bg-white/5 hover:bg-white/10 border-white/10 transition-colors">
                            <div className="mb-4 text-purple-400">
                                <crime.icon size={32} />
                            </div>
                            <h3 className="text-lg font-bold text-white mb-2">{crime.title}</h3>
                            <p className="text-sm text-gray-400 mb-4 h-16">{crime.definition}</p>

                            <div className="space-y-2">
                                <p className="text-xs font-bold text-gray-500 uppercase">Prevention</p>
                                <ul className="space-y-1">
                                    {crime.steps.map((step, j) => (
                                        <li key={j} className="text-xs text-gray-300 flex items-start gap-2">
                                            <span className="text-purple-500">•</span> {step}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>

            {/* Background Elements */}
            <div className="fixed top-0 left-0 w-full h-full pointer-events-none -z-10">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-900/10 rounded-full blur-[128px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-900/10 rounded-full blur-[128px]" />
            </div>
        </main>
    )
}
