/* Lógica de la experiencia CAMELIA: inicio, estados del reconocimiento y botones. */
(function () {
  const sceneEl = document.getElementById('scene');
  const targetEl = document.getElementById('target');
  const cameliaEl = document.getElementById('camelia');
  const brocheEl = document.getElementById('broche');

  const startScreen = document.getElementById('start');
  const btnStart = document.getElementById('btn-start');
  const startError = document.getElementById('start-error');
  const statusEl = document.getElementById('status');
  const storyEl = document.getElementById('story');
  const controls = document.getElementById('controls');
  const btnStory = document.getElementById('btn-story');
  const btnPause = document.getElementById('btn-pause');

  const state = { found: false, storyOpen: false, paused: false };

  // Los scripts de preparación escriben assets/config.json con las medidas reales
  // de los fotogramas y del póster; si no existe se usan los valores del HTML.
  fetch('assets/config.json')
    .then((r) => (r.ok ? r.json() : null))
    .then((cfg) => cfg && applyConfig(cfg))
    .catch(() => {});

  function applyConfig(cfg) {
    const s = cfg.sprite;
    if (s) {
      cameliaEl.setAttribute('sprite-sheet', { frames: s.frames, columns: s.columns, rows: s.rows, fps: s.fps });
    }
    const p = cfg.placement || {};
    if (s && p.cameliaHeight) {
      // Los pies del sprite quedan sobre la línea del suelo del póster
      const h = p.cameliaHeight;
      const w = h * s.frameWidth / s.frameHeight;
      const feetOffset = h * (s.feetPadding || 0) / s.frameHeight;
      cameliaEl.setAttribute('width', w);
      cameliaEl.setAttribute('height', h);
      cameliaEl.setAttribute('position', { x: p.cameliaX || 0, y: p.cameliaFeetY + h / 2 - feetOffset, z: 0.02 });
    }
    if (p.brocheSize) {
      brocheEl.setAttribute('width', p.brocheSize);
      brocheEl.setAttribute('height', p.brocheSize);
      brocheEl.setAttribute('position', p.brochePosition);
    }
  }

  function showStatus(text, kind) {
    statusEl.textContent = text;
    statusEl.className = 'status' + (kind ? ' status-' + kind : '');
    statusEl.hidden = !text;
  }

  function render() {
    storyEl.hidden = !(state.found && state.storyOpen);
    brocheEl.setAttribute('visible', state.storyOpen);
    btnStory.textContent = state.storyOpen ? 'Ocultar historia' : 'Revelar historia';
    btnStory.setAttribute('aria-pressed', String(state.storyOpen));
    btnPause.textContent = state.paused ? 'Reanudar' : 'Pausar';
    btnPause.setAttribute('aria-pressed', String(state.paused));
    cameliaEl.setAttribute('sprite-sheet', 'playing', !state.paused);
  }

  function enableStart() {
    btnStart.disabled = false;
    btnStart.textContent = 'Iniciar RA';
  }

  if (sceneEl.hasLoaded) enableStart();
  else sceneEl.addEventListener('loaded', enableStart);

  if (!window.isSecureContext) {
    startError.textContent = 'Abre esta página por HTTPS: sin conexión segura el navegador no permite usar la cámara.';
    startError.hidden = false;
  }

  btnStart.addEventListener('click', () => {
    btnStart.disabled = true;
    btnStart.textContent = 'Iniciando cámara…';
    startError.hidden = true;
    const ar = sceneEl.systems['mindar-image-system'];
    ar.start();
  });

  sceneEl.addEventListener('arReady', () => {
    startScreen.hidden = true;
    controls.hidden = false;
    showStatus('Enfoca el póster', 'info');
    console.log('[camelia] arReady');
  });

  sceneEl.addEventListener('arError', (e) => {
    console.log('[camelia] arError', e && e.detail);
    btnStart.disabled = false;
    btnStart.textContent = 'Reintentar';
    startError.textContent = 'No se pudo iniciar la cámara. Revisa que hayas dado permiso, que la página se abra por HTTPS y que exista assets/targets.mind.';
    startError.hidden = false;
  });

  targetEl.addEventListener('targetFound', () => {
    state.found = true;
    showStatus('', null);
    render();
    console.log('[camelia] targetFound');
  });

  targetEl.addEventListener('targetLost', () => {
    // MindAR ya oculta el contenido anclado; ocultamos también el texto.
    state.found = false;
    showStatus('Vuelve a enfocar el póster', 'lost');
    render();
    console.log('[camelia] targetLost');
  });

  btnStory.addEventListener('click', () => {
    state.storyOpen = !state.storyOpen;
    render();
  });

  btnPause.addEventListener('click', () => {
    state.paused = !state.paused;
    render();
  });

  // Libera la cámara al salir de la página
  window.addEventListener('pagehide', () => {
    const ar = sceneEl.systems['mindar-image-system'];
    if (ar && ar.controller) ar.stop();
  });
})();
