// Privacy model: every page is first checked LOCALLY against the official-domain list and brand keywords.
// Only domains that look like a bank/brand look-alike are sent to the CyberGuard API (or any domain when the
// user explicitly clicks "Check this site"). Ordinary browsing never leaves the browser.

const DEFAULT_API = "http://localhost:8000";
const LISTS_TTL_MS = 24 * 60 * 60 * 1000;
const RESULT_TTL_MS = 6 * 60 * 60 * 1000;
const FALLBACK_LISTS = { official: {}, brand_keywords: {}, always_official_suffixes: [".gov.in", ".nic.in", ".bank.in"] };

async function apiBase() {
  const { apiBase } = await chrome.storage.sync.get("apiBase");
  return (apiBase || DEFAULT_API).replace(/\/$/, "");
}

async function lists() {
  const { lists, listsAt } = await chrome.storage.local.get(["lists", "listsAt"]);
  if (lists && Date.now() - listsAt < LISTS_TTL_MS) return lists;
  try {
    const res = await fetch(`${await apiBase()}/api/official-domains`);
    const fresh = await res.json();
    await chrome.storage.local.set({ lists: fresh, listsAt: Date.now() });
    return fresh;
  } catch {
    return lists || FALLBACK_LISTS;
  }
}

function hostOf(url) {
  try {
    const u = new URL(url);
    if (!["http:", "https:"].includes(u.protocol)) return null;
    return u.hostname.replace(/^www\./, "").toLowerCase();
  } catch {
    return null;
  }
}

async function localVerdict(host) {
  const l = await lists();
  const official = Object.values(l.official).flat();
  if (l.always_official_suffixes.some(s => host.endsWith(s)) || official.some(d => host === d || host.endsWith("." + d))) {
    return { verdict: "official" };
  }
  const labels = host.split(/[.-]/).slice(0, -1);
  for (const [keyword, brand] of Object.entries(l.brand_keywords)) {
    if (labels.some(label => label.includes(keyword))) return { verdict: "lookalike", brand };
  }
  return { verdict: "ordinary" };
}

async function remoteCheck(url) {
  const key = `result:${hostOf(url)}`;
  const cached = (await chrome.storage.local.get(key))[key];
  if (cached && Date.now() - cached.at < RESULT_TTL_MS) return cached.result;
  const res = await fetch(`${await apiBase()}/api/url-check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  const result = await res.json();
  await chrome.storage.local.set({ [key]: { at: Date.now(), result } });
  return result;
}

function showBanner(tabId, result) {
  chrome.scripting.executeScript({
    target: { tabId },
    args: [result],
    func: r => {
      if (document.getElementById("cyberguard-warning")) return;
      const bar = document.createElement("div");
      bar.id = "cyberguard-warning";
      bar.setAttribute("role", "alert");
      bar.style.cssText = "position:fixed;top:0;left:0;right:0;z-index:2147483647;background:#b91c1c;color:#fff;font:14px/1.4 system-ui,sans-serif;padding:12px 16px;box-shadow:0 2px 8px rgba(0,0,0,.4)";
      bar.textContent = "CyberGuard warning: this site (" + r.domain + ") looks unsafe. " + (r.signals || []).join(" · ") +
        " Do not enter passwords, OTPs, card or UPI details.";
      const close = document.createElement("button");
      close.textContent = "Dismiss";
      close.style.cssText = "margin-left:12px;background:#fff;color:#b91c1c;border:0;border-radius:4px;padding:2px 8px;cursor:pointer";
      close.onclick = () => bar.remove();
      bar.appendChild(close);
      document.documentElement.appendChild(bar);
    },
  }).catch(() => {});
}

function setBadge(tabId, verdict) {
  const style = { malicious: ["!", "#dc2626"], suspicious: ["?", "#d97706"], official: ["OK", "#059669"] }[verdict];
  chrome.action.setBadgeText({ tabId, text: style ? style[0] : "" });
  if (style) chrome.action.setBadgeBackgroundColor({ tabId, color: style[1] });
}

chrome.tabs.onUpdated.addListener(async (tabId, info, tab) => {
  if (info.status !== "complete" || !tab.url) return;
  const host = hostOf(tab.url);
  if (!host) return;
  const local = await localVerdict(host);
  if (local.verdict === "official") return setBadge(tabId, "official");
  if (local.verdict !== "lookalike") return setBadge(tabId, null);
  try {
    const result = await remoteCheck(tab.url);
    setBadge(tabId, result.verdict);
    if (result.verdict === "malicious" || result.verdict === "suspicious") showBanner(tabId, result);
  } catch {
    // Backend unreachable: still warn on the local look-alike signal.
    setBadge(tabId, "suspicious");
    showBanner(tabId, { domain: host, signals: [`Uses the name '${local.brand}' but is not an official ${local.brand} website.`] });
  }
});

// The popup asks for a manual check of the current tab.
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type !== "check") return;
  remoteCheck(msg.url).then(r => sendResponse({ ok: true, result: r })).catch(e => sendResponse({ ok: false, error: String(e) }));
  return true; // keeps the channel open for the async response
});
