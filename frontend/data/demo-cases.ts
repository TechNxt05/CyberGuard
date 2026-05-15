export const demoCases = [
  {
    id: "demo-upi-001",
    title: "UPI Payment Fraud — ₹47,000",
    type: "financial_fraud",
    summary: "Victim received a fake Google Pay refund link via WhatsApp. Clicked link, entered UPI PIN, lost ₹47,000 in 3 transactions to mule accounts.",
    evidence: {
      description: "WhatsApp screenshot showing fake GPay refund message with malicious link. Bank statement showing 3 debit entries within 4 minutes.",
      extractedEntities: {
        upiIds: ["pay.refund8821@ybl", "support.gpay991@paytm"],
        phoneNumbers: ["+91-98XXXXXXXX"],
        urls: ["gpay-refund-portal.xyz/claim"],
        amount: "₹47,000",
        timeWindow: "4 minutes"
      }
    },
    attackChain: ["WhatsApp social engineering", "Fake refund portal", "UPI PIN harvesting", "Rapid fund transfer to mule accounts"],
    urgency: "HIGH",
    recoveryProbability: 62
  },
  {
    id: "demo-phish-002",
    title: "SBI NetBanking Phishing — Credentials Stolen",
    type: "phishing",
    summary: "Received SMS with fake SBI KYC update link. Entered credentials on cloned SBI page. Account accessed from Rajasthan IP within 1 hour.",
    evidence: {
      description: "SMS screenshot with spoofed sender ID 'SBI-Alert'. Cloned website URL in browser history. Unauthorized login alert email from real SBI.",
      extractedEntities: {
        urls: ["sbi-kyc-update.in/verify", "sbi-netbanking.co/login"],
        spoofedSender: "SBI-Alert",
        unauthorizedIP: "103.XX.XX.XX (Rajasthan)",
        timeToCompromise: "47 minutes"
      }
    },
    attackChain: ["SMS spoofing", "Credential phishing page", "Session hijacking", "Account takeover"],
    urgency: "CRITICAL",
    recoveryProbability: 78
  },
  {
    id: "demo-sext-003",
    title: "Sextortion Threat — ₹2L Demand",
    type: "sextortion",
    summary: "Received email claiming attacker has webcam footage. Demanding ₹2,00,000 in Bitcoin within 48 hours. Email contains partial real password (from old breach).",
    evidence: {
      description: "Threatening email with Bitcoin wallet address. Partial real password included to establish credibility. Sent from ProtonMail address.",
      extractedEntities: {
        bitcoinWallet: "1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf",
        demandAmount: "₹2,00,000",
        deadline: "48 hours",
        senderEmail: "secure.warning@proton.me",
        breachSource: "LinkedIn 2021 breach (likely)"
      }
    },
    attackChain: ["Credential stuffing from breach data", "Psychological manipulation", "Crypto payment demand", "Deadline pressure"],
    urgency: "MEDIUM",
    recoveryProbability: 91
  }
];
