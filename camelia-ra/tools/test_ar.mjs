// Prueba automática de la app con cámara SIMULADA (no sustituye la prueba en un teléfono real).
// Abre index.html en Chromium, inyecta revision/camara_simulada.y4m como cámara y comprueba:
// inicio, reconocimiento, animación, pausa/reanudar, revelar historia y pérdida del póster.
//
// Uso: python3 tools/make_test_video.py && node tools/test_ar.mjs
import { createServer } from 'node:http';
import { readFile, readdir, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REV = path.join(ROOT, 'revision');
const video = path.join(REV, 'camara_simulada.y4m');
await mkdir(REV, { recursive: true });

async function findChromium() {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;
  const base = '/opt/pw-browsers';
  if (!existsSync(base)) return undefined;
  for (const d of (await readdir(base)).sort().reverse()) {
    const p = path.join(base, d, 'chrome-linux', 'chrome');
    if (d.startsWith('chromium-') && existsSync(p)) return p;
  }
  return undefined;
}

const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png',
  '.json': 'application/json', '.mind': 'application/octet-stream', '.woff2': 'font/woff2' };
const server = createServer(async (req, res) => {
  let url = decodeURIComponent(req.url.split('?')[0]);
  if (url.endsWith('/')) url += 'index.html';
  const file = path.join(ROOT, path.normalize(url));
  if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
  try {
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' });
    res.end(body);
  } catch { res.writeHead(404); res.end(); }
});
await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
const base = `http://127.0.0.1:${server.address().port}/`;

const results = [];
const check = (name, ok, detail = '') => { results.push({ name, ok, detail }); console.log(`${ok ? 'OK   ' : 'FALLA'} ${name}${detail ? ' — ' + detail : ''}`); };

const browser = await chromium.launch({
  executablePath: await findChromium(),
  args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream', `--use-file-for-fake-video-capture=${video}`,
    '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'],
});
try {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, permissions: ['camera'] });
  const page = await context.newPage();
  const events = [];
  page.on('console', (m) => { const t = m.text(); if (t.startsWith('[camelia]')) { events.push({ t, at: Date.now() }); console.log('   ', t); } });
  page.on('pageerror', (e) => console.log('   error de página:', e.message));

  await page.goto(base);
  await page.waitForFunction(() => !document.getElementById('btn-start').disabled, null, { timeout: 60000 });
  check('Pantalla de inicio y botón «Iniciar RA»', (await page.textContent('#btn-start')).trim() === 'Iniciar RA');
  await page.screenshot({ path: path.join(REV, 'prueba_1_inicio.png') });

  await page.click('#btn-start');
  await page.waitForFunction(() => document.getElementById('start').hidden, null, { timeout: 90000 });
  check('Cámara iniciada (arReady)', true);

  const waitEvent = async (name, ms) => {
    const t0 = Date.now();
    while (Date.now() - t0 < ms) {
      if (events.some((e) => e.t.includes(name) && e.at >= t0 - 50)) return true;
      await page.waitForTimeout(200);
    }
    return false;
  };
  // Esperar al primer reconocimiento (el vídeo empieza con el póster)
  let found = events.some((e) => e.t.includes('targetFound')) || await waitEvent('targetFound', 60000);
  check('Reconocimiento del póster (targetFound)', found);
  await page.waitForTimeout(1500);

  const st = () => page.evaluate(() => {
    const cam = document.getElementById('camelia');
    const tex = cam.getObject3D('mesh').material.map;
    const target = document.getElementById('target').object3D;
    return { visible: target.visible, offset: tex ? tex.offset.x : null,
      story: !document.getElementById('story').hidden, status: document.getElementById('status').hidden ? '' : document.getElementById('status').textContent,
      broche: document.getElementById('broche').getAttribute('visible') };
  });
  const offsets = new Set();
  for (let k = 0; k < 8; k++) { offsets.add((await st()).offset); await page.waitForTimeout(110); }
  check('Animación en bucle (cambian los fotogramas)', offsets.size >= 4, `${offsets.size} fotogramas distintos en ~0,9 s`);
  await page.screenshot({ path: path.join(REV, 'prueba_2_reconocido.png') });

  await page.click('#btn-pause');
  const p1 = (await st()).offset; await page.waitForTimeout(600); const p2 = (await st()).offset;
  check('Botón Pausar detiene la animación', p1 === p2 && (await page.textContent('#btn-pause')) === 'Reanudar');
  await page.click('#btn-pause');
  const r1 = (await st()).offset; await page.waitForTimeout(600); const r2 = (await st()).offset;
  check('Botón Reanudar continúa la animación', r1 !== r2 && (await page.textContent('#btn-pause')) === 'Pausar');

  await page.click('#btn-story');
  await page.waitForTimeout(300);
  const s = await st();
  const storyText = (await page.textContent('#story')).trim();
  check('Revelar historia muestra broche y texto', s.broche === true && s.story && storyText.includes('Este broche conserva el recuerdo de mi madre'), storyText);
  await page.screenshot({ path: path.join(REV, 'prueba_3_historia.png') });

  // El vídeo muestra el póster 10 s y luego 5 s sin póster
  const lost = await waitEvent('targetLost', 20000);
  await page.waitForTimeout(300);
  const l = await st();
  check('Pérdida del póster oculta contenido y avisa', lost && !l.visible && !l.story && l.status === 'Vuelve a enfocar el póster', `mensaje: «${l.status}»`);
  await page.screenshot({ path: path.join(REV, 'prueba_4_perdido.png') });

  const again = await waitEvent('targetFound', 30000);
  await page.waitForTimeout(500);
  const a = await st();
  check('Recupera el póster y vuelve a mostrar la historia abierta', again && a.visible && a.story);
} finally {
  await browser.close();
  server.close();
}
const ok = results.every((r) => r.ok);
await writeFile(path.join(REV, 'prueba_automatica.json'), JSON.stringify({ fecha: new Date().toISOString(), camara: 'simulada', resultados: results }, null, 2));
console.log(ok ? '\nTodas las comprobaciones automáticas pasaron (cámara simulada).' : '\nHay comprobaciones fallidas.');
process.exit(ok ? 0 : 1);
