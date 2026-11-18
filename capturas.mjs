// Capturas de página completa del sitio WPU, en teléfono real (emulación por CDP) y en escritorio.
// Recorre cada página para que carguen las fotos diferidas antes de capturar.
// Uso: node capturas.mjs [--base=http://localhost:8773/sitio] [--anchos=390,1366] [--solo=index,industrias] [--salida=_capturas]
// Corre fuera del sandbox (Chrome necesita su perfil y su puerto).
import { spawn } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const arg = (k, d) => (process.argv.find(a => a.startsWith(`--${k}=`)) || "").split("=")[1] || d;
const BASE = arg("base", "http://localhost:8773/sitio");
const ANCHOS = arg("anchos", "390,1366").split(",").map(Number);
const TODAS = ["index", "transporte-por-sus-propios-medios", "distribucion-retail-b2b", "cross-docking", "torre-de-control", "industrias", "nosotros",
  "blog", "preguntas-frecuentes", "contacto", "privacidad", "blog/traslado-por-sus-propios-medios", "blog/cross-docking", "blog/seguimiento-de-carga"];
const SOLO = arg("solo", "") ? arg("solo").split(",") : TODAS;
const SALIDA = join(AQUI, arg("salida", "_capturas")); mkdirSync(SALIDA, { recursive: true });

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PUERTO = 9400 + Math.floor(Math.random() * 400);
const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PUERTO}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), "cap-wpu-"))}`,
  "--hide-scrollbars", "--no-first-run", "about:blank"], { stdio: "ignore" });
const espera = ms => new Promise(r => setTimeout(r, ms));
async function conectar() {
  for (let i = 0; i < 50; i++) { await espera(200);
    try { const t = await (await fetch(`http://127.0.0.1:${PUERTO}/json/list`)).json(); const p = t.find(x => x.type === "page"); if (p) return p.webSocketDebuggerUrl; } catch {} }
  throw new Error("Chrome no respondió");
}
const ws = new WebSocket(await conectar());
await new Promise(r => ws.addEventListener("open", r));
let n = 0; const pend = new Map();
ws.addEventListener("message", e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
const cdp = (method, params = {}) => new Promise(res => { const id = ++n; pend.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
const evaluar = async expr => (await cdp("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result?.result?.value;
await cdp("Page.enable");

for (const W of ANCHOS) {
  const movil = W < 768;
  await cdp("Emulation.setDeviceMetricsOverride", { width: W, height: movil ? 844 : 900, deviceScaleFactor: 1, mobile: movil });
  await cdp("Emulation.setTouchEmulationEnabled", { enabled: movil });
  for (const p of SOLO) {
    await cdp("Page.navigate", { url: `${BASE}/${p}.html?estatico` }); await espera(1200);
    await evaluar(`(async()=>{const H=document.documentElement.scrollHeight;for(let y=0;y<H;y+=500){scrollTo(0,y);await new Promise(r=>setTimeout(r,40));}scrollTo(0,0);
      await Promise.all([...document.images].map(i=>i.complete&&i.naturalWidth?0:new Promise(r=>{i.onload=i.onerror=r;setTimeout(r,4000);})));
      await document.fonts.ready; return true;})()`);
    await espera(300);
    // por tramos de pantalla: capturar la página entera de una vez deja sin pintar las fotos que están fuera de pantalla
    const H = await evaluar("document.documentElement.scrollHeight"), V = movil ? 844 : 900;
    const base = `${W}_${p.replace("/", "_")}`;
    let k = 0;
    for (let y = 0; y < H; y += V, k++) {
      await evaluar(`(async()=>{scrollTo(0,${y});await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));await new Promise(r=>setTimeout(r,150));return 1;})()`);
      const r = await cdp("Page.captureScreenshot", { format: "jpeg", quality: 70 });
      writeFileSync(join(SALIDA, `${base}__${String(k).padStart(2, "0")}.jpg`), Buffer.from(r.result.data, "base64"));
    }
    console.log(base, H, k, "tramos");
  }
}
ws.close(); chrome.kill();
