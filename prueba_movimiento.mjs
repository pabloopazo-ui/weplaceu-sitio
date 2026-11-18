// Prueba del movimiento del sitio WPU en Chrome real (página activa), con y sin «reducir movimiento».
// Uso: node prueba_movimiento.mjs [--base=http://localhost:8773/sitio]   (fuera del sandbox)
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const BASE = (process.argv.find(a => a.startsWith("--base=")) || "").split("=")[1] || "http://localhost:8773/sitio";
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PUERTO = 9800 + Math.floor(Math.random() * 150);
const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PUERTO}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), "mov-wpu-"))}`, "about:blank"], { stdio: "ignore" });
const espera = ms => new Promise(r => setTimeout(r, ms));
let url;
for (let i = 0; i < 50 && !url; i++) { await espera(200); try { const t = await (await fetch(`http://127.0.0.1:${PUERTO}/json/list`)).json(); url = t.find(x => x.type === "page")?.webSocketDebuggerUrl; } catch {} }
const ws = new WebSocket(url); await new Promise(r => ws.addEventListener("open", r));
let n = 0; const pend = new Map();
ws.addEventListener("message", e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
const cdp = (method, params = {}) => new Promise(res => { const id = ++n; pend.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
const ev = async x => (await cdp("Runtime.evaluate", { expression: x, awaitPromise: true, returnByValue: true })).result?.result?.value;
await cdp("Emulation.setDeviceMetricsOverride", { width: 1366, height: 900, deviceScaleFactor: 1, mobile: false });

const MEDIR = `(async()=>{const on=()=>[...document.querySelectorAll('.hero-slide')].findIndex(s=>s.classList.contains('on'));
 const svg=document.querySelector('.tv-mapa svg'), feed=document.querySelector('.tv-feed'); const f0=feed.firstChild.textContent, a=on(), t0=svg.getCurrentTime();
 await new Promise(r=>setTimeout(r,3400)); const b=on(), t1=svg.getCurrentTime();
 const ref=document.querySelector('#control-tower'); ref.scrollIntoView(); await new Promise(r=>setTimeout(r,1200));
 const p=+getComputedStyle(document.querySelector('.progreso')).getPropertyValue('--p'); const f1=feed.firstChild.textContent;
 const dot=document.querySelector('.movil-dot').getBoundingClientRect(); await new Promise(r=>setTimeout(r,800)); const dot2=document.querySelector('.movil-dot').getBoundingClientRect();
 const reveal=[...document.querySelectorAll('#control-tower .reveal')].map(e=>getComputedStyle(e).opacity);
 return {carrusel_avanza:a!==b, rutas_animadas:t1>t0, unidad_se_mueve:Math.abs(dot.x-dot2.x)+Math.abs(dot.y-dot2.y)>1, eventos_nuevos:f0!==f1,
   progreso:+p.toFixed(2), cabecera_compacta:document.querySelector('.nav').classList.contains('scrolled'), apariciones_visibles:reveal.every(o=>+o>0.9)};})()`;

for (const reducido of [false, true]) {
  await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: reducido ? "reduce" : "no-preference" }] });
  await cdp("Page.navigate", { url: `${BASE}/index.html` }); await espera(1500);
  console.log(reducido ? "Con «reducir movimiento»:" : "Normal:", JSON.stringify(await ev(MEDIR)));
}
ws.close(); chrome.kill();
