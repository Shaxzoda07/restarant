(function () {
  var nav = document.getElementById('nav');
  var bar = document.getElementById('progress');
  var para = [].slice.call(document.querySelectorAll('[data-speed]'));
  var ticking = false;

  function onScroll() {
    var y = window.scrollY || 0;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    if (bar) bar.style.width = (h > 0 ? (y / h) * 100 : 0) + '%';
    if (nav) nav.classList.toggle('scrolled', y > 40);
    if (y < window.innerHeight * 1.5) {
      para.forEach(function (el) {
        el.style.transform = 'translate3d(0,' + (y * parseFloat(el.dataset.speed)) + 'px,0)';
      });
    }
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  onScroll();

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  document.querySelectorAll('.reveal').forEach(function (el, i) {
    if (el.classList.contains('dish') || el.classList.contains('table')) {
      el.style.transitionDelay = ((i % 4) * 70) + 'ms';
    }
    io.observe(el);
  });

  var cio = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target, end = parseInt(el.dataset.count, 10) || 0, t0 = null;
      function step(t) {
        if (!t0) t0 = t;
        var p = Math.min((t - t0) / 1400, 1);
        el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
      cio.unobserve(el);
    });
  }, { threshold: 0.5 });
  document.querySelectorAll('[data-count]').forEach(function (el) { cio.observe(el); });

  if (window.matchMedia('(hover:hover)').matches) {
    document.addEventListener('mousemove', function (e) {
      var card = e.target.closest && e.target.closest('.dish');
      document.querySelectorAll('.dish.tilt').forEach(function (c) {
        if (c !== card) { c.classList.remove('tilt'); c.style.transform = ''; }
      });
      if (!card || !card.classList.contains('in')) return;
      var r = card.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      card.classList.add('tilt');
      card.style.transform = 'perspective(900px) rotateY(' + (x * 8) + 'deg) rotateX(' + (-y * 8) + 'deg) translateY(-8px)';
    });
  }

  var burger = document.getElementById('burger');
  if (burger) {
    burger.addEventListener('click', function () { document.body.classList.toggle('menu-open'); });
    document.querySelectorAll('#menu-links a').forEach(function (a) {
      a.addEventListener('click', function () { document.body.classList.remove('menu-open'); });
    });
  }

  window.toast = function (msg) {
    var t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg; t.classList.add('show');
    clearTimeout(window._tt);
    window._tt = setTimeout(function () { t.classList.remove('show'); }, 2200);
  };
})();
