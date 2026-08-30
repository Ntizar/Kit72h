/* Kit72h — fondo Mad Max: dunas wireframe de cobre, polvo y sol ardiente */
(() => {
  const canvas = document.getElementById('fondo3d');
  if (!canvas || !window.THREE) return;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x150b05);
  scene.fog = new THREE.FogExp2(0x1c0e06, 0.022);

  const camera = new THREE.PerspectiveCamera(62, window.innerWidth / window.innerHeight, 0.1, 300);
  camera.position.set(0, 4.2, 14);

  // --- Dunas: dos capas de malla desplazada, cobre oxidado ---
  function duneLayer(color, opacity, scale, seed) {
    const geo = new THREE.PlaneGeometry(220, 220, 80, 80);
    geo.rotateX(-Math.PI / 2);
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i) * scale + seed;
      const z = pos.getZ(i) * scale;
      const y =
        Math.sin(x * 0.07) * Math.cos(z * 0.05) * 2.2 +
        Math.sin(x * 0.023 + z * 0.031) * 3.4 +
        Math.cos(z * 0.11) * 0.8;
      pos.setY(i, y - 3);
    }
    const mat = new THREE.MeshBasicMaterial({
      color, wireframe: true, transparent: true, opacity
    });
    const mesh = new THREE.Mesh(geo, mat);
    scene.add(mesh);
    return mesh;
  }
  const dunes1 = duneLayer(0x9a5423, 0.32, 1.0, 0);
  const dunes2 = duneLayer(0x5e3013, 0.45, 1.6, 40);
  dunes2.position.z = -30;

  // --- Sol ardiente: sprite con gradiente radial ---
  function sunTexture() {
    const c = document.createElement('canvas');
    c.width = c.height = 256;
    const g = c.getContext('2d');
    const grad = g.createRadialGradient(128, 128, 10, 128, 128, 128);
    grad.addColorStop(0, 'rgba(255,196,110,1)');
    grad.addColorStop(0.25, 'rgba(230,120,40,0.85)');
    grad.addColorStop(0.6, 'rgba(160,60,15,0.25)');
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = grad;
    g.fillRect(0, 0, 256, 256);
    return new THREE.CanvasTexture(c);
  }
  const sun = new THREE.Sprite(new THREE.SpriteMaterial({
    map: sunTexture(), transparent: true, depthWrite: false
  }));
  sun.scale.set(60, 60, 1);
  sun.position.set(-25, 14, -90);
  scene.add(sun);

  // --- Polvo del páramo ---
  const N = 700;
  const dustGeo = new THREE.BufferGeometry();
  const positions = new Float32Array(N * 3);
  const speeds = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 80;
    positions[i * 3 + 1] = Math.random() * 14 - 1;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 80;
    speeds[i] = 0.4 + Math.random() * 1.2;
  }
  dustGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const dust = new THREE.Points(dustGeo, new THREE.PointsMaterial({
    color: 0xd9955a, size: 0.09, transparent: true, opacity: 0.55, depthWrite: false
  }));
  scene.add(dust);

  // --- Residuos flotantes (chatarrería): cubos oxidos girando a lo lejos ---
  const debris = [];
  for (let i = 0; i < 12; i++) {
    const s = 0.4 + Math.random() * 1.4;
    const m = new THREE.Mesh(
      new THREE.BoxGeometry(s, s * 0.4, s * 0.7),
      new THREE.MeshBasicMaterial({ color: 0x6e3d1a, wireframe: true, transparent: true, opacity: 0.5 })
    );
    m.position.set((Math.random() - 0.5) * 70, 2 + Math.random() * 10, -20 - Math.random() * 50);
    m.userData.rot = { x: (Math.random() - 0.5) * 0.3, y: (Math.random() - 0.5) * 0.4 };
    scene.add(m);
    debris.push(m);
  }

  let t = 0;
  function animar() {
    t += 0.008;
    // dunas arrastrándose lentamente
    dunes1.position.z = (t * 6) % 8;
    dunes2.position.z = -30 + ((t * 3) % 10);
    // polvo lateral
    const p = dustGeo.attributes.position;
    for (let i = 0; i < N; i++) {
      let x = p.getX(i) + speeds[i] * 0.045;
      if (x > 40) x = -40;
      p.setX(i, x);
      p.setY(i, p.getY(i) + Math.sin(t * 2 + i) * 0.002);
    }
    p.needsUpdate = true;
    // chatarra
    debris.forEach(m => { m.rotation.x += m.userData.rot.x * 0.01; m.rotation.y += m.userData.rot.y * 0.01; });
    // cámara respira
    camera.position.x = Math.sin(t * 0.4) * 1.2;
    camera.position.y = 4.2 + Math.sin(t * 0.25) * 0.4;
    camera.lookAt(0, 2, -20);
    renderer.render(scene, camera);
    requestAnimationFrame(animar);
  }
  animar();

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
})();
