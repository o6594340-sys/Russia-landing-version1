/* ═══════════════════════════════════════════
   Admin Panel Logic
   Пароль: forum2024
   Данные хранятся в localStorage — доступны
   на том же домене в index.html
═══════════════════════════════════════════ */

const Admin = (() => {

  const PASSWORD = 'forum2024';
  const KEYS = {
    event:        'admin_event',
    days:         'admin_days',
    restaurants:  'admin_restaurants',
    announcement: 'admin_announcement',
    business:     'admin_business',
    hotel:        'admin_hotel',
    sights:       'admin_sights',
    cuisine:      'admin_cuisine',
    history:      'admin_history',
    typography:   'admin_typography',
    gradient:     'admin_gradient',
    cardStyle:    'admin_card_style',
    motion:       'admin_motion',
    brandKits:    'admin_brand_kits',
  };

  const MOTION_STYLES = {
    swift:   { icon: '⚡', name: 'Swift',   desc: 'Быстрые функциональные переходы', spec: '0.25s ease' },
    elegant: { icon: '🎬', name: 'Elegant', desc: 'Плавные замедленные переходы',    spec: '0.4s expo-out' },
    minimal: { icon: '○',  name: 'Minimal', desc: 'Только появление, без движения',  spec: '0.15s fade' },
  };

  const CARD_STYLES = {
    elevated: { name: 'Elevated', mood: 'По умолчанию', previewClass: 'p-elevated' },
    flat:     { name: 'Flat',     mood: 'Минимализм',   previewClass: 'p-flat'     },
    glass:    { name: 'Glass',    mood: 'Стекло',       previewClass: 'p-glass'    },
    outlined: { name: 'Outlined', mood: 'Акцент-рамка', previewClass: 'p-outlined' },
  };

  const GRADIENT_RECIPES = {
    glow:     { name: 'Glow',     mood: 'По умолчанию' },
    diagonal: { name: 'Diagonal', mood: 'Диагональ ↗'  },
    vertical: { name: 'Vertical', mood: 'Глубина ↓'    },
    mesh:     { name: 'Mesh',     mood: 'Органичный'   },
    flat:     { name: 'Flat',     mood: 'Минимализм'   },
  };

  function shadeHex(hex, pct) {
    const n = parseInt(hex.replace('#',''), 16);
    const r = Math.min(255, Math.max(0, (n >> 16) + pct));
    const g = Math.min(255, Math.max(0, ((n >> 8) & 0xff) + pct));
    const b = Math.min(255, Math.max(0, (n & 0xff) + pct));
    return '#' + [r,g,b].map(v => v.toString(16).padStart(2,'0')).join('');
  }

  function gradientForRecipe(key, accent) {
    const dark   = shadeHex(accent, -40);
    const darker = shadeHex(accent, -60);
    const light  = shadeHex(accent, +50);
    switch (key) {
      case 'diagonal': return { header: `linear-gradient(135deg, ${accent} 0%, ${dark} 100%)`,   now: `linear-gradient(135deg, ${accent} 0%, ${dark} 100%)` };
      case 'vertical': return { header: `linear-gradient(180deg, ${accent} 0%, ${darker} 100%)`, now: `linear-gradient(180deg, ${accent} 0%, ${darker} 100%)` };
      case 'mesh':     return { header: `radial-gradient(ellipse at 20% 50%, ${light} 0%, ${accent} 55%, ${dark} 100%)`, now: `radial-gradient(ellipse at 30% 20%, ${light} 0%, ${accent} 50%, ${dark} 100%)` };
      case 'flat':     return { header: accent, now: accent };
      default:         return { header: accent, now: `linear-gradient(135deg, ${accent} 0%, ${dark} 100%)` };
    }
  }

  const FONT_PAIRS = {
    modern:    { name: 'Modern',    mood: 'Нейтральный',  dispLabel: 'Poppins',           bodyLabel: 'Inter',    disp: 'Poppins',            body: 'Inter',    url: null },
    executive: { name: 'Executive', mood: 'Люкс · банки', dispLabel: 'Playfair Display',  bodyLabel: 'Inter',    disp: 'Playfair Display',   body: 'Inter',    url: 'Playfair+Display:wght@600;700|Inter:wght@400;500;600;700' },
    editorial: { name: 'Editorial', mood: 'Премиум',      dispLabel: 'Cormorant',         bodyLabel: 'Jost',     disp: 'Cormorant Garamond', body: 'Jost',     url: 'Cormorant+Garamond:wght@600;700|Jost:wght@400;500;600' },
    friendly:  { name: 'Friendly',  mood: 'Тепло · MICE', dispLabel: 'Jakarta Sans',      bodyLabel: 'DM Sans',  disp: 'Plus Jakarta Sans',  body: 'DM Sans',  url: 'Plus+Jakarta+Sans:wght@600;700;800|DM+Sans:wght@400;500;600' },
    tech:      { name: 'Tech',      mood: 'IT-компании',  dispLabel: 'Space Grotesk',     bodyLabel: 'DM Sans',  disp: 'Space Grotesk',      body: 'DM Sans',  url: 'Space+Grotesk:wght@600;700|DM+Sans:wght@400;500;600' },
  };

  let state = {
    section:        'announcement',
    programDay:     0,
    historySection: 0,
    days:           null,
    restaurants:    null,
    event:          null,
    business:       null,
    hotel:          null,
    sights:         null,
    cuisine:        null,
    history:        null,
  };

  /* ─── AUTH ────────────────────────────── */
  function login() {
    const val = document.getElementById('auth-input').value;
    if (val === PASSWORD) {
      document.getElementById('auth-screen').classList.add('hidden');
      document.getElementById('admin-panel').classList.remove('hidden');
      loadAll();
      showSection('announcement', document.querySelector('.nav-btn'));
    } else {
      document.getElementById('auth-error').classList.remove('hidden');
      document.getElementById('auth-input').value = '';
    }
  }

  function logout() {
    document.getElementById('auth-screen').classList.remove('hidden');
    document.getElementById('admin-panel').classList.add('hidden');
    document.getElementById('auth-input').value = '';
  }

  /* ─── LOAD DATA ───────────────────────── */
  function loadAll() {
    state.days        = getStored(KEYS.days)        || JSON.parse(JSON.stringify(DAYS));
    state.restaurants = getStored(KEYS.restaurants) || JSON.parse(JSON.stringify(RESTAURANTS));
    state.event       = getStored(KEYS.event)       || JSON.parse(JSON.stringify(EVENT));
    state.business    = getStored(KEYS.business)    || JSON.parse(JSON.stringify(BUSINESS_SESSIONS));
    state.hotel       = getStored(KEYS.hotel)       || JSON.parse(JSON.stringify(HOTEL));
    state.sights      = getStored(KEYS.sights)      || JSON.parse(JSON.stringify(SIGHTS));
    state.cuisine     = getStored(KEYS.cuisine)     || JSON.parse(JSON.stringify(CUISINE));
    state.history     = getStored(KEYS.history)     || JSON.parse(JSON.stringify(HISTORY));
    loadAnnouncementPreview();
    loadSettingsForm();
  }

  function getStored(key) {
    try { const s = localStorage.getItem(key); return s ? JSON.parse(s) : null; } catch { return null; }
  }

  function save(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
  }

  /* ─── NAVIGATION ──────────────────────── */
  function showSection(name, btn) {
    document.querySelectorAll('.admin-section').forEach(s => s.classList.add('hidden'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('section-' + name).classList.remove('hidden');
    if (btn) btn.classList.add('active');
    state.section = name;

    if (name === 'program')     renderProgramSection();
    if (name === 'templates')   renderTemplatesSection();
    if (name === 'business')    renderBusinessSection();
    if (name === 'hotel')       renderHotelSection();
    if (name === 'sights')      renderSightsSection();
    if (name === 'restaurants') renderRestaurantsSection();
    if (name === 'cuisine')     renderCuisineSection();
    if (name === 'history')     renderHistorySection();
    if (name === 'brandkits')   renderBrandKitsSection();
  }

  /* ─── TEMPLATES ──────────────────────── */
  function renderTemplatesSection() {
    const activeKey = localStorage.getItem('admin_template') || '';
    const grid = document.getElementById('template-grid');

    grid.innerHTML = Object.entries(TEMPLATES).map(([key, tpl]) => {
      const active = key === activeKey;
      return `
        <div class="template-card ${active ? 'active' : ''}" onclick="Admin.applyTemplate('${key}')"
          style="${active ? '--tpl-color:' + tpl.meta.color : ''}">
          <div class="template-flag">${tpl.meta.flag}</div>
          <div class="template-name">${tpl.meta.name}</div>
          <div class="template-desc">${tpl.meta.desc}</div>
          <div class="template-bar" style="background:${tpl.meta.color}"></div>
          ${active ? '<div class="template-badge">✓ Активен</div>' : ''}
        </div>
      `;
    }).join('');

    const activeInfo = document.getElementById('template-active');
    if (activeKey && TEMPLATES[activeKey]) {
      const tpl = TEMPLATES[activeKey];
      activeInfo.innerHTML = `
        <div class="template-hint">
          Сейчас загружен: <strong>${tpl.meta.flag} ${tpl.meta.name}</strong>.
          Чтобы сменить направление — нажмите на другую карточку.
        </div>
      `;
    } else {
      activeInfo.innerHTML = `<div class="template-hint">Шаблон не выбран. Нажмите на страну, чтобы загрузить данные.</div>`;
    }
  }

  function applyTemplate(key) {
    const tpl = TEMPLATES[key];
    if (!tpl) return;
    const current = localStorage.getItem('admin_template') || '';
    if (current === key) return;

    if (!confirm(`Загрузить шаблон «${tpl.meta.flag} ${tpl.meta.name}»?\n\nЭто перезапишет: историю, кухню, достопримечательности, рестораны и отель.\nПрограмма мероприятия и расписание останутся без изменений.`)) return;

    // Beijing reuses existing data.js constants
    const hotel       = tpl.hotel       || JSON.parse(JSON.stringify(HOTEL));
    const sights      = tpl.sights      || JSON.parse(JSON.stringify(SIGHTS));
    const restaurants = tpl.restaurants || JSON.parse(JSON.stringify(RESTAURANTS));
    const cuisine     = tpl.cuisine     || JSON.parse(JSON.stringify(CUISINE));
    const history     = tpl.history     || JSON.parse(JSON.stringify(HISTORY));

    // patch event: update location + brand, keep title/dates/wifi/organizer/emergency
    const currentEvent = getStored(KEYS.event) || JSON.parse(JSON.stringify(EVENT));
    const patchedEvent = {
      ...currentEvent,
      location: tpl.event.location,
      subtitle: tpl.event.subtitle,
      brand:    tpl.event.brand,
    };

    save(KEYS.event,       patchedEvent);
    save(KEYS.hotel,       hotel);
    save(KEYS.sights,      sights);
    save(KEYS.restaurants, restaurants);
    save(KEYS.cuisine,     cuisine);
    save(KEYS.history,     history);
    localStorage.setItem('admin_template', key);

    // reload state
    state.event       = patchedEvent;
    state.hotel       = hotel;
    state.sights      = sights;
    state.restaurants = restaurants;
    state.cuisine     = cuisine;
    state.history     = history;

    renderTemplatesSection();
    showToast(`${tpl.meta.flag} Шаблон «${tpl.meta.name}» загружен`);
  }

  /* ─── ANNOUNCEMENT ────────────────────── */
  function saveAnnouncement() {
    const text = document.getElementById('announcement-text').value.trim();
    const type = document.getElementById('announcement-type').value;
    if (!text) { clearAnnouncement(); return; }
    const data = { text, type, date: new Date().toLocaleString('ru') };
    save(KEYS.announcement, data);
    loadAnnouncementPreview();
    showToast('Объявление опубликовано');
  }

  function clearAnnouncement() {
    localStorage.removeItem(KEYS.announcement);
    document.getElementById('announcement-text').value = '';
    loadAnnouncementPreview();
    showToast('Объявление убрано');
  }

  function loadAnnouncementPreview() {
    const stored = getStored(KEYS.announcement);
    const box = document.getElementById('announcement-preview');
    if (stored) {
      const icons = { info: 'ℹ️', warning: '⚠️', success: '✅' };
      box.innerHTML = `
        <div class="preview-label">Сейчас показывается участникам:</div>
        <div class="announcement-banner ${stored.type}">
          ${icons[stored.type] || 'ℹ️'} ${stored.text}
          <div class="ann-date">Опубликовано: ${stored.date}</div>
        </div>
      `;
      document.getElementById('announcement-text').value = stored.text;
      document.getElementById('announcement-type').value = stored.type;
    } else {
      box.innerHTML = `<div class="preview-empty">Объявление не активно</div>`;
    }
  }

  /* ─── SETTINGS ────────────────────────── */
  function loadSettingsForm() {
    const e     = state.event;
    const brand = e.brand || {};
    const color = brand.color || '#C9353F';

    document.getElementById('s-brand-color').value     = color;
    document.getElementById('s-brand-color-hex').value = color;
    document.getElementById('s-brand-logo').value      = brand.logo || '';
    document.getElementById('s-title').value           = e.title             || '';
    document.getElementById('s-dates').value           = e.dates             || '';
    document.getElementById('s-location').value        = e.location          || '';
    document.getElementById('s-org-name').value        = e.organizer?.name   || '';
    document.getElementById('s-org-tg').value          = e.organizer?.telegram || '';
    document.getElementById('s-wifi-net').value        = e.wifi?.network     || '';
    document.getElementById('s-wifi-pass').value       = e.wifi?.password    || '';
    document.getElementById('s-hotel-name').value      = e.hotel?.name       || '';
    document.getElementById('s-hotel-phone').value     = e.hotel?.phone      || '';
    document.getElementById('s-emergency').value       = e.emergency         || '';
    renderMotionGrid();
    renderCardStyleGrid();
    renderGradientGrid();
    renderTypoGrid();
    updateBrandPreview();
  }

  function renderMotionGrid() {
    const grid = document.getElementById('motion-grid');
    if (!grid) return;
    const current = localStorage.getItem(KEYS.motion) || 'swift';

    grid.innerHTML = Object.entries(MOTION_STYLES).map(([key, m]) => {
      const active = key === current;
      return `
        <div class="motion-card ${active ? 'active' : ''}" onclick="Admin.selectMotion('${key}')">
          ${active ? '<div class="motion-card-check">✓</div>' : ''}
          <div class="motion-card-icon">${m.icon}</div>
          <div class="motion-card-name">${m.name}</div>
          <div class="motion-card-desc">${m.desc}</div>
          <div class="motion-card-spec">${m.spec}</div>
        </div>`;
    }).join('');
  }

  function selectMotion(key) {
    if (!MOTION_STYLES[key]) return;
    localStorage.setItem(KEYS.motion, key);
    renderMotionGrid();
  }

  function renderCardStyleGrid() {
    const grid = document.getElementById('cardstyle-grid');
    if (!grid) return;
    const current = localStorage.getItem(KEYS.cardStyle) || 'elevated';

    grid.innerHTML = Object.entries(CARD_STYLES).map(([key, s]) => {
      const active = key === current;
      return `
        <div class="cardstyle-card ${active ? 'active' : ''}" onclick="Admin.selectCardStyle('${key}')">
          ${active ? '<div class="cardstyle-check">✓</div>' : ''}
          <div class="cardstyle-preview ${s.previewClass}">Программа</div>
          <div class="cardstyle-name">${s.name}</div>
          <div class="cardstyle-mood">${s.mood}</div>
        </div>`;
    }).join('');
  }

  function selectCardStyle(key) {
    if (!CARD_STYLES[key]) return;
    localStorage.setItem(KEYS.cardStyle, key);
    renderCardStyleGrid();
  }

  function renderGradientGrid() {
    const grid = document.getElementById('gradient-grid');
    if (!grid) return;
    const current = localStorage.getItem(KEYS.gradient) || 'glow';
    const accent  = state.event?.brand?.color || '#C9353F';

    grid.innerHTML = Object.entries(GRADIENT_RECIPES).map(([key, r]) => {
      const active = key === current;
      const grad   = gradientForRecipe(key, accent);
      return `
        <div class="grad-card ${active ? 'active' : ''}" onclick="Admin.selectGradient('${key}')">
          ${active ? '<div class="grad-card-check">✓</div>' : ''}
          <div class="grad-card-preview" style="background:${grad.now}"></div>
          <div class="grad-card-name">${r.name}</div>
          <div class="grad-card-mood">${r.mood}</div>
        </div>`;
    }).join('');
  }

  function selectGradient(key) {
    if (!GRADIENT_RECIPES[key]) return;
    localStorage.setItem(KEYS.gradient, key);
    renderGradientGrid();
  }

  function renderTypoGrid() {
    const grid = document.getElementById('typo-grid');
    if (!grid) return;
    const current = localStorage.getItem(KEYS.typography) || 'modern';

    // preload all non-default fonts for preview
    Object.values(FONT_PAIRS).forEach(p => {
      if (p.url && !document.querySelector(`link[data-typo="${p.name}"]`)) {
        const lk = document.createElement('link');
        lk.rel = 'stylesheet';
        lk.dataset.typo = p.name;
        lk.href = `https://fonts.googleapis.com/css2?family=${p.url}&display=swap`;
        document.head.appendChild(lk);
      }
    });

    grid.innerHTML = Object.entries(FONT_PAIRS).map(([key, p]) => {
      const active = key === current;
      return `
        <div class="typo-card ${active ? 'active' : ''}" onclick="Admin.selectTypography('${key}')">
          ${active ? '<div class="typo-card-check">✓</div>' : ''}
          <div class="typo-card-sample-disp" style="font-family:'${p.disp}',serif">Aa</div>
          <div class="typo-card-sample-body" style="font-family:'${p.body}',sans-serif">Программа · 15:00</div>
          <div class="typo-card-name">${p.name}</div>
          <div class="typo-card-meta">${p.dispLabel} · ${p.bodyLabel}</div>
          <div class="typo-card-meta">${p.mood}</div>
        </div>`;
    }).join('');
  }

  function selectTypography(key) {
    if (!FONT_PAIRS[key]) return;
    localStorage.setItem(KEYS.typography, key);
    renderTypoGrid();
  }

  function updateBrandPreview() {
    const color   = document.getElementById('s-brand-color').value;
    const logo    = document.getElementById('s-brand-logo').value.trim();
    const title   = document.getElementById('s-title').value || 'Название события';
    const bar     = document.getElementById('brand-preview-bar');
    const titleEl = document.getElementById('brand-preview-title');
    const logoEl  = document.getElementById('brand-preview-logo');
    if (bar)     bar.style.background = color;
    if (titleEl) titleEl.textContent  = title;
    if (logoEl) {
      if (logo) { logoEl.src = logo; logoEl.classList.remove('hidden'); }
      else      { logoEl.classList.add('hidden'); }
    }
  }

  // sync hex text ↔ color picker
  function onBrandColorPicker(val) {
    document.getElementById('s-brand-color-hex').value = val;
    updateBrandPreview();
  }
  function onBrandColorHex(val) {
    if (/^#[0-9a-fA-F]{6}$/.test(val)) {
      document.getElementById('s-brand-color').value = val;
      updateBrandPreview();
    }
  }

  function saveSettings() {
    state.event = {
      ...state.event,
      brand: {
        color: document.getElementById('s-brand-color').value,
        logo:  document.getElementById('s-brand-logo').value.trim(),
      },
      title:    document.getElementById('s-title').value,
      dates:    document.getElementById('s-dates').value,
      location: document.getElementById('s-location').value,
      organizer: {
        name:     document.getElementById('s-org-name').value,
        telegram: document.getElementById('s-org-tg').value,
      },
      wifi: {
        network:  document.getElementById('s-wifi-net').value,
        password: document.getElementById('s-wifi-pass').value,
      },
      hotel: {
        ...state.event.hotel,
        name:  document.getElementById('s-hotel-name').value,
        phone: document.getElementById('s-hotel-phone').value,
      },
      emergency: document.getElementById('s-emergency').value,
    };
    save(KEYS.event, state.event);
    const hint = document.getElementById('settings-saved');
    hint.classList.remove('hidden');
    setTimeout(() => hint.classList.add('hidden'), 2500);
  }

  /* ─── PROGRAM ─────────────────────────── */
  function renderProgramSection() {
    const selector = document.getElementById('day-selector');
    selector.innerHTML = state.days.map((d, i) => `
      <button class="day-pill ${i === state.programDay ? 'active' : ''}"
        style="${i === state.programDay ? 'background:' + d.color : ''}"
        onclick="Admin.selectProgramDay(${i})">${d.label}</button>
    `).join('');
    renderActivityList();
  }

  function selectProgramDay(i) {
    state.programDay = i;
    renderProgramSection();
  }

  function renderActivityList() {
    const day  = state.days[state.programDay];
    const list = document.getElementById('program-list');
    if (!day.activities.length) {
      list.innerHTML = `<div class="empty-state">Активностей нет. Добавьте первую.</div>`;
      return;
    }
    list.innerHTML = day.activities.map((a, i) => `
      <div class="list-item" onclick="Admin.openActivityModal(${i})">
        <div class="list-item-left">
          <span class="list-time">${a.time}</span>
          <div>
            <div class="list-title">${a.title}</div>
            <div class="list-sub">📍 ${a.location}${a.note ? ' · ' + a.note : ''}</div>
          </div>
        </div>
        <span class="list-edit">✏️</span>
      </div>
    `).join('');
  }

  function openActivityModal(index) {
    const isNew = index === null;
    const a = isNew ? { time: '', title: '', location: '', type: 'business', note: '' }
                    : state.days[state.programDay].activities[index];

    document.getElementById('activity-modal-title').textContent = isNew ? 'Добавить активность' : 'Редактировать';
    document.getElementById('a-index').value    = isNew ? '' : index;
    document.getElementById('a-time').value     = a.time     || '';
    document.getElementById('a-title').value    = a.title    || '';
    document.getElementById('a-location').value = a.location || '';
    document.getElementById('a-type').value     = a.type     || 'business';
    document.getElementById('a-note').value     = a.note     || '';
    document.getElementById('a-delete-btn').style.display = isNew ? 'none' : 'inline-block';
    openModal('modal-activity');
  }

  function saveActivity() {
    const idx   = document.getElementById('a-index').value;
    const isNew = idx === '';
    const activity = {
      time:     document.getElementById('a-time').value.trim(),
      title:    document.getElementById('a-title').value.trim(),
      location: document.getElementById('a-location').value.trim(),
      type:     document.getElementById('a-type').value,
      note:     document.getElementById('a-note').value.trim() || undefined,
    };
    if (!activity.title || !activity.time) { alert('Заполните время и название'); return; }

    const acts = state.days[state.programDay].activities;
    if (isNew) acts.push(activity);
    else       acts[parseInt(idx)] = activity;

    save(KEYS.days, state.days);
    closeModal('modal-activity');
    renderActivityList();
    showToast('Сохранено');
  }

  function deleteActivity() {
    const idx = parseInt(document.getElementById('a-index').value);
    state.days[state.programDay].activities.splice(idx, 1);
    save(KEYS.days, state.days);
    closeModal('modal-activity');
    renderActivityList();
    showToast('Удалено');
  }

  /* ─── BUSINESS SESSIONS ───────────────── */
  const TRACK_LABELS = { '': 'Пленарная', A: 'Трек A', B: 'Трек B', C: 'Трек C' };
  const TRACK_COLORS = { '': '#6B7280', A: '#C9353F', B: '#2563EB', C: '#16A34A' };

  function renderBusinessSection() {
    const list = document.getElementById('business-list');
    if (!state.business.length) {
      list.innerHTML = `<div class="empty-state">Сессий нет. Добавьте первую.</div>`;
      return;
    }
    list.innerHTML = state.business.map((s, i) => {
      const trackColor = TRACK_COLORS[s.track || ''] || '#6B7280';
      const trackLabel = TRACK_LABELS[s.track || ''] || s.track;
      return `
        <div class="list-item" onclick="Admin.openBusinessModal(${i})">
          <div class="list-item-left">
            <span class="list-time">${s.time}</span>
            <div>
              <div class="list-title">${s.title}</div>
              <div class="list-sub">
                <span style="color:${trackColor};font-weight:700">${trackLabel}</span>
                · ${s.day} · ${s.room || ''}
              </div>
            </div>
          </div>
          <span class="list-edit">✏️</span>
        </div>
      `;
    }).join('');
  }

  function openBusinessModal(index) {
    const isNew = index === null;
    const s = isNew
      ? { day: 'День 2', time: '', duration: '', track: '', title: '', room: '', speakers: [], desc: '' }
      : state.business[index];

    document.getElementById('business-modal-title').textContent = isNew ? 'Добавить сессию' : 'Редактировать';
    document.getElementById('b-index').value    = isNew ? '' : index;
    document.getElementById('b-day').value      = s.day      || 'День 2';
    document.getElementById('b-time').value     = s.time     || '';
    document.getElementById('b-duration').value = s.duration || '';
    document.getElementById('b-track').value    = s.track    || '';
    document.getElementById('b-title').value    = s.title    || '';
    document.getElementById('b-room').value     = s.room     || '';
    document.getElementById('b-speakers').value = (s.speakers || []).join('\n');
    document.getElementById('b-desc').value     = s.desc     || '';
    document.getElementById('b-delete-btn').style.display = isNew ? 'none' : 'inline-block';
    openModal('modal-business');
  }

  function saveBusiness() {
    const idx   = document.getElementById('b-index').value;
    const isNew = idx === '';
    const speakersRaw = document.getElementById('b-speakers').value.trim();
    const session = {
      id:       isNew ? 'b' + Date.now() : state.business[parseInt(idx)].id,
      day:      document.getElementById('b-day').value,
      time:     document.getElementById('b-time').value.trim(),
      duration: document.getElementById('b-duration').value.trim(),
      track:    document.getElementById('b-track').value,
      title:    document.getElementById('b-title').value.trim(),
      room:     document.getElementById('b-room').value.trim(),
      speakers: speakersRaw ? speakersRaw.split('\n').map(l => l.trim()).filter(Boolean) : [],
      desc:     document.getElementById('b-desc').value.trim(),
    };
    if (!session.title) { alert('Введите название сессии'); return; }

    if (isNew) state.business.push(session);
    else       state.business[parseInt(idx)] = session;

    save(KEYS.business, state.business);
    closeModal('modal-business');
    renderBusinessSection();
    showToast('Сохранено');
  }

  function deleteBusiness() {
    const idx = parseInt(document.getElementById('b-index').value);
    state.business.splice(idx, 1);
    save(KEYS.business, state.business);
    closeModal('modal-business');
    renderBusinessSection();
    showToast('Удалено');
  }

  /* ─── HOTEL ──────────────────────────── */
  function renderHotelSection() {
    const h = state.hotel;
    document.getElementById('h-name').value      = h.name      || '';
    document.getElementById('h-name-cn').value   = h.nameCn    || '';
    document.getElementById('h-phone').value     = h.phone     || '';
    document.getElementById('h-metro').value     = h.metro     || '';
    document.getElementById('h-checkin').value   = h.checkin   || '';
    document.getElementById('h-checkout').value  = h.checkout  || '';
    document.getElementById('h-breakfast').value = h.breakfast || '';
    document.getElementById('h-address').value   = h.address   || '';
    document.getElementById('h-address-cn').value= h.addressCn || '';
    document.getElementById('h-desc').value      = h.desc      || '';
    document.getElementById('h-image').value     = h.image     || '';
    showImgThumb('h-image', h.image || '');
    document.getElementById('h-tips').value      = (h.tips || []).join('\n');
    renderHotelAmenities();
  }

  function renderHotelAmenities() {
    const list = document.getElementById('hotel-amenities-list');
    const amenities = state.hotel.amenities || [];
    if (!amenities.length) {
      list.innerHTML = `<div class="empty-state">Удобств нет. Добавьте первое.</div>`;
      return;
    }
    list.innerHTML = amenities.map((a, i) => `
      <div class="list-item" onclick="Admin.openAmenityModal(${i})">
        <div class="list-item-left">
          <span style="font-size:22px">${a.icon}</span>
          <div>
            <div class="list-title">${a.title}</div>
            <div class="list-sub">${a.note}</div>
          </div>
        </div>
        <span class="list-edit">✏️</span>
      </div>
    `).join('');
  }

  function saveHotel() {
    const tipsRaw = document.getElementById('h-tips').value.trim();
    state.hotel = {
      ...state.hotel,
      name:      document.getElementById('h-name').value.trim(),
      nameCn:    document.getElementById('h-name-cn').value.trim(),
      phone:     document.getElementById('h-phone').value.trim(),
      metro:     document.getElementById('h-metro').value.trim(),
      checkin:   document.getElementById('h-checkin').value.trim(),
      checkout:  document.getElementById('h-checkout').value.trim(),
      breakfast: document.getElementById('h-breakfast').value.trim(),
      address:   document.getElementById('h-address').value.trim(),
      addressCn: document.getElementById('h-address-cn').value.trim(),
      desc:      document.getElementById('h-desc').value.trim(),
      image:     document.getElementById('h-image').value.trim() || state.hotel.image,
      tips:      tipsRaw ? tipsRaw.split('\n').map(l => l.trim()).filter(Boolean) : [],
    };
    save(KEYS.hotel, state.hotel);
    const hint = document.getElementById('hotel-saved');
    hint.classList.remove('hidden');
    setTimeout(() => hint.classList.add('hidden'), 2500);
  }

  function openAmenityModal(index) {
    const isNew = index === null;
    const used  = (state.hotel.amenities || []).map(a => a.icon);
    const a = isNew
      ? { icon: pickUniqueEmoji('amenities', used), title: '', note: '' }
      : (state.hotel.amenities || [])[index];

    document.getElementById('amenity-modal-title').textContent = isNew ? 'Добавить удобство' : 'Редактировать';
    document.getElementById('am-index').value = isNew ? '' : index;
    document.getElementById('am-title').value = a.title || '';
    document.getElementById('am-note').value  = a.note  || '';
    document.getElementById('am-delete-btn').style.display = isNew ? 'none' : 'inline-block';
    renderEmojiPicker('am-icon-grid', 'am-icon', 'amenities', a.icon);
    openModal('modal-amenity');
  }

  function saveAmenity() {
    const idx   = document.getElementById('am-index').value;
    const isNew = idx === '';
    const amenity = {
      icon:  document.getElementById('am-icon').value.trim() || '✅',
      title: document.getElementById('am-title').value.trim(),
      note:  document.getElementById('am-note').value.trim(),
    };
    if (!amenity.title) { alert('Введите название'); return; }

    if (!state.hotel.amenities) state.hotel.amenities = [];
    if (isNew) state.hotel.amenities.push(amenity);
    else       state.hotel.amenities[parseInt(idx)] = amenity;

    save(KEYS.hotel, state.hotel);
    closeModal('modal-amenity');
    renderHotelAmenities();
    showToast('Сохранено');
  }

  function deleteAmenity() {
    const idx = parseInt(document.getElementById('am-index').value);
    state.hotel.amenities.splice(idx, 1);
    save(KEYS.hotel, state.hotel);
    closeModal('modal-amenity');
    renderHotelAmenities();
    showToast('Удалено');
  }

  /* ─── SIGHTS ──────────────────────────── */
  function renderSightsSection() {
    const list = document.getElementById('sights-list');
    if (!state.sights.length) {
      list.innerHTML = `<div class="empty-state">Мест нет. Добавьте первое.</div>`;
      return;
    }
    list.innerHTML = state.sights.map((s, i) => `
      <div class="list-item" onclick="Admin.openSightModal(${i})">
        <div class="list-item-left">
          <span style="font-size:22px">${s.emoji}</span>
          <div>
            <div class="list-title">${s.title}</div>
            <div class="list-sub">${s.sub || ''} · ${s.distance || ''}</div>
          </div>
        </div>
        <span class="list-edit">✏️</span>
      </div>
    `).join('');
  }

  function openSightModal(index) {
    const isNew = index === null;
    const used  = state.sights.map(s => s.emoji);
    const s = isNew
      ? { title: '', emoji: pickUniqueEmoji('sights', used), sub: '', distance: '', hours: '', price: '', tags: [], desc: '', tip: '', image: '' }
      : state.sights[index];

    document.getElementById('sight-modal-title').textContent = isNew ? 'Добавить место' : 'Редактировать';
    document.getElementById('si-index').value    = isNew ? '' : index;
    document.getElementById('si-title').value    = s.title    || '';
    document.getElementById('si-emoji').value    = s.emoji    || '🏛';
    document.getElementById('si-sub').value      = s.sub      || '';
    document.getElementById('si-distance').value = s.distance || '';
    document.getElementById('si-hours').value    = s.hours    || '';
    document.getElementById('si-price').value    = s.price    || '';
    document.getElementById('si-tags').value     = (s.tags || []).join(', ');
    document.getElementById('si-desc').value     = s.desc     || '';
    document.getElementById('si-tip').value      = s.tip      || '';
    document.getElementById('si-image').value    = s.image    || '';
    showImgThumb('si-image', s.image || '');
    document.getElementById('si-delete-btn').style.display = isNew ? 'none' : 'inline-block';
    renderEmojiPicker('si-emoji-grid', 'si-emoji', 'sights', s.emoji);
    openModal('modal-sight');
  }

  function saveSight() {
    const idx   = document.getElementById('si-index').value;
    const isNew = idx === '';
    const tagsRaw = document.getElementById('si-tags').value.trim();
    const sight = {
      id:       isNew ? 's' + Date.now() : state.sights[parseInt(idx)].id,
      title:    document.getElementById('si-title').value.trim(),
      emoji:    document.getElementById('si-emoji').value.trim() || '🏛',
      sub:      document.getElementById('si-sub').value.trim(),
      distance: document.getElementById('si-distance').value.trim(),
      hours:    document.getElementById('si-hours').value.trim(),
      price:    document.getElementById('si-price').value.trim(),
      tags:     tagsRaw ? tagsRaw.split(',').map(t => t.trim()).filter(Boolean) : [],
      desc:     document.getElementById('si-desc').value.trim(),
      tip:      document.getElementById('si-tip').value.trim(),
      image:    document.getElementById('si-image').value.trim() ||
                'https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?w=700&q=80',
    };
    if (!sight.title) { alert('Введите название'); return; }

    if (isNew) state.sights.push(sight);
    else       state.sights[parseInt(idx)] = sight;

    save(KEYS.sights, state.sights);
    closeModal('modal-sight');
    renderSightsSection();
    showToast('Сохранено');
  }

  function deleteSight() {
    const idx = parseInt(document.getElementById('si-index').value);
    state.sights.splice(idx, 1);
    save(KEYS.sights, state.sights);
    closeModal('modal-sight');
    renderSightsSection();
    showToast('Удалено');
  }

  /* ─── RESTAURANTS ─────────────────────── */
  function renderRestaurantsSection() {
    const list = document.getElementById('restaurants-list');
    if (!state.restaurants.length) {
      list.innerHTML = `<div class="empty-state">Ресторанов нет. Добавьте первый.</div>`;
      return;
    }
    list.innerHTML = state.restaurants.map((r, i) => `
      <div class="list-item" onclick="Admin.openRestaurantModal(${i})">
        <div class="list-item-left">
          <span style="font-size:22px">${r.emoji}</span>
          <div>
            <div class="list-title">${r.title}</div>
            <div class="list-sub">${r.cuisine} · ${r.price} · ${r.type === 'program' ? 'По программе' : 'Самостоятельно'}</div>
          </div>
        </div>
        <span class="list-edit">✏️</span>
      </div>
    `).join('');
  }

  function openRestaurantModal(index) {
    const isNew = index === null;
    const used  = state.restaurants.map(r => r.emoji);
    const r = isNew
      ? { title: '', emoji: pickUniqueEmoji('restaurants', used), cuisine: '', price: '¥¥', type: 'free', metro: '', hours: '', address: '', note: '', desc: '', image: '' }
      : state.restaurants[index];

    document.getElementById('restaurant-modal-title').textContent = isNew ? 'Добавить ресторан' : 'Редактировать';
    document.getElementById('r-index').value   = isNew ? '' : index;
    document.getElementById('r-title').value   = r.title   || '';
    document.getElementById('r-emoji').value   = r.emoji   || '🍜';
    document.getElementById('r-cuisine').value = r.cuisine || '';
    document.getElementById('r-price').value   = r.price   || '¥¥';
    document.getElementById('r-type').value    = r.type    || 'free';
    document.getElementById('r-metro').value   = r.metro   || '';
    document.getElementById('r-hours').value   = r.hours   || '';
    document.getElementById('r-address').value = r.address || '';
    document.getElementById('r-note').value    = r.note    || '';
    document.getElementById('r-desc').value    = r.desc    || '';
    document.getElementById('r-image').value   = r.image   || '';
    showImgThumb('r-image', r.image || '');
    document.getElementById('r-delete-btn').style.display = isNew ? 'none' : 'inline-block';
    renderEmojiPicker('r-emoji-grid', 'r-emoji', 'restaurants', r.emoji);
    openModal('modal-restaurant');
  }

  function saveRestaurant() {
    const idx   = document.getElementById('r-index').value;
    const isNew = idx === '';
    const rest = {
      id:      isNew ? 'r' + Date.now() : state.restaurants[parseInt(idx)].id,
      title:   document.getElementById('r-title').value.trim(),
      emoji:   document.getElementById('r-emoji').value.trim() || '🍜',
      cuisine: document.getElementById('r-cuisine').value.trim(),
      price:   document.getElementById('r-price').value,
      type:    document.getElementById('r-type').value,
      metro:   document.getElementById('r-metro').value.trim(),
      hours:   document.getElementById('r-hours').value.trim(),
      address: document.getElementById('r-address').value.trim(),
      note:    document.getElementById('r-note').value.trim(),
      desc:    document.getElementById('r-desc').value.trim(),
      image:   document.getElementById('r-image').value.trim() ||
               'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=700&q=80',
    };
    if (!rest.title) { alert('Введите название'); return; }

    if (isNew) state.restaurants.push(rest);
    else       state.restaurants[parseInt(idx)] = rest;

    save(KEYS.restaurants, state.restaurants);
    closeModal('modal-restaurant');
    renderRestaurantsSection();
    showToast('Сохранено');
  }

  function deleteRestaurant() {
    const idx = parseInt(document.getElementById('r-index').value);
    state.restaurants.splice(idx, 1);
    save(KEYS.restaurants, state.restaurants);
    closeModal('modal-restaurant');
    renderRestaurantsSection();
    showToast('Удалено');
  }

  /* ─── CUISINE ─────────────────────────── */
  function renderCuisineSection() {
    const list = document.getElementById('cuisine-list');
    if (!state.cuisine.length) {
      list.innerHTML = `<div class="empty-state">Блюд нет. Добавьте первое.</div>`;
      return;
    }
    list.innerHTML = state.cuisine.map((d, i) => `
      <div class="list-item" onclick="Admin.openCuisineModal(${i})">
        <div class="list-item-left">
          <span style="font-size:22px">${d.emoji}</span>
          <div>
            <div class="list-title">${d.title} ${d.must ? '<span style="color:#C9353F;font-size:11px;font-weight:700">МАСТ</span>' : ''}</div>
            <div class="list-sub">${d.cn || ''} · ${d.price || ''}</div>
          </div>
        </div>
        <span class="list-edit">✏️</span>
      </div>
    `).join('');
  }

  function openCuisineModal(index) {
    const isNew = index === null;
    const used  = state.cuisine.map(d => d.emoji);
    const d = isNew
      ? { title: '', emoji: pickUniqueEmoji('cuisine', used), cn: '', price: '', where: '', desc: '', must: false }
      : state.cuisine[index];

    document.getElementById('cuisine-modal-title').textContent = isNew ? 'Добавить блюдо' : 'Редактировать';
    document.getElementById('c-index').value = isNew ? '' : index;
    document.getElementById('c-title').value = d.title || '';
    document.getElementById('c-emoji').value = d.emoji || '🥢';
    document.getElementById('c-cn').value    = d.cn    || '';
    document.getElementById('c-price').value = d.price || '';
    document.getElementById('c-where').value = d.where || '';
    document.getElementById('c-desc').value  = d.desc  || '';
    document.getElementById('c-must').checked = !!d.must;
    document.getElementById('c-delete-btn').style.display = isNew ? 'none' : 'inline-block';
    renderEmojiPicker('c-emoji-grid', 'c-emoji', 'cuisine', d.emoji);
    openModal('modal-cuisine');
  }

  function saveCuisine() {
    const idx   = document.getElementById('c-index').value;
    const isNew = idx === '';
    const dish = {
      id:    isNew ? 'c' + Date.now() : state.cuisine[parseInt(idx)].id,
      title: document.getElementById('c-title').value.trim(),
      emoji: document.getElementById('c-emoji').value.trim() || '🥢',
      cn:    document.getElementById('c-cn').value.trim(),
      price: document.getElementById('c-price').value.trim(),
      where: document.getElementById('c-where').value.trim(),
      desc:  document.getElementById('c-desc').value.trim(),
      must:  document.getElementById('c-must').checked,
    };
    if (!dish.title) { alert('Введите название блюда'); return; }

    if (isNew) state.cuisine.push(dish);
    else       state.cuisine[parseInt(idx)] = dish;

    save(KEYS.cuisine, state.cuisine);
    closeModal('modal-cuisine');
    renderCuisineSection();
    showToast('Сохранено');
  }

  function deleteCuisine() {
    const idx = parseInt(document.getElementById('c-index').value);
    state.cuisine.splice(idx, 1);
    save(KEYS.cuisine, state.cuisine);
    closeModal('modal-cuisine');
    renderCuisineSection();
    showToast('Удалено');
  }

  /* ─── HISTORY ─────────────────────────── */
  function renderHistorySection() {
    const selector = document.getElementById('history-section-selector');
    selector.innerHTML = state.history.map((sec, i) => `
      <button class="day-pill ${i === state.historySection ? 'active' : ''}"
        style="${i === state.historySection ? 'background:#C9353F' : ''}"
        onclick="Admin.selectHistorySection(${i})">${sec.emoji} ${sec.section}</button>
    `).join('');
    renderHistoryList();
  }

  function selectHistorySection(i) {
    state.historySection = i;
    renderHistorySection();
  }

  function renderHistoryList() {
    const sec  = state.history[state.historySection];
    const list = document.getElementById('history-list');
    if (!sec.facts.length) {
      list.innerHTML = `<div class="empty-state">Фактов нет. Добавьте первый.</div>`;
      return;
    }
    list.innerHTML = sec.facts.map((f, i) => `
      <div class="list-item" onclick="Admin.openHistoryModal(${i})">
        <div class="list-item-left">
          <span style="font-size:20px">${f.wow ? '🤯' : '📌'}</span>
          <div>
            <div class="list-title">${f.title}</div>
            <div class="list-sub">${(f.text || '').slice(0, 60)}${f.text && f.text.length > 60 ? '…' : ''}</div>
          </div>
        </div>
        <span class="list-edit">✏️</span>
      </div>
    `).join('');
  }

  function openHistoryModal(index) {
    const isNew = index === null;
    const f = isNew
      ? { title: '', text: '', wow: false }
      : state.history[state.historySection].facts[index];

    // populate section dropdown
    const sel = document.getElementById('h-section-select');
    sel.innerHTML = state.history.map((sec, i) => `
      <option value="${i}" ${i === state.historySection ? 'selected' : ''}>${sec.emoji} ${sec.section}</option>
    `).join('');

    document.getElementById('history-modal-title').textContent = isNew ? 'Добавить факт' : 'Редактировать';
    document.getElementById('h-index').value         = isNew ? '' : index;
    document.getElementById('h-section-index').value = state.historySection;
    document.getElementById('h-title').value = f.title || '';
    document.getElementById('h-text').value  = f.text  || '';
    document.getElementById('h-wow').checked = !!f.wow;
    document.getElementById('h-delete-btn').style.display = isNew ? 'none' : 'inline-block';
    openModal('modal-history');
  }

  function saveHistory() {
    const idx        = document.getElementById('h-index').value;
    const isNew      = idx === '';
    const fromSec    = parseInt(document.getElementById('h-section-index').value);
    const toSec      = parseInt(document.getElementById('h-section-select').value);
    const fact = {
      title: document.getElementById('h-title').value.trim(),
      text:  document.getElementById('h-text').value.trim(),
      wow:   document.getElementById('h-wow').checked,
    };
    if (!fact.title) { alert('Введите заголовок факта'); return; }

    if (!isNew && fromSec !== toSec) {
      // move fact to different section
      state.history[fromSec].facts.splice(parseInt(idx), 1);
      state.history[toSec].facts.push(fact);
    } else if (isNew) {
      state.history[toSec].facts.push(fact);
    } else {
      state.history[fromSec].facts[parseInt(idx)] = fact;
    }

    save(KEYS.history, state.history);
    state.historySection = toSec;
    closeModal('modal-history');
    renderHistorySection();
    showToast('Сохранено');
  }

  function deleteHistory() {
    const idx    = parseInt(document.getElementById('h-index').value);
    const secIdx = parseInt(document.getElementById('h-section-index').value);
    state.history[secIdx].facts.splice(idx, 1);
    save(KEYS.history, state.history);
    closeModal('modal-history');
    renderHistorySection();
    showToast('Удалено');
  }

  /* ─── EMOJI PICKER ───────────────────── */
  const EMOJI_POOLS = {
    cuisine:     ['🦆','🍜','🍤','🥟','🍲','🥩','🍣','🍱','🫕','🧆','🍛','🍝','🥗','🫔','🍢','🍡','🥮','🧋','🍕','🌮','🌯','🥪','🍖','🍗','🧀','🍩','🍰','🎂','🍦','🍵','🥐','🦐','🦀','🦞','🐟','🍔','🥙','🌽','🥑','🫙'],
    sights:      ['🏯','🏛️','🗼','🌿','🏔️','🗻','🏖️','🌊','🏙️','⛩️','🕌','⛪','🏰','🎡','🌃','🌉','🗽','🏟️','🎭','🌅','🏜️','💎','🔮','🌸','🌋','🏝️','🎪','🚀','🌁','🏞️','⛰️','🌄','🗿','🏗️','🌺','🚦','⛵','🛕','☸️','🕍'],
    restaurants: ['🍜','🦆','🍣','🥩','🍕','🌮','🥐','🦞','🍢','🥟','🍛','🧆','🫕','🐟','🥗','🦐','🦀','☕','🥂','🍷','🍺','🍱','🌯','🍔','🥙','🍝','🫖','🍻','🍾','🥘'],
    amenities:   ['🏊','💪','🧖','🍽','🏪','👔','🚤','⛵','🎾','♨️','🛎️','🌴','🏖️','🛁','💆','🏋️','🅿️','📺','🌐','🏌️','🚁','🎯','🛍️','🧹','🎱','🎰','🧘','🛗','🍸','🌡️'],
  };

  function pickUniqueEmoji(poolKey, usedEmojis) {
    const pool = EMOJI_POOLS[poolKey] || EMOJI_POOLS.cuisine;
    return pool.find(e => !usedEmojis.includes(e)) || pool[0];
  }

  function renderEmojiPicker(gridId, inputId, poolKey, selected) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    const pool = EMOJI_POOLS[poolKey] || EMOJI_POOLS.cuisine;
    grid.innerHTML = pool.map(e => `
      <button type="button" class="emoji-btn ${e === selected ? 'selected' : ''}"
        onclick="Admin.selectEmoji('${gridId}','${inputId}','${e}')">${e}</button>
    `).join('');
  }

  function selectEmoji(gridId, inputId, emoji) {
    document.getElementById(inputId).value = emoji;
    document.querySelectorAll('#' + gridId + ' .emoji-btn').forEach(btn => {
      btn.classList.toggle('selected', btn.textContent.trim() === emoji);
    });
  }

  /* ─── IMAGE PICKER ───────────────────── */
  function pickImage(input, targetId) {
    const file = input.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
      const img = new Image();
      img.onload = () => {
        const MAX    = 900;
        const scale  = Math.min(1, MAX / Math.max(img.width, img.height));
        const canvas = document.createElement('canvas');
        canvas.width  = Math.round(img.width  * scale);
        canvas.height = Math.round(img.height * scale);
        canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.80);
        const field   = document.getElementById(targetId);
        if (field) field.value = dataUrl;
        showImgThumb(targetId, dataUrl);
        input.value = '';
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  function showImgThumb(targetId, src) {
    const thumb = document.getElementById(targetId + '-preview');
    if (!thumb) return;
    if (src) {
      thumb.src = src;
      thumb.classList.remove('hidden');
    } else {
      thumb.classList.add('hidden');
    }
  }

  /* ─── BRAND KITS ─────────────────────── */
  const LABEL_MAP = {
    typography: { modern: 'Modern', executive: 'Executive', editorial: 'Editorial', friendly: 'Friendly', tech: 'Tech' },
    gradient:   { glow: 'Glow', diagonal: 'Diagonal', vertical: 'Vertical', mesh: 'Mesh', flat: 'Flat' },
    cardStyle:  { elevated: 'Elevated', flat: 'Flat', glass: 'Glass', outlined: 'Outlined' },
    motion:     { swift: 'Swift', elegant: 'Elegant', minimal: 'Minimal' },
  };

  function renderBrandKitsSection() {
    const list  = document.getElementById('brand-kits-list');
    if (!list) return;
    const kits  = getStored(KEYS.brandKits) || [];

    if (!kits.length) {
      list.innerHTML = '<div class="brandkit-empty">Нет сохранённых пресетов.<br>Настройте оформление и нажмите «Сохранить текущие настройки».</div>';
      return;
    }

    list.innerHTML = kits.map(kit => {
      const date = new Date(kit.savedAt).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' });
      return `
        <div class="brandkit-card">
          <div class="brandkit-card-header" style="background:${kit.color}">
            <div class="brandkit-card-swatch" style="background:${kit.color}; filter:brightness(1.3)"></div>
            <div class="brandkit-card-name">${kit.name}</div>
            <button class="brandkit-card-delete" onclick="Admin.deleteBrandKit('${kit.id}')" title="Удалить">✕</button>
          </div>
          <div class="brandkit-card-body">
            <div class="brandkit-card-row"><span>Шрифт</span><span>${LABEL_MAP.typography[kit.typography] || kit.typography}</span></div>
            <div class="brandkit-card-row"><span>Градиент</span><span>${LABEL_MAP.gradient[kit.gradient] || kit.gradient}</span></div>
            <div class="brandkit-card-row"><span>Карточки</span><span>${LABEL_MAP.cardStyle[kit.cardStyle] || kit.cardStyle}</span></div>
            <div class="brandkit-card-row"><span>Анимации</span><span>${LABEL_MAP.motion[kit.motion] || kit.motion}</span></div>
            <div class="brandkit-date">Сохранён ${date}</div>
            <button class="brandkit-card-apply" onclick="Admin.applyBrandKit('${kit.id}')">Применить к событию</button>
          </div>
        </div>`;
    }).join('');
  }

  function saveBrandKit() {
    const nameInput = document.getElementById('kit-name-input');
    const name = (nameInput?.value || '').trim();
    if (!name) { nameInput?.focus(); showToast('Введите название пресета'); return; }

    const kit = {
      id:         Date.now().toString(),
      name,
      color:      state.event?.brand?.color || '#C9353F',
      logo:       state.event?.brand?.logo  || '',
      typography: localStorage.getItem(KEYS.typography) || 'modern',
      gradient:   localStorage.getItem(KEYS.gradient)   || 'glow',
      cardStyle:  localStorage.getItem(KEYS.cardStyle)  || 'elevated',
      motion:     localStorage.getItem(KEYS.motion)     || 'swift',
      savedAt:    new Date().toISOString(),
    };

    const kits = getStored(KEYS.brandKits) || [];
    kits.unshift(kit);
    save(KEYS.brandKits, kits);

    if (nameInput) nameInput.value = '';
    renderBrandKitsSection();
    showToast('Brand Kit «' + name + '» сохранён');
  }

  function applyBrandKit(id) {
    const kits = getStored(KEYS.brandKits) || [];
    const kit  = kits.find(k => k.id === id);
    if (!kit) return;

    state.event = {
      ...state.event,
      brand: { color: kit.color, logo: kit.logo },
    };
    save(KEYS.event, state.event);
    localStorage.setItem(KEYS.typography, kit.typography);
    localStorage.setItem(KEYS.gradient,   kit.gradient);
    localStorage.setItem(KEYS.cardStyle,  kit.cardStyle);
    localStorage.setItem(KEYS.motion,     kit.motion);

    loadSettingsForm();
    showToast('Применён «' + kit.name + '»');
  }

  function deleteBrandKit(id) {
    const kits    = getStored(KEYS.brandKits) || [];
    const updated = kits.filter(k => k.id !== id);
    save(KEYS.brandKits, updated);
    renderBrandKitsSection();
    showToast('Пресет удалён');
  }

  /* ─── BACKUP / RESTORE ────────────────── */
  function exportData() {
    const backup = { _version: 1, _exported: new Date().toISOString() };
    Object.values(KEYS).forEach(key => {
      const val = localStorage.getItem(key);
      if (val) { try { backup[key] = JSON.parse(val); } catch { backup[key] = val; } }
    });
    const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
    const a    = document.createElement('a');
    a.href     = URL.createObjectURL(blob);
    a.download = 'mice-backup-' + new Date().toISOString().slice(0, 10) + '.json';
    a.click();
    URL.revokeObjectURL(a.href);
    showToast('Бэкап скачан');
  }

  function importData(input) {
    const file = input.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
      try {
        const data = JSON.parse(e.target.result);
        if (!data._version) throw new Error('Неверный формат — не похоже на файл бэкапа этого приложения');
        const dateStr = data._exported ? new Date(data._exported).toLocaleString('ru') : 'неизвестно';
        if (!confirm(`Восстановить данные из файла?\nЭкспортирован: ${dateStr}\n\nТекущие данные будут перезаписаны.`)) {
          input.value = '';
          return;
        }
        Object.values(KEYS).forEach(key => {
          if (data[key] !== undefined) localStorage.setItem(key, JSON.stringify(data[key]));
        });
        loadAll();
        input.value = '';
        const status = document.getElementById('backup-status');
        if (status) status.innerHTML = `<div class="backup-success">✓ Данные восстановлены из файла от ${dateStr}</div>`;
        showToast('Данные восстановлены');
      } catch (err) {
        alert('Ошибка при чтении файла: ' + err.message);
        input.value = '';
      }
    };
    reader.readAsText(file);
  }

  /* ─── MODAL / TOAST ───────────────────── */
  function openModal(id) {
    document.getElementById(id).classList.remove('hidden');
  }

  function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
  }

  let toastTimer;
  function showToast(msg) {
    let el = document.getElementById('admin-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'admin-toast';
      el.className = 'admin-toast';
      document.body.appendChild(el);
    }
    el.textContent = '✓ ' + msg;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), 2200);
  }

  /* ─── PUBLIC ──────────────────────────── */
  return {
    login, logout, showSection, applyTemplate,
    // backup
    exportData, importData,
    // program
    selectProgramDay, openActivityModal, saveActivity, deleteActivity,
    // business
    openBusinessModal, saveBusiness, deleteBusiness,
    // hotel
    saveHotel, openAmenityModal, saveAmenity, deleteAmenity,
    // sights
    openSightModal, saveSight, deleteSight,
    // restaurants
    openRestaurantModal, saveRestaurant, deleteRestaurant,
    // cuisine
    openCuisineModal, saveCuisine, deleteCuisine,
    // history
    selectHistorySection, openHistoryModal, saveHistory, deleteHistory,
    // announcement + settings
    saveAnnouncement, clearAnnouncement,
    saveSettings, updateBrandPreview, onBrandColorPicker, onBrandColorHex,
    selectTypography,
    selectGradient,
    selectCardStyle,
    selectMotion,
    // brand kits
    saveBrandKit, applyBrandKit, deleteBrandKit,
    // emoji
    selectEmoji,
    // image
    pickImage,
    // modal
    openModal, closeModal,
  };

})();

// Close modals on overlay click
document.querySelectorAll('.modal-overlay').forEach(el => {
  el.addEventListener('click', e => {
    if (e.target === el) el.classList.add('hidden');
  });
});
