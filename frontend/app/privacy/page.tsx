import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export const metadata = { title: "Privacy - CyberGuardAI" };

const sections: { title: string; body: string[] }[] = [
  {
    title: "What we store",
    body: [
      "ScamShield and CyberResolve (no login): your text and screenshots are sent to our AI providers to produce the result. CyberResolve stores nothing. ScamShield keeps the analysis result (verdict, risk score, explanation and extracted details such as links or numbers) for up to 90 days to improve detection, without any account information.",
      "Cases (signed in): your case title, chat messages, generated plan, tasks and analysis are stored in our database, linked to your account, until you delete them.",
      "Threat memory (signed in): fraud indicators found in your investigations (UPI IDs, phone numbers, links, emails, wallet addresses) are stored with your account id so we can warn other users. An indicator is only marked 'confirmed' after three different people report it. Indicators nobody reports for a year are removed automatically.",
      "Screenshots themselves are not stored - only the text and details extracted from them, and a fingerprint (SHA-256 hash) used in your evidence package.",
    ],
  },
  {
    title: "Who processes it",
    body: [
      "AI analysis: Groq and Google Gemini. Database: MongoDB Atlas. Sign-in: Clerk. Hosting: Vercel and Render. Web research uses DuckDuckGo with the scam pattern, not your personal details.",
    ],
  },
  {
    title: "Your controls",
    body: [
      "Delete a single case from the case page, or download / delete all your data from the dashboard. Deleting your data also withdraws your reports from threat memory.",
      "Never share OTPs, PINs, passwords or full card numbers with this app - it will never ask for them.",
    ],
  },
  {
    title: "Not legal advice",
    body: [
      "CyberGuardAI gives guidance, not legal advice. For financial fraud in India call 1930 immediately and report at cybercrime.gov.in.",
    ],
  },
];

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-background px-4 py-10">
      <div className="max-w-3xl mx-auto">
        <Link href="/" className="inline-flex items-center text-gray-400 hover:text-white mb-8 text-sm">
          <ArrowLeft size={16} className="mr-2" /> Home
        </Link>
        <h1 className="text-3xl font-bold text-white mb-8">Privacy &amp; your data</h1>
        <div className="space-y-8">
          {sections.map(s => (
            <section key={s.title}>
              <h2 className="text-lg font-semibold text-white mb-3">{s.title}</h2>
              <div className="space-y-3">
                {s.body.map((p, i) => <p key={i} className="text-sm text-gray-300 leading-relaxed">{p}</p>)}
              </div>
            </section>
          ))}
        </div>
      </div>
    </main>
  );
}
