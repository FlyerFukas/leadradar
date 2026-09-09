"""LeadRadar Kontrol Paneli — yerel web arayuzu.

Tarama baslatmadan once sehir, semt ve sektorleri secmeni saglar; dosya
duzenlemeye gerek kalmaz. Firecrawl'i da buradan acip kapatabilirsin.

Kullanim:
    py panel.py
Ardindan tarayici otomatik acilir: http://127.0.0.1:8765
(Acilmazsa bu adresi elle yaz.)

Bagimlilik yok — Python'un yerlesik http.server modulunu kullanir.
"""

import html
import json
import os
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from leadradar.config import load_config

CFG = load_config(os.path.join(BASE_DIR, "config.json"))
PORT = 8765

# Calisan islerin durumu: id -> {proc, log_path, pdf, done, started}
JOBS = {}


# ----------------------------- HTML -----------------------------

def render_form():
    cities = "".join(
        f'<option value="{html.escape(c)}"{" selected" if c == "Berlin" else ""}>{html.escape(c)}</option>'
        for c in CFG["city_catalog"].keys()
    )
    labels = CFG.get("sector_labels_tr", {})
    default_sectors = {"Friseur", "Restaurant", "Zahnarzt", "Fitnessstudio"}
    sectors = ""
    for key in CFG["category_osm"].keys():
        tr = labels.get(key, key)
        checked = " checked" if key in default_sectors else ""
        sectors += (
            f'<label class="chip"><input type="checkbox" name="sector" value="{html.escape(key)}"{checked}>'
            f'<span>{html.escape(tr)}<small>{html.escape(key)}</small></span></label>'
        )
    return PAGE.replace("{{CITIES}}", cities).replace("{{SECTORS}}", sectors)


PAGE = """<!doctype html>
<html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LeadRadar — Lead Avcısı Kontrol Paneli</title>
<style>
  :root { --navy:#1a1a2e; --accent:#2d6cdf; --bg:#f4f4f8; --line:#d9d9e3; }
  * { box-sizing:border-box; }
  body { font-family:Segoe UI,Arial,sans-serif; background:var(--bg); margin:0; color:#222230; }
  header { background:var(--navy); color:#fff; padding:22px 28px; }
  header h1 { margin:0; font-size:22px; }
  header p { margin:6px 0 0; opacity:.75; font-size:13px; }
  .wrap { max-width:900px; margin:22px auto; padding:0 18px; }
  .card { background:#fff; border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,.06); padding:22px; margin-bottom:18px; }
  h2 { font-size:15px; margin:0 0 12px; color:var(--navy); }
  label.field { display:block; margin-bottom:14px; font-size:13px; font-weight:600; }
  input[type=text], input[type=number], select { width:100%; padding:9px 11px; border:1px solid var(--line);
    border-radius:8px; font-size:14px; margin-top:5px; font-family:inherit; }
  .row { display:flex; gap:16px; flex-wrap:wrap; }
  .row > * { flex:1; min-width:180px; }
  .grid { display:flex; flex-wrap:wrap; gap:8px; }
  .chip { position:relative; }
  .chip input { position:absolute; opacity:0; }
  .chip span { display:block; padding:8px 12px; border:1px solid var(--line); border-radius:20px;
    cursor:pointer; font-size:13px; font-weight:600; background:#fafafe; user-select:none; }
  .chip span small { display:block; font-weight:400; opacity:.55; font-size:10px; }
  .chip input:checked + span { background:var(--accent); color:#fff; border-color:var(--accent); }
  .chip input:checked + span small { opacity:.8; }
  .toggle { display:flex; align-items:center; gap:10px; font-size:13px; font-weight:600; margin-top:6px; }
  .hint { font-size:12px; color:#777; font-weight:400; margin-top:4px; }
  button { background:var(--accent); color:#fff; border:0; padding:13px 28px; border-radius:9px;
    font-size:15px; font-weight:700; cursor:pointer; }
  button:disabled { opacity:.5; cursor:not-allowed; }
  .btnrow { display:flex; gap:10px; align-items:center; }
  #log { background:#12121e; color:#d6e4ff; font-family:Consolas,monospace; font-size:12.5px;
    padding:14px; border-radius:9px; height:300px; overflow:auto; white-space:pre-wrap; display:none; }
  #result { display:none; margin-top:14px; padding:14px; background:#eef7ee; border:1px solid #bfe0bf;
    border-radius:9px; font-size:14px; }
  #result a { color:var(--accent); font-weight:700; }
  .muted { color:#888; font-size:12px; }
</style></head>
<body>
<header>
  <h1>🏗️ LeadRadar — Lead Avcısı</h1>
  <p>Taramayı başlatmadan önce şehir, semt ve sektörleri seç. Çıktı: output/ klasörüne PDF.</p>
</header>
<div class="wrap">
  <form id="f">
    <div class="card">
      <h2>1) Konum</h2>
      <div class="row">
        <label class="field">Şehir
          <select name="city" id="city">{{CITIES}}</select>
          <div class="hint">Listede yoksa aşağıya elle yazabilirsin.</div>
        </label>
        <label class="field">Şehir (elle, opsiyonel)
          <input type="text" name="city_custom" placeholder="ör. Regensburg">
        </label>
      </div>
      <label class="field">Semtler (opsiyonel, virgülle ayır)
        <input type="text" name="districts" placeholder="boş bırak = tüm şehir taranır">
        <div class="hint">Örn: Mitte, Neukölln, Kreuzberg — boş bırakırsan bütün şehir taranır.</div>
      </label>
    </div>

    <div class="card">
      <h2>2) Sektörler</h2>
      <div class="grid">{{SECTORS}}</div>
      <div class="hint" style="margin-top:10px">İstediğin kadar sektör seçebilirsin.</div>
    </div>

    <div class="card">
      <h2>3) Ayarlar</h2>
      <div class="row">
        <label class="field">Kaç aday raporlansın?
          <input type="number" name="target_leads" value="10" min="1" max="50">
        </label>
        <label class="field">Firecrawl zenginleştirme
          <span class="toggle"><input type="checkbox" name="firecrawl" checked> Puan/yorum + JS'li site tarama (açık)</span>
          <div class="hint">Kapatırsan sistem tamamen ücretsiz çalışır.</div>
        </label>
      </div>
      <div class="btnrow">
        <button type="submit" id="go">▶ Taramayı Başlat</button>
        <span class="muted" id="status"></span>
      </div>
    </div>
  </form>

  <div class="card" id="logcard" style="display:none">
    <h2>Çalışma günlüğü</h2>
    <div id="log"></div>
    <div id="result"></div>
  </div>
</div>

<script>
const f = document.getElementById('f');
const go = document.getElementById('go');
const logEl = document.getElementById('log');
const logCard = document.getElementById('logcard');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');

f.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(f);
  const sectors = fd.getAll('sector');
  if (sectors.length === 0) { alert('En az bir sektör seç.'); return; }
  const body = {
    city: (fd.get('city_custom')||'').trim() || fd.get('city'),
    districts: (fd.get('districts')||'').split(',').map(s=>s.trim()).filter(Boolean),
    sectors: sectors,
    target_leads: parseInt(fd.get('target_leads')||'10'),
    firecrawl: fd.get('firecrawl') === 'on'
  };
  go.disabled = true; go.textContent = '⏳ Çalışıyor...';
  logCard.style.display = 'block'; logEl.style.display = 'block';
  resultEl.style.display = 'none'; logEl.textContent = '';
  statusEl.textContent = 'başlatılıyor...';

  const r = await fetch('/run', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const {id} = await r.json();

  const poll = setInterval(async () => {
    const s = await (await fetch('/status?id='+id)).json();
    logEl.textContent = s.log;
    logEl.scrollTop = logEl.scrollHeight;
    statusEl.textContent = s.done ? 'tamamlandı' : 'taranıyor...';
    if (s.done) {
      clearInterval(poll);
      go.disabled = false; go.textContent = '▶ Taramayı Başlat';
      if (s.pdf) {
        resultEl.innerHTML = '✅ Rapor hazır: <a href="/open?id='+id+'">PDF\\'i aç</a> &nbsp;·&nbsp; '
          + '<a href="/folder">output klasörünü aç</a>';
        resultEl.style.display = 'block';
      } else {
        resultEl.innerHTML = '⚠️ Çalışma bitti ama PDF bulunamadı. Günlüğe bak.';
        resultEl.style.display = 'block';
      }
    }
  }, 1500);
});
</script>
</body></html>"""


# ----------------------------- Sunucu -----------------------------

def _start_job(body):
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(BASE_DIR, "output")
    os.makedirs(out_dir, exist_ok=True)
    rc_path = os.path.join(out_dir, f"_panel_runconfig_{job_id}.json")

    city = body.get("city") or "Berlin"
    run_conf = {
        "city": city,
        "districts": body.get("districts") or [],
        "sectors": body.get("sectors") or [],
        "target_leads": body.get("target_leads") or 10,
        "firecrawl": bool(body.get("firecrawl", True)),
        "admin_level": CFG["city_catalog"].get(city),  # bilinmiyorsa None -> run.py "6|8" dener
    }
    with open(rc_path, "w", encoding="utf-8") as f:
        json.dump(run_conf, f, ensure_ascii=False)

    log_path = os.path.join(out_dir, f"_panel_log_{job_id}.txt")
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    log_f = open(log_path, "w", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, os.path.join(BASE_DIR, "run.py"), "--run-config", rc_path],
        stdout=log_f, stderr=subprocess.STDOUT, cwd=BASE_DIR, env=env,
    )
    JOBS[job_id] = {"proc": proc, "log_path": log_path, "log_f": log_f,
                    "pdf": None, "done": False}
    return job_id


def _job_status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return {"log": "(bilinmeyen iş)", "done": True, "pdf": None}
    try:
        with open(job["log_path"], encoding="utf-8", errors="replace") as f:
            log = f.read()
    except FileNotFoundError:
        log = ""
    if job["proc"].poll() is not None and not job["done"]:
        job["done"] = True
        try:
            job["log_f"].close()
        except Exception:
            pass
        # Son uretilen PDF'i bul
        for line in reversed(log.splitlines()):
            if "PDF raporu hazır:" in line:
                job["pdf"] = line.split("PDF raporu hazır:", 1)[1].strip()
                break
    return {"log": log, "done": job["done"], "pdf": job["pdf"]}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        self.wfile.write(body if isinstance(body, bytes) else body.encode("utf-8"))

    def log_message(self, *a):
        pass  # sessiz

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self._send(200, "text/html; charset=utf-8", render_form())
        elif self.path.startswith("/status"):
            qs = parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
            self._send(200, "application/json", json.dumps(_job_status(qs.get("id", [""])[0])))
        elif self.path.startswith("/open"):
            qs = parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
            job = JOBS.get(qs.get("id", [""])[0])
            if job and job.get("pdf") and os.path.exists(job["pdf"]):
                os.startfile(job["pdf"])  # noqa: S606 (Windows'ta PDF'i acar)
                self._send(200, "text/plain; charset=utf-8", "PDF açıldı.")
            else:
                self._send(404, "text/plain; charset=utf-8", "PDF bulunamadı.")
        elif self.path == "/folder":
            os.startfile(os.path.join(BASE_DIR, "output"))
            self._send(200, "text/plain; charset=utf-8", "Klasör açıldı.")
        else:
            self._send(404, "text/plain; charset=utf-8", "yok")

    def do_POST(self):
        if self.path == "/run":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            job_id = _start_job(body)
            self._send(200, "application/json", json.dumps({"id": job_id}))
        else:
            self._send(404, "text/plain; charset=utf-8", "yok")


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print("=" * 56)
    print("LeadRadar Kontrol Paneli çalışıyor:")
    print(f"   {url}")
    print("Kapatmak için bu pencerede Ctrl+C.")
    print("=" * 56)
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPanel kapatıldı.")
        server.shutdown()


if __name__ == "__main__":
    main()
