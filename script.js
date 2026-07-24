/* -------------------------------------------------------------------
   Ferzbow.github.io - AI Logistics Architect Interactive Script
   ------------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initRoleTabs();
  initSlideViewer();
  initModal();
  initStatCounters();
});

/* Navbar scroll effect & smooth navigation */
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  const navLinks = document.querySelectorAll('.nav-links a');

  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar.style.background = 'rgba(11, 15, 25, 0.95)';
      navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.5)';
    } else {
      navbar.style.background = 'rgba(11, 15, 25, 0.85)';
      navbar.style.boxShadow = 'none';
    }

    // Active link highlighting
    let currentSection = '';
    const sections = document.querySelectorAll('section[id]');
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 100;
      if (window.scrollY >= sectionTop) {
        currentSection = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${currentSection}`) {
        link.classList.add('active');
      }
    });
  });
}

/* W1-W4 Role Showcase Filtering */
function initRoleTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  const roleCards = document.querySelectorAll('.role-card');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const filter = tab.getAttribute('data-filter');

      roleCards.forEach(card => {
        if (filter === 'all' || card.getAttribute('data-role') === filter) {
          card.style.display = 'flex';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, 50);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'translateY(10px)';
          setTimeout(() => {
            card.style.display = 'none';
          }, 200);
        }
      });
    });
  });
}

/* BOSS_I Presentation Interactive Slide Viewer */
const slidesData = [
  {
    tag: "Slide 1/6 • 封面",
    title: "Day 20 BOSS_I AI 賦能作品集簡報",
    body: "青年 AI 實戰養成班 • 智慧物流班 | 智慧物流 AI 架構師：Ferzbow。聚焦 W1-W4 四週實踐成果與商業價值論述。"
  },
  {
    tag: "Slide 2/6 • 第一階段總覽",
    title: "從資料到 Agent 的四週能力躍遷",
    body: "跨越 RFM 資料治理(W1)、WMS/TMS 排程瓶頸(W2)、流失預測與機器學習(W3) 到 文本探勘/路徑最佳化與 Agent 控制塔(W4)。"
  },
  {
    tag: "Slide 3/6 • W1-W2 核心發現",
    title: "數據驅動與管理架構的本質",
    body: "『80% 業績來自 20% 客戶』— 精準 RFM 分群驅動營運；『排程的核心是瓶頸而非平均』— 消除物流產線約束。"
  },
  {
    tag: "Slide 4/6 • W3 AI 價值賦能",
    title: "AI 不是替代人，是放大人能做的事",
    body: "透過監督式學習與流失預測模型，將被動客服轉化為主動客戶留存；用 AI 放大供應鏈預測與精準決策能力。"
  },
  {
    tag: "Slide 5/6 • W4 智慧架構師深度論述",
    title: "整合控制塔與 AI Agent 落地實踐",
    body: "整合難在資料治理，Agent 強在執行做而非空想。使用 OR-Tools 與 LLM Agent 打造智慧物流自動化作業鏈。"
  },
  {
    tag: "Slide 6/6 • 未來展望與 W5 題目聲明",
    title: "W5-W8 企業真實難題承接",
    body: "已準備好承接『智慧倉儲庫存與路徑最佳化』與『需求預測與商業決策 Agent』題目，賦能企業供應鏈轉型。"
  }
];

let currentSlideIndex = 0;

function initSlideViewer() {
  const slideTag = document.getElementById('slideTag');
  const slideTitle = document.getElementById('slideTitle');
  const slideBody = document.getElementById('slideBody');
  const slideNum = document.getElementById('slideNum');
  const prevBtn = document.getElementById('prevSlide');
  const nextBtn = document.getElementById('nextSlide');

  if (!slideTitle) return;

  function updateSlide(index) {
    const slide = slidesData[index];
    slideTag.textContent = slide.tag;
    slideTitle.textContent = slide.title;
    slideBody.textContent = slide.body;
    slideNum.textContent = `0${index + 1} / 0${slidesData.length}`;
  }

  prevBtn.addEventListener('click', () => {
    currentSlideIndex = (currentSlideIndex - 1 + slidesData.length) % slidesData.length;
    updateSlide(currentSlideIndex);
  });

  nextBtn.addEventListener('click', () => {
    currentSlideIndex = (currentSlideIndex + 1) % slidesData.length;
    updateSlide(currentSlideIndex);
  });

  updateSlide(0);
}

/* Contact & Collaboration Modal */
function initModal() {
  const modal = document.getElementById('contactModal');
  const openBtns = document.querySelectorAll('.open-modal');
  const closeBtn = document.getElementById('closeModal');

  openBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      modal.classList.add('active');
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      modal.classList.remove('active');
    });
  }

  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.remove('active');
    }
  });
}

/* Stat Counter Animation */
function initStatCounters() {
  const counters = document.querySelectorAll('.metric-val');
  let animated = false;

  window.addEventListener('scroll', () => {
    const heroCard = document.querySelector('.hero-card');
    if (!heroCard) return;

    const cardTop = heroCard.getBoundingClientRect().top;
    if (cardTop < window.innerHeight && !animated) {
      animated = true;
      counters.forEach(counter => {
        const target = +counter.getAttribute('data-target');
        let count = 0;
        const increment = target / 40;

        const updateCount = () => {
          count += increment;
          if (count < target) {
            counter.innerText = Math.ceil(count) + (counter.getAttribute('data-suffix') || '');
            setTimeout(updateCount, 30);
          } else {
            counter.innerText = target + (counter.getAttribute('data-suffix') || '');
          }
        };
        updateCount();
      });
    }
  });
}

/* Copy email function */
function copyToClipboard(text, label) {
  navigator.clipboard.writeText(text).then(() => {
    alert(`已複製 ${label}：${text}`);
  }).catch(err => {
    console.error('複製失敗', err);
  });
}
