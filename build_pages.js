const fs = require('fs');
const path = require('path');

// Shared page template
function makePage(title, subtitle, content, backLink = './') {
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
    :root{--bg:#0a0a0a;--card:#141414;--border:rgba(255,255,255,0.08);--text:#e5e5e5;--muted:#888;--dim:#555;--accent:#38bdf8;--font:'Inter','Noto Sans TC',sans-serif;--mono:'Fira Code',monospace;--radius:12px}
    *{margin:0;padding:0;box-sizing:border-box}
    html{scroll-behavior:smooth}
    body{background:var(--bg);color:var(--text);font-family:var(--font);line-height:1.7;-webkit-font-smoothing:antialiased}
    .top-bar{position:sticky;top:0;z-index:100;background:rgba(10,10,10,0.9);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:0 24px;height:56px;display:flex;align-items:center;gap:16px}
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
  <embed src="./W1/BOOS_I_%E6%95%B8%E6%93%9A%E9%AB%94%E6%AA%A2%E5%A0%B1%E5%91%8A_W1%E6%9C%AC%E5%91%A8%E7%B5%84%7B3%7D.pdf" type="application/pdf" class="pdf-frame">
</div>
<div id="w1-slides" class="tab-panel">
  <embed src="./W1/BOOS_I_%E7%B0%A1%E5%A0%B1_W1%E6%9C%AC%E5%91%A8%E7%B5%84%7B3%7D.pdf" type="application/pdf" class="pdf-frame">
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
const w2Py = readFile('W2/任務09_決策建議.py');

const w2Content = `
<div class="tabs">
  <button class="tab active" data-target="w2-dashboard">📊 供應鏈健診儀表板</button>
  <button class="tab" data-target="w2-code">🐍 決策建議腳本</button>
</div>
<div id="w2-dashboard" class="tab-panel active">
  <embed src="./W2/%E4%BE%9B%E6%87%89%E9%8D%85%E5%81%A5%E8%A8%BA%E5%84%80%E8%A1%A8%E6%9D%BF%20%C2%B7.pdf" type="application/pdf" class="pdf-frame">
</div>
<div id="w2-code" class="tab-panel">
  <div class="code-section">
    <h3><span class="file-icon">🐍</span> 任務09_決策建議.py</h3>
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
  <button class="tab active" data-target="w3-readme">📖 專案說明</button>
  ${w3CodeTabs}
</div>
<div id="w3-readme" class="tab-panel active">
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

console.log('\nAll project pages generated.');
