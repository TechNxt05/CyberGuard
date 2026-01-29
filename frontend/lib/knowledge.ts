import { ShieldAlert, Phone, Smartphone, Lock, CreditCard, UserX, Video, Fingerprint, Briefcase, Package, Heart, QrCode, Wifi, Coins, Headphones, FileWarning, Monitor } from "lucide-react"

export const SCAM_TYPES = [
    {
        title: "Digital Arrest Scam",
        description: "Fraudsters pose as CBI/ED/Police officers on video calls (Skype/WhatsApp). They claim you are under 'virtual arrest' for money laundering or drug trafficking and demand money to 'verify' or 'settle' the case.",
        examples: [
            "Video call from 'Mumbai Police' claiming a parcel with drugs was seized in your name.",
            "Officer claims your Aadhaar is linked to money laundering and demands transfer to 'RBI Safe Account'."
        ],
        red_flags: ["Video call interrogation", "Demands to keep camera on 24/7", "Transfer money for 'verification'", "Threat of immediate arrest"]
    },
    {
        title: "AEPS (Aadhaar) Fraud",
        description: "Cybercriminals use your locked/stolen biometric data (fingerprints) to withdraw money from your bank account using Aadhaar Enabled Payment System without your OTP or PIN.",
        examples: [
            "Money deducted from account without receiving any OTP.",
            "Fingerprint cloned from property registry documents used for withdrawal."
        ],
        red_flags: ["Unexpected bank debit SMS", "No OTP received for transaction", "Property registration activity recently"]
    },
    {
        title: "Part-Time Job / Task Scam",
        description: "Offers of high income for simple tasks like 'liking videos', 'rating hotels', or 'investing in crypto'. They pay small amounts initially to build trust, then ask for a large deposit and block you.",
        examples: [
            "Work from home: Earn 5000/day just by liking YouTube videos. Join Telegram now.",
            "Prepaid Task: Invest 10k to get 15k return in 10 minutes."
        ],
        red_flags: ["Too good to be true returns", "Joining via Telegram", "Initial deposit asked", "Tasks like 'liking' videos"]
    },
    {
        title: "Electricity Bill Scam",
        description: "Fake SMS warning that power will be cut tonight unless you pay a small amount or call a specific number. They trick you into installing screen-sharing apps (AnyDesk/TeamViewer).",
        examples: [
            "Dear User, Your electricity power will be disconnected at 9:30 PM. Previous month bill was not updated. Contact officer 99XXXXXXX."
        ],
        red_flags: ["Threat of disconnection tonight", "Personal mobile number given", "Request to download AnyDesk/QuickSupport"]
    },
    {
        title: "FedEx / Courier Scam",
        description: "Fraudsters claim a parcel in your name containing illegal items (drugs, passports) has been seized by Customs/Police. They demand a penalty payment or connect you to a fake 'Police Officer'.",
        examples: [
            "IVR Call: 'Press 1 to talk to FedEx executive regarding your seized parcel.'",
            "Call from 'Customs Officer' regarding a package going from Mumbai to Taiwan."
        ],
        red_flags: ["Unexpected call about a parcel", "Threat of legal action", "Demands for Skype/Video statement"]
    },
    {
        title: "Instant Loan App Harassment",
        description: "Apps offer quick loans but hack your contacts/gallery. Even after repayment (or without taking a loan), they blackmail you by threatening to send morphed nude photos to your contacts.",
        examples: [
            "Loan app accesses contacts and sends abusive messages to family.",
            "Morphing user's photo onto pornographic images for blackmail."
        ],
        red_flags: ["App asks for Gallery/Contact permissions", "High processing fees", "Abusive language/threats"]
    },
    {
        title: "QR Code / OLX Fraud",
        description: "Scammers posing as buyers on OLX/Quikr send a QR code and ask you to scan it to 'receive' money. Scanning a QR code ALWAYS deducts money from your account.",
        examples: [
            "Buyer sends a QR code: 'Scan this to get your payment of Rs 5000'.",
            "army officer' selling a car/bike urgently and asking for advance."
        ],
        red_flags: ["Asked to scan QR to RECEIVE money", "Buyer is in a hurry/Army impersonation", "Advance payment request"]
    },
    {
        title: "Matrimonial / Romance Scam",
        description: "Fraudsters create fake profiles on matrimonial sites, build emotional trust, and then ask for money for a 'medical emergency', 'customs clearance' for a gift, or travel issues.",
        examples: [
            "Prospective groom stuck at airport customs, needs money to clear penalty.",
            "Foreign doctor sends expensive gift, asks you to pay customs duty."
        ],
        red_flags: ["Quick declaration of love", "Never video calls (or fake profile)", "Requests for money/customs fees"]
    },
    {
        title: "SIM Swap Fraud",
        description: "Scammers clone your SIM card or trick you into approving a SIM swap. Once they control your number, they get all your OTPs and empty your bank accounts.",
        examples: [
            "Call from 'Airtel/Jio' offering 5G upgrade, asking you to send an SMS.",
            "Sudden loss of signal on your phone for extended period."
        ],
        red_flags: ["Signal lost suddenly", "Request to forward SMS to '121'", "Offers for SIM upgrade over phone"]
    },
    {
        title: "Customer Care Fraud",
        description: "Scammers upload fake customer care numbers on Google/Social Media for banks, airlines, or apps. When you call, they steal your card details or make you install remote access apps.",
        examples: [
            "Searching 'Zomato refund number' on Google and calling a scammer.",
            "calling 'Airline support' to reschedule flight, they ask for AnyDesk access."
        ],
        red_flags: ["Mobile number listed as support", "Representative asks for AnyDesk/TeamViewer", "Asks for UPI PIN/Card CVV"]
    },
    {
        title: "Crypto Investment Scam",
        description: "Fake websites or Telegram groups promising huge returns on Crypto/Forex trading. They show fake profits on a dashboard but block you when you try to withdraw.",
        examples: [
            "WhatsApp group 'Crypto VIP Signals' promising 300% returns.",
            "Fake exchange app that allows deposit but no withdrawal."
        ],
        red_flags: ["Guaranteed high returns", "Unknown exchange apps (APK files)", "Pressure to invest more to 'unlock' profit"]
    },
    {
        title: "Sextortion",
        description: "Scammers (often female profiles) induce you into a video call, record a nude/compromising clip (or morph it), and threaten to upload it to YouTube/Family unless you pay.",
        examples: [
            "Video call from unknown number, screen shows explicit content.",
            "Threat to send video to Instagram friends list."
        ],
        red_flags: ["Video call from unknown number", "Seductive messages from strangers", "Blackmail for money"]
    },
    {
        title: "Ransomware Attack",
        description: "Malicious software locks your computer files or entire system. Attackers demand a ransom (usually in Bitcoin) to provide the decryption key.",
        examples: [
            "Computer screen locked with 'Your files are encrypted' message.",
            "Email attachment 'Invoice.exe' infects system."
        ],
        red_flags: ["Cannot open files", "Ransom note on desktop", "Demand for crypto payment"]
    },
    {
        title: "Tech Support Scam",
        description: "Pop-ups on your computer claim 'Virus Detected' and ask you to call a 'Microsoft/Windows' support number. They charge you for fake antivirus or steal data.",
        examples: [
            "Loud beep and full-screen warning: 'Call Microsoft Support immediately'.",
            "Technician claims your IP is hacked and asks for remote access."
        ],
        red_flags: ["Browser popup that won't close", "Toll-free number for 'Microsoft'", "Request for remote access"]
    }
]

export const CYBER_CRIMES = [
    {
        title: "Digital Arrest / Impersonation",
        icon: Video,
        definition: "Criminals impersonating Police/CBI on video calls to extort money under threat of arrest.",
        steps: ["Disconnect the call immediately", "Do NOT transfer money (Govt never asks for transfers)", "Report on cybercrime.gov.in or Dial 1930"]
    },
    {
        title: "AEPS Biometric Fraud",
        icon: Fingerprint,
        definition: "Unauthorized money withdrawal using cloned fingerprints via Aadhaar Payment System.",
        steps: ["Lock Biometrics in mAadhaar App immediately", "Report transaction to Bank & Dial 1930", "Visit Bank to dispute transaction"]
    },
    {
        title: "Part-Time Job Scams",
        icon: Briefcase,
        definition: "Fake job offers (liking videos) requiring upfront deposits.",
        steps: ["Stop paying immediately", "Exit the Telegram group", "Report UPI ID to bank"]
    },
    {
        title: "FedEx / Courier Scam",
        icon: Package,
        definition: "Fake calls about seized parcels with drugs/passports.",
        steps: ["Don't pay any 'penalty'", "Verify tracking number on official site", "Report number to 1930"]
    },
    {
        title: "QR Code / OLX Fraud",
        icon: QrCode,
        definition: "Scammers sending QR codes to 'pay' you.",
        steps: ["Never scan QR to RECEIVE money", "Report user on OLX/Platform", "Block the number"]
    },
    {
        title: "Loan App Harassment",
        icon: Smartphone,
        definition: "Illegal loan apps blackmails using contacts/gallery access.",
        steps: ["Uninstall app immediately", "Inform contacts it's a scam", "File complaint with RBI Sachet"]
    },
    {
        title: "Romance / Matrimonial",
        icon: Heart,
        definition: "Fake lovers asking for money for customs/hospital.",
        steps: ["Never send money to online friends", "Reverse image search profile photos", "Report profile to platform"]
    },
    {
        title: "SIM Swap Fraud",
        icon: Wifi,
        definition: "SIM signal lost due to unauthorized cloning.",
        steps: ["Contact mobile operator immediately", "Check bank accounts for transactions", "Change banking passwords"]
    },
    {
        title: "Crypto / Investment",
        icon: Coins,
        definition: "Fake schemes promising guaranteed high returns.",
        steps: ["Don't invest in unregulated apps", "Check exchange on FIU-IND list", "Report to Cyber Crime"]
    },
    {
        title: "Customer Care Fraud",
        icon: Headphones,
        definition: "Fake helpline numbers stealing card details.",
        steps: ["Only use numbers from official app/site", "Never download AnyDesk/TeamViewer", "Block card if details shared"]
    },
    {
        title: "Ransomware",
        icon: FileWarning,
        definition: "Malware locking files and demanding ransom.",
        steps: ["Disconnect internet immediately", "Don't pay ransom", "Consult cyber security expert"]
    },
    {
        title: "Tech Support Scam",
        icon: Monitor,
        definition: "Fake virus alerts asking to call support.",
        steps: ["Force close browser (Alt+F4)", "Don't call the number", "Run trusted antivirus scan"]
    },
    {
        title: "Sextortion",
        icon: UserX,
        definition: "Threatening to release private/morphed images/videos unless money is paid.",
        steps: ["Do NOT pay money (demand never ends)", "Don't delete chat history (evidence)", "Block the user & Report to Cyber Crime (1930)"]
    },
    {
        title: "Phishing & Vishing",
        icon: Phone,
        definition: "Fake calls/links pretending to be Bank/KYC agents to steal OTPs or passwords.",
        steps: ["Never share OTP/CVV over call", "Don't click short links (bit.ly) in SMS", "Call official bank support to verify"]
    }
]
