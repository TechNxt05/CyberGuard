const out = document.getElementById("out");
const button = document.getElementById("check");

function addLine(tag, text, className) {
  const el = document.createElement(tag);
  el.textContent = text;
  if (className) el.className = className;
  out.appendChild(el);
  return el;
}

chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
  let host = "";
  try { host = new URL(tab.url).hostname; } catch { /* not a web page */ }
  document.getElementById("host").textContent = host || "This page can't be checked.";
  button.disabled = !host;

  button.onclick = () => {
    out.textContent = "Checking...";
    chrome.runtime.sendMessage({ type: "check", url: tab.url }, res => {
      out.textContent = "";
      if (!res || !res.ok) {
        addLine("p", "Could not reach CyberGuard. Check the API address in Settings.");
        return;
      }
      const r = res.result;
      addLine("p", r.verdict, `verdict ${r.verdict}`);
      const list = addLine("ul", "");
      (r.signals.length ? r.signals : ["No warning signs found (this is not a guarantee)."]).forEach(s => {
        const li = document.createElement("li");
        li.textContent = s;
        list.appendChild(li);
      });
      if (r.domain_age_days !== undefined) addLine("small", `Domain age: ${r.domain_age_days} days`);
    });
  };
});
