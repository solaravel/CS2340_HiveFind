(function () {
    'use strict';
    if (typeof THREE === 'undefined') { return; }
    var canvas = document.getElementById('beeCanvas');
    if (!canvas) { return; }
    var wrap = canvas.parentElement;
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    var W = wrap.clientWidth, H = wrap.clientHeight;
    var renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(W, H);

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(42, W / H, 0.1, 100);
    camera.position.set(0, 0, 9);

    scene.add(new THREE.AmbientLight(0xfff2cc, 0.85));
    var key = new THREE.DirectionalLight(0xffffff, 1.15); key.position.set(4, 7, 6); scene.add(key);
    var warm = new THREE.PointLight(0xffb300, 1.3, 60); warm.position.set(-6, -2, 5); scene.add(warm);
    var rim = new THREE.DirectionalLight(0xffd54f, 0.7); rim.position.set(-5, 3, -6); scene.add(rim);

    var yellow = new THREE.MeshStandardMaterial({ color: 0xffb300, roughness: 0.42, metalness: 0.12 });
    var black = new THREE.MeshStandardMaterial({ color: 0x2b2015, roughness: 0.5, metalness: 0.1 });
    var wingMat = new THREE.MeshStandardMaterial({ color: 0xd6f0fb, transparent: true, opacity: 0.5, roughness: 0.15, side: THREE.DoubleSide });
    var white = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 });

    var bee = new THREE.Group();

    var body = new THREE.Mesh(new THREE.SphereGeometry(1.25, 48, 32), yellow);
    body.scale.set(1.5, 1.05, 1.05);
    bee.add(body);

    function stripe(x, r) {
        var m = new THREE.Mesh(new THREE.TorusGeometry(r, 0.17, 18, 44), black);
        m.rotation.y = Math.PI / 2;
        m.position.x = x;
        m.scale.set(1, 1.04, 1.04);
        return m;
    }
    bee.add(stripe(0.25, 1.23));
    bee.add(stripe(-0.45, 1.12));
    bee.add(stripe(-1.05, 0.82));

    var stinger = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.55, 18), black);
    stinger.position.set(-1.98, 0, 0);
    stinger.rotation.z = Math.PI / 2;
    bee.add(stinger);

    var head = new THREE.Mesh(new THREE.SphereGeometry(0.86, 32, 24), black);
    head.position.set(1.55, 0.12, 0);
    bee.add(head);

    function eye(z) {
        var g = new THREE.Group();
        var e = new THREE.Mesh(new THREE.SphereGeometry(0.22, 20, 16), white);
        e.position.set(2.02, 0.32, z);
        var p = new THREE.Mesh(new THREE.SphereGeometry(0.1, 16, 12), black);
        p.position.set(2.19, 0.34, z);
        g.add(e); g.add(p);
        return g;
    }
    bee.add(eye(0.44)); bee.add(eye(-0.44));

    function antenna(z) {
        var g = new THREE.Group();
        var stalk = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.95, 8), black);
        stalk.position.set(2.0, 0.92, z);
        stalk.rotation.z = -0.5;
        var ball = new THREE.Mesh(new THREE.SphereGeometry(0.13, 12, 10), yellow);
        ball.position.set(2.32, 1.38, z);
        g.add(stalk); g.add(ball);
        return g;
    }
    bee.add(antenna(0.32)); bee.add(antenna(-0.32));

    function wing(side) {
        var g = new THREE.Group();
        var w = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), wingMat);
        w.scale.set(1.35, 0.07, 0.72);
        w.position.set(0, 0, side);
        g.add(w);
        g.position.set(-0.1, 0.92, 0.5 * side);
        return g;
    }
    var wingL = wing(1), wingR = wing(-1);
    bee.add(wingL); bee.add(wingR);

    bee.rotation.y = -0.3;
    scene.add(bee);

    var N = 90;
    var pGeo = new THREE.BufferGeometry();
    var pos = new Float32Array(N * 3);
    for (var i = 0; i < N; i++) {
        pos[i * 3] = (Math.random() - 0.5) * 16;
        pos[i * 3 + 1] = (Math.random() - 0.5) * 10;
        pos[i * 3 + 2] = (Math.random() - 0.5) * 8 - 2;
    }
    pGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    var pollen = new THREE.Points(pGeo, new THREE.PointsMaterial({ color: 0xffd54f, size: 0.09, transparent: true, opacity: 0.75 }));
    scene.add(pollen);

    var mouse = { x: 0, y: 0 }, spin = 0;
    window.addEventListener('pointermove', function (e) {
        mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
        mouse.y = (e.clientY / window.innerHeight) * 2 - 1;
    });
    canvas.style.cursor = 'pointer';
    canvas.addEventListener('click', function () { if (spin <= 0) { spin = Math.PI * 2; } });

    function resize() {
        W = wrap.clientWidth; H = wrap.clientHeight;
        renderer.setSize(W, H);
        camera.aspect = W / H;
        camera.updateProjectionMatrix();
    }
    window.addEventListener('resize', resize);

    var t = 0;
    function animate() {
        requestAnimationFrame(animate);
        t += 0.016;
        if (reduce) {
            wingL.rotation.x = 0.4; wingR.rotation.x = -0.4;
            renderer.render(scene, camera);
            return;
        }
        bee.position.y = Math.sin(t * 1.5) * 0.28;
        bee.position.x = Math.sin(t * 0.7) * 0.2;
        if (spin > 0) {
            bee.rotation.y += 0.32;
            spin -= 0.32;
            if (spin <= 0) { bee.rotation.y = bee.rotation.y % (Math.PI * 2); }
        } else {
            bee.rotation.y += ((mouse.x * 0.7 - 0.3) - bee.rotation.y) * 0.05;
        }
        bee.rotation.x += ((mouse.y * 0.35) - bee.rotation.x) * 0.05;
        bee.rotation.z = Math.sin(t * 1.5) * 0.04;
        var flap = Math.sin(t * 38) * 0.7 + 0.35;
        wingL.rotation.x = flap;
        wingR.rotation.x = -flap;
        pollen.rotation.y = t * 0.035;
        renderer.render(scene, camera);
    }
    animate();
})();
