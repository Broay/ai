from flask import Flask, render_template_string, jsonify, request, Response
import time, io, os, requests, threading, base64, random, json, traceback
from threading import Lock
from urllib.parse import urljoin

app = Flask(__name__)

# --- NETSWAP SOVEREIGN IMPERIAL-CONTROL v137.0 ---
# Vizyon: Bireysel cüzdan yönetimi, anlık hız vanası ve mutlak otorite. [cite: 2026-01-03]
VERSION = "v137.0"
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

MOBILE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-A556B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36",
    "X-Requested-With": "com.android.chrome"
}

transaction_lock = Lock()
state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "actual_mbps": 0.0,
    "last_op_time": time.perf_counter(),
    "global_lock": False,
    "evolution_count": 38,
    "s100_temp": "34°C",
    "banned_peers": [],
    "user_registry": {} # Bireysel veri tabanı [cite: 2026-01-03]
}

def check_admin_auth(req):
    ua = req.headers.get('User-Agent', '').upper()
    key = req.args.get('key')
    pin = req.args.get('pin', '').strip()
    is_a55 = "437F" in ua or "SM-A55" in ua or "MOBILE" in ua
    if key == ADMIN_KEY and pin == ADMIN_PIN and is_a55: return True
    return False

# --- IMPERIAL CONTROL API ---
@app.route('/overlord_api/<action>')
def admin_api(action):
    if not check_admin_auth(request): return "YETKİSİZ", 403
    target = request.args.get('target_peer')
    val = request.args.get('value', 0)
    
    with transaction_lock:
        if action == "lock": state["global_lock"] = not state["global_lock"]
        elif target in state["user_registry"]:
            if action == "gift": state["user_registry"][target]["credits"] += float(val)
            elif action == "throttle": state["user_registry"][target]["max_mbps"] = float(val)
            elif action == "kick": state["user_registry"][target]["status"] = "KICKED"
            elif action == "ban": state["banned_peers"].append(target)
    return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "<h1>REDDEDİLDİ</h1>", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Imperial Control v137</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono">
    <div class="border-b-2 border-red-600 pb-4 mb-6 flex justify-between items-center">
        <h1 class="text-2xl font-black text-red-600 italic">IMPERIAL CONTROL</h1>
        <button onclick="f('lock')" class="bg-red-900 px-6 py-2 rounded-full font-bold text-[10px]">GLOBAL KİLİT</button>
    </div>

    <div class="bg-zinc-950 rounded-3xl border border-zinc-900 overflow-hidden shadow-2xl">
        <div class="p-4 bg-zinc-900/50 text-xs font-bold text-red-500 uppercase tracking-widest italic">Anlık Tabiyet ve Müdahale Listesi</div>
        <table class="w-full text-[10px] text-left">
            <thead class="bg-black text-zinc-600">
                <tr><th class="p-4">PEER ID</th><th>BAKİYE (MB)</th><th>HIZ SINIRI</th><th>VERİ AKIŞI</th><th>MÜDAHALE</th></tr>
            </thead>
            <tbody id="userTable"></tbody>
        </table>
    </div>

    <script>
        const k="{{a_key}}", p="{{a_pin}}";
        async function f(a, t="", v=0){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${v}`); }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json();
            let html="";
            for(let id in d.user_registry){
                let u = d.user_registry[id];
                html += `<tr class="border-b border-zinc-900 hover:bg-zinc-900/30 transition">
                    <td class="p-4 font-bold ${u.status=='ACTIVE'?'text-white':'text-red-700'}">${id}</td>
                    <td class="text-green-500 font-black">${u.credits.toFixed(2)}</td>
                    <td class="text-blue-400 font-bold">${u.max_mbps} Mbps</td>
                    <td>${u.received.toFixed(1)} / ${u.sent.toFixed(1)} MB</td>
                    <td>
                        <button onclick="f('gift','${id}', 50)" class="text-green-500 underline mr-2">+50</button>
                        <button onclick="f('gift','${id}', -50)" class="text-red-400 underline mr-2">-50</button>
                        <button onclick="f('throttle','${id}', 1)" class="text-yellow-500 underline mr-2">KIS (1M)</button>
                        <button onclick="f('kick','${id}')" class="text-orange-600 underline">KICK</button>
                    </td>
                </tr>`;
            }
            document.getElementById('userTable').innerHTML = html; setTimeout(update, 1000);
        } update();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

@app.route('/action/<type>')
def handle_action(type):
    now = time.perf_counter()
    p_id = request.args.get('peer_id', 'GUEST')
    with transaction_lock:
        if p_id in state["banned_peers"]: return jsonify({"error": "BANNED"}), 403
        if state["global_lock"] and type != "stop": return jsonify({"error": "LOCKED"}), 423
        
        # Bireysel Cüzdan ve Hız Kaydı [cite: 2026-01-03]
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {"credits": 50.0, "max_mbps": 96.0, "received": 0, "sent": 0, "status": "ACTIVE", "last_seen": ""}
        
        user = state["user_registry"][p_id]
        if user["status"] == "KICKED" and type == "receive": return jsonify({"error": "KICKED"}), 401
        
        dt, state["last_op_time"] = now - state["last_op_time"], now
        # Hız Vanası Uygulama: Random hız artık bireysel sınırı geçemez [cite: 2026-01-03]
        state["actual_mbps"] = round(random.uniform(1.0, user["max_mbps"]), 2)
        
        data_mb = (state["actual_mbps"] / 8) * dt
        
        if type == "share":
            user["credits"] += data_mb
            user["sent"] += data_mb
        elif type == "receive":
            if user["credits"] <= 0: return jsonify({"error": "No Credits"}), 402
            user["credits"] = max(0, user["credits"] - data_mb)
            user["received"] += data_mb
            
        user["last_seen"] = time.strftime('%H:%M:%S')
    return jsonify(state)

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NetSwap Hub</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-green-500 font-mono p-4" onload="mainLoop()">
    <div class="text-center mb-10"><h1 class="text-3xl font-black text-blue-600 italic uppercase">IMPERIAL HUB</h1><p class="text-[8px] text-zinc-600">v137.0 Imperial-Control Ready</p></div>
    <div class="bg-zinc-950 p-12 rounded-[40px] border-2 border-zinc-900 mb-10 text-center">
        <div id="credits" class="text-7xl font-black text-white italic">0.00</div><span class="text-[10px] text-zinc-700 uppercase mt-4 block">KİŞİSEL CÜZDAN (MB)</span>
    </div>
    <div class="grid grid-cols-2 gap-4"><button onclick="control('share')" class="py-10 bg-green-700 text-black font-black rounded-3xl text-3xl transition active:scale-90 shadow-xl">VER (+)</button>
    <button onclick="control('receive')" class="py-10 bg-blue-700 text-white font-black rounded-3xl text-3xl transition active:scale-90 shadow-xl">AL (-)</button></div>
    <div id="secretSpot" onclick="triggerAdmin()" class="fixed bottom-0 right-0 w-24 h-24 opacity-0"></div>
    <script>
        let myId = "NS-" + Math.floor(1000 + Math.random() * 9000);
        function triggerAdmin() {
            window.clickCount = (window.clickCount || 0) + 1;
            if(window.clickCount >= 5) {
                const pin = prompt("Hükümdar PIN:");
                if(pin) window.location.href = `/overlord?key={{a_key}}&pin=` + pin.trim();
                window.clickCount = 0;
            }
            setTimeout(() => { window.clickCount = 0; }, 3000);
        }
        async function control(type) { await fetch(`/action/${type}?peer_id=${myId}`); }
        async function mainLoop() {
            try {
                const res = await fetch('/api/status'); const data = await res.json();
                let myData = data.user_registry[myId] || {credits: 0};
                document.getElementById('credits').innerText = myData.credits.toFixed(2);
                if(data.is_active) await fetch(`/action/${data.mode==='SHARING'?'share':'receive'}?peer_id=${myId}`);
            } catch(e) {} setTimeout(mainLoop, 1000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
