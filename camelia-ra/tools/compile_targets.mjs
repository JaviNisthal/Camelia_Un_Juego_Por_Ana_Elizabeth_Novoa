// Compila entrega/camelia_poster.png en assets/targets.mind con el compilador oficial de MindAR,
// ejecutado en Chromium sin ventana.
//
// Uso:  node tools/compile_targets.mjs [ruta/del/poster.png]
// Requiere: npm install playwright-core   y un Chromium (variable CHROMIUM_PATH si no está en /opt/pw-browsers).
import { createServer } from 'node:http';
import { readFile, writeFile, readdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const poster = path.resolve(process.argv[2] || path.join(ROOT, 'entrega', 'camelia_poster.png'));
const out = path.join(ROOT, 'assets', 'targets.mind');

async function findChromium() {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;
  const base = '/opt/pw-browsers';
  if (!existsSync(base)) return undefined; // playwright-core usará su navegador si está instalado
  for (const d of (await readdir(base)).sort().reverse()) {
    const p = path.join(base, d, 'chrome-linux', 'chrome');
    if (d.startsWith('chromium-') && existsSync(p)) return p;
  }
  return undefined;
}

const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg' };
const server = createServer(async (req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  const file = url === '/poster' ? poster : path.join(ROOT, 'tools', 'compiler', path.basename(url));
  try {
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404); res.end();
  }
});
await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
const port = server.address().port;

const browser = await chromium.launch({ executablePath: await findChromium(), args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl'] });
try {
  const page = await browser.newPage();
  page.on('console', (m) => console.log('[navegador]', m.text()));
  await page.goto(`http://127.0.0.1:${port}/compile.html`);
  await page.waitForFunction(() => window.ready === true);
  const t0 = Date.now();
  const b64 = await page.evaluate(() => window.compileTarget('/poster'), null, { timeout: 0 });
  await writeFile(out, Buffer.from(b64, 'base64'));
  const sha = createHash('sha256').update(await readFile(poster)).digest('hex');
  console.log(`targets.mind: ${out} (${Math.round(b64.length * 0.75 / 1024)} KB, ${((Date.now() - t0) / 1000).toFixed(1)} s)`);
  console.log(`Compilado desde ${poster}\nSHA-256 del póster: ${sha}`);
  const cfgPath = path.join(ROOT, 'assets', 'config.json');
  const cfg = existsSync(cfgPath) ? JSON.parse(await readFile(cfgPath, 'utf8')) : {};
  if (cfg.poster && cfg.poster.sha256 && cfg.poster.sha256 !== sha) {
    console.log('AVISO: este archivo NO es el póster final registrado por make_poster.py.');
  }
  cfg.targets = { compiledFrom: path.relative(ROOT, poster), posterSha256: sha, mindar: '1.2.5' };
  await writeFile(cfgPath, JSON.stringify(cfg, null, 2));
} finally {
  await browser.close();
  server.close();
}
