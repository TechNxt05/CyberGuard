# CyberGuard Link Shield (browser extension)

Warns you when you open a website that imitates a bank, payment app or government site, and lets you check any site
on demand.

**Privacy:** every page is checked locally against the official-domain list first. Only domains that *look like* a
brand look-alike (for example `sbi-kyc-update.in`) are sent to the CyberGuard API, plus any site you check manually
from the popup. Your normal browsing never leaves your browser.

## Install (developer mode, free)
1. Chrome → `chrome://extensions` → turn on **Developer mode** → **Load unpacked** → select this `extension/` folder.
2. Open the extension's **Settings** and enter your backend URL (for example `https://your-backend.onrender.com`).

Publishing on the Chrome Web Store requires a one-time $5 developer registration.
