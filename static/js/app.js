const $ = (id) => document.getElementById(id);
const CARDS = ["preview", "summary", "credibility", "claims", "misinfo", "source", "factcheck"];
let report = {};   // module -> markdown
let article = null;

// ---------- helpers ----------
function showError(msg) {
  const el = $("error-card");
  el.textContent = "⚠ " + msg;
  el.classList.remove("hidden");
}
function clearError() { $("error-card").classList.add("hidden"); }

function showSpinner(text) {
  $("spinner-text").textContent = text;
  $("spinner").classList.remove("hidden");
  $("analyze-btn").disabled = true;
}
function hideSpinner() {
  $("spinner").classList.add("hidden");
  $("analyze-btn").disabled = false;
}

function renderMd(targetId, md) {
  const el = $(targetId);
  el.innerHTML = marked.parse(md || "_No result._");
  el.querySelectorAll("pre code").forEach((b) => hljs.highlightElement(b));
}

// ---------- UX helpers ----------
let toastTimer;
function toast(msg) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add("hidden"), 2200);
}

function setStatus(key, state) {
  const chip = document.querySelector(`[data-status="${key}"]`);
  if (chip) chip.className = `status-chip ${state}`;
}

function resetStatuses() {
  document.querySelectorAll(".status-chip").forEach((c) => (c.className = "status-chip"));
}

function showSkeleton(card) {
  const el = $("out-" + card);
  $("card-" + card).classList.remove("hidden");
  el.innerHTML = [100, 92, 96, 60].map(
    (w) => `<div class="skel" style="width:${w}%"></div>`
  ).join("");
}

function badgeFor(md) {
  const m = (md.match(/Likely (Credible|Misleading|False)|Unverifiable/i) || [null])[0];
  if (!m) return "";
  const v = m.toLowerCase();
  const cls = v.includes("credible") ? "badge-credible"
    : v.includes("misleading") ? "badge-misleading"
    : v.includes("false") ? "badge-false" : "badge-unverifiable";
  return `<span class="badge ${cls}">${m}</span>`;
}

function validUrl(s) {
  return /^https?:\/\/[^\s]+\.[^\s]+/.test(s) || /^[^\s]+\.[^\s]{2,}(\/\S*)?$/.test(s);
}

async function post(endpoint, body) {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok || !data.success) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// ---------- main flow ----------
async function analyze() {
  const url = $("url-input").value.trim();
  clearError();
  if (!url) return showError("Please enter a URL.");
  if (!validUrl(url)) return showError("That doesn't look like a valid URL.");
  resetResults();
  $("status-bar").classList.remove("hidden");
  resetStatuses();

  showSpinner("Extracting content & assessing credibility...");
  setStatus("credibility", "running");
  showSkeleton("credibility");
  try {
    const first = await post("/analyze-url", { url });
    article = first.article;
    report["Credibility Assessment"] = first.result;
    showArticle(article);
    showCard("credibility", first.result);
    setStatus("credibility", "done");
    $("card-credibility").scrollIntoView({ behavior: "smooth", block: "nearest" });

    // run remaining modules in parallel, reusing extracted content
    const tasks = [
      ["summary", "/summary", "Summary", "summary"],
      ["claims", "/claims", "Claims Extracted", "claims"],
      ["misinfo", "/misinformation", "Misinformation Indicators", "misinfo"],
      ["source", "/source-analysis", "Source Analysis", "source"],
      ["factcheck", "/fact-check", "Fact Check Suggestions", "factcheck"],
    ];
    $("spinner-text").textContent = "Running full analysis...";
    tasks.forEach(([key, , , card]) => { setStatus(key, "running"); showSkeleton(card); });
    await Promise.all(tasks.map(async ([key, ep, title, card]) => {
      try {
        const d = await post(ep, article);
        report[title] = d.result;
        showCard(card, d.result);
        setStatus(key, "done");
      } catch (e) {
        showCard(card, `**Error:** ${e.message}`);
        setStatus(key, "error");
      }
    }));
    ["copy-btn", "download-btn", "clear-btn"].forEach((id) => $(id).classList.remove("hidden"));
    toast("Analysis complete");
  } catch (e) {
    showError(e.message);
    setStatus("credibility", "error");
  } finally {
    hideSpinner();
    lucide.createIcons();
  }
}

function showCard(card, md) {
  $("card-" + card).classList.remove("hidden");
  renderMd("out-" + card, md);
  if (card === "credibility") {
    const b = badgeFor(md);
    if (b) $("out-" + card).insertAdjacentHTML("afterbegin", b);
  }
}

function showArticle(a) {
  $("card-preview").classList.remove("hidden");
  $("preview-body").innerHTML = `
    <div class="grid sm:grid-cols-2 gap-x-6 gap-y-1">
      <p><span class="font-semibold text-slate-600">Headline:</span> ${escapeHtml(a.headline || "—")}</p>
      <p><span class="font-semibold text-slate-600">Author/Page:</span> ${escapeHtml(a.author || "—")}</p>
      <p><span class="font-semibold text-slate-600">Published:</span> ${escapeHtml(a.published_date || "—")}</p>
      <p><span class="font-semibold text-slate-600">Platform:</span> ${escapeHtml(a.platform)}</p>
      <p class="sm:col-span-2 break-all"><span class="font-semibold text-slate-600">Source:</span>
        <a class="text-blue-600 hover:underline" href="${escapeHtml(a.url)}" target="_blank" rel="noopener">${escapeHtml(a.url)}</a></p>
    </div>
    <details class="mt-2">
      <summary class="cursor-pointer text-blue-600 text-xs font-semibold">View extracted text</summary>
      <p class="mt-2 text-slate-600 whitespace-pre-wrap">${escapeHtml(a.content || "")}</p>
    </details>`;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function resetResults() {
  report = {};
  article = null;
  CARDS.forEach((c) => {
    $("card-" + c).classList.add("hidden");
    const out = $("out-" + c);
    if (out) out.innerHTML = "";
  });
  $("status-bar").classList.add("hidden");
  ["copy-btn", "download-btn", "clear-btn"].forEach((id) => $(id).classList.add("hidden"));
}

// ---------- actions ----------
$("analyze-btn").addEventListener("click", analyze);
$("url-input").addEventListener("keydown", (e) => { if (e.key === "Enter") analyze(); });

$("clear-btn").addEventListener("click", () => {
  resetResults();
  $("url-input").value = "";
  clearError();
});

$("copy-btn").addEventListener("click", async () => {
  await navigator.clipboard.writeText(buildReport());
  toast("Report copied to clipboard");
});

$("download-btn").addEventListener("click", () => {
  const blob = new Blob([buildReport()], { type: "text/markdown" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "fake_news_analysis.md";
  a.click();
  URL.revokeObjectURL(a.href);
  toast("Report downloaded");
});

document.querySelectorAll(".sample-btn").forEach((btn) =>
  btn.addEventListener("click", () => {
    $("url-input").value = btn.dataset.url;
    analyze();
  })
);

function buildReport() {
  let md = `# AI Fake News Detector — Analysis Report\n\n`;
  if (article) {
    md += `**URL:** ${article.url}\n**Platform:** ${article.platform}\n**Headline:** ${article.headline || "—"}\n**Author:** ${article.author || "—"}\n**Published:** ${article.published_date || "—"}\n\n---\n\n`;
  }
  for (const [title, body] of Object.entries(report)) {
    md += `# ${title}\n\n${body}\n\n---\n\n`;
  }
  md += `_Generated by AI Fake News Detector — Webvoid Technologies_\n`;
  return md;
}
