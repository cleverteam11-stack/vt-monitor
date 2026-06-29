#!/usr/bin/env python3
"""
VT Monitor — TikTok Brand Monitoring Tool
Memantau kreator TikTok untuk 6 brand:
Ourfish Store, Willowcat, Clever Solutions Indonesia,
PiOONERVET Indonesia, Golden Paw, Pakewuh
"""

from flask import Flask, request, jsonify, Response
import os, json, re
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

BRANDS = [
    "Ourfish Store",
    "Willowcat",
    "Clever Solutions Indonesia",
    "PiOONERVET Indonesia",
    "Golden Paw",
    "Pakewuh",
]

MAX_LINKS = 50

# ═══════════════════════════════════════════════════════════════════════════════
# HTML FRONTEND
# ═══════════════════════════════════════════════════════════════════════════════

HTML = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VT Monitor — Brand Tracker</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #07071a;
  --surface: #0d0d22;
  --card: #111128;
  --card-hover: #151533;
  --border: #1c1c3a;
  --border-light: #252545;
  --brand: #fe2c55;
  --brand-dim: rgba(254,44,85,0.15);
  --brand-glow: rgba(254,44,85,0.35);
  --success: #10b981;
  --success-dim: rgba(16,185,129,0.12);
  --success-border: rgba(16,185,129,0.3);
  --error: #ef4444;
  --error-dim: rgba(239,68,68,0.12);
  --error-border: rgba(239,68,68,0.3);
  --purple: #818cf8;
  --purple-dim: rgba(129,140,248,0.1);
  --purple-border: rgba(129,140,248,0.25);
  --text: #e8e8f0;
  --text-muted: #6b6b8d;
  --text-subtle: #2e2e50;
}

body {
  font-family: 'Inter', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  line-height: 1.5;
}

/* ── HEADER ── */
.header {
  background: linear-gradient(180deg, #0b0b1f 0%, var(--bg) 100%);
  border-bottom: 1px solid var(--border);
  padding: 18px 0 14px;
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(12px);
}

.header-inner {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px;
}

.logo-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
}

.logo-icon {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #fe2c55 0%, #ff7043 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 800;
  color: white;
  box-shadow: 0 0 24px rgba(254,44,85,0.45);
  flex-shrink: 0;
}

.logo-name {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #ffffff 0%, #c7c7e0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-sub {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 400;
  margin-top: 1px;
}

.brand-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  background: var(--brand-dim);
  border: 1px solid rgba(254,44,85,0.22);
  color: #fc8397;
  padding: 3px 11px;
  border-radius: 100px;
  font-size: 0.71rem;
  font-weight: 500;
  letter-spacing: 0.1px;
}

/* ── API WARNING ── */
.api-warning {
  background: rgba(239,68,68,0.08);
  border: 1px solid rgba(239,68,68,0.25);
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 0.82rem;
  color: #fca5a5;
  margin-bottom: 20px;
  display: none;
}

/* ── MAIN ── */
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 28px 24px 60px;
}

/* ── INPUT SECTION ── */
.section-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1.2px;
  margin-bottom: 10px;
}

.input-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px;
  margin-bottom: 16px;
}

textarea {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text);
  font-family: 'Inter', monospace;
  font-size: 0.83rem;
  padding: 14px 16px;
  resize: vertical;
  min-height: 180px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  line-height: 1.7;
}

textarea:focus {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--brand-dim);
}

textarea::placeholder { color: var(--text-subtle); }

.action-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  flex-wrap: wrap;
}

.btn-start {
  background: linear-gradient(135deg, #fe2c55 0%, #ff5533 100%);
  border: none;
  border-radius: 10px;
  color: white;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.88rem;
  font-weight: 700;
  padding: 11px 26px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  box-shadow: 0 4px 18px rgba(254,44,85,0.35);
}

.btn-start:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(254,44,85,0.45);
}

.btn-start:disabled { opacity: 0.55; cursor: not-allowed; transform: none; box-shadow: none; }

.btn-reset {
  background: transparent;
  border: 1px solid var(--border-light);
  border-radius: 10px;
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.82rem;
  padding: 10px 18px;
  transition: all 0.2s;
}
.btn-reset:hover { border-color: #3a3a5c; color: var(--text); }

.link-count {
  margin-left: auto;
  font-size: 0.78rem;
  color: var(--text-muted);
}
.link-count.over { color: var(--error); }

/* ── PROGRESS ── */
.progress-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px 18px;
  margin-bottom: 20px;
  display: none;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.progress-track {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 100px;
  height: 8px;
  overflow: hidden;
}

.progress-fill {
  background: linear-gradient(90deg, #fe2c55, #ff8c55);
  height: 100%;
  border-radius: 100px;
  width: 0%;
  transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
}

/* ── STATS ── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3,1fr);
  gap: 12px;
  margin-bottom: 20px;
  display: none;
}

.stat-box {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 12px;
  text-align: center;
  transition: border-color 0.3s;
}

.stat-num {
  font-size: 1.75rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 5px;
  letter-spacing: -1px;
}

.stat-lbl {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

/* ── RESULTS HEADER ── */
.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  display: none;
}

.btn-export {
  background: transparent;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.75rem;
  padding: 6px 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}
.btn-export:hover { border-color: #3a3a5c; color: var(--text); }

/* ── RESULT CARD ── */
.result-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  margin-bottom: 10px;
  overflow: hidden;
  transition: border-color 0.35s, background 0.35s;
}
.result-card:hover { background: var(--card-hover); }
.result-card.benar { border-color: rgba(16,185,129,0.3); }
.result-card.salah { border-color: rgba(239,68,68,0.3); }

.card-inner {
  display: flex;
  gap: 14px;
  padding: 14px;
  align-items: flex-start;
}

.thumb-wrap {
  width: 62px;
  height: 82px;
  border-radius: 8px;
  background: var(--surface);
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
}
.thumb-wrap img { width: 100%; height: 100%; object-fit: cover; }
.thumb-icon { font-size: 1.4rem; opacity: 0.3; }

.card-body { flex: 1; min-width: 0; }

.card-top {
  display: flex;
  align-items: center;
  gap: 7px;
  flex-wrap: wrap;
  margin-bottom: 5px;
}

.creator { font-size: 0.88rem; font-weight: 700; }

.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 9px;
  border-radius: 100px;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.4px;
}
.badge.benar { background: var(--success-dim); border: 1px solid var(--success-border); color: var(--success); }
.badge.salah { background: var(--error-dim); border: 1px solid var(--error-border); color: var(--error); }
.badge.unknown { background: rgba(100,116,139,0.1); border: 1px solid rgba(100,116,139,0.25); color: #64748b; }
.badge.brand { background: var(--purple-dim); border: 1px solid var(--purple-border); color: var(--purple); font-weight: 600; font-size: 0.7rem; letter-spacing: 0.1px; }

.caption {
  font-size: 0.77rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 7px;
  line-height: 1.4;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 5px;
}

.keranjang-tag {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.73rem;
}
.dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

.alasan { font-size: 0.72rem; color: var(--text-muted); font-style: italic; }

.conf-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 7px;
}
.conf-track {
  flex: 1;
  max-width: 140px;
  height: 4px;
  background: var(--surface);
  border-radius: 100px;
  overflow: hidden;
}
.conf-fill { height: 100%; border-radius: 100px; transition: width 0.6s ease; }
.conf-pct { font-size: 0.7rem; color: var(--text-muted); min-width: 32px; }
.open-link { font-size: 0.72rem; color: var(--text-subtle); text-decoration: none; transition: color 0.2s; margin-left: auto; }
.open-link:hover { color: var(--brand); }

/* ── LOADING CARD ── */
.load-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
}

.skeleton {
  background: linear-gradient(90deg, #14142a 25%, #1c1c38 50%, #14142a 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 6px;
}
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

.spin {
  width: 15px; height: 15px;
  border: 2px solid rgba(254,44,85,0.15);
  border-top-color: var(--brand);
  border-radius: 50%;
  animation: spin .65s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── ERROR CARD ── */
.err-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  font-size: 0.78rem;
}
.err-icon { font-size: 1.1rem; flex-shrink: 0; margin-top: 1px; }
.err-url { color: var(--text-muted); font-size: 0.72rem; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.err-msg { color: var(--error); }

/* ── FOOTER ── */
.footer {
  text-align: center;
  padding: 24px;
  font-size: 0.72rem;
  color: var(--text-subtle);
  border-top: 1px solid var(--border);
}

@media(max-width:600px){
  .header-inner, .container { padding-left: 16px; padding-right: 16px; }
  .stat-num { font-size: 1.4rem; }
  .chip { font-size: 0.65rem; padding: 2px 8px; }
}
</style>
</head>
<body>

<!-- ── HEADER ── -->
<div class="header">
  <div class="header-inner">
    <div class="logo-row">
      <div class="logo-icon">VT</div>
      <div>
        <div class="logo-name">VT Monitor</div>
        <div class="logo-sub">Brand Tracker &mdash; TikTok Creator Monitoring</div>
      </div>
    </div>
    <div class="brand-chips">
      <span class="chip">Ourfish Store</span>
      <span class="chip">Willowcat</span>
      <span class="chip">Clever Solutions Indonesia</span>
      <span class="chip">PiOONERVET Indonesia</span>
      <span class="chip">Golden Paw</span>
      <span class="chip">Pakewuh</span>
    </div>
  </div>
</div>

<!-- ── MAIN ── -->
<div class="container">

  <!-- API Warning -->
  <div class="api-warning" id="api-warning">
    ⚠ API Key belum dikonfigurasi di server. Hubungi administrator.
  </div>

  <!-- Input -->
  <div class="section-label">Input Link VT Kreator</div>
  <div class="input-card">
    <textarea id="url-input"
      placeholder="Paste link TikTok di sini — satu link per baris (maks. 50 link)

Contoh:
https://www.tiktok.com/@kreator1/video/7654397824204918037
https://vt.tiktok.com/ZSxxxxxx/"></textarea>
    <div class="action-row">
      <button class="btn-start" id="start-btn" onclick="startAnalysis()">
        <span id="btn-icon">&#9654;</span>
        <span id="btn-txt">Mulai Analisis</span>
      </button>
      <button class="btn-reset" onclick="resetAll()">Reset</button>
      <div class="link-count" id="link-count">0 / 50 link</div>
    </div>
  </div>

  <!-- Progress -->
  <div class="progress-card" id="progress-card">
    <div class="progress-labels">
      <span id="prog-label">Memulai...</span>
      <span id="prog-count">0 / 0</span>
    </div>
    <div class="progress-track">
      <div class="progress-fill" id="prog-fill"></div>
    </div>
  </div>

  <!-- Stats -->
  <div class="stats-row" id="stats-row">
    <div class="stat-box">
      <div class="stat-num" id="s-total" style="color:var(--text)">0</div>
      <div class="stat-lbl">Total</div>
    </div>
    <div class="stat-box">
      <div class="stat-num" id="s-benar" style="color:var(--success)">0</div>
      <div class="stat-lbl">&#10003; Benar</div>
    </div>
    <div class="stat-box">
      <div class="stat-num" id="s-salah" style="color:var(--error)">0</div>
      <div class="stat-lbl">&#10007; Salah</div>
    </div>
  </div>

  <!-- Results header -->
  <div class="results-header" id="results-header">
    <div class="section-label" style="margin:0">Hasil Analisis</div>
    <button class="btn-export" onclick="exportCSV()">&#8595; Export CSV</button>
  </div>

  <!-- Results list -->
  <div id="results-list"></div>

</div>

<div class="footer">VT Monitor &bull; 6 Brand &bull; Maks. 50 Link per Sesi</div>

<script>
const MAX = 50;
const DELAY_MS = 4500;
let allResults = [], stats = {total:0, benar:0, salah:0}, running = false;

function handleThumbError(el) {
  el.parentElement.innerHTML = '<span class="thumb-icon">&#127916;</span>';
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── On page load: check API status ──
window.addEventListener('DOMContentLoaded', async () => {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    if (!d.api_key_configured) {
      document.getElementById('api-warning').style.display = 'block';
    }
  } catch(e) {}
});

// ── Link counter ──
document.getElementById('url-input').addEventListener('input', function() {
  const n = parseUrls(this.value).length;
  const el = document.getElementById('link-count');
  el.textContent = n + ' / 50 link';
  el.className = 'link-count' + (n > MAX ? ' over' : '');
});

function parseUrls(t) {
  return t.split('\\n').map(u => u.trim()).filter(u => u.startsWith('http'));
}

function esc(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Main ──
async function startAnalysis() {
  if (running) return;
  const raw = document.getElementById('url-input').value.trim();
  if (!raw) { alert('Masukkan minimal 1 link TikTok.'); return; }
  const urls = parseUrls(raw);
  if (!urls.length) { alert('Tidak ada URL valid ditemukan (harus diawali https://).'); return; }
  if (urls.length > MAX) { alert('Maks. ' + MAX + ' link per sesi. Kamu memasukkan ' + urls.length + ' link.'); return; }

  allResults = [];
  stats = {total: urls.length, benar: 0, salah: 0};
  document.getElementById('results-list').innerHTML = '';
  show('progress-card');
  show('stats-row');
  show('results-header');
  updateStats();
  setProgress(0, urls.length);

  running = true;
  document.getElementById('start-btn').disabled = true;
  document.getElementById('btn-icon').textContent = '...';
  document.getElementById('btn-txt').textContent = 'Menganalisis';

  urls.forEach((url, i) => appendPlaceholder(i, url));

  for (let i = 0; i < urls.length; i++) {
    setProgress(i, urls.length, i + 1);
    await processOne(urls[i], i);
    setProgress(i + 1, urls.length);
    if (i < urls.length - 1) {
      document.getElementById('prog-label').textContent = 'Jeda sebentar untuk menghindari limit API...';
      await sleep(DELAY_MS);
    }
  }

  document.getElementById('prog-label').textContent = 'Analisis selesai!';
  document.getElementById('btn-icon').innerHTML = '&#9654;';
  document.getElementById('btn-txt').textContent = 'Mulai Analisis';
  document.getElementById('start-btn').disabled = false;
  running = false;
}

function show(id) { document.getElementById(id).style.display = id === 'stats-row' ? 'grid' : id === 'results-header' ? 'flex' : 'block'; }

function appendPlaceholder(i, url) {
  const el = document.createElement('div');
  el.id = 'card-' + i;
  el.className = 'result-card';
  el.innerHTML =
    '<div class="load-card">' +
    '<div class="skeleton" style="width:62px;height:82px;border-radius:8px;flex-shrink:0;"></div>' +
    '<div style="flex:1;">' +
    '<div class="skeleton" style="height:13px;width:38%;margin-bottom:9px;"></div>' +
    '<div class="skeleton" style="height:10px;width:75%;margin-bottom:6px;"></div>' +
    '<div class="skeleton" style="height:10px;width:55%;margin-bottom:12px;"></div>' +
    '<div style="display:flex;align-items:center;gap:6px;">' +
    '<span class="spin"></span>' +
    '<span id="step-' + i + '" style="font-size:0.73rem;color:#6b6b8d;">Mengambil data video...</span>' +
    '</div></div></div>';
  document.getElementById('results-list').appendChild(el);
}

async function processOne(url, i) {
  // Step 1
  setStep(i, 'Mengambil data dari TikTok...');
  let info;
  try {
    const r = await fetch('/api/fetch', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({url})});
    info = await r.json();
  } catch(e) { renderError(i, url, 'Tidak dapat terhubung ke server.'); return; }
  if (!info.success) { renderError(i, url, info.error || 'Gagal mengambil data video.'); return; }

  // Step 2
  setStep(i, 'Menganalisis dengan AI...');
  let analysis;
  try {
    const r = await fetch('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({caption: info.caption, store_name: info.store_name, product_name: info.product_name, creator: info.creator})
    });
    analysis = await r.json();
  } catch(e) { renderError(i, url, 'Gagal menghubungi AI.'); return; }
  if (!analysis.success) { renderError(i, url, analysis.error || 'Error analisis AI.'); return; }

  const res = analysis.result;
  if (res.status === 'BENAR') stats.benar++;
  else stats.salah++;
  updateStats();

  allResults.push({url, ...info, ...res});
  renderResult(i, url, info, res);
}

function setStep(i, msg) {
  const el = document.getElementById('step-' + i);
  if (el) el.textContent = msg;
}

function renderError(i, url, msg) {
  const card = document.getElementById('card-' + i);
  if (!card) return;
  card.innerHTML =
    '<div class="err-card">' +
    '<span class="err-icon">&#9888;</span>' +
    '<div style="min-width:0;flex:1;">' +
    '<div class="err-url">' + esc(url.slice(0, 80)) + '</div>' +
    '<div class="err-msg">' + esc(msg) + '</div>' +
    '</div></div>';
  stats.salah++;
  updateStats();
  allResults.push({url, status:'ERROR', error:msg});
}

function renderResult(i, url, info, res) {
  const card = document.getElementById('card-' + i);
  if (!card) return;

  const ok = res.status === 'BENAR';
  card.className = 'result-card ' + (ok ? 'benar' : 'salah');

  const conf = Math.max(0, Math.min(100, res.confidence || 0));
  const confColor = conf >= 70 ? 'var(--success)' : conf >= 40 ? '#f59e0b' : 'var(--error)';

  const thumbSrc = info.thumbnail ? ('/api/thumb?url=' + encodeURIComponent(info.thumbnail)) : '';
  const thumbHtml = thumbSrc
    ? '<div class="thumb-wrap"><img src="' + esc(thumbSrc) + '" alt="" onerror="handleThumbError(this)"></div>'
    : '<div class="thumb-wrap"><span class="thumb-icon">&#127916;</span></div>';

  const keranjangHtml = info.store_name
    ? '<span class="dot" style="background:var(--success)"></span><span style="color:var(--success);font-size:0.73rem;">' + esc(info.store_name) + '</span>'
    : '<span class="dot" style="background:var(--text-subtle)"></span><span style="color:var(--text-muted);font-size:0.73rem;">Tidak terdeteksi</span>';

  card.innerHTML =
    '<div class="card-inner">' +
    thumbHtml +
    '<div class="card-body">' +

    '<div class="card-top">' +
    '<span class="creator">@' + esc(info.creator || 'unknown') + '</span>' +
    '<span class="badge ' + (ok ? 'benar' : 'salah') + '">' + (ok ? '&#10003; BENAR' : '&#10007; SALAH') + '</span>' +
    (res.brand_ditemukan ? '<span class="badge brand">' + esc(res.brand_ditemukan) + '</span>' : '') +
    '</div>' +

    '<div class="caption">' + esc((info.caption || '').slice(0, 130)) + '</div>' +

    '<div class="meta-row">' +
    '<div class="keranjang-tag"><span style="font-size:0.68rem;color:var(--text-muted);margin-right:3px;">Keranjang:</span>' + keranjangHtml + '</div>' +
    '</div>' +

    (res.alasan ? '<div class="alasan">' + esc(res.alasan) + '</div>' : '') +

    '<div class="conf-row">' +
    '<div class="conf-track"><div class="conf-fill" style="width:' + conf + '%;background:' + confColor + '"></div></div>' +
    '<span class="conf-pct">' + conf + '%</span>' +
    '<a href="' + esc(url) + '" target="_blank" rel="noopener" class="open-link">&#8599; Buka Video</a>' +
    '</div>' +

    '</div></div>';
}

function setProgress(done, total, current) {
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;
  document.getElementById('prog-fill').style.width = pct + '%';
  document.getElementById('prog-count').textContent = done + ' / ' + total;
  if (current !== undefined) {
    document.getElementById('prog-label').textContent = 'Memproses video ' + current + ' dari ' + total + '...';
  }
}

function updateStats() {
  document.getElementById('s-total').textContent = stats.total;
  document.getElementById('s-benar').textContent = stats.benar;
  document.getElementById('s-salah').textContent = stats.salah;
}

function resetAll() {
  if (running) return;
  document.getElementById('url-input').value = '';
  document.getElementById('link-count').textContent = '0 / 50 link';
  document.getElementById('link-count').className = 'link-count';
  document.getElementById('results-list').innerHTML = '';
  ['progress-card','stats-row','results-header'].forEach(id => {
    document.getElementById(id).style.display = 'none';
  });
  allResults = [];
  stats = {total:0, benar:0, salah:0};
}

function exportCSV() {
  if (!allResults.length) { alert('Belum ada data.'); return; }
  const h = ['URL','Kreator','Caption','Brand Ditemukan','Toko Keranjang Kuning','Status','Confidence (%)','Catatan AI'];
  const rows = allResults.map(r => [r.url, r.creator, r.caption, r.brand_ditemukan, r.store_name, r.status, r.confidence, r.alasan]);
  const csv = '\\uFEFF' + [h, ...rows].map(row => row.map(v => '"' + (v||'').toString().replace(/"/g,'""') + '"').join(',')).join('\\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], {type:'text/csv;charset=utf-8;'}));
  a.download = 'vt-monitor-' + new Date().toISOString().slice(0,10) + '.csv';
  a.click();
}
</script>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════════════════
# TIKTOK SCRAPING
# ═══════════════════════════════════════════════════════════════════════════════

def scrape_tiktok(url: str) -> dict:
    """
    Ambil data video TikTok.
    Urutan: page JSON → yt-dlp → oEmbed
    """
    result = {
        "url": url, "caption": "", "creator": "",
        "thumbnail": "", "store_name": None, "product_name": None,
    }

    # ── 1. Scrape halaman TikTok langsung ──
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.tiktok.com/",
        }
        resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        html = resp.text

        m = re.search(
            r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
            html, re.DOTALL
        )
        if m:
            data = json.loads(m.group(1))
            item = (
                data.get("__DEFAULT_SCOPE__", {})
                    .get("webapp.video-detail", {})
                    .get("itemInfo", {})
                    .get("itemStruct", {})
            )
            if item:
                result["caption"] = item.get("desc", "")
                author = item.get("author", {})
                result["creator"] = author.get("uniqueId", "") or author.get("nickname", "")
                vid = item.get("video", {})
                result["thumbnail"] = (
                    vid.get("originCover") or vid.get("cover") or vid.get("dynamicCover", "")
                )
                # Commerce / keranjang kuning
                products = item.get("commerce", {}).get("commerceProducts", [])
                if products:
                    result["store_name"] = (
                        products[0].get("shopName") or products[0].get("shop_name")
                    )
                    result["product_name"] = (
                        products[0].get("title") or products[0].get("product_title")
                    )
    except Exception:
        pass

    # ── 2. Fallback: yt-dlp ──
    if not result["creator"]:
        try:
            import yt_dlp
            ydl_opts = {
                "quiet": True, "no_warnings": True,
                "skip_download": True, "socket_timeout": 15,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                result["caption"] = info.get("description", "") or info.get("title", "")
                result["creator"] = info.get("uploader", "") or info.get("creator", "")
                result["thumbnail"] = info.get("thumbnail", "")
        except Exception:
            pass

    # ── 3. Last resort: oEmbed ──
    if not result["creator"]:
        try:
            import urllib.parse
            oe = f"https://www.tiktok.com/oembed?url={urllib.parse.quote(url)}"
            r = requests.get(oe, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            d = r.json()
            result["caption"] = d.get("title", "")
            result["creator"] = d.get("author_unique_id", "") or d.get("author_name", "")
            result["thumbnail"] = d.get("thumbnail_url", "")
        except Exception:
            pass

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return HTML


@app.route("/api/status")
def api_status():
    return jsonify({
        "api_key_configured": bool(GEMINI_API_KEY),
        "brands": BRANDS,
        "max_links": MAX_LINKS,
    })


@app.route("/api/thumb")
def proxy_thumb():
    url = request.args.get("url", "")
    if not url:
        return "", 404
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.tiktok.com/"},
            timeout=10,
        )
        return Response(r.content, content_type=r.headers.get("content-type", "image/jpeg"))
    except Exception:
        return "", 404


@app.route("/api/fetch", methods=["POST"])
def fetch_video():
    url = (request.json or {}).get("url", "").strip()
    if not url:
        return jsonify({"success": False, "error": "URL kosong"})
    try:
        info = scrape_tiktok(url)
        if not info["creator"] and not info["caption"]:
            return jsonify({
                "success": False,
                "error": "Tidak dapat mengambil data video (mungkin private, dihapus, atau link tidak valid)",
            })
        return jsonify({"success": True, **info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)[:120]})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    if not GEMINI_API_KEY:
        return jsonify({"success": False, "error": "API Key tidak dikonfigurasi di server"})

    data = request.json or {}
    caption      = data.get("caption", "")
    store_name   = data.get("store_name") or ""
    product_name = data.get("product_name") or ""
    creator      = data.get("creator", "")

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        brand_list = "\n".join(f"{i+1}. {b}" for i, b in enumerate(BRANDS))

        prompt = f"""Kamu adalah sistem monitoring brand untuk agency marketing Indonesia.

6 BRAND YANG DIPANTAU:
{brand_list}

DATA VIDEO TIKTOK:
- Kreator: @{creator}
- Caption/Teks video: {caption[:1500] if caption else "(tidak ada)"}
- Nama produk (keranjang kuning): {product_name or "(tidak terdeteksi)"}
- Nama toko (keranjang kuning): {store_name or "(tidak terdeteksi)"}

ATURAN ANALISIS:
1. Prioritas utama: cek apakah caption/teks video atau nama produk menyebut salah satu dari 6 brand
2. Pencocokan CASE-INSENSITIVE dan FLEKSIBEL — variasi penulisan yang jelas merujuk brand yang sama = cocok
   Contoh: "ourfish" = "Ourfish Store", "golden paw store" = "Golden Paw", "pioonernet" ≈ "PiOONERVET Indonesia"
3. Keranjang kuning (store_name/product_name) sebagai referensi tambahan, bukan penentu utama
4. Jika TIDAK ADA indikasi brand sama sekali → status "SALAH"
5. Jika ragu tapi ada kemungkinan cocok → turunkan confidence, status tetap "BENAR"

Kembalikan HANYA JSON ini (tanpa teks lain):
{{"brand_ditemukan": "nama brand yang paling cocok atau null", "status": "BENAR" atau "SALAH", "confidence": 0-100, "alasan": "penjelasan singkat max 80 karakter"}}"""

        resp = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=200,
            ),
        )

        text = resp.text.strip()
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            text = m.group(0)

        result = json.loads(text)
        return jsonify({"success": True, "result": result})

    except json.JSONDecodeError:
        return jsonify({"success": False, "error": "Respons AI tidak dapat diparsing"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)[:150]})


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\nVT Monitor berjalan di http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
