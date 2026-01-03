from flask import Flask, render_template_string, jsonify, request, Response
import time, io, os, requests, threading, base64, random, json, traceback
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN IDENTITY-FIX v132.0 ---
# Amacı: A55 kimlik doğrulama hatasını gidermek ve güvenliği mühürlemek. [cite: 2026-01-03]
VERSION = "v132.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" # Ali Yiğit, PIN kodun bu [cite: 2026-01-03]

transaction_lock = Lock()
state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "internet_credits_mb": 120.0,
    "actual_mbps": 0.0,
    "last_op_time": time.perf_counter(),
    "ai_status": "Kimlik Onarıldı",
    "global_lock": False,
    "evolution_count": 32,
    "s100_temp": "34°C"
}

def check_admin_auth(req):
    """Cihaz kimliğini ve PIN'i daha esnek ama güvenli doğrular [cite: 2026-01-03]"""
    ua = req.headers.get('User-Agent', '')
    key = req.args.get('key')
    pin = req.args.get('pin', '').strip()
    
    # PC Koruması: Sadece Samsung A55 modellerine izin ver
    is_a55 = "SM-A55" in ua or "A556" in ua
    is_key_valid = key == ADMIN_KEY
    is_pin_valid = pin == ADMIN_PIN
    
    if is_a55 and is_key_valid and is_pin_valid:
        return True, "OK"
    return False, f"Hata: Cihaz:{is_a55}, Key:{is_key_valid}, PIN:{is_pin_valid}"

@app.route('/overlord_api/<action>')
def admin_api(action):
    auth_ok, msg = check_admin_auth(request)
    if not auth_ok: return msg, 403
    with transaction_lock:
        if action == "lock": state["global_lock"] = not state["global_lock"]
        elif action == "gift": state["internet_credits_mb"] += 100.0
    return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    auth_ok, msg = check_admin_auth(request)
    if not auth_ok: return f"<h1>{msg}</h1>", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Vault v132</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-red-500 p-6 font-mono">
    <div class="border-2 border-red-900 p-4 rounded-3xl mb-6 bg-red-950/20">
        <h1 class="text-xl font-black italic">HÜKÜMDAR KASASI</h1>
        <p class="text-[9px] text-zinc-500">KİMLİK: SAMSUNG A55</p>
    </div>
    <div class="bg-zinc-900 p-6 rounded-2xl mb-4 text-center border border-zinc-800">
        <div id="c" class="text-4xl font-black text-white italic">...</div>
        <p class="text-[10px] text-zinc-600 uppercase mt-2 tracking-widest">Rezerv Rezervi</p>
    </div>
    <button onclick="f('gift')" class="w-full py-5 bg-green-800 text-white font-black rounded-xl mb-3 shadow-xl active:scale-95 transition">100 MB EKLE</button>
    <button onclick="f('lock')" class="w-full py-5 bg-red-800 text-white font-black rounded-xl shadow-xl active:scale-95 transition">SİSTEMİ KİLİTLE</button>
    <script>
        const k = "{{ a_key }}"; const p = "{{ a_pin }}";
        async function f(a){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}`); }
        async function u(){
            const r = await fetch('/api/status'); const d = await r.json();
            document.getElementById('c').innerText = d.internet_credits_mb.toFixed(2) + " MB";
            setTimeout(u, 1500);
        } u();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

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
    <title>NetSwap Hub v132</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4" onload="mainLoop()">
    <div class="text-center mb-10">
        <h1 class="text-3xl font-black italic text-blue-500 uppercase">NETSWAP HUB</h1>
        <p class="text-[9px] text-zinc-600">Sovereign Fix v132.0</p>
    </div>

    <div class="bg-zinc-950 p-12 rounded-[40px] border-2 border-zinc-900 mb-10 text-center shadow-2xl">
        <div id="credits" class="text-7xl font-black text-white italic">0.00</div>
        <span class="text-[10px] text-zinc-700 font-bold uppercase mt-4 block tracking-widest">GÜVENLİ MB</span>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-10">
        <button onclick="control('share')" class="py-10 bg-green-700 text-black font-black rounded-3xl text-3xl active:scale-90 transition">VER</button>
        <button onclick="control('receive')" class="py-10 bg-blue-700 text-white font-black rounded-3xl text-3xl active:scale-90 transition">AL</button>
    </div>

    <div id="secretSpot" onclick="triggerAdmin()" class="fixed bottom-0 right-0 w-20 h-20 opacity-0 cursor-default"></div>

    <script>
        let clickCount = 0;
        function triggerAdmin() {
            clickCount++;
            if(clickCount >= 5) {
                const pin = prompt("HÜKÜMDAR PIN KODUNU GİRİN:");
                if(pin) window.location.href = `/overlord?key={{ a_key }}&pin=` + pin.trim();
                clickCount = 0;
            }
            setTimeout(() => { clickCount = 0; }, 3000);
        }

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
