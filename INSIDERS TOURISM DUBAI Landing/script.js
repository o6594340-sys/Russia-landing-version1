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
