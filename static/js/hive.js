(function () {
    'use strict';

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var hasAnime = typeof window.anime !== 'undefined';
    var el = document.currentScript;
    var combUrl = el.getAttribute('data-honeycomb');
    var beeUrl = el.getAttribute('data-bee');

    function rand(min, max) { return Math.random() * (max - min) + min; }

    /* ---------- reveal-on-scroll ---------- */
    function revealAll() {
        document.querySelectorAll('[data-reveal]').forEach(function (e) { e.style.opacity = 1; });
        document.querySelectorAll('[data-reveal-group]').forEach(function (g) {
            for (var i = 0; i < g.children.length; i++) { g.children[i].style.opacity = 1; }
        });
    }

    function setupReveals() {
        if (reduce || !hasAnime || !('IntersectionObserver' in window)) { revealAll(); return; }
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) { return; }
                var node = entry.target;
                if (node.hasAttribute('data-reveal-group')) {
                    anime({
                        targets: node.children,
                        opacity: [0, 1],
                        translateY: [40, 0],
                        scale: [0.9, 1],
                        rotate: [-3, 0],
                        duration: 720,
                        delay: anime.stagger(90, { start: 60 }),
                        easing: 'easeOutElastic(1, .7)'
                    });
                } else {
                    anime({
                        targets: node,
                        opacity: [0, 1],
                        translateY: [34, 0],
                        rotate: [-2, 0],
                        duration: 680,
                        easing: 'easeOutBack'
                    });
                }
                io.unobserve(node);
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
        document.querySelectorAll('[data-reveal], [data-reveal-group]').forEach(function (n) { io.observe(n); });
    }

    /* ---------- honeycomb backdrop ---------- */
    function injectHoneycomb() {
        var bg = document.querySelector('.hive-bg');
        if (!bg || !combUrl) { return; }
        fetch(combUrl).then(function (r) { return r.text(); }).then(function (t) {
            if (reduce) { t = t.replace(/<animate[^>]*>/g, ''); }
            bg.innerHTML = t;
        }).catch(function () {});
    }

    /* ---------- bobbing brand bee ---------- */
    function bobBrand() {
        if (reduce || !hasAnime) { return; }
        var brand = document.querySelector('.brand img');
        if (brand) {
            anime({ targets: brand, translateY: [0, -5], rotate: [-6, 6], duration: 1200,
                    direction: 'alternate', loop: true, easing: 'easeInOutSine' });
        }
    }

    /* ---------- scroll progress drip ---------- */
    function scrollProgress() {
        var bar = document.createElement('div');
        bar.className = 'scroll-progress';
        document.body.appendChild(bar);
        var ticking = false;
        function update() {
            var h = document.documentElement;
            var max = h.scrollHeight - h.clientHeight;
            var pct = max > 0 ? (h.scrollTop || window.pageYOffset) / max * 100 : 0;
            bar.style.width = pct + '%';
            ticking = false;
        }
        window.addEventListener('scroll', function () {
            if (!ticking) { ticking = true; requestAnimationFrame(update); }
        }, { passive: true });
        update();
    }

    /* ---------- bee confetti burst on any click ---------- */
    var fxLayer = null;
    function getFx() {
        if (!fxLayer) {
            fxLayer = document.createElement('div');
            fxLayer.className = 'fx-layer';
            document.body.appendChild(fxLayer);
        }
        return fxLayer;
    }

    function burst(x, y) {
        if (reduce || !hasAnime || !beeUrl) { return; }
        var layer = getFx();
        var n = 10 + Math.floor(Math.random() * 4);
        for (var i = 0; i < n; i++) {
            var bit = document.createElement('img');
            bit.className = 'fx-bit';
            bit.src = beeUrl;
            bit.alt = '';
            var size = 16 + Math.random() * 16;
            bit.style.width = size + 'px';
            bit.style.height = 'auto';
            bit.style.left = x + 'px';
            bit.style.top = y + 'px';
            layer.appendChild(bit);
            (function (node) {
                var ang = -Math.PI / 2 + (Math.random() - 0.5) * Math.PI * 1.5;
                var speed = 70 + Math.random() * 150;
                var dx = Math.cos(ang) * speed;
                var dy = Math.sin(ang) * speed;
                anime({
                    targets: node,
                    translateX: [0, dx],
                    translateY: [
                        { value: dy, duration: 380, easing: 'easeOutQuad' },
                        { value: dy + 200 + Math.random() * 140, duration: 950, easing: 'easeInQuad' }
                    ],
                    rotate: Math.random() * 720 - 360,
                    scale: [0.3, 1, 0.75],
                    opacity: [1, 1, 0],
                    duration: 1250 + Math.random() * 500,
                    complete: function () { node.remove(); }
                });
            })(bit);
        }
    }

    function setupBurst() {
        document.addEventListener('click', function (e) {
            burst(e.clientX, e.clientY);
        });
    }

    /* ---------- magnetic buttons ---------- */
    function setupMagnetic() {
        if (reduce || window.matchMedia('(hover: none)').matches) { return; }
        document.querySelectorAll('.button, .btn-honey').forEach(function (b) {
            b.classList.add('magnetic');
            b.addEventListener('mousemove', function (e) {
                var r = b.getBoundingClientRect();
                var mx = e.clientX - r.left - r.width / 2;
                var my = e.clientY - r.top - r.height / 2;
                b.style.transform = 'translate(' + (mx * 0.3) + 'px,' + (my * 0.4 - 2) + 'px) scale(1.06)';
            });
            b.addEventListener('mouseleave', function () { b.style.transform = ''; });
        });
    }

    /* ---------- 3D tilt on cards ---------- */
    function setupTilt() {
        if (reduce || window.matchMedia('(hover: none)').matches) { return; }
        document.querySelectorAll('.card, .hive-card').forEach(function (card) {
            card.addEventListener('mousemove', function (e) {
                var r = card.getBoundingClientRect();
                var px = (e.clientX - r.left) / r.width - 0.5;
                var py = (e.clientY - r.top) / r.height - 0.5;
                card.style.transform =
                    'perspective(700px) rotateY(' + (px * 10) + 'deg) rotateX(' + (-py * 10) +
                    'deg) translateY(-4px) scale(1.02)';
            });
            card.addEventListener('mouseleave', function () { card.style.transform = ''; });
        });
    }

    /* ---------- count-up numbers (data-count) ---------- */
    function setupCounters() {
        if (!hasAnime) { return; }
        document.querySelectorAll('[data-count]').forEach(function (node) {
            var target = parseFloat(node.getAttribute('data-count')) || 0;
            var obj = { v: 0 };
            anime({
                targets: obj, v: target, round: 1, duration: 1600, easing: 'easeOutExpo',
                update: function () { node.textContent = obj.v; }
            });
        });
    }

    function init() {
        injectHoneycomb();
        setupReveals();
        bobBrand();
        scrollProgress();
        setupBurst();
        setupMagnetic();
        setupTilt();
        setupCounters();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else { init(); }
})();
