const fs = require('fs');
const path = require('path');

// Shared page template
function makePage(title, subtitle, content, backLink = '../') {
  return `<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} | Ferzbow</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Inter:wght@400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root{--bg:#0a0a0a;--card:#141414;--border:rgba(255,255,255,0.15);--text:#ffffff;--muted:#cbd5e1;--dim:#94a3b8;--accent:#38bdf8;--font:'Inter','Noto Sans TC',sans-serif;--mono:'Fira Code',monospace;--radius:12px}
    *{margin:0;padding:0;box-sizing:border-box}
    html{scroll-behavior:smooth}
    body{background:#04040a;color:var(--text);font-family:var(--font);line-height:1.7;-webkit-font-smoothing:antialiased;min-height:100vh;position:relative;overflow-x:hidden}
    body::before{content:'';position:fixed;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle at 20% 20%, rgba(255, 0, 100, 0.8), transparent 40%),radial-gradient(circle at 80% 20%, rgba(0, 240, 255, 0.8), transparent 40%),radial-gradient(circle at 80% 80%, rgba(0, 255, 100, 0.8), transparent 40%),radial-gradient(circle at 20% 80%, rgba(255, 220, 0, 0.8), transparent 40%),radial-gradient(circle at 50% 50%, rgba(200, 0, 255, 0.75), transparent 45%);z-index:-2;pointer-events:none;filter:blur(60px) saturate(250%) brightness(130%);animation:rgbHueRotate 6s linear infinite, rgbSpin 10s ease-in-out infinite alternate}
    body::after{content:'';position:fixed;inset:0;background:radial-gradient(circle at 50% 50%, rgba(0,0,0,0.1), rgba(4,4,10,0.45));z-index:-1;pointer-events:none}
    @keyframes rgbHueRotate{0%{filter:blur(60px) saturate(250%) brightness(130%) hue-rotate(0deg)}100%{filter:blur(60px) saturate(250%) brightness(130%) hue-rotate(360deg)}}
    @keyframes rgbSpin{0%{transform:scale(1) rotate(0deg)}50%{transform:scale(1.2) rotate(180deg)}100%{transform:scale(1) rotate(360deg)}}
    @keyframes rgbFlow{0%{background-position:0% 50%}100%{background-position:300% 50%}}
    .top-bar{position:sticky;top:0;z-index:100;background:rgba(10,10,12,0.85);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:0 24px;height:56px;display:flex;align-items:center;gap:16px}
    .top-bar a{color:var(--accent);text-decoration:none;font-size:0.9rem;font-weight:600}
    .top-bar a:hover{text-decoration:underline}
    .top-bar span{color:var(--dim);font-size:0.85rem}
    .page-header{max-width:960px;margin:0 auto;padding:48px 24px 24px}
    .page-header h1{font-size:1.8rem;font-weight:800;letter-spacing:-0.02em;margin-bottom:8px}
    .page-header p{color:var(--muted);font-size:1rem}
    .content{max-width:960px;margin:0 auto;padding:0 24px 80px}
    /* PDF embed */
    .pdf-frame{width:100%;height:85vh;border:1px solid var(--border);border-radius:var(--radius);background:#111}
    /* Code block */
    .code-section{margin-bottom:32px}
    .code-section h3{font-size:1.1rem;font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:8px}
    .code-section h3 .file-icon{color:var(--accent)}
    pre{background:#111;border:1px solid var(--border);border-radius:var(--radius);padding:24px;overflow-x:auto;font-family:var(--mono);font-size:0.82rem;line-height:1.6;color:#d4d4d4;tab-size:4;white-space:pre}
    /* File list */
    .file-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;margin:24px 0}
    .file-item{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;display:flex;align-items:center;gap:12px;font-size:0.9rem;color:var(--muted);text-decoration:none;transition:all 0.2s}
    .file-item:hover{border-color:var(--accent);color:var(--text);transform:translateY(-2px)}
    .file-item .fi{font-size:1.2rem}
    /* Markdown rendered */
    .md-content{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:32px;font-size:0.92rem;line-height:1.8;color:var(--muted)}
    .md-content h1,.md-content h2,.md-content h3{color:var(--text);margin:24px 0 12px;font-weight:700}
    .md-content h1{font-size:1.5rem;border-bottom:1px solid var(--border);padding-bottom:8px}
    .md-content h2{font-size:1.25rem}
    .md-content h3{font-size:1.05rem}
    .md-content p{margin-bottom:12px}
    .md-content code{background:rgba(56,189,248,0.1);padding:2px 6px;border-radius:4px;font-family:var(--mono);font-size:0.85em;color:var(--accent)}
    .md-content pre{background:#0d0d0d;border:1px solid var(--border);border-radius:8px;padding:16px;overflow-x:auto;margin:12px 0}
    .md-content pre code{background:none;padding:0;color:#d4d4d4}
    .md-content table{width:100%;border-collapse:collapse;margin:16px 0;font-size:0.85rem}
    .md-content th,.md-content td{padding:10px 14px;border:1px solid var(--border);text-align:left}
    .md-content th{background:rgba(255,255,255,0.03);color:var(--text);font-weight:600}
    .md-content blockquote{border-left:3px solid var(--accent);padding:8px 16px;margin:12px 0;color:var(--dim);background:rgba(56,189,248,0.03);border-radius:0 8px 8px 0}
    .md-content ul,.md-content ol{padding-left:24px;margin-bottom:12px}
    .md-content li{margin-bottom:4px}
    .md-content strong{color:var(--text)}
    .tabs{display:flex;gap:4px;margin-bottom:24px;border-bottom:1px solid var(--border);padding-bottom:0}
    .tab{padding:10px 20px;font-size:0.9rem;font-weight:600;color:var(--dim);background:none;border:none;cursor:pointer;border-bottom:2px solid transparent;transition:all 0.2s;font-family:var(--font)}
    .tab:hover{color:var(--muted)}
    .tab.active{color:var(--accent);border-bottom-color:var(--accent)}
    .tab-panel{display:none}
    .tab-panel.active{display:block}
  </style>
</head>
<body>
  <div class="top-bar">
    <a href="${backLink}">← 返回作品集</a>
    <span>/</span>
    <span>${subtitle}</span>
  </div>
  <div class="page-header">
    <h1>${title}</h1>
    <p>${subtitle}</p>
  </div>
  <div class="content">
    ${content}
  </div>
  <script>
    document.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', () => {
        const group = tab.closest('.content') || document;
        group.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        group.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.target).classList.add('active');
      });
    });
  </script>
</body>
</html>`;
}

function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function readFile(p) {
  return fs.readFileSync(path.join(__dirname, p), 'utf8');
}

// Simple markdown to HTML (good enough for display)
function mdToHtml(md) {
  let html = escapeHtml(md);
  // Code blocks
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
  // Tables
  html = html.replace(/^\|(.+)\|\s*\n\|[-| :]+\|\s*\n((?:\|.+\|\s*\n)*)/gm, (match, header, body) => {
    const ths = header.split('|').map(h => `<th>${h.trim()}</th>`).join('');
    const rows = body.trim().split('\n').map(row => {
      const tds = row.replace(/^\||\|$/g,'').split('|').map(c => `<td>${c.trim()}</td>`).join('');
      return `<tr>${tds}</tr>`;
    }).join('');
    return `<table><thead><tr>${ths}</tr></thead><tbody>${rows}</tbody></table>`;
  });
  // Headers
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Blockquotes
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');
  // Lists
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
  // Paragraphs (lines not already tagged)
  html = html.replace(/^(?!<[hupltb]|<\/|$)(.+)$/gm, '<p>$1</p>');
  // Clean up empty paragraphs
  html = html.replace(/<p>\s*<\/p>/g, '');
  return html;
}

// ============ W1 Page ============
const w1Code = readFile('W1/RFM.ipynb');
const w1Notebook = JSON.parse(w1Code);
let notebookHtml = '';
w1Notebook.cells.forEach(cell => {
  if (cell.cell_type === 'markdown') {
    notebookHtml += '<div class="md-content" style="margin-bottom:16px;padding:16px 20px">' + mdToHtml(cell.source.join('')) + '</div>';
  } else if (cell.cell_type === 'code') {
    notebookHtml += '<pre>' + escapeHtml(cell.source.join('')) + '</pre>';
  }
});

const w1Content = `
<div class="tabs">
  <button class="tab active" data-target="w1-report">📊 數據體檢報告</button>
  <button class="tab" data-target="w1-slides">📈 週報簡報</button>
  <button class="tab" data-target="w1-notebook">📓 RFM Notebook</button>
</div>
<div id="w1-report" class="tab-panel active">
  <embed src="./W1/w1_data_report.pdf" type="application/pdf" class="pdf-frame">
</div>
<div id="w1-slides" class="tab-panel">
  <embed src="./W1/w1_slides.pdf" type="application/pdf" class="pdf-frame">
</div>
<div id="w1-notebook" class="tab-panel">
  ${notebookHtml}
</div>`;

fs.writeFileSync('w1.html', makePage(
  'RFM 客戶價值分群與數據體檢',
  'Week 1 · 資料驅動師',
  w1Content
));
console.log('✓ w1.html');

// ============ W2 Page ============
const w2Py = readFile('W2/w2_decision.py');

const w2Content = `
<div class="tabs">
  <button class="tab active" data-target="w2-dashboard">📊 供應鏈健診儀表板</button>
  <button class="tab" data-target="w2-code">🐍 決策建議腳本</button>
</div>
<div id="w2-dashboard" class="tab-panel active">
  <embed src="./W2/w2_dashboard.pdf" type="application/pdf" class="pdf-frame">
</div>
<div id="w2-code" class="tab-panel">
  <div class="code-section">
    <h3><span class="file-icon">🐍</span> w2_decision.py</h3>
    <pre>${escapeHtml(w2Py)}</pre>
  </div>
</div>`;

fs.writeFileSync('w2.html', makePage(
  '供應鏈健診與倉儲路徑最佳化',
  'Week 2 · 管理工程師',
  w2Content
));
console.log('✓ w2.html');

// ============ W3 Page ============
const w3Readme = readFile('W3/精準行銷引擎報告/README.md');
const w3Home = readFile('W3/精準行銷引擎報告/Home.py');
const w3Pages = [
  { name: '1_M1_客戶儀表板.py', label: 'M1 客戶儀表板' },
  { name: '2_M2_流失預警.py', label: 'M2 流失預警' },
  { name: '3_M3_銷量預測.py', label: 'M3 銷量預測' },
  { name: '4_M4_推薦引擎.py', label: 'M4 推薦引擎' },
  { name: '5_M5_一頁建議書.py', label: 'M5 一頁建議書' },
];

let w3CodeTabs = '';
let w3CodePanels = '';

// Home.py tab
w3CodeTabs += '<button class="tab" data-target="w3-home">Home.py</button>';
w3CodePanels += `<div id="w3-home" class="tab-panel"><div class="code-section"><h3><span class="file-icon">🐍</span> Home.py</h3><pre>${escapeHtml(w3Home)}</pre></div></div>`;

w3Pages.forEach((p, i) => {
  const code = readFile('W3/精準行銷引擎報告/pages/' + p.name);
  const id = 'w3-m' + (i+1);
  w3CodeTabs += `<button class="tab" data-target="${id}">${p.label}</button>`;
  w3CodePanels += `<div id="${id}" class="tab-panel"><div class="code-section"><h3><span class="file-icon">🐍</span> ${p.name}</h3><pre>${escapeHtml(code)}</pre></div></div>`;
});

const w3Content = `
<div class="tabs">
  <button class="tab active" data-target="w3-app">🖥️ 互動系統 Demo</button>
  <button class="tab" data-target="w3-slides">📈 NotebookLM 簡報 PDF</button>
  <button class="tab" data-target="w3-readme">📖 專案說明</button>
  ${w3CodeTabs}
</div>

<div id="w3-slides" class="tab-panel">
  <embed src="./Precision_Marketing_Prism.pdf" type="application/pdf" class="pdf-frame">
</div>

<!-- Embedded Interactive Web App -->
<div id="w3-app" class="tab-panel active">
  <div style="background: rgba(20,20,24,0.85); border: 1px solid rgba(56,189,248,0.3); border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
    
    <!-- Sub-navigation -->
    <div style="display: flex; gap: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 14px; margin-bottom: 20px; flex-wrap: wrap;">
      <button class="app-subtab active" onclick="switchSubtab(event, 'sub-home')">🎯 決策總覽</button>
      <button class="app-subtab" onclick="switchSubtab(event, 'sub-m1')">📊 M1 客戶儀表板</button>
      <button class="app-subtab" onclick="switchSubtab(event, 'sub-m2')">⚠️ M2 流失預警</button>
      <button class="app-subtab" onclick="switchSubtab(event, 'sub-m3')">📈 M3 銷量預測</button>
      <button class="app-subtab" onclick="switchSubtab(event, 'sub-m4')">🛒 M4 推薦引擎</button>
      <button class="app-subtab" onclick="switchSubtab(event, 'sub-m5')">📋 M5 一頁建議書</button>
    </div>

    <!-- Subtab 1: Home / 決策總覽 -->
    <div id="sub-home" class="subtab-panel active">
      <div style="background: rgba(56,189,248,0.06); border: 1px solid rgba(56,189,248,0.2); border-radius: 10px; padding: 18px; margin-bottom: 20px;">
        <h3 style="color: #38bdf8; margin-bottom: 12px; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
          🎛️ What-if 模擬器：調整行銷假設，結論與風險即時重算
        </h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-top: 12px;">
          <div>
            <label style="font-size: 0.85rem; color: #aaa; display: flex; justify-content: space-between; margin-bottom: 6px;">
              <span>流失挽留成功率</span>
              <span id="lbl-retention" style="color: #38bdf8; font-weight: 700; font-family: var(--mono);">30%</span>
            </label>
            <input type="range" id="slider-retention" min="0" max="100" value="30" step="5" style="width:100%; accent-color: #38bdf8;" oninput="updateWhatif()">
          </div>
          <div>
            <label style="font-size: 0.85rem; color: #aaa; display: flex; justify-content: space-between; margin-bottom: 6px;">
              <span>VIP 套組轉換率</span>
              <span id="lbl-vip" style="color: #38bdf8; font-weight: 700; font-family: var(--mono);">20%</span>
            </label>
            <input type="range" id="slider-vip" min="0" max="100" value="20" step="5" style="width:100%; accent-color: #38bdf8;" oninput="updateWhatif()">
          </div>
          <div>
            <label style="font-size: 0.85rem; color: #aaa; display: flex; justify-content: space-between; margin-bottom: 6px;">
              <span>沉睡客喚醒率</span>
              <span id="lbl-wake" style="color: #38bdf8; font-weight: 700; font-family: var(--mono);">10%</span>
            </label>
            <input type="range" id="slider-wake" min="0" max="100" value="10" step="5" style="width:100%; accent-color: #38bdf8;" oninput="updateWhatif()">
          </div>
        </div>
      </div>

      <!-- KPI Live Output Banner -->
      <div style="background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); border-radius: 10px; padding: 16px; margin-bottom: 12px; color: #4ade80;">
        📌 <strong>CMO 30 秒結論：聚焦『流失高風險挽留』+『VIP 套組升級』+『沉睡客喚醒』</strong><br>
        預估月度淨增營收 <span id="kpi-total-rev" style="font-size: 1.2rem; font-weight: 800; font-family: var(--mono); color: #86efac;">+64.5 萬</span>（年化約 <span id="kpi-yearly-rev" style="font-weight: 700; color: #86efac;">+774 萬</span>）── 
        挽留 107 位 (<span id="kpi-retain-rev">+25.7 萬</span>) · VIP 354 位 (<span id="kpi-vip-rev">+35.4 萬</span>) · 喚醒 429 位 (<span id="kpi-wake-rev">+3.4 萬</span>)
      </div>

      <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 10px; padding: 16px; margin-bottom: 12px; color: #f87171;">
        ⏳ <strong>什麼都不做，每月損失 −85.6 萬，且會擴大</strong> ── 流失高風險 107 位的月消費一旦流失就全數蒸發（年化約 −1,027 萬）
      </div>
    </div>

    <!-- Subtab 2: M1 客戶儀表板 -->
    <div id="sub-m1" class="subtab-panel">
      <h3 style="margin-bottom: 16px; color: #e5e5e5;">📊 客戶集群分佈概覽 (1,500 人主檔)</h3>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
        <div style="background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 8px; padding: 16px; text-align: center;">
          <span style="font-size: 0.8rem; color: #888;">總客戶數</span>
          <h2 style="color: #38bdf8; font-family: var(--mono); margin-top: 4px;">1,500 人</h2>
        </div>
        <div style="background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 8px; padding: 16px; text-align: center;">
          <span style="font-size: 0.8rem; color: #888;">核心 VIP 客群</span>
          <h2 style="color: #22c55e; font-family: var(--mono); margin-top: 4px;">354 人 (23.6%)</h2>
        </div>
        <div style="background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 8px; padding: 16px; text-align: center;">
          <span style="font-size: 0.8rem; color: #888;">流失高風險客群</span>
          <h2 style="color: #ef4444; font-family: var(--mono); margin-top: 4px;">107 人 (7.1%)</h2>
        </div>
        <div style="background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 8px; padding: 16px; text-align: center;">
          <span style="font-size: 0.8rem; color: #888;">沉睡客群</span>
          <h2 style="color: #f59e0b; font-family: var(--mono); margin-top: 4px;">429 人 (28.6%)</h2>
        </div>
      </div>
    </div>

    <!-- Subtab 3: M2 流失預警 -->
    <div id="sub-m2" class="subtab-panel">
      <h3 style="margin-bottom: 16px; color: #e5e5e5;">⚠️ 流失高風險 TOP 10 名單與建議處方</h3>
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
          <thead>
            <tr style="background: rgba(255,255,255,0.05); text-align: left;">
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">客戶 ID</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">流失機率</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">未購買天數</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">消費金額 (NT$)</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">主要主因</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">建議動作</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border);">C1358</td><td style="padding:10px; color:#ef4444; font-weight:700;">99.5%</td><td style="padding:10px;">364 天</td><td style="padding:10px;">$12,295</td><td style="padding:10px;">長時間沒下單 + 頻次低</td><td style="padding:10px; color:#38bdf8;">VIP 電話挽留 + 折扣券</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border);">C1397</td><td style="padding:10px; color:#ef4444; font-weight:700;">99.5%</td><td style="padding:10px;">360 天</td><td style="padding:10px;">$10,808</td><td style="padding:10px;">長時間沒下單 + 頻次低</td><td style="padding:10px; color:#38bdf8;">VIP 電話挽留 + 折扣券</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border);">C1373</td><td style="padding:10px; color:#ef4444; font-weight:700;">99.5%</td><td style="padding:10px;">360 天</td><td style="padding:10px;">$8,726</td><td style="padding:10px;">長時間沒下單 + 頻次低</td><td style="padding:10px; color:#38bdf8;">VIP 電話挽留 + 折扣券</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border);">C1444</td><td style="padding:10px; color:#ef4444; font-weight:700;">99.5%</td><td style="padding:10px;">357 天</td><td style="padding:10px;">$23,346</td><td style="padding:10px;">長時間沒下單 + 頻次低</td><td style="padding:10px; color:#38bdf8;">VIP 電話挽留 + 折扣券</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border);">C1485</td><td style="padding:10px; color:#ef4444; font-weight:700;">99.5%</td><td style="padding:10px;">354 天</td><td style="padding:10px;">$8,046</td><td style="padding:10px;">長時間沒下單 + 頻次低</td><td style="padding:10px; color:#38bdf8;">VIP 電話挽留 + 折扣券</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Subtab 4: M3 銷量預測 -->
    <div id="sub-m3" class="subtab-panel">
      <h3 style="margin-bottom: 16px; color: #e5e5e5;">📈 Top 5 品項下月需求預測 (Prophet vs Baseline)</h3>
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
          <thead>
            <tr style="background: rgba(255,255,255,0.05); text-align: left;">
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">品名</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">Prophet MAPE</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">Baseline MAPE</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">決策模型</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">採購建議</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border); font-weight:700; color:#38bdf8;">尿布</td><td style="padding:10px;">4.49%</td><td style="padding:10px;">14.54%</td><td style="padding:10px; color:#22c55e;">★ 用 Prophet (領先 10.1pp)</td><td style="padding:10px;">備貨 1,480 ± 164 件</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border); font-weight:700; color:#38bdf8;">啤酒</td><td style="padding:10px;">9.40%</td><td style="padding:10px;">9.32%</td><td style="padding:10px; color:#f59e0b;">用 Baseline</td><td style="padding:10px;">備貨 620 ± 42 件</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border); font-weight:700; color:#38bdf8;">紅酒</td><td style="padding:10px;">6.36%</td><td style="padding:10px;">11.52%</td><td style="padding:10px; color:#22c55e;">★ 用 Prophet (領先 5.2pp)</td><td style="padding:10px;">備貨 863 ± 38 件</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border); font-weight:700; color:#38bdf8;">起司</td><td style="padding:10px;">3.66%</td><td style="padding:10px;">4.33%</td><td style="padding:10px; color:#f59e0b;">用 Baseline</td><td style="padding:10px;">備貨 862 ± 25 件</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border); font-weight:700; color:#38bdf8;">米</td><td style="padding:10px;">15.69%</td><td style="padding:10px;">18.71%</td><td style="padding:10px; color:#22c55e;">★ 用 Prophet (領先 3.0pp)</td><td style="padding:10px;">備貨 800 ± 19 件</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Subtab 5: M4 推薦引擎 -->
    <div id="sub-m4" class="subtab-panel">
      <h3 style="margin-bottom: 16px; color: #e5e5e5;">🛒 購物籃關聯規則 (Apriori Top 5 Rules)</h3>
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
          <thead>
            <tr style="background: rgba(255,255,255,0.05); text-align: left;">
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">先驗商品 (A)</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">後繼商品 (B)</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">支持度 (Support)</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">置信度 (Confidence)</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">提升度 (Lift)</th>
              <th style="padding: 10px; border-bottom: 1px solid var(--border);">建議策略</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border);">尿布</td><td style="padding:10px; color:#22c55e; font-weight:700;">啤酒</td><td style="padding:10px;">14.88%</td><td style="padding:10px;">63.03%</td><td style="padding:10px; color:#38bdf8; font-weight:700;">3.13x</td><td style="padding:10px;">配套販售（經典套組）</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border);">啤酒</td><td style="padding:10px; color:#22c55e; font-weight:700;">尿布</td><td style="padding:10px;">14.88%</td><td style="padding:10px;">73.83%</td><td style="padding:10px; color:#38bdf8; font-weight:700;">3.13x</td><td style="padding:10px;">配套販售（經典套組）</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border);">醬油</td><td style="padding:10px; color:#22c55e; font-weight:700;">米</td><td style="padding:10px;">13.39%</td><td style="padding:10px;">55.04%</td><td style="padding:10px; color:#38bdf8; font-weight:700;">3.04x</td><td style="padding:10px;">配套販售（經典套組）</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border);">米</td><td style="padding:10px; color:#22c55e; font-weight:700;">醬油</td><td style="padding:10px;">13.39%</td><td style="padding:10px;">73.91%</td><td style="padding:10px; color:#38bdf8; font-weight:700;">3.04x</td><td style="padding:10px;">配套販售（經典套組）</td></tr>
            <tr><td style="padding:10px; border-bottom:1px solid var(--border);">紅酒</td><td style="padding:10px; color:#22c55e; font-weight:700;">起司</td><td style="padding:10px;">13.30%</td><td style="padding:10px;">56.14%</td><td style="padding:10px; color:#38bdf8; font-weight:700;">3.01x</td><td style="padding:10px;">配套販售（經典套組）</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Subtab 6: M5 一頁建議書 -->
    <div id="sub-m5" class="subtab-panel">
      <h3 style="margin-bottom: 16px; color: #e5e5e5;">📋 CMO 一頁執行建議書與情境分析</h3>
      <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 8px; padding: 20px; line-height: 1.8;">
        <h4 style="color: #38bdf8; margin-bottom: 10px;">一、核心策略聚焦</h4>
        <p>1. <strong>流失高風險挽留</strong>：針對 107 位 High-Risk 客戶派發專屬回流優惠券，預估挽留 32 人，保護月營收 +25.7 萬元。</p>
        <p>2. <strong>VIP 升級套組</strong>：對 354 位 VIP 推動交叉銷售關聯套裝（如紅酒+起司/啤酒+尿布），預估轉換 +35.4 萬元。</p>
        <p>3. <strong>沉睡客喚醒</strong>：對 429 位 沉睡客自動發送簡訊/EDM 喚醒觸發，預估動員 +3.4 萬元。</p>
      </div>
    </div>

  </div>
</div>

<style>
  .app-subtab {
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  .app-subtab:hover {
    color: var(--text);
    background: rgba(255,255,255,0.1);
  }
  .app-subtab.active {
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
  }
  .subtab-panel {
    display: none;
  }
  .subtab-panel.active {
    display: block;
  }
</style>

<script>
  function switchSubtab(e, id) {
    document.querySelectorAll('.app-subtab').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.subtab-panel').forEach(p => p.classList.remove('active'));
    e.target.classList.add('active');
    document.getElementById(id).classList.add('active');
  }

  function updateWhatif() {
    const ret = parseInt(document.getElementById('slider-retention').value) / 100;
    const vip = parseInt(document.getElementById('slider-vip').value) / 100;
    const wake = parseInt(document.getElementById('slider-wake').value) / 100;

    document.getElementById('lbl-retention').innerText = Math.round(ret * 100) + '%';
    document.getElementById('lbl-vip').innerText = Math.round(vip * 100) + '%';
    document.getElementById('lbl-wake').innerText = Math.round(wake * 100) + '%';

    const revRetain = 107 * 8000 * ret / 10000;
    const revVip = 354 * 5000 * vip / 10000;
    const revWake = 429 * 800 * wake / 10000;
    const revTotal = revRetain + revVip + revWake;

    document.getElementById('kpi-retain-rev').innerText = '+' + revRetain.toFixed(1) + ' 萬';
    document.getElementById('kpi-vip-rev').innerText = '+' + revVip.toFixed(1) + ' 萬';
    document.getElementById('kpi-wake-rev').innerText = '+' + revWake.toFixed(1) + ' 萬';
    document.getElementById('kpi-total-rev').innerText = '+' + revTotal.toFixed(1) + ' 萬';
    document.getElementById('kpi-yearly-rev').innerText = '+' + Math.round(revTotal * 12) + ' 萬';
  }
</script>

<div id="w3-readme" class="tab-panel">
  <div class="md-content">
    ${mdToHtml(w3Readme)}
  </div>
</div>
${w3CodePanels}`;

fs.writeFileSync('w3.html', makePage(
  '精準行銷引擎 — 5 模組 Streamlit App',
  'Week 3 · AI 價值師',
  w3Content
));
console.log('✓ w3.html');

// ============ W4 Page ============
const w4Content = `
<div class="tabs">
  <button class="tab active" data-target="w4-demo">🕹️ 控制塔與 VRP 最佳化 Demo</button>
  <button class="tab" data-target="w4-arch">🏗️ 系統架構說明</button>
</div>

<div id="w4-demo" class="tab-panel active">
  <div style="background: rgba(20,20,24,0.85); border: 1px solid rgba(167,139,250,0.4); border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
    <h3 style="color: #a78bfa; margin-bottom: 12px; font-size: 1.2rem; display: flex; align-items: center; gap: 8px;">
      🤖 OR-Tools 車輛路徑最佳化 (VRP) & LLM Agent 控制塔
    </h3>
    <p style="color: #aaa; font-size: 0.92rem; margin-bottom: 20px;">
      整合 W1 客戶主檔、W2 倉庫瓶頸分析與 W3 需求預測數據，透過 Google OR-Tools 演算法進行動態配送車隊路徑規劃，並結合 LLM Agent 實現自然語言控制塔交互。
    </p>

    <!-- Interactive VRP Metrics Simulation -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
      <div style="background: rgba(167,139,250,0.08); border: 1px solid rgba(167,139,250,0.2); border-radius: 8px; padding: 16px; text-align: center;">
        <span style="font-size: 0.8rem; color: #aaa;">車輛行駛總里程</span>
        <h2 style="color: #a78bfa; font-family: var(--mono); margin-top: 4px;">-18.4%</h2>
        <span style="font-size: 0.75rem; color: #22c55e;">↓ 由 1,420 km 降至 1,158 km</span>
      </div>
      <div style="background: rgba(167,139,250,0.08); border: 1px solid rgba(167,139,250,0.2); border-radius: 8px; padding: 16px; text-align: center;">
        <span style="font-size: 0.8rem; color: #aaa;">車隊出勤數最佳化</span>
        <h2 style="color: #38bdf8; font-family: var(--mono); margin-top: 4px;">12 台 → 10 台</h2>
        <span style="font-size: 0.75rem; color: #22c55e;">↓ 節省 2 台車派遣成本</span>
      </div>
      <div style="background: rgba(167,139,250,0.08); border: 1px solid rgba(167,139,250,0.2); border-radius: 8px; padding: 16px; text-align: center;">
        <span style="font-size: 0.8rem; color: #aaa;">準時達交率 (OTD)</span>
        <h2 style="color: #22c55e; font-family: var(--mono); margin-top: 4px;">98.6%</h2>
        <span style="font-size: 0.75rem; color: #22c55e;">↑ 比基期提升 +13.3%</span>
      </div>
    </div>

    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 10px; padding: 20px;">
      <h4 style="color: #a78bfa; margin-bottom: 12px;">💬 LLM Agent 智慧控制塔對話測試</h4>
      <div style="background: rgba(0,0,0,0.4); border-radius: 8px; padding: 16px; font-family: var(--mono); font-size: 0.88rem; line-height: 1.8; color: #d4d4d4;">
        <p style="color: #38bdf8;"><strong>User:</strong> 今日北部物流中心遇到豪雨告警，請重新最佳化台北五區的配送順序並計算延誤風險。</p>
        <p style="color: #a78bfa; margin-top: 10px;"><strong>Agent:</strong> 正在呼叫 OR-Tools VRP 求解器工具...</p>
        <p style="color: #4ade80; margin-top: 6px;">➔ 成功避開淹水路段！已將車輛 Fleet_03 與 Fleet_07 自動改走高架動線。<br>預估 OTD 降幅控制在 1.2% 以內，整體額外成本 +0 元。</p>
      </div>
    </div>
  </div>
</div>

<div id="w4-arch" class="tab-panel">
  <div class="md-content">
    <h1>W4 端到端智慧物流控制塔架構</h1>
    <p>智慧物流控制塔整合了從前端數據監控到後端最佳化決策的完整閉環：</p>
    <ul>
      <li><strong>數據流</strong>：W1 訂單與客戶主檔 + W2 WMS/TMS 瓶頸分析 + W3 銷量預測需求。</li>
      <li><strong>最佳化引擎</strong>：採用 Google OR-Tools 針對帶容量限制與時間窗的車輛路徑問題（CVRPTW）求解。</li>
      <li><strong>LLM 決策層</strong>：整合 Agent 工具調用能力，能以自然語言指令驅動資源調配與異常處理。</li>
    </ul>
  </div>
</div>`;

fs.writeFileSync('w4.html', makePage(
  '智慧物流控制塔與路徑最佳化',
  'Week 4 · 智慧架構師',
  w4Content
));
console.log('✓ w4.html');

console.log('\nAll project pages generated.');
