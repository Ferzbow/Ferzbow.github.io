/**
 * locales/locales.js
 * Comprehensive 4-Language Dictionary (zh, en, de, it)
 */
window.I18N_LOCALES = {
  zh: {
    meta: { name: "讓我們說中文", flag: "🇹🇼" },
    tooltipTheme: "切換 ☀️/🌙 雙主題（⚠️ 警告：請勿連續快速點擊！）",
    easterEgg: {
      rescueDark: "🌑 沉入黑暗",
      rescueLight: "☀️ 擁抱光明",
      corruptedQuote: "「這裡已經沒有彩蛋了...<br>如你所見，一直在兩種情緒下切換的人，是會壞掉的。」"
    },
    nav: {
      about: "關於我",
      projects: "作品集",
      skills: "技術能力",
      contact: "聯絡"
    },
    hero: {
      tag: "Hi, I'm",
      name: "Ferzbow",
      roles: ["🎮 遊戲開發者", "🤖 AI 工程師", "💻 全端開發者"],
      descDark: "沒什麼，一個路過的遊戲開發者罷了。<br>在深夜用程式碼與咖啡因將混沌腦洞化為現實，打造極致體驗。",
      descLight: "專注於遊戲設計、AI 數據視覺化與現代 Web 架構。<br>以清晰邏輯與精緻 UI 打造優雅的產品與使用者體驗。",
      btnPortfolio: "查看作品集",
      btnContact: "聯絡我"
    },
    about: {
      label: "👤 About Me",
      title: "關於我",
      p1Dark: "我是 <strong>Ferzbow</strong>，一個帶有夜貓屬性的跨領域創作者。遊戲設計讓我學會掌控遊戲規則，AI 讓我學會從資料混沌中捕捉規律，全端開發則是我向世界輸出想法的實態介面。",
      p1Light: "我是 <strong>Ferzbow</strong>，一個專注於優雅體驗的產品開發者。遊戲設計讓我學會說好故事，AI 讓我學會從數據中尋找洞察，全端開發則是我將創意優雅落地的產品載體。",
      p2Dark: "目前正在持續累積作品——包含 <strong>Unity 2D 地牢冒險 Fluxus</strong>、<strong>智慧物流 AI 控制塔</strong> 與各式極客實驗。我相信真正酷的作品不只是技術 Demo，而是帶有靈魂與細節的藝術品。",
      p2Light: "目前正在持續累積作品——包含 <strong>Unity 2D 地牢冒險 Fluxus</strong>、<strong>智慧物流 AI 控制塔</strong> 與各式 Web 應用。我相信好的作品不只是技術展示，而是能兼具美感與實用價值的溝通橋樑。",
      p3Dark: "未來想做什麼？繼續把腦中那些瘋狂的想法實態化。",
      p3Light: "未來想做什麼？繼續打造讓人耳目一新的高品質體驗。",
      stats: [
        { num: "Unity", label: "遊戲引擎開發" },
        { num: "7+", label: "AI 專案產出" },
        { num: "5+", label: "程式語言" },
        { num: "∞", label: "學習中" }
      ]
    },
    projects: {
      label: "🗂️ Works",
      title: "作品集",
      sub: "涵蓋遊戲開發、AI 應用、智慧物流與 Web 開發的多元作品。",
      hintBadge: "✨ 懸停卡片觸發專屬動態特效 · 試試點擊右上角切換 ☀️/🌙",
      cards: {
        fluxus: {
          cat: "🎮 遊戲開發",
          title: "Fluxus — Unity 2D 地牢冒險遊戲",
          desc: "以 Unity 2D 開發的地牢冒險 Prototype，包含完整的物理系統、敵人 AI 與互動機制。已發布至 itch.io，可下載試玩。",
          btn: "🎮 前往 itch.io 頁面 →"
        },
        logistics: {
          cat: "🚚 智慧物流 AI",
          title: "青年 AI 實戰養成班 — 智慧物流四週完整成果",
          desc: "四週密集訓練的完整成果：RFM 客戶分群、供應鏈健診、精準行銷引擎（Streamlit App），到智慧控制塔 + OR-Tools VRP 最佳化。端到端 AI 物流解決方案。",
          btn: "查看物流課程專頁 →"
        },
        cyberArena: {
          cat: "🔫 多人連線遊戲",
          title: "Neon Cyber Arena — 多人連線霓虹射擊大亂鬥",
          desc: "以 Node.js + Socket.io 建置的即時多人連線射擊遊戲，玩家在霓虹賽博龐克競技場中對戰。包含即時同步、玩家房間管理與碰撞偵測系統。",
          btn: "查看原始碼 →"
        },
        aiResearch: {
          cat: "🤖 AI 研究",
          title: "分群大師：K-means 精準行銷 NotebookLM 簡報",
          desc: "以 NotebookLM 整合 K-means 分群與個人化推薦引擎成果，製作成 12 頁精煉簡報《Precision Marketing Prism》，展示 AI 驅動的行銷決策框架。",
          btn: "開啟 PDF →"
        },
        webDev: {
          cat: "💻 Web 開發",
          title: "個人作品集網站 — GitHub Pages 靜態部署",
          desc: "你正在瀏覽的這個網站。以純 HTML/CSS/JS 手刻，包含動態 RGB 背景、玻璃擬態卡片、雙主題切換與微動畫，部署於 GitHub Pages。",
          btn: "查看原始碼 →"
        },
        moreComing: {
          title: "更多作品建置中…",
          desc: "持續在做新東西。<br>敬請期待。",
          btn: "追蹤 GitHub →"
        }
      }
    },
    skills: {
      label: "⚡ Skills",
      title: "技術能力",
      sub: "涵蓋程式語言、機器學習、Web 開發與遊戲引擎的技能組合。",
      items: [
        {
          title: "AI & Data Science",
          list: [
            "Python / Scikit-learn / Pandas / NumPy",
            "K-means 客戶分群 & RFM 分析",
            "Prophet 時序預測 & Apriori 關聯規則",
            "OR-Tools 最佳化引擎",
            "LLM Prompt Engineering / NotebookLM"
          ]
        },
        {
          title: "Web & Software Development",
          list: [
            "JavaScript (ES6+) / Node.js / Express",
            "Socket.io 即時通訊",
            "HTML5 / CSS3 / Vanilla CSS",
            "Streamlit 數據 App 快速開發",
            "RESTful API 設計"
          ]
        },
        {
          title: "遊戲開發 & Unity",
          list: [
            "Unity 2D / 3D 基礎開發",
            "C# 物件導向程式設計",
            "物理引擎、UI Toolkit 與 Shader",
            "程序生成與地牢設計",
            "跨平台建置與發布 (itch.io)"
          ]
        },
        {
          title: "智慧物流 & 運籌",
          list: [
            "OR-Tools 車輛路徑最佳化 (VRP)",
            "WMS 倉儲 & TMS 運輸排程",
            "TOC 約束理論 & 瓶頸排解",
            "供應鏈數據治理與控制塔"
          ]
        },
        {
          title: "開發工具 & 部署",
          list: [
            "Git / GitHub / GitHub Pages",
            "VS Code / Jupyter Notebook",
            "端到端系統架構設計"
          ]
        }
      ]
    },
    contact: {
      label: "📬 Contact",
      title: "聯絡我",
      sub: "有任何合作機會、想法交流或單純想說哈囉，都歡迎聯繫。"
    }
  },

  en: {
    meta: { name: "I speak English", flag: "🇬🇧" },
    tooltipTheme: "Switch ☀️/🌙 themes (⚠️ Warning: Do NOT click repeatedly!)",
    easterEgg: {
      rescueDark: "🌑 Sink into Darkness",
      rescueLight: "☀️ Embrace the Light",
      corruptedQuote: "\"There are no more easter eggs here...<br>As you can see, someone who constantly toggles between two emotions eventually breaks.\""
    },
    nav: {
      about: "About",
      projects: "Works",
      skills: "Skills",
      contact: "Contact"
    },
    hero: {
      tag: "Hi, I'm",
      name: "Ferzbow",
      roles: ["🎮 Game Dev", "🤖 AI Engineer", "💻 Full-Stack Dev"],
      descDark: "Just a passing-by game developer, nothing more.<br>Crafting wild ideas into reality with code & caffeine late at night.",
      descLight: "Focused on game design, AI data visualization, and modern web architecture.<br>Building elegant products & UX with clear logic and refined UI.",
      btnPortfolio: "View Portfolio",
      btnContact: "Contact Me"
    },
    about: {
      label: "👤 About Me",
      title: "About Me",
      p1Dark: "I'm <strong>Ferzbow</strong>, a night-owl cross-disciplinary creator. Game design teaches me control, AI reveals order in chaos, and web dev is my physical interface.",
      p1Light: "I'm <strong>Ferzbow</strong>, a product-focused developer. Game design tells stories, AI extracts insights, and full-stack dev elegantly lands creative products.",
      p2Dark: "Building projects like <strong>Fluxus 2D Dungeon</strong>, <strong>AI Logistics Control Tower</strong>, and geeky experiments. Real craft has a soul in its details.",
      p2Light: "Building projects like <strong>Fluxus 2D Dungeon</strong>, <strong>AI Logistics Control Tower</strong>, and web apps. Good code bridges aesthetics and utility.",
      p3Dark: "What's next? Keep turning crazy ideas into tangible reality.",
      p3Light: "What's next? Keep creating refreshing, top-quality experiences.",
      stats: [
        { num: "Unity", label: "Game Engine Dev" },
        { num: "7+", label: "AI Projects Delivered" },
        { num: "5+", label: "Programming Languages" },
        { num: "∞", label: "Keep Learning" }
      ]
    },
    projects: {
      label: "🗂️ Works",
      title: "Portfolio",
      sub: "A diverse collection spanning game dev, AI applications, logistics, and web development.",
      hintBadge: "✨ Hover cards for dynamic effects · Try switching ☀️/🌙 theme",
      cards: {
        fluxus: {
          cat: "🎮 Game Dev",
          title: "Fluxus — Unity 2D Dungeon Adventure",
          desc: "A prototype dungeon game built in Unity 2D with physics, enemy AI, and interactive mechanics. Published on itch.io for download.",
          btn: "🎮 Play on itch.io →"
        },
        logistics: {
          cat: "🚚 Smart Logistics AI",
          title: "AI Intensive Program — 4-Week Logistics Solutions",
          desc: "End-to-end AI logistics: RFM segmentation, supply chain diagnostics, Streamlit marketing engine, and OR-Tools VRP optimization.",
          btn: "View Logistics Page →"
        },
        cyberArena: {
          cat: "🔫 Multiplayer Game",
          title: "Neon Cyber Arena — Online Multiplayer Shooter",
          desc: "Real-time multiplayer shooter in a cyberpunk neon arena built with Node.js + Socket.io. Features room management & collision sync.",
          btn: "View Source Code →"
        },
        aiResearch: {
          cat: "🤖 AI Research",
          title: "Cluster Master: K-means Marketing Presentation",
          desc: "A 12-page pitch deck 'Precision Marketing Prism' integrating K-means clustering and personalized recommendation frameworks via NotebookLM.",
          btn: "Open PDF →"
        },
        webDev: {
          cat: "💻 Web Dev",
          title: "Personal Portfolio Site — GitHub Pages Deployment",
          desc: "The site you're browsing. Hand-crafted with vanilla HTML/CSS/JS, dynamic RGB backgrounds, glassmorphism, and dual themes.",
          btn: "View Source Code →"
        },
        moreComing: {
          title: "More Coming Soon…",
          desc: "Continuously crafting new projects.<br>Stay tuned.",
          btn: "Follow GitHub →"
        }
      }
    },
    skills: {
      label: "⚡ Skills",
      title: "Technical Skills",
      sub: "A skill set covering programming languages, machine learning, web, and game engines.",
      items: [
        {
          title: "AI & Data Science",
          list: [
            "Python / Scikit-learn / Pandas / NumPy",
            "K-means Customer Segmentation & RFM",
            "Prophet Forecasting & Apriori Rules",
            "OR-Tools Optimization Engine",
            "LLM Prompt Engineering / NotebookLM"
          ]
        },
        {
          title: "Web & Software Development",
          list: [
            "JavaScript (ES6+) / Node.js / Express",
            "Socket.io Real-time Communication",
            "HTML5 / CSS3 / Vanilla CSS",
            "Streamlit Rapid Data App Dev",
            "RESTful API Architecture"
          ]
        },
        {
          title: "Game Dev & Unity",
          list: [
            "Unity 2D / 3D Core Development",
            "C# Object-Oriented Design",
            "Physics, UI Toolkit & Shaders",
            "Procedural Generation & Dungeon Design",
            "Cross-platform Build & itch.io Publish"
          ]
        },
        {
          title: "Smart Logistics & Operations",
          list: [
            "OR-Tools Vehicle Routing (VRP)",
            "WMS Warehousing & TMS Dispatching",
            "TOC Bottleneck Resolution",
            "Supply Chain Control Tower & Data Governance"
          ]
        },
        {
          title: "Dev Tools & Deployment",
          list: [
            "Git / GitHub / GitHub Pages",
            "VS Code / Jupyter Notebook",
            "End-to-End System Architecture"
          ]
        }
      ]
    },
    contact: {
      label: "📬 Contact",
      title: "Get in Touch",
      sub: "Feel free to reach out for collaborations, idea exchanges, or just to say hello."
    }
  },

  de: {
    meta: { name: "Ich spreche ein wenig Deutsch", flag: "🇩🇪" },
    tooltipTheme: "☀️/🌙 Themen wechseln (⚠️ Warnung: Nicht zu schnell klicken!)",
    easterEgg: {
      rescueDark: "🌑 In die Dunkelheit",
      rescueLight: "☀️ Das Licht Umarmen",
      corruptedQuote: "\"Hier gibt es keine Easter Eggs mehr...<br>Wie du siehst: Jemand, der ständig zwischen zwei Emotionen wechselt, geht am Ende kaputt.\""
    },
    nav: {
      about: "Über Mich",
      projects: "Werke",
      skills: "Fähigkeiten",
      contact: "Kontakt"
    },
    hero: {
      tag: "Hallo, ich bin",
      name: "Ferzbow",
      roles: ["🎮 Spieleentwickler", "🤖 KI-Ingenieur", "💻 Full-Stack-Entwickler"],
      descDark: "Nichts weiter als ein vorbeiziehender Spieleentwickler.<br>Wilde Ideen nachts mit Code & Koffein umsetzen.",
      descLight: "Ich spreche ein wenig Deutsch. Konzentriert auf Spieldesign, KI-Datenvisualisierung und elegante Produkte.<br>Klare Logik und raffiniertes UI.",
      btnPortfolio: "Portfolio Ansehen",
      btnContact: "Kontaktieren"
    },
    about: {
      label: "👤 Über Mich",
      title: "Über Mich",
      p1Dark: "Ich bin <strong>Ferzbow</strong>, ein nachtaktiver Entwickler. Spieldesign lehrt mich Regeln, KI bringt Ordnung ins Chaos, Web-Dev ist meine Schnittstelle zur Welt.",
      p1Light: "Ich bin <strong>Ferzbow</strong>, ein produktorientierter Entwickler. Spieldesign erzählt Geschichten, KI bringt Erkenntnisse, Full-Stack bringt Ideen ins Leben.",
      p2Dark: "Projekte wie <strong>Fluxus 2D Dungeon</strong>, <strong>KI-Logistik-Steuerung</strong> und Experimente. Wahres Handwerk zeigt Seele im Detail.",
      p2Light: "Projekte wie <strong>Fluxus 2D Dungeon</strong>, <strong>KI-Logistik-Steuerung</strong> und Web-Apps. Guter Code verbindet Ästhetik und Nutzen.",
      p3Dark: "Was kommt als Nächstes? Verrückte Ideen in die Realität umsetzen.",
      p3Light: "Was kommt als Nächstes? Hochwertige Erlebnisse schaffen.",
      stats: [
        { num: "Unity", label: "Spiele-Engine Entwickler" },
        { num: "7+", label: "KI-Projekte Umgesetzt" },
        { num: "5+", label: "Programmiersprachen" },
        { num: "∞", label: "Ständiges Lernen" }
      ]
    },
    projects: {
      label: "🗂️ Werke",
      title: "Portfolio",
      sub: "Eine vielfältige Sammlung aus Spieleentwicklung, KI-Anwendungen, Logistik und Web.",
      hintBadge: "✨ Effekte beim Hovern · Versuchen Sie den Thema-Wechsel ☀️/🌙",
      cards: {
        fluxus: {
          cat: "🎮 Spieleentwicklung",
          title: "Fluxus — Unity 2D Dungeon-Abenteuer",
          desc: "Ein in Unity 2D entwickelter Prototyp mit Physiksystem, Gegner-KI und Interaktion. Auf itch.io veröffentlicht.",
          btn: "🎮 Auf itch.io Spielen →"
        },
        logistics: {
          cat: "🚚 KI-Logistik",
          title: "Intensivprogramm — 4-Wochen Logistik-KI",
          desc: "End-to-End Logistiklösung: RFM-Segmentierung, Lieferketten-Diagnose, Streamlit-App und OR-Tools VRP-Optimierung.",
          btn: "Logistik-Seite Ansehen →"
        },
        cyberArena: {
          cat: "🔫 Multiplayer-Spiel",
          title: "Neon Cyber Arena — Online Shooter",
          desc: "Echtzeit-Multiplayer-Shooter in einer Cyberpunk-Neon-Arena mit Node.js + Socket.io und Kollisionssynchronisation.",
          btn: "Quellcode Ansehen →"
        },
        aiResearch: {
          cat: "🤖 KI-Forschung",
          title: "Cluster Master: K-means Marketing-Präsentation",
          desc: "12-seitiges Präsentationsdeck 'Precision Marketing Prism' mit K-means-Clustering und Empfehlungssystem via NotebookLM.",
          btn: "PDF Öffnen →"
        },
        webDev: {
          cat: "💻 Web-Entwicklung",
          title: "Persönliches Portfolio — GitHub Pages Deployment",
          desc: "Die Website, die Sie gerade durchsuchen. Mit HTML/CSS/JS, dynamischen RGB-Hintergründen und zwei Themen.",
          btn: "Quellcode Ansehen →"
        },
        moreComing: {
          title: "Weitere Werke Folgen…",
          desc: "Ständig neue Projekte in Arbeit.<br>Bleiben Sie dran.",
          btn: "GitHub Folgen →"
        }
      }
    },
    skills: {
      label: "⚡ Fähigkeiten",
      title: "Technische Fähigkeiten",
      sub: "Programmiersprachen, Maschinelles Lernen, Web-Entwicklung und Game Engines.",
      items: [
        {
          title: "KI & Datenwissenschaft",
          list: [
            "Python / Scikit-learn / Pandas / NumPy",
            "K-means Kundensegmentierung & RFM",
            "Prophet Prognosen & Apriori-Regeln",
            "OR-Tools Optimierungs-Engine",
            "LLM Prompt Engineering / NotebookLM"
          ]
        },
        {
          title: "Web- & Software-Entwicklung",
          list: [
            "JavaScript (ES6+) / Node.js / Express",
            "Socket.io Echtzeitkommunikation",
            "HTML5 / CSS3 / Vanilla CSS",
            "Streamlit Daten-App Entwicklung",
            "RESTful API-Architektur"
          ]
        },
        {
          title: "Spieleentwicklung & Unity",
          list: [
            "Unity 2D / 3D Kernentwicklung",
            "C# Objektorientierte Programmierung",
            "Physik, UI Toolkit & Shader",
            "Prozedurale Generierung & Dungeon-Design",
            "Plattformübergreifender Build & itch.io"
          ]
        },
        {
          title: "Intelligente Logistik & Betrieb",
          list: [
            "OR-Tools Routenoptimierung (VRP)",
            "WMS Lagerhaltung & TMS Disposition",
            "TOC Engpassbeseitigung",
            "Lieferketten-Steuerung & Governance"
          ]
        },
        {
          title: "Entwickler-Tools & Bereitstellung",
          list: [
            "Git / GitHub / GitHub Pages",
            "VS Code / Jupyter Notebook",
            "End-to-End Systemarchitektur"
          ]
        }
      ]
    },
    contact: {
      label: "📬 Kontakt",
      title: "Kontaktieren",
      sub: "Treten Sie gerne für Zusammenarbeiten, Auslandsgespräche oder einen Austausch in Kontakt."
    }
  },

  it: {
    meta: { name: "Sto imparando l'italiano", flag: "🇮🇹" },
    tooltipTheme: "Cambia temi ☀️/🌙 (⚠️ Attenzione: Non cliccare troppo velocemente!)",
    easterEgg: {
      rescueDark: "🌑 Sprofonda nell'Oscurità",
      rescueLight: "☀️ Abbraccia la Luce",
      corruptedQuote: "\"Non ci sono più easter egg qui...<br>Come puoi vedere, chi passa continuamente da un'emozione all'altra finisce per rompersi.\""
    },
    nav: {
      about: "Su di Me",
      projects: "Lavori",
      skills: "Competenze",
      contact: "Contatto"
    },
    hero: {
      tag: "Ciao, sono",
      name: "Ferzbow",
      roles: ["🎮 Sviluppatore Giochi", "🤖 Ingegnere AI", "💻 Sviluppatore Full-Stack"],
      descDark: "Niente di che, solo uno sviluppatore di giochi di passaggio.<br>Trasformo le idee folli in realtà di notte con codice e caffeina.",
      descLight: "Sto imparando l'italiano. Focalizzato sul design di giochi, visualizzazione dati AI e architettura web.<br>Creazione di prodotti eleganti con logica chiara e UI raffinata.",
      btnPortfolio: "Vedi Portfolio",
      btnContact: "Contattami"
    },
    about: {
      label: "👤 Su di Me",
      title: "Su di Me",
      p1Dark: "Sono <strong>Ferzbow</strong>, un creatore notturno multidisciplinare. Il game design mi insegna il controllo, l'AI trova l’ordine nel caos, il web dev è la mia interfaccia.",
      p1Light: "Sono <strong>Ferzbow</strong>, uno sviluppatore orientato ai prodotti. Il game design racconta storie, l'AI estrae intuizioni, il full-stack realizza le idee.",
      p2Dark: "Progetti come <strong>Fluxus 2D Dungeon</strong>, <strong>Torre di Controllo Logistica AI</strong> ed esperimenti. L'artigianato reale ha un'anima nei dettagli.",
      p2Light: "Progetti come <strong>Fluxus 2D Dungeon</strong>, <strong>Torre di Controllo Logistica AI</strong> e app web. Il buon codice unisce estetica e utilità.",
      p3Dark: "Cosa c'est dopo? Continuare a trasformare le idee folli in realtà.",
      p3Light: "Cosa c'est dopo? Continuare a creare esperienze di alta qualità.",
      stats: [
        { num: "Unity", label: "Sviluppo Game Engine" },
        { num: "7+", label: "Progetti AI Realizzati" },
        { num: "5+", label: "Linguaggi di Programmazione" },
        { num: "∞", label: "Apprendimento Continuo" }
      ]
    },
    projects: {
      label: "🗂️ Lavori",
      title: "Portfolio",
      sub: "Una collezione diversificata tra sviluppo giochi, AI, logistica e web.",
      hintBadge: "✨ Passa il mouse per gli effetti · Prova il cambio tema ☀️/🌙",
      cards: {
        fluxus: {
          cat: "🎮 Sviluppo Giochi",
          title: "Fluxus — Avventura Dungeon 2D in Unity",
          desc: "Prototipo di gioco dungeon in Unity 2D con fisica, AI nemici e meccaniche interattive. Pubblicato su itch.io.",
          btn: "🎮 Gioca su itch.io →"
        },
        logistics: {
          cat: "🚚 Logistica AI",
          title: "Programma AI — Soluzioni Logistiche 4 Settimane",
          desc: "Soluzione AI end-to-end: segmentazione RFM, diagnostica supply chain, app Streamlit e ottimizzazione OR-Tools VRP.",
          btn: "Vedi Pagina Logistica →"
        },
        cyberArena: {
          cat: "🔫 Gioco Multiplayer",
          title: "Neon Cyber Arena — Shooter Online",
          desc: "Shooter multiplayer in tempo reale in arena cyberpunk neon realizzato con Node.js + Socket.io e sincronizzazione collisioni.",
          btn: "Vedi Codice Sorgente →"
        },
        aiResearch: {
          cat: "🤖 Ricerca AI",
          title: "Cluster Master: Presentazione Marketing K-means",
          desc: "Presentazione di 12 pagine 'Precision Marketing Prism' con clustering K-means e raccomandazioni via NotebookLM.",
          btn: "Apri PDF →"
        },
        webDev: {
          cat: "💻 Sviluppo Web",
          title: "Portfolio Personale — GitHub Pages",
          desc: "Il sito che stai navigando. Realizzato a mano in HTML/CSS/JS, sfondi RGB dinamici e doppio tema.",
          btn: "Vedi Codice Sorgente →"
        },
        moreComing: {
          title: "Altri Lavori in Arrivo…",
          desc: "In continuo sviluppo di nuovi progetti.<br>Rimani sintonizzato.",
          btn: "Segui GitHub →"
        }
      }
    },
    skills: {
      label: "⚡ Competenze",
      title: "Competenze Tecniche",
      sub: "Linguaggi di programmazione, Machine Learning, Web e Game Engine.",
      items: [
        {
          title: "AI & Scienza dei Dati",
          list: [
            "Python / Scikit-learn / Pandas / NumPy",
            "Segmentazione Clienti K-means & RFM",
            "Previsioni Prophet & Regole Apriori",
            "Engine di Ottimizzazione OR-Tools",
            "LLM Prompt Engineering / NotebookLM"
          ]
        },
        {
          title: "Sviluppo Web e Software",
          list: [
            "JavaScript (ES6+) / Node.js / Express",
            "Comunicazione in Tempo Reale Socket.io",
            "HTML5 / CSS3 / Vanilla CSS",
            "Sviluppo Rapido App Streamlit",
            "Architettura API RESTful"
          ]
        },
        {
          title: "Sviluppo Giochi & Unity",
          list: [
            "Sviluppo Core Unity 2D / 3D",
            "Programmazione C# OOP",
            "Fisica, UI Toolkit & Shader",
            "Generazione Procedurale & Design Dungeon",
            "Build Multipiattaforma & Pubblicazione itch.io"
          ]
        },
        {
          title: "Logistica Intelligente & Operazioni",
          list: [
            "Ottimizzazione Percorsi OR-Tools (VRP)",
            "Gestione Magazzino WMS & Spedizioni TMS",
            "Risoluzione Bottleneck TOC",
            "Torre di Controllo Supply Chain & Data Governance"
          ]
        },
        {
          title: "Strumenti di Sviluppo & Deployment",
          list: [
            "Git / GitHub / GitHub Pages",
            "VS Code / Jupyter Notebook",
            "Architettura di Sistema End-to-End"
          ]
        }
      ]
    },
    contact: {
      label: "📬 Contatto",
      title: "Contattami",
      sub: "Nessun problema a contattarmi per collaborazioni o anche solo per un saluto."
    }
  }
};
