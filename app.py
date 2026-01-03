from flask import Flask, render_template_string, jsonify, request, Response
import time, io, os, requests, threading, base64, random, json, traceback
from threading import Lock
from urllib.parse import urljoin

app = Flask(__name__)

# --- NETSWAP SOVEREIGN ABSOLUTE-AUTHORITY v139.0 ---
# Vizyon: Dinamik miktar, Özel uyarı mesajı ve Tam müdahale gücü. [cite: 2026-01-03]
VERSION = "v139.0"
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
    "is_active": False, "mode": "IDLE", "actual_mbps": 0.0,
    "last_op_time": time.perf_counter(), "global_lock": False,
    "evolution_count": 40, "s100_temp": "34°C",
    "banned_peers": [], "user_registry": {} 
}

def check_admin_auth(req):
    ua = req.headers.get('User-Agent', '').upper()
    key, pin = req.args.get('key'), req.args.get('pin', '').strip()
    is_a55 = "437F" in ua or "SM-A55" in ua or "MOBILE" in ua or "ANDROID" in ua
    return key == ADMIN_KEY and pin == ADMIN_PIN and is_a55

@app.route('/overlord_api/<action>')
def admin_api(action):
    if not check_admin_auth(request): return "YETKİSİZ", 403
    target = request.args.get('target_peer')
    val = request.args.get('value', "")
    with transaction_lock:
        if action == "lock": state["global_lock"] = not state["global_lock"]
        elif target in state["user_registry"]:
            u = state["user_registry"][target]
            if action == "gift": u["credits"] = max(0, u["credits"] + float(val)) # Dinamik Miktar [cite: 2026-01-03]
            elif action == "reset": u["credits"] = 0 
            elif action == "throttle": u["max_mbps"] = float(val)
            elif action == "warn": u["alert"] = val # Özel Uyarı Metni [cite: 2026-01-03]
            elif action == "kick": u["status"] = "KICKED" # Atma Özelliği [cite: 2026-01-03]
            elif action == "ban": 
                if target not in state["banned_peers"]: state["banned_peers"].append(target)
    return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "<h1>REDDEDİLDİ</h1>", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Absolute Console</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono">
    <div class="border-b-2 border-red-600 pb-4 mb-6 flex justify-between items-center">
        <h1 class="text-xl font-black text-red-600 italic uppercase">Absolute Authority v139</h1>
        <button onclick="f('lock')" class="bg-red-900 px-4 py-1 rounded text-[8px] font-bold">AĞI KİLİTLE</button>
    </div>
    <div class="bg-zinc-950 rounded-2xl border border-zinc-900 overflow-hidden shadow-2xl">
        <table class="w-full text-[10px] text-left">
            <thead class="bg-black text-zinc-600"><tr><th class="p-4">ID</th><th>BAKİYE</th><th>HIZ</th><th>AKSİYON</th></tr></thead>
            <tbody id="userTable"></tbody>
        </table>
    </div>
    <script>
        const k="{{a_key}}", p="{{a_pin}}";
        async function f(a, t="", v=""){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${encodeURIComponent(v)}`); }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json();
            let html="";
            for(let id in d.user_registry){
                let u = d.user_registry[id];
                html += `<tr class="border-b border-zinc-900 hover:bg-zinc-900/20 transition">
                    <td class="p-4 text-white font-bold">${id}</td>
                    <td class="text-green-500 font-black">${u.credits.toFixed(2)} MB</td>
                    <td class="text-blue-400">${u.max_mbps}M</td>
                    <td>
                        <button onclick="f('gift','${id}', prompt('Ekle/Çıkar (MB):'))" class="text-green-600 underline mr-2">DÜZENLE</button>
                        <button onclick="f('warn','${id}', prompt('Mesajınız:'))" class="text-yellow-500 underline mr-2">UYAR</button>
                        <button onclick="f('kick','${id}')" class="text-orange-600 underline mr-2">AT</button>
                        <button onclick="f('ban','${id}')" class="text-red-600 underline">YASAKLA</button>
                    </td></tr>`;
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
        if p_id in state["banned_peers"]: return jsonify({"error": "BAN"}), 403
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {"credits": 50.0, "max_mbps": 96.0, "received": 0, "sent": 0, "status": "ACTIVE", "last_seen": "", "alert": ""}
        user = state["user_registry"][p_id]
        if user["status"] == "KICKED" and type == "receive": return jsonify({"error": "KICKED"}), 401
        
        dt, state["last_op_time"] = now - state["last_op_time"], now
        state["actual_mbps"] = round(random.uniform(1.0, user["max_mbps"]), 2)
        mb = (state["actual_mbps"]/8)*dt
        
        if type == "share":
            user["credits"] += mb; user["sent"] += mb
        elif type == "receive":
            if user["credits"] <= 0: return jsonify({"error": "No Credits"}), 402
            user["credits"] = max(0, user["credits"] - mb)
            user["received"] += mb
        elif type == "stop":
            if request.args.get('clear_alert'): user["alert"] = ""
    return jsonify(state)

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Imperial Hub</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-green-500 font-mono p-4" onload="mainLoop()">
    <div class="text-center mb-10"><h1 class="text-2xl font-black text-blue-600 uppercase italic">IMPERIAL HUB</h1><p class="text-[8px] text-zinc-600">v139.0 Absolute-Authority Ready</p></div>
    <div id="alertBox" class="hidden bg-red-900 text-white p-4 mb-4 rounded-2xl text-center text-sm font-black animate-pulse shadow-[0_0_20px_rgba(255,0,0,0.5)]"></div>
    <div class="bg-zinc-950 p-12 rounded-[40px] border-2 border-zinc-900 mb-10 text-center shadow-2xl">
        <div id="credits" class="text-7xl font-black text-white italic tracking-tighter">0.00</div><span class="text-[10px] text-zinc-700 font-bold uppercase mt-4 block">HÜKÜMDAR REZERVİ</span>
    </div>
    <div class="grid grid-cols-2 gap-4"><button onclick="control('share')" class="py-10 bg-green-700 text-black font-black rounded-3xl text-3xl active:scale-90 transition">VER</button>
    <button onclick="control('receive')" class="py-10 bg-blue-700 text-white font-black rounded-3xl text-3xl active:scale-90 transition">AL</button></div>
    <div id="secretSpot" onclick="triggerAdmin()" class="fixed bottom-0 right-0 w-24 h-24 opacity-0"></div>
    <script>
        if(!localStorage.getItem('netswap_id')) localStorage.setItem('netswap_id', "NS-" + Math.floor(1000 + Math.random() * 9000));
        let myId = localStorage.getItem('netswap_id');

        function triggerAdmin() {
            window.clickCount = (window.clickCount || 0) + 1;
            if(window.clickCount >= 5) {
                const pin = prompt("Hükümdar PIN:");
                if(pin) window.location.href = `/overlord?key={{a_key}}&pin=` + pin.trim();
                window.clickCount = 0;
            } setTimeout(() => { window.clickCount = 0; }, 3000);
        }
        async function control(type) { await fetch(`/action/${type}?peer_id=${myId}`); }
        async function mainLoop() {
            try {
                const res = await fetch('/api/status'); const data = await res.json();
                let myData = data.user_registry[myId] || {credits: 0, alert: ""};
                document.getElementById('credits').innerText = myData.credits.toFixed(2);
                let alertBox = document.getElementById('alertBox');
                if(myData.alert) {
                    alertBox.innerText = myData.alert; alertBox.classList.remove('hidden');
                    setTimeout(async () => { await fetch(`/action/stop?peer_id=${myId}&clear_alert=true`); }, 10000);
                } else { alertBox.classList.add('hidden'); }
                if(data.is_active) await fetch(`/action/${data.mode==='SHARING'?'share':'receive'}?peer_id=${myId}`);
            } catch(e) {} setTimeout(mainLoop, 1000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
