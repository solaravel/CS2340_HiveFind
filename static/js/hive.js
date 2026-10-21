(function () {
    'use strict';

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var hasAnime = typeof window.anime !== 'undefined';
    var el = document.currentScript;
    var combUrl = el.getAttribute('data-honeycomb');

    function revealAll() {
        document.querySelectorAll('[data-reveal]').forEach(function (e) { e.style.opacity = 1; });
        document.querySelectorAll('[data-reveal-group]').forEach(function (g) {
            for (var i = 0; i < g.children.length; i++) { g.children[i].style.opacity = 1; }
        });
    }

    function injectHoneycomb() {
        var bg = document.querySelector('.hive-bg');
        if (!bg || !combUrl) { return; }
        fetch(combUrl).then(function (r) { return r.text(); }).then(function (t) {
            if (reduce) { t = t.replace(/<animate[^>]*>/g, ''); }
            bg.innerHTML = t;
        }).catch(function () {});
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
                        translateY: [30, 0],
                        scale: [0.96, 1],
                        duration: 620,
                        delay: function (el, i) { return i * 80 + (i % 3 === 0 ? 70 : 0); },
                        easing: 'easeOutQuad'
                    });
                } else {
                    anime({
                        targets: node,
                        opacity: [0, 1, 0.82, 1],
                        translateY: [28, 0],
                        rotate: [-1.5, 0],
                        duration: 600,
                        easing: 'easeOutQuad'
                    });
                }
                io.unobserve(node);
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
        document.querySelectorAll('[data-reveal], [data-reveal-group]').forEach(function (n) { io.observe(n); });
    }

    function bobBrand() {
        if (reduce || !hasAnime) { return; }
        var brand = document.querySelector('.brand img');
        if (brand) {
            anime({ targets: brand, translateY: [0, -5], rotate: [-4, 4], duration: 1300,
                    direction: 'alternate', loop: true, easing: 'linear' });
        }
    }

    function init() {
        injectHoneycomb();
        setupReveals();
        bobBrand();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else { init(); }
})();
