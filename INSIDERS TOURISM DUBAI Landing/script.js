/* ═══════════════════════════════════════════
   INSIDERS TOURISM — Main Scripts
═══════════════════════════════════════════ */

/* ─── STICKY HEADER ──────────────────────── */
const header = document.getElementById('header');

window.addEventListener('scroll', () => {
  if (window.scrollY > 60) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
}, { passive: true });


/* ─── MOBILE MENU ────────────────────────── */
const navToggle = document.getElementById('navToggle');
const nav       = document.querySelector('.nav');

navToggle.addEventListener('click', () => {
  nav.classList.toggle('open');
  // Animate burger → X
  const spans = navToggle.querySelectorAll('span');
  if (nav.classList.contains('open')) {
    spans[0].style.cssText = 'transform: rotate(45deg) translate(4px, 5px)';
    spans[1].style.cssText = 'opacity: 0; transform: scaleX(0)';
    spans[2].style.cssText = 'transform: rotate(-45deg) translate(4px, -5px)';
  } else {
    spans.forEach(s => s.style.cssText = '');
  }
});

// Close menu on link click
nav.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    nav.classList.remove('open');
    navToggle.querySelectorAll('span').forEach(s => s.style.cssText = '');
  });
});


/* ─── SCROLL FADE-IN ─────────────────────── */
const fadeEls = document.querySelectorAll('.fade-in');

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, {
  threshold: 0.12,
  rootMargin: '0px 0px -40px 0px'
});

fadeEls.forEach(el => observer.observe(el));


/* ─── COUNTER ANIMATION ──────────────────── */
function animateCounter(el, target, duration = 1800) {
  const start     = performance.now();
  const isLarge   = target > 999;

  const update = (now) => {
    const elapsed  = now - start;
    const progress = Math.min(elapsed / duration, 1);
    // Ease out cubic
    const ease     = 1 - Math.pow(1 - progress, 3);
    const current  = Math.floor(ease * target);

    el.textContent = isLarge
      ? current.toLocaleString('en')
      : current;

    if (progress < 1) requestAnimationFrame(update);
    else el.textContent = isLarge ? target.toLocaleString('en') : target;
  };

  requestAnimationFrame(update);
}

const statNumbers = document.querySelectorAll('.stat__number[data-target]');

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el     = entry.target;
      const target = parseInt(el.dataset.target, 10);
      animateCounter(el, target);
      counterObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

statNumbers.forEach(el => counterObserver.observe(el));


/* ─── SCROLL PURPLE EFFECT (à la oplus) ─────── */
(function () {
  const statsEl  = document.getElementById('stats');
  const gridEl   = statsEl.querySelector('.stats__grid');
  const statEls  = statsEl.querySelectorAll('.stat');
  const numEls   = statsEl.querySelectorAll('.stat__number');
  const lblEls   = statsEl.querySelectorAll('.stat__label');

  function lerp(a, b, t) { return Math.round(a + (b - a) * t); }
  function rgb(from, to, t) {
    return `rgb(${lerp(from[0],to[0],t)},${lerp(from[1],to[1],t)},${lerp(from[2],to[2],t)})`;
  }

  const BG_WHITE   = [255, 255, 255];
  const BG_PURPLE  = [22,  8,  42 ];   // #16082A — very deep purple
  const LINE_WHITE = [228, 214, 220];
  const LINE_PUR   = [90,  40, 140];
  const NUM_PINK   = [168, 64, 110];   // current accent
  const NUM_LAV    = [196, 150, 230];  // light lavender
  const LBL_MID    = [107, 90,  98];
  const LBL_LIGHT  = [195, 175, 215];

  window.addEventListener('scroll', () => {
    const rect = statsEl.getBoundingClientRect();
    const vh   = window.innerHeight;

    // t: 0 when section just enters, 1 when fully in view, back to 0 when leaving
    const entering = 1 - Math.max(0, Math.min(1, rect.top / vh));
    const leaving  = Math.max(0, Math.min(1, (rect.bottom) / vh));
    const t = Math.min(entering, leaving);

    statsEl.style.backgroundColor  = rgb(BG_WHITE, BG_PURPLE, t);
    statsEl.style.borderColor       = rgb(LINE_WHITE, LINE_PUR, t);
    numEls.forEach(el  => { el.style.color = rgb(NUM_PINK, NUM_LAV, t); });
    lblEls.forEach(el  => { el.style.color = rgb(LBL_MID, LBL_LIGHT, t); });
  }, { passive: true });
})();


/* ─── REVIEWS CAROUSEL ───────────────────── */
(function () {
  const track   = document.getElementById('reviewsTrack');
  const btnPrev = document.getElementById('reviewsPrev');
  const btnNext = document.getElementById('reviewsNext');
  if (!track) return;

  const cards    = track.querySelectorAll('.review-card');
  const total    = cards.length;
  const visible  = () => window.innerWidth < 700 ? 1 : 3;
  let current = 0;

  function update() {
    const v = visible();
    const cardW = track.parentElement.offsetWidth;
    const gap   = parseFloat(getComputedStyle(track).gap) || 0;
    const step  = (cardW + gap) / v;
    track.style.transform = `translateX(-${current * step}px)`;
    btnPrev.disabled = current === 0;
    btnNext.disabled = current >= total - v;
  }

  btnNext.addEventListener('click', () => { current++; update(); });
  btnPrev.addEventListener('click', () => { current--; update(); });
  window.addEventListener('resize', () => { current = 0; update(); });
  update();
})();


/* ─── SMOOTH SCROLL for anchor links ─────── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    const offset = header.offsetHeight + 16;
    const top    = target.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top, behavior: 'smooth' });
  });
});
