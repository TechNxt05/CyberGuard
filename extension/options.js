const input = document.getElementById("api");

chrome.storage.sync.get("apiBase", ({ apiBase }) => {
  input.value = apiBase || "";
});

document.getElementById("save").onclick = async () => {
  await chrome.storage.sync.set({ apiBase: input.value.trim() });
  await chrome.storage.local.remove(["lists", "listsAt"]); // refetch the official lists from the new backend
  document.getElementById("status").textContent = "Saved.";
};
