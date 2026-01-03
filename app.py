from flask import Flask, render_template_string, jsonify, request, Response
import time, io, os, requests, threading, base64, random, json, traceback
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN LINK-FIXER v130.0 ---
# Amacı: 404 hatalarını aşmak için Direct Link Injection ve Overlord Fix. [cite: 2026-01-03]
VERSION = "v130.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"
ADMIN_KEY = "ali_yigit_overlord_A55" 

transaction_lock = Lock()
state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "internet_credits_mb": 120.0, # Bakiyen image_6b37bf'den mühürlendi
    "actual_mbps": 0.0,
    "last_op_time": time.perf_counter(),
    "ai_status": "Link Onarıldı",
    "global_lock": False,
    "banned_peers": [],
    "evolution_count": 30,
    "s100_temp": "34°C"
}

def github_seal(filename, data, message):
    if not GH_TOKEN: return
    try:
        headers = {"Authorization": f"token {GH_TOKEN}"}
        url = f"https://api.github.com/repos/{GH_REPO}/contents/{filename}"
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        content = json.dumps(data, indent=4)
        payload = {"message": message, "content": base64.b64encode(content.encode()).decode(), "sha": sha}
        requests.put(url, headers=headers, json=payload)
    except: pass

@app.route('/overlord_api/<action>')
def admin_api(action):
    if request.args.get('key') != ADMIN_KEY: return "ERİŞİM REDDEDİLDİ", 403
    with transaction_lock:
        if action == "lock": state["global_lock"] = not state["global_lock"]
        elif action == "gift": state["internet_credits_mb"] += 100.0
    return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if request.args.get('key') != ADMIN_KEY: return "Admin Key Hatası", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Overlord v130</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-red-500 p-6 font-monospace">
    <div class="border border-red-900 p-4 rounded-xl mb-6">
        <h1 class="text-xl font-black">HÜKÜMDAR KONSOLU</h1>
        <p class="text-[8px]">BAKİYE: <span id="c" class="text-white">...</span> MB</p>
    </div>
    <button onclick="f('gift')" class="w-full py-3 bg-green-900 text-white font-bold rounded mb-2">100 MB EKLE</button>
    <button onclick="f('lock')" class="w-full py-3 bg-red-900 text-white font-bold rounded">GLOBAL KİLİT</button>
    <script>
        const k = "{{ a_key }}";
        async function f(a){ await fetch(`/overlord_api/${a}?key=${k}`); }
        async function u(){
            const r = await fetch('/api/status');
            const d = await r.json();
            document.getElementById('c').innerText = d.internet_credits_mb.toFixed(2);
            setTimeout(u, 2000);
        } u();
    </script>
</body></html>
""", a_key=ADMIN_KEY)

@app.route('/action/<type>')
def handle_action(type):
    now = time.perf_counter()
    with transaction_lock:
        if state["global_lock"] and type != "stop": return jsonify({"error": "LOCKED"}), 423
        dt = now - state["last_op_time"]
        state["last_op_time"] = now
        state["actual_mbps"] = round(random.uniform(5.0, 98.0), 2)
        if type == "share":
            state["is_active"], state["mode"] = True, "SHARING"
            state["internet_credits_mb"] += round((state["actual_mbps"]/8)*dt, 6)
        elif type == "receive":
            state["is_active"], state["mode"] = True, "RECEIVING"
            state["internet_credits_mb"] = max(0, round(state["internet_credits_mb"] - (state["actual_mbps"]/8)*dt, 6))
        elif type == "stop":
            state["is_active"], state["mode"] = False, "IDLE"
            github_seal("credits.json", {"credits": state["internet_credits_mb"]}, "Final Seal v130")
    return jsonify(state)

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetSwap Hub v130</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4" onload="mainLoop()">
    <div class="text-center mb-8">
        <h1 class="text-3xl font-black italic text-blue-500 uppercase">NETSWAP HUB</h1>
        <p class="text-[9px] text-zinc-600">PAÜ Programcılık - v130.0</p>
    </div>

    <div class="bg-zinc-950 p-10 rounded-3xl border-2 border-zinc-900 mb-8 text-center">
        <div id="credits" class="text-7xl font-black text-white italic">0.00</div>
        <span class="text-[10px] text-zinc-700 uppercase">DOĞRULANMIŞ REZERV</span>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-8">
        <button onclick="control('share')" class="py-8 bg-green-700 text-black font-black rounded-2xl text-2xl active:scale-95 transition">VER</button>
        <button onclick="control('receive')" class="py-8 bg-blue-700 text-white font-black rounded-2xl text-2xl active:scale-95 transition">AL</button>
    </div>

    <button onclick="control('stop')" class="w-full py-4 bg-zinc-900 text-red-500 font-bold rounded-xl border border-zinc-800 mb-20 text-xs">DURDUR</button>

    <div class="text-center opacity-20 hover:opacity-100 transition">
        <a href="/overlord?key={{ a_key }}" class="text-[9px] text-zinc-800 font-bold uppercase tracking-widest underline">Hükümdar Girişi</a>
    </div>

    <script>
        async function control(type) { await fetch('/action/' + type); }
        async function mainLoop() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('credits').innerText = data.internet_credits_mb.toFixed(2);
                if(data.is_active) await fetch('/action/' + (data.mode === 'SHARING' ? 'share' : 'receive'));
            } catch(e) {}
            setTimeout(mainLoop, 1000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
