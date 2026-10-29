"use client";

import { useEffect, useState } from "react";

export type Lang = "en" | "hi";

const STORAGE_KEY = "cyberguard-lang";

const strings = {
  en: {
    scamTitle: "ScamShield Detector",
    scamSubtitle: "Paste any suspicious message, email, or UPI ID below.",
    scamPlaceholder: "e.g. 'Dear customer, your electricity will be cut at 9PM. Call this number...'",
    upload: "Upload",
    analyze: "Analyze Risk",
    riskScore: "RISK SCORE",
    analysisFailed: "Automated analysis could not be completed, so this is a cautious default - not a verdict. Treat the message as unverified.",
    extracted: "Extracted Details",
    mechanism: "How the trick works",
    consequences: "What you could lose",
    recommendation: "Recommendation",
    simpleWords: "In simple words",
    whatToDo: "What to do now",
    linkChecks: "Link checks",
    serverDown: "Could not reach the server. If it was idle it may take up to a minute to wake up - please retry.",
    resolveIntro: "I am CyberResolve. Describe your incident briefly (e.g., 'My Instagram was hacked').",
    resolvePlaceholder: "Describe incident...",
    resolveFollowUp: "Ask a doubt or next step...",
    currentPriority: "Current Priority",
    resolutionPlan: "Resolution Plan",
    quickTools: "Quick Tools",
    legalHelp: "Legal Help",
    draftFir: "Draft FIR",
    resolveEmpty: "Describe your incident to generate a custom recovery plan.",
  },
  hi: {
    scamTitle: "स्कैमशील्ड जाँच",
    scamSubtitle: "कोई भी संदिग्ध मैसेज, ईमेल या UPI ID नीचे पेस्ट करें।",
    scamPlaceholder: "जैसे: 'प्रिय ग्राहक, आज रात 9 बजे आपकी बिजली कट जाएगी। इस नंबर पर कॉल करें...'",
    upload: "अपलोड",
    analyze: "जोखिम जाँचें",
    riskScore: "जोखिम स्कोर",
    analysisFailed: "स्वचालित जाँच पूरी नहीं हो सकी, इसलिए यह एक सावधानी भरा अनुमान है, अंतिम फैसला नहीं। इस मैसेज को असत्यापित मानें।",
    extracted: "निकाली गई जानकारी",
    mechanism: "धोखा कैसे काम करता है",
    consequences: "आपका क्या नुकसान हो सकता है",
    recommendation: "सलाह",
    simpleWords: "आसान शब्दों में",
    whatToDo: "अभी क्या करें",
    linkChecks: "लिंक जाँच",
    serverDown: "सर्वर से जुड़ नहीं सके। अगर सर्वर निष्क्रिय था तो उसे शुरू होने में एक मिनट लग सकता है - कृपया दोबारा कोशिश करें।",
    resolveIntro: "मैं साइबर-रिज़ॉल्व हूँ। अपनी घटना संक्षेप में बताएँ (जैसे, 'मेरा इंस्टाग्राम हैक हो गया')।",
    resolvePlaceholder: "घटना के बारे में बताएँ...",
    resolveFollowUp: "कोई सवाल या अगला कदम पूछें...",
    currentPriority: "अभी की प्राथमिकता",
    resolutionPlan: "समाधान योजना",
    quickTools: "त्वरित साधन",
    legalHelp: "कानूनी मदद",
    draftFir: "FIR ड्राफ्ट",
    resolveEmpty: "अपनी रिकवरी योजना बनाने के लिए अपनी घटना बताएँ।",
  },
} as const;

export type StringKey = keyof typeof strings.en;

/** Language preference remembered per browser (falls back to English if storage is unavailable). */
export function useLang() {
  const [lang, setLangState] = useState<Lang>("en");

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      // Read after mount (not in useState's initializer) so the server-rendered HTML and first client render match.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      if (saved === "hi" || saved === "en") setLangState(saved);
    } catch { /* storage blocked: keep default */ }
  }, []);

  const setLang = (next: Lang) => {
    setLangState(next);
    try { localStorage.setItem(STORAGE_KEY, next); } catch { /* ignore */ }
  };

  const t = (key: StringKey) => strings[lang][key];
  return { lang, setLang, t };
}
