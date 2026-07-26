/**
 * scripts/i18n.js
 * Modular Internationalization Manager for Ferzbow Portfolio
 */
(function() {
  function getLocales() {
    return window.I18N_LOCALES || {};
  }

  function applyLanguage(lang) {
    var locales = getLocales();
    if (!locales[lang]) lang = 'zh';
    localStorage.setItem('lang', lang);
    var t = locales[lang];

    // Update Language Buttons Active State
    document.querySelectorAll('.lang-btn').forEach(function(b) {
      if (b.getAttribute('data-lang') === lang) b.classList.add('active');
      else b.classList.remove('active');
    });

    // Update Navigation
    var elNavAbout = document.getElementById('nav-about'); if (elNavAbout && t.nav.about) elNavAbout.textContent = t.nav.about;
    var elNavProj  = document.getElementById('nav-projects'); if (elNavProj && t.nav.projects) elNavProj.textContent = t.nav.projects;
    var elNavSkill = document.getElementById('nav-skills'); if (elNavSkill && t.nav.skills) elNavSkill.textContent = t.nav.skills;
    var elNavCont  = document.getElementById('nav-contact'); if (elNavCont && t.nav.contact) elNavCont.textContent = t.nav.contact;

    // Update Theme Toggle Tooltip
    var themeToggle = document.getElementById('theme-toggle');
    if (themeToggle && t.tooltipTheme) themeToggle.setAttribute('data-tooltip', t.tooltipTheme);

    // Update Hero
    var heroTag = document.querySelector('.hero-tag'); if (heroTag && t.hero.tag) heroTag.textContent = t.hero.tag;
    var rolePills = document.querySelectorAll('.role-pill');
    if (rolePills.length >= 3 && t.hero.roles) {
      rolePills[0].textContent = t.hero.roles[0];
      rolePills[1].textContent = t.hero.roles[1];
      rolePills[2].textContent = t.hero.roles[2];
    }
    var heroDark = document.querySelector('.hero-desc .text-dark');
    if (heroDark && t.hero.descDark) heroDark.innerHTML = t.hero.descDark;
    var heroLight = document.querySelector('.hero-desc .text-light');
    if (heroLight && t.hero.descLight) heroLight.innerHTML = t.hero.descLight;
    var isCorrupted = document.documentElement.getAttribute('data-theme') === 'corrupted';
    var isDecoding = window.isDecodingRescue;
    var btnPort = document.getElementById('btn-portfolio');
    var btnCont = document.getElementById('btn-contact');
    var egg = t.easterEgg || { rescueDark: "🌑 沉入黑暗", rescueLight: "☀️ 擁抱光明" };

    var quoteEl = document.querySelector('[data-i18n="corruptedQuote"]');
    if (quoteEl && egg.corruptedQuote) quoteEl.innerHTML = egg.corruptedQuote;

    if (isDecoding) {
      if (window.currentRescueType === 'dark') {
        if (btnPort) {
          btnPort.innerHTML = egg.rescueDark;
          btnPort.className = 'btn-fill btn-rescue-dark chosen-rescue-dark';
        }
        if (btnCont && t.hero.btnContact) btnCont.textContent = t.hero.btnContact;
      } else if (window.currentRescueType === 'light') {
        if (btnCont) {
          btnCont.innerHTML = egg.rescueLight;
          btnCont.className = 'btn-ghost btn-rescue-light chosen-rescue-light';
        }
        if (btnPort && t.hero.btnPortfolio) btnPort.textContent = t.hero.btnPortfolio;
      }
    } else if (isCorrupted) {
      if (btnPort) btnPort.innerHTML = egg.rescueDark;
      if (btnCont) btnCont.innerHTML = egg.rescueLight;
    } else {
      if (btnPort && t.hero.btnPortfolio) btnPort.textContent = t.hero.btnPortfolio;
      if (btnCont && t.hero.btnContact) btnCont.textContent = t.hero.btnContact;
    }

    // Update About
    var aboutLabel = document.querySelector('#about .section-label'); if (aboutLabel && t.about.label) aboutLabel.textContent = t.about.label;
    var aboutTitle = document.querySelector('#about .section-title'); if (aboutTitle && t.about.title) aboutTitle.textContent = t.about.title;
    var aboutP1Dark = document.querySelector('#about .about-text p:nth-of-type(1) .text-dark'); if (aboutP1Dark && t.about.p1Dark) aboutP1Dark.innerHTML = t.about.p1Dark;
    var aboutP1Light = document.querySelector('#about .about-text p:nth-of-type(1) .text-light'); if (aboutP1Light && t.about.p1Light) aboutP1Light.innerHTML = t.about.p1Light;
    var aboutP2Dark = document.querySelector('#about .about-text p:nth-of-type(2) .text-dark'); if (aboutP2Dark && t.about.p2Dark) aboutP2Dark.innerHTML = t.about.p2Dark;
    var aboutP2Light = document.querySelector('#about .about-text p:nth-of-type(2) .text-light'); if (aboutP2Light && t.about.p2Light) aboutP2Light.innerHTML = t.about.p2Light;
    var aboutP3Dark = document.querySelector('#about .about-text p:nth-of-type(3) .text-dark'); if (aboutP3Dark && t.about.p3Dark) aboutP3Dark.innerHTML = t.about.p3Dark;
    var aboutP3Light = document.querySelector('#about .about-text p:nth-of-type(3) .text-light'); if (aboutP3Light && t.about.p3Light) aboutP3Light.innerHTML = t.about.p3Light;

    // Update Stat Boxes
    var statBoxes = document.querySelectorAll('.stat-box');
    if (statBoxes.length >= 4 && t.about.stats) {
      for (var i = 0; i < 4; i++) {
        var n = statBoxes[i].querySelector('.stat-n');
        var l = statBoxes[i].querySelector('.stat-l');
        if (n) n.textContent = t.about.stats[i].num;
        if (l) l.textContent = t.about.stats[i].label;
      }
    }

    // Update Projects
    var projLabel = document.querySelector('#projects .section-label'); if (projLabel && t.projects.label) projLabel.textContent = t.projects.label;
    var projTitle = document.querySelector('#projects .section-title'); if (projTitle && t.projects.title) projTitle.textContent = t.projects.title;
    var projSub = document.querySelector('#projects .section-sub');
    if (projSub && t.projects.sub) {
      var badgeHtml = projSub.querySelector('.hint-badge') ? projSub.querySelector('.hint-badge').outerHTML : '';
      projSub.innerHTML = t.projects.sub + '<br>' + (t.projects.hintBadge ? '<span class="hint-badge">' + t.projects.hintBadge + '</span>' : badgeHtml);
    }

    // Update Project Cards
    var projCards = document.querySelectorAll('.proj-card');
    if (projCards.length >= 6 && t.projects.cards) {
      // 1. Fluxus
      updateCard(projCards[0], t.projects.cards.fluxus);
      // 2. Logistics
      updateCard(projCards[1], t.projects.cards.logistics);
      // 3. Cyber Arena
      updateCard(projCards[2], t.projects.cards.cyberArena);
      // 4. AI Research
      updateCard(projCards[3], t.projects.cards.aiResearch);
      // 5. Web Dev
      updateCard(projCards[4], t.projects.cards.webDev);
      // 6. More Coming
      var c6 = projCards[5];
      if (c6 && t.projects.cards.moreComing) {
        var h3 = c6.querySelector('h3'); if (h3) h3.textContent = t.projects.cards.moreComing.title;
        var p  = c6.querySelector('p');  if (p)  p.innerHTML  = t.projects.cards.moreComing.desc;
        var a  = c6.querySelector('a');  if (a)  a.textContent = t.projects.cards.moreComing.btn;
      }
    }

    // Update Skills Header & Cards
    var skillLabel = document.querySelector('#skills .section-label'); if (skillLabel && t.skills.label) skillLabel.textContent = t.skills.label;
    var skillTitle = document.querySelector('#skills .section-title'); if (skillTitle && t.skills.title) skillTitle.textContent = t.skills.title;
    var skillSub   = document.querySelector('#skills .section-sub');   if (skillSub && t.skills.sub)     skillSub.textContent   = t.skills.sub;

    var skillCards = document.querySelectorAll('.skill-card');
    if (skillCards.length >= 5 && t.skills.items) {
      for (var k = 0; k < 5; k++) {
        var skCard = skillCards[k];
        var itemData = t.skills.items[k];
        if (skCard && itemData) {
          var h4 = skCard.querySelector('h4');
          if (h4 && itemData.title) h4.textContent = itemData.title;
          var lis = skCard.querySelectorAll('ul li');
          if (lis.length > 0 && itemData.list) {
            for (var m = 0; m < lis.length; m++) {
              if (itemData.list[m]) lis[m].textContent = itemData.list[m];
            }
          }
        }
      }
    }

    // Update Contact Header
    var contLabel = document.querySelector('#contact .section-label'); if (contLabel && t.contact.label) contLabel.textContent = t.contact.label;
    var contTitle = document.querySelector('#contact .section-title'); if (contTitle && t.contact.title) contTitle.textContent = t.contact.title;
    var contSub   = document.querySelector('#contact .section-sub');   if (contSub && t.contact.sub)     contSub.textContent   = t.contact.sub;
  }

  function updateCard(card, data) {
    if (!card || !data) return;
    var cat  = card.querySelector('.proj-cat'); if (cat && data.cat) cat.textContent = data.cat;
    var h3   = card.querySelector('h3');       if (h3 && data.title) h3.innerHTML = data.title;
    var p    = card.querySelector('p');        if (p && data.desc) p.textContent = data.desc;
    var link = card.querySelector('.proj-link');if (link && data.btn) link.textContent = data.btn;
  }

  function init() {
    document.querySelectorAll('.lang-btn').forEach(function(b) {
      b.addEventListener('click', function() {
        applyLanguage(b.getAttribute('data-lang'));
      });
    });

    var savedLang = localStorage.getItem('lang') || 'zh';
    applyLanguage(savedLang);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
