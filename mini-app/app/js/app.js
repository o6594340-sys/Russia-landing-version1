/* ═══════════════════════════════════════════
   Деловой форум Пекин 2024 — App Logic
═══════════════════════════════════════════ */

const App = (() => {

  /* ─── ADMIN DATA OVERRIDE ─────────────── */
  function adminData(key, fallback) {
    try {
      const s = localStorage.getItem('admin_' + key);
      return s ? JSON.parse(s) : fallback;
    } catch { return fallback; }
  }

  function getEvent()        { return adminData('event', EVENT); }
  function getDays()         { return adminData('days', DAYS); }
  function getRestaurants()  { return adminData('restaurants', RESTAURANTS); }
  function getBusiness()     { return adminData('business', BUSINESS_SESSIONS); }
  function getHotel()        { return adminData('hotel', HOTEL); }
  function getSights()       { return adminData('sights', SIGHTS); }
  function getCuisine()      { return adminData('cuisine', CUISINE); }
  function getHistory()      { return adminData('history', HISTORY); }

  function getAnnouncement() {
    try {
      const s = localStorage.getItem('admin_announcement');
      return s ? JSON.parse(s) : null;
    } catch { return null; }
  }

  const EMOJI = {
    transfer: '🚌', meal: '🍽', excursion: '🏛', hotel: '🏨',
    business: '💼', dinner: '🍷', gala: '🥂', free: '🛍',
    break: '☕', arrival: '📍', key: '🔑', default: '📌',
  };

  let state = { tab: 'program', programDay: TODAY_INDEX };

  /* ─── BRANDING ───────────────────────── */
  function applyBranding() {
    const ev    = getEvent();
    const brand = ev.brand || {};
    const color = brand.color || '#C9353F';

    // accent colour cascade
    document.documentElement.style.setProperty('--accent', color);
    document.documentElement.style.setProperty('--accent-dark', shadeColor(color, -15));
    document.documentElement.style.setProperty('--accent-light', hexToRgba(color, 0.08));

    // header title + sub
    const titleEl = document.getElementById('header-title');
    const subEl   = document.getElementById('header-sub');
    if (titleEl) titleEl.textContent = ev.title    || titleEl.textContent;
    if (subEl)   subEl.textContent   = ev.dates    ? ev.dates + (ev.location ? ' · ' + ev.location : '') : subEl.textContent;

    // logo
    const logoEl = document.getElementById('header-logo');
    if (logoEl) {
      if (brand.logo) {
        logoEl.src = brand.logo;
        logoEl.classList.remove('hidden');
      } else {
        logoEl.classList.add('hidden');
      }
    }
  }

  function shadeColor(hex, pct) {
    const num = parseInt(hex.replace('#', ''), 16);
    const r = Math.min(255, Math.max(0, (num >> 16) + pct));
    const g = Math.min(255, Math.max(0, ((num >> 8) & 0xff) + pct));
    const b = Math.min(255, Math.max(0, (num & 0xff) + pct));
    return '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');
  }

  function hexToRgba(hex, alpha) {
    const num = parseInt(hex.replace('#', ''), 16);
    return `rgba(${num >> 16},${(num >> 8) & 0xff},${num & 0xff},${alpha})`;
  }

  const FONT_PAIRS = {
    modern:    { disp: 'Poppins',            body: 'Inter',    url: null },
    executive: { disp: 'Playfair Display',   body: 'Inter',    url: 'Playfair+Display:wght@600;700|Inter:wght@400;500;600;700' },
    editorial: { disp: 'Cormorant Garamond', body: 'Jost',     url: 'Cormorant+Garamond:wght@600;700|Jost:wght@400;500;600' },
    friendly:  { disp: 'Plus Jakarta Sans',  body: 'DM Sans',  url: 'Plus+Jakarta+Sans:wght@600;700;800|DM+Sans:wght@400;500;600' },
    tech:      { disp: 'Space Grotesk',      body: 'DM Sans',  url: 'Space+Grotesk:wght@600;700|DM+Sans:wght@400;500;600' },
  };

  function applyTypography() {
    const key  = localStorage.getItem('admin_typography') || 'modern';
    const pair = FONT_PAIRS[key];
    if (!pair || !pair.url) return;
    const lk = document.createElement('link');
    lk.rel  = 'stylesheet';
    lk.href = `https://fonts.googleapis.com/css2?family=${pair.url}&display=swap`;
    document.head.appendChild(lk);
    document.documentElement.style.setProperty('--font',      `'${pair.body}', -apple-system, BlinkMacSystemFont, sans-serif`);
    document.documentElement.style.setProperty('--font-disp', `'${pair.disp}', var(--font)`);
  }

  function applyGradient() {
    const root   = document.documentElement;
    const accent = root.style.getPropertyValue('--accent').trim() || '#C9353F';
    const dark   = shadeColor(accent, -40);
    const darker = shadeColor(accent, -60);
    const light  = shadeColor(accent, +50);
    const recipe = localStorage.getItem('admin_gradient') || 'glow';

    let headerBg, nowBg;
    switch (recipe) {
      case 'diagonal':
        headerBg = `linear-gradient(135deg, ${accent} 0%, ${dark} 100%)`;
        nowBg    = `linear-gradient(135deg, ${accent} 0%, ${dark} 100%)`;
        break;
      case 'vertical':
        headerBg = `linear-gradient(180deg, ${accent} 0%, ${darker} 100%)`;
        nowBg    = `linear-gradient(180deg, ${accent} 0%, ${darker} 100%)`;
        break;
      case 'mesh':
        headerBg = `radial-gradient(ellipse at 20% 50%, ${light} 0%, ${accent} 55%, ${dark} 100%)`;
        nowBg    = `radial-gradient(ellipse at 30% 20%, ${light} 0%, ${accent} 50%, ${dark} 100%)`;
        break;
      case 'flat':
        headerBg = accent;
        nowBg    = accent;
        break;
      default: // glow
        headerBg = accent;
        nowBg    = `linear-gradient(135deg, ${accent} 0%, ${dark} 100%)`;
    }

    root.style.setProperty('--header-bg', headerBg);
    root.style.setProperty('--now-bg',    nowBg);
    root.style.setProperty('--now-shadow', `0 4px 20px ${hexToRgba(accent, 0.35)}`);
  }

  function applyMotion() {
    const style = localStorage.getItem('admin_motion') || 'swift';
    const root  = document.documentElement;
    switch (style) {
      case 'elegant':
        root.style.setProperty('--motion-tab-dur',  '0.4s');
        root.style.setProperty('--motion-tab-ease', 'cubic-bezier(0.16, 1, 0.3, 1)');
        root.style.setProperty('--motion-tab-anim', 'fadeSlideDeep');
        root.style.setProperty('--motion-ui-dur',   '0.3s');
        root.style.setProperty('--motion-ui-ease',  'cubic-bezier(0.16, 1, 0.3, 1)');
        break;
      case 'minimal':
        root.style.setProperty('--motion-tab-dur',  '0.15s');
        root.style.setProperty('--motion-tab-ease', 'ease');
        root.style.setProperty('--motion-tab-anim', 'fadePlain');
        root.style.setProperty('--motion-ui-dur',   '0.1s');
        root.style.setProperty('--motion-ui-ease',  'ease');
        break;
      default: // swift
        root.style.removeProperty('--motion-tab-dur');
        root.style.removeProperty('--motion-tab-ease');
        root.style.removeProperty('--motion-tab-anim');
        root.style.removeProperty('--motion-ui-dur');
        root.style.removeProperty('--motion-ui-ease');
    }
  }

  function applyCardStyle() {
    const style = localStorage.getItem('admin_card_style') || 'elevated';
    document.body.classList.remove('cs-flat', 'cs-glass', 'cs-outlined');
    if (style !== 'elevated') document.body.classList.add('cs-' + style);
  }

  /* ─── INIT ────────────────────────────── */
  function init() {
    applyTypography();
    applyBranding();
    applyGradient();
    applyMotion();
    applyCardStyle();
    renderAnnouncement();
    renderProgram();
  }

  /* ─── ANNOUNCEMENT BANNER ─────────────── */
  function renderAnnouncement() {
    const ann = getAnnouncement();
    let el = document.getElementById('announcement-bar');
    if (!el) {
      el = document.createElement('div');
      el.id = 'announcement-bar';
      document.querySelector('.main-content').prepend(el);
    }
    if (!ann || !ann.text) { el.style.display = 'none'; return; }
    const icons = { info: 'ℹ️', warning: '⚠️', success: '✅' };
    el.className = 'announcement-bar ann-' + ann.type;
    el.innerHTML = `${icons[ann.type] || 'ℹ️'} ${ann.text}`;
    el.style.display = 'block';
  }

  /* ─── TAB SWITCHER ────────────────────── */
  function switchTab(tab, btn) {
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.remove('hidden');
    btn.classList.add('active');
    btn.scrollIntoView({ inline: 'center', behavior: 'smooth' });
    state.tab = tab;

    const renderers = {
      program: renderProgram, transfers: renderTransfers, hotel: renderHotel,
      sights: renderSights, cuisine: renderCuisine, history: renderHistory,
      contacts: renderContacts,
    };
    if (renderers[tab]) renderers[tab]();
  }

  /* ─── TODAY ───────────────────────────── */
  function renderToday() {
    const day   = getDays()[TODAY_INDEX];
    const now   = day.activities.find(a => a.isNow);
    const next  = day.activities.find(a => a.isNext);
    const short = day.date.replace(/,.*$/, '');

    let html = `
      <div class="today-hero" style="background:linear-gradient(135deg,#1a0a0c 0%,#5b1116 35%,${day.color} 70%,#e8a020 100%)">
        <div class="today-eyebrow">${day.label} · ${short}</div>
        <div class="today-name">Добрый день! 👋</div>
        <div class="today-theme">${day.theme}</div>
        <div class="today-live"><span class="live-dot"></span> Программа актуальна</div>
      </div>

      <div class="section-pad">
    `;

    // NOW block
    if (now) {
      html += `
        <div class="now-block">
          <div class="now-label">● СЕЙЧАС</div>
          <div class="now-title">${now.title}</div>
          <div class="now-meta">📍 ${now.location} · ${now.time}</div>
          ${now.note ? `<div class="now-note">${now.note}</div>` : ''}
        </div>
      `;
    }

    // NEXT block
    if (next) {
      html += `
        <div class="next-block">
          <div class="next-label">Следующее</div>
          <div class="next-title">${EMOJI[next.type] || EMOJI.default} ${next.title}</div>
          <div class="next-meta">📍 ${next.location} · ${next.time}</div>
        </div>
      `;
    }

    // WiFi quick access — сразу после NEXT, до таймлайна
    const ev = getEvent();
    html += `
      <div class="wifi-row" onclick="App.copyWifi()">
        <span>📶</span>
        <span class="wifi-net">${ev.wifi.network}</span>
        <span class="wifi-sep">·</span>
        <span class="wifi-pass">${ev.wifi.password}</span>
        <span class="wifi-copy" id="wifi-copied">Скопировано ✓</span>
      </div>
    `;

    // Full day mini-timeline
    html += `<div class="section-title" style="margin-top:24px">Программа дня</div>`;
    html += `<div class="card"><div class="card-body">`;
    day.activities.forEach(a => {
      const active = a.isNow ? 'active' : '';
      html += `
        <div class="mini-timeline-item ${active}">
          <span class="mini-time">${a.time}</span>
          <span class="mini-dot ${active}"></span>
          <div class="mini-info">
            <div class="mini-title">${a.title}</div>
            <div class="mini-loc">📍 ${a.location}</div>
          </div>
        </div>
      `;
    });
    html += `</div></div>`;

    // Practical tip — sessionStorage чтобы не менялся при каждом возврате
    const tipKey = 'today_tip_idx';
    let tipIdx = parseInt(sessionStorage.getItem(tipKey));
    if (isNaN(tipIdx) || tipIdx >= PRACTICAL.length) {
      tipIdx = Math.floor(Math.random() * PRACTICAL.length);
      sessionStorage.setItem(tipKey, tipIdx);
    }
    const tip = PRACTICAL[tipIdx];
    html += `
      <div class="tip-card">
        <div class="tip-icon">${tip.icon}</div>
        <div>
          <div class="tip-title">Совет: ${tip.title}</div>
          <div class="tip-text">${tip.text}</div>
        </div>
      </div>
    `;

    html += `</div>`; // section-pad
    document.getElementById('tab-today').innerHTML = html;
  }

  function copyWifi() {
    navigator.clipboard.writeText(EVENT.wifi.password).catch(() => {});
    const el = document.getElementById('wifi-copied');
    if (el) { el.style.opacity = '1'; setTimeout(() => el.style.opacity = '0', 2000); }
  }

  /* ─── PROGRAM ─────────────────────────── */
  function renderProgram() {
    const container = document.getElementById('tab-program');
    const day = getDays()[state.programDay];

    let tabs = '<div class="day-tabs">';
    getDays().forEach((d, i) => {
      const act = i === state.programDay ? 'active' : '';
      tabs += `<button class="day-tab ${act}" style="${act ? 'background:' + d.color + ';color:white' : ''}"
               onclick="App.selectProgramDay(${i})">${d.label}</button>`;
    });
    tabs += '</div>';

    let items = `<div class="program-meta">${day.date} · ${day.theme}</div>`;
    items += `<div class="card"><div class="card-body">`;
    day.activities.forEach(a => {
      const active = a.isNow ? 'active' : '';
      items += `
        <div class="program-item">
          <span class="program-time" style="color:${day.color}">${a.time}</span>
          <span class="program-dot ${active}" style="${active ? '' : 'background:' + day.color}"></span>
          <div class="program-info">
            <div class="program-title">${a.title}</div>
            <div class="program-loc">📍 ${a.location}</div>
            ${a.note ? `<div class="program-note">${a.note}</div>` : ''}
          </div>
          ${active ? `<span class="now-badge" style="background:${day.color}22;color:${day.color}">Сейчас</span>` : ''}
        </div>
      `;
    });
    items += `</div></div>`;

    // деловая программа для этого дня
    const dayLabel = day.label;
    const trackColors = { A: '#C9353F', B: '#1D4ED8', C: '#047857' };
    const daySessions = getBusiness().filter(s => s.day === dayLabel);
    let businessHtml = '';
    if (daySessions.length) {
      businessHtml += `<div class="section-title" style="margin-top:24px">💼 Деловая программа</div>`;
      daySessions.forEach(s => {
        const tc = s.track ? trackColors[s.track] : '#6B7280';
        businessHtml += `
          <div class="business-card">
            <div class="business-header">
              <div>
                <div class="business-time">${s.time} · ${s.duration}</div>
                <div class="business-title">${s.title}</div>
              </div>
              ${s.track ? `<span class="track-badge" style="background:${tc}22;color:${tc}">Трек ${s.track}</span>` : ''}
            </div>
            <div class="business-meta">🏛 ${s.room}</div>
            <div class="business-desc">${s.desc}</div>
            <div class="speakers-list">
              ${s.speakers.map(sp => `<div class="speaker-item">👤 ${sp}</div>`).join('')}
            </div>
          </div>
        `;
      });
    }

    container.innerHTML = `<div class="section-pad">${tabs}${items}${businessHtml}</div>`;
  }

  function selectProgramDay(i) {
    state.programDay = i;
    renderProgram();
  }

  /* ─── BUSINESS ────────────────────────── */
  function renderBusiness() {
    const container = document.getElementById('tab-business');
    let html = `<div class="section-pad">`;
    html += `<div class="section-title">Деловая программа</div>`;

    const trackColors = { A: '#C9353F', B: '#1D4ED8', C: '#047857' };

    getBusiness().forEach(s => {
      const tc = s.track ? trackColors[s.track] : '#6B7280';
      html += `
        <div class="business-card">
          <div class="business-header">
            <div>
              <div class="business-time">${s.day} · ${s.time}</div>
              <div class="business-title">${s.title}</div>
            </div>
            ${s.track ? `<span class="track-badge" style="background:${tc}22;color:${tc}">Трек ${s.track}</span>` : ''}
          </div>
          <div class="business-meta">
            🏛 ${s.room} &nbsp;·&nbsp; ⏱ ${s.duration}
          </div>
          <div class="business-desc">${s.desc}</div>
          <div class="speakers-list">
            ${s.speakers.map(sp => `<div class="speaker-item">👤 ${sp}</div>`).join('')}
          </div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;
  }

  /* ─── TRANSFERS ─────────────────────── */
  function renderTransfers() {
    const container = document.getElementById('tab-transfers');
    const data = adminData('transfers', TRANSFERS);
    let html = `<div class="section-pad">`;

    data.forEach(day => {
      html += `
        <div class="transfers-day-header">
          <span class="transfers-day-dot" style="background:${day.color}"></span>
          <span class="transfers-day-label" style="color:${day.color}">${day.day}</span>
          <span class="transfers-day-date">${day.date}</span>
        </div>
      `;
      day.routes.forEach(r => {
        html += `
          <div class="transfer-card">
            <div class="transfer-time">${r.time}</div>
            <div class="transfer-body">
              <div class="transfer-title">${r.title}</div>
              <div class="transfer-route">
                <div class="transfer-point"><span class="tr-dot tr-dot-from"></span>${r.from}</div>
                <div class="transfer-line"></div>
                <div class="transfer-point"><span class="tr-dot tr-dot-to" style="background:${day.color}"></span>${r.to}</div>
              </div>
              <div class="transfer-meta">
                <span>${r.vehicle}</span>
                <span>⏱ ${r.duration}</span>
              </div>
              <div class="transfer-meet">🕐 Сбор: ${r.meet}</div>
              ${r.note ? `<div class="transfer-note">⚠️ ${r.note}</div>` : ''}
            </div>
          </div>
        `;
      });
    });

    html += `</div>`;
    container.innerHTML = html;
  }

  /* ─── HOTEL ──────────────────────────── */
  function renderHotel() {
    const h   = getHotel();
    const ev  = getEvent();
    const container = document.getElementById('tab-hotel');

    const stars = '★'.repeat(h.stars || 5);

    const amenityCards = (h.amenities || []).map(a => `
      <div class="hotel-amenity">
        <div class="hotel-amenity-icon">${a.icon}</div>
        <div class="hotel-amenity-title">${a.title}</div>
        <div class="hotel-amenity-note">${a.note}</div>
      </div>
    `).join('');

    const tipRows = (h.tips || []).map(t => `
      <div class="hotel-tip-row">💡 ${t}</div>
    `).join('');

    container.innerHTML = `
      <img class="hotel-photo" src="${h.image}" alt="${h.name}">
      <div class="section-pad">

        <div class="hotel-name-block">
          <div class="hotel-stars">${stars}</div>
          <h2 class="hotel-name">${h.name}</h2>
          <div class="hotel-name-cn">${h.nameCn || ''}</div>
        </div>

        <div class="hotel-quickgrid">
          <div class="hotel-quickitem">
            <div class="hotel-quick-label">Заезд</div>
            <div class="hotel-quick-val">${h.checkin}</div>
          </div>
          <div class="hotel-quickitem">
            <div class="hotel-quick-label">Выезд</div>
            <div class="hotel-quick-val">${h.checkout}</div>
          </div>
          <div class="hotel-quickitem">
            <div class="hotel-quick-label">Метро</div>
            <div class="hotel-quick-val" style="font-size:12px">${(h.metro || '').split('—')[0].trim()}</div>
          </div>
          <div class="hotel-quickitem" onclick="window.location='tel:${h.phone}'" style="cursor:pointer">
            <div class="hotel-quick-label">Телефон</div>
            <div class="hotel-quick-val" style="font-size:12px;color:var(--accent)">${h.phone}</div>
          </div>
        </div>

        <p class="hotel-desc">${h.desc}</p>

        ${h.breakfast ? `
          <div class="hotel-breakfast">
            ☕ <strong>Завтрак:</strong> ${h.breakfast}
          </div>
        ` : ''}

        <div class="section-title" style="margin-bottom:12px">Удобства</div>
        <div class="hotel-amenities-grid">${amenityCards}</div>

        ${tipRows ? `
          <div class="section-title" style="margin-top:24px;margin-bottom:12px">Советы</div>
          <div class="hotel-tips">${tipRows}</div>
        ` : ''}

        <div class="section-title" style="margin-top:24px;margin-bottom:12px">Адрес для такси</div>
        <div class="hotel-address-card">
          <div class="hotel-address-cn">${h.addressCn || ''}</div>
          <div class="hotel-address-en">${h.address || ''}</div>
        </div>

        <div class="section-title" style="margin-top:24px;margin-bottom:12px">📍 Рядом пешком</div>
        ${NEARBY.map(cat => `
          <div class="nearby-category">
            <div class="nearby-cat-title">${cat.emoji} ${cat.category}</div>
            ${cat.places.map(p => `
              <div class="nearby-item">
                <span class="nearby-icon">${p.icon}</span>
                <div class="nearby-info">
                  <div class="nearby-title">${p.title}</div>
                  <div class="nearby-distance">${p.distance}</div>
                  <div class="nearby-note">${p.note}</div>
                </div>
              </div>
            `).join('')}
          </div>
        `).join('')}

      </div>
    `;
  }

  /* ─── SIGHTS ──────────────────────────── */
  function renderSights() {
    const container = document.getElementById('tab-sights');
    let html = `<div class="section-pad">`;
    html += `<div class="section-title">Достопримечательности Пекина</div>`;

    getSights().forEach(s => {
      html += `
        <div class="sight-card">
          <img class="sight-img" src="${s.image}" alt="${s.title}">
          <div class="sight-body">
            <div class="sight-tags">${s.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>
            <h3 class="sight-title">${s.emoji} ${s.title}</h3>
            <div class="sight-sub">${s.sub}</div>
            <p class="sight-desc">${s.desc}</p>
            <div class="sight-meta">
              <div>🕐 ${s.hours}</div>
              <div>📍 ${s.distance}</div>
              <div>🎟 ${s.price}</div>
            </div>
            <div class="sight-tip">💡 ${s.tip}</div>
          </div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;
  }

  /* ─── RESTAURANTS ─────────────────────── */
  function renderRestaurants() {
    const container = document.getElementById('tab-restaurants');
    const program = getRestaurants().filter(r => r.type === 'program');
    const free    = getRestaurants().filter(r => r.type === 'free');

    let html = `<div class="section-pad">`;

    html += `<div class="section-title">По программе</div>`;
    program.forEach(r => html += restaurantCard(r));

    html += `<div class="section-title" style="margin-top:24px">Самостоятельно</div>`;
    free.forEach(r => html += restaurantCard(r));

    html += `</div>`;
    container.innerHTML = html;
  }

  function restaurantCard(r) {
    return `
      <div class="rest-card">
        <img class="rest-img" src="${r.image}" alt="${r.title}">
        <div class="rest-body">
          <div class="rest-header">
            <div>
              <div class="rest-title">${r.emoji} ${r.title}</div>
              <div class="rest-cuisine">${r.cuisine}</div>
            </div>
            <span class="rest-price">${r.price}</span>
          </div>
          <p class="rest-desc">${r.desc}</p>
          <div class="rest-meta">
            <span>🕐 ${r.hours}</span>
            <span>🚇 ${r.metro}</span>
          </div>
          <div class="rest-note ${r.type === 'program' ? 'program' : ''}">${r.note}</div>
        </div>
      </div>
    `;
  }

  /* ─── CUISINE ─────────────────────────── */
  function renderCuisine() {
    const container = document.getElementById('tab-cuisine');
    const must   = getCuisine().filter(c => c.must);
    const others = getCuisine().filter(c => !c.must);

    let html = `<div class="section-pad">`;

    html += `<div class="section-title">Обязательно попробуйте</div>`;
    must.forEach(c => html += cuisineCard(c));

    html += `<div class="section-title" style="margin-top:24px">Стоит попробовать</div>`;
    others.forEach(c => html += cuisineCard(c));

    html += `<div class="section-title" style="margin-top:24px">Этикет за столом</div>`;
    html += `<div class="card"><div class="card-body">`;
    ETIQUETTE.forEach(e => {
      html += `
        <div class="etiquette-row">
          <span class="etiquette-icon">${e.icon}</span>
          <div>
            <div class="etiquette-title">${e.title}</div>
            <div class="etiquette-text">${e.text}</div>
          </div>
        </div>
      `;
    });
    html += `</div></div>`;

    html += `<div class="section-title" style="margin-top:24px">Практические советы</div>`;
    html += `<div class="card"><div class="card-body">`;
    PRACTICAL.forEach(p => {
      html += `
        <div class="etiquette-row">
          <span class="etiquette-icon">${p.icon}</span>
          <div>
            <div class="etiquette-title">${p.title}</div>
            <div class="etiquette-text">${p.text}</div>
          </div>
        </div>
      `;
    });
    html += `</div></div>`;

    html += `</div>`;
    container.innerHTML = html;
  }

  function cuisineCard(c) {
    return `
      <div class="cuisine-card">
        <div class="cuisine-header">
          <span class="cuisine-emoji">${c.emoji}</span>
          <div>
            <div class="cuisine-title">${c.title}</div>
            <div class="cuisine-cn">${c.cn}</div>
          </div>
          ${c.must ? '<span class="must-badge">Маст</span>' : ''}
        </div>
        <p class="cuisine-desc">${c.desc}</p>
        <div class="cuisine-meta">
          <span>📍 ${c.where}</span>
          <span>💰 ${c.price}</span>
        </div>
      </div>
    `;
  }

  /* ─── HISTORY ────────────────────────────*/
  function renderHistory() {
    const container = document.getElementById('tab-history');
    let html = `<div class="section-pad">`;

    getHistory().forEach(section => {
      html += `
        <div class="history-section-header">
          <span class="history-section-emoji">${section.emoji}</span>
          <span class="history-section-title">${section.section}</span>
        </div>
      `;

      section.facts.forEach(fact => {
        html += `
          <div class="fact-card ${fact.wow ? 'wow' : ''}">
            ${fact.wow ? '<div class="fact-wow-badge">🤯 Вот это да!</div>' : ''}
            <div class="fact-title">${fact.title}</div>
            <div class="fact-text">${fact.text}</div>
          </div>
        `;
      });
    });

    html += `</div>`;
    container.innerHTML = html;
  }

  /* ─── CONTACTS ──────────────────────────*/
  function renderContacts() {
    const container = document.getElementById('tab-contacts');
    let html = `<div class="section-pad">`;
    html += `<div class="section-title">Контакты</div>`;

    CONTACTS.forEach(c => {
      html += `
        <div class="contact-card ${c.accent ? 'contact-accent' : ''}">
          <div class="contact-header">
            <span class="contact-emoji">${c.emoji}</span>
            <div class="contact-info">
              <div class="contact-role">${c.role}</div>
              <div class="contact-name">${c.name}</div>
              <div class="contact-note">${c.note}</div>
            </div>
          </div>
          <div class="contact-actions">
            <a class="contact-btn" href="tel:${c.phone}">📞 ${c.phone}</a>
            ${c.telegram ? `<a class="contact-btn contact-btn-tg" href="https://t.me/${c.telegram.replace('@','')}">${c.telegram}</a>` : ''}
          </div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;
  }

  /* ─── FAQ ─────────────────────────────── */
  function openFAQ() {
    renderFAQ(FAQ);
    document.getElementById('modal-faq').classList.add('open');
    setTimeout(() => document.getElementById('faq-search').focus(), 300);
  }

  function closeFAQ() {
    document.getElementById('modal-faq').classList.remove('open');
    document.getElementById('faq-search').value = '';
  }

  function searchFAQ(query) {
    const q = query.toLowerCase().trim();
    const filtered = q ? FAQ.filter(f => f.q.toLowerCase().includes(q) || f.a.toLowerCase().includes(q)) : FAQ;
    renderFAQ(filtered);
  }

  function renderFAQ(items) {
    const list = document.getElementById('faq-list');
    if (!items.length) {
      list.innerHTML = `<div style="text-align:center;padding:32px;color:var(--text-hint)">Ничего не найдено</div>`;
      return;
    }
    list.innerHTML = items.map((f, i) => `
      <div class="faq-item" id="faq-${i}" onclick="App.toggleFAQ(${i})">
        <div class="faq-q">
          <span>${f.q}</span>
          <span class="faq-chevron">›</span>
        </div>
        <div class="faq-a">${f.a}</div>
      </div>
    `).join('');
  }

  function toggleFAQ(i) {
    const el = document.getElementById('faq-' + i);
    if (el) el.classList.toggle('open');
  }

  /* ─── PUBLIC ──────────────────────────── */
  return {
    init, switchTab,
    selectProgramDay,
    copyWifi,
    openFAQ, closeFAQ, searchFAQ, toggleFAQ,
    renderContacts,
  };

})();

document.addEventListener('DOMContentLoaded', App.init);
