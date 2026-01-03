from flask import Flask, render_template_string, jsonify, request, Response
import time, io, os, requests, threading, base64, random, json, traceback
from threading import Lock
from urllib.parse import urljoin

app = Flask(__name__)

# --- NETSWAP SOVEREIGN VIP-COMMANDER v142.0 ---
# Vizyon: VIP Yönetimi, Cihaz/IP Tespiti ve Çift Erişimli Otorite. [cite: 2026-01-03]
VERSION = "v142.0"
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

# VIP LİSTESİ MÜHÜRÜ
VIP_LIST = {
    "CEYLIN": {"priority": 1, "unlimited": True},
    "ELMIRA": {"priority": 2, "unlimited": True},
    "EFE": {"priority": 3, "unlimited": True}
}

MOBILE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-A556B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36",
    "X-Requested-With": "com.android.chrome"
}

transaction_lock = Lock()
state = {
    "is_active": False, "mode": "IDLE", "actual_mbps": 0.0,
    "last_op_time": time.perf_counter(), "global_lock": False,
    "evolution_count": 43, "s100_temp": "34°C",
    "banned_peers": [], "user_registry": {} 
}

def get_device_info(ua):
    if "SM-A55" in ua or "437F" in ua: return "Samsung A55"
    if "WINDOWS" in ua: return "Windows PC"
    if "ANDROID" in ua: return "Android Cihaz"
    if "IPHONE" in ua: return "iPhone"
    return "Bilinmeyen"

def check_admin_auth(req):
    ua = req.headers.get('User-Agent', '').upper()
    key, pin = req.args.get('key'), req.args.get('pin', '').strip()
    is_authorized = "437F" in ua or "SM-A55" in ua or "WINDOWS" in ua
    return key == ADMIN_KEY and pin == ADMIN_PIN and is_authorized

@app.route('/overlord_api/<action>')
def admin_api(action):
    if not check_admin_auth(request): return "YETKİSİZ", 403
    target = request.args.get('target_peer')
    val = request.args.get('value', "")
    with transaction_lock:
        if action == "lock": state["global_lock"] = not state["global_lock"]
        elif action == "unban" and target:
            if target in state["banned_peers"]: state["banned_peers"].remove(target)
            if target in state["user_registry"]: state["user_registry"][target]["status"] = "ACTIVE"
        elif target in state["user_registry"]:
            u = state["user_registry"][target]
            if action == "gift": u["credits"] = max(0, u["credits"] + float(val))
            elif action == "warn": u["alert"] = val 
            elif action == "kick": u["status"] = "KICKED"
            elif action == "vip": u["is_vip"] = not u["is_vip"] # VIP Atama [cite: 2026-01-03]
            elif action == "ban": 
                if target not in state["banned_peers"]: state["banned_peers"].append(target)
                u["status"] = "BANNED"
    return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "<h1>REDDEDİLDİ</h1>", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>VIP Commander</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[10px]">
    <div class="border-b-2 border-yellow-600 pb-4 mb-6 flex justify-between items-center">
        <h1 class="text-xl font-black text-yellow-500 italic uppercase">VIP COMMANDER v142</h1>
        <div id="vipNotice" class="hidden px-3 py-1 bg-red-600 animate-pulse rounded-full font-bold uppercase">VIP GİRİŞİ!</div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
        <div class="lg:col-span-1 bg-zinc-950 p-4 border border-yellow-900 rounded-2xl">
            <h2 class="text-yellow-500 font-bold mb-3 uppercase italic border-b border-yellow-900 pb-1">Aktif VIP'ler</h2>
            <div id="vipList" class="space-y-2"></div>
        </div>

        <div class="lg:col-span-3 bg-zinc-950 rounded-2xl border border-zinc-900 overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-zinc-900 text-zinc-500 font-bold">
                    <tr><th class="p-3">CIHAZ / IP</th><th>ID</th><th>BAKİYE</th><th>HIZ</th><th>MÜDAHALE</th></tr>
                </thead>
                <tbody id="userTable"></tbody>
            </table>
        </div>
    </div>

    <div class="bg-zinc-950 rounded-2xl border border-red-900 overflow-hidden p-2">
        <p class="text-red-500 font-bold uppercase text-[8px] mb-2">Kara Liste</p>
        <div id="banList" class="space-y-1"></div>
    </div>

    <script>
        const k="{{a_key}}", p="{{a_pin}}";
        async function f(a, t="", v=""){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${encodeURIComponent(v)}`); }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json();
            let uH="", bH="", vH="", vipIn = false;
            for(let id in d.user_registry){
                let u = d.user_registry[id];
                if(d.banned_peers.includes(id)){
                    bH += `<div class="flex justify-between p-2 border-b border-zinc-900 text-red-500"><span>${id}</span><button onclick="f('unban','${id}')" class="underline">AFFET</button></div>`;
                } else {
                    if(u.is_vip) { vH += `<div class="p-2 bg-yellow-900/20 text-yellow-500 rounded-lg font-bold">👑 ${id} (${u.device})</div>`; vipIn = true; }
                    uH += `<tr class="border-b border-zinc-900">
                        <td class="p-3"><b>${u.device}</b><br><span class="text-zinc-600">${u.ip}</span></td>
                        <td class="font-bold text-blue-400">${id}</td>
                        <td class="text-green-500 font-black">${u.credits.toFixed(1)}</td>
                        <td class="text-yellow-600">${u.max_mbps}M</td>
                        <td>
                            <button onclick="f('gift','${id}', prompt('MB:'))" class="mr-2 underline">DÜZENLE</button>
                            <button onclick="f('warn','${id}', prompt('Mesaj:'))" class="mr-2 underline text-yellow-500">UYAR</button>
                            <button onclick="f('vip','${id}')" class="mr-2 underline text-yellow-400">VIP</button>
                            <button onclick="f('kick','${id}')" class="text-red-600 underline">AT</button>
                        </td></tr>`;
                }
            }
            document.getElementById('userTable').innerHTML = uH; document.getElementById('banList').innerHTML = bH;
            document.getElementById('vipList').innerHTML = vH || "<p class='text-zinc-700 italic'>Aktif VIP yok.</p>";
            document.getElementById('vipNotice').style.display = vipIn ? 'block' : 'none';
            setTimeout(update, 1000);
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
            state["user_registry"][p_id] = {"credits": 50.0, "max_mbps": 96.0, "received": 0, "sent": 0, "status": "ACTIVE", "alert": "", 
                                           "device": get_device_info(request.headers.get('User-Agent','')), "ip": request.remote_addr, "is_vip": False}
        u = state["user_registry"][p_id]
        if u["status"] == "KICKED" and type == "receive": return jsonify({"error": "KICK"}), 401
        dt, state["last_op_time"] = now - state["last_op_time"], now
        state["actual_mbps"] = round(random.uniform(1.0, u["max_mbps"]), 2)
        mb = (state["actual_mbps"]/8)*dt
        if type == "share":
            u["credits"] += mb; u["sent"] += mb
        elif type == "receive":
            # VIP'ler kredi harcamaz [cite: 2026-01-03]
            if not u["is_vip"]:
                if u["credits"] <= 0: return jsonify({"error": "Empty"}), 402
                u["credits"] = max(0, u["credits"] - mb)
            u["received"] += mb
        if request.args.get('clear_alert'): u["alert"] = ""
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
    <div class="text-center mb-8"><h1 class="text-2xl font-black text-blue-600 uppercase italic">IMPERIAL HUB</h1><p class="text-[8px] text-zinc-600">v142.0 Commander Ready</p></div>
    <div id="aB" class="hidden bg-red-900 text-white p-4 mb-4 rounded-2xl text-center text-sm font-black animate-pulse shadow-lg"></div>
    <div class="bg-zinc-950 p-12 rounded-[40px] border-2 border-zinc-900 mb-8 text-center shadow-2xl">
        <div id="credits" class="text-7xl font-black text-white italic tracking-tighter">0.00</div><span class="text-[10px] text-zinc-700 font-bold uppercase mt-4 block">MB BAKİYE</span>
    </div>
    <div class="grid grid-cols-2 gap-4"><button onclick="control('share')" class="py-10 bg-green-700 text-black font-black rounded-3xl text-3xl transition active:scale-90">VER</button>
    <button onclick="control('receive')" class="py-10 bg-blue-700 text-white font-black rounded-3xl text-3xl transition active:scale-90">AL</button></div>
    <div id="sS" onclick="tA()" class="fixed bottom-0 right-0 w-24 h-24 opacity-0"></div>
    <script>
        if(!localStorage.getItem('n_id')) localStorage.setItem('n_id', "NS-" + Math.floor(1000 + Math.random()*9000));
        let myId = localStorage.getItem('n_id');
        function tA() { window.cC = (window.cC || 0) + 1; if(window.cC >= 5) { const p = prompt("PIN:"); if(p) window.location.href = `/overlord?key={{a_key}}&pin=` + p.trim(); window.cC = 0; } setTimeout(() => { window.cC = 0; }, 3000); }
        async function control(type) { await fetch(`/action/${type}?peer_id=${myId}`); }
        async function mainLoop() {
            try {
                const r = await fetch('/api/status'); const d = await r.json();
                let u = d.user_registry[myId] || {credits: 0, alert: ""};
                document.getElementById('credits').innerText = u.credits.toFixed(2);
                let box = document.getElementById('aB');
                if(u.alert) { box.innerText = u.alert; box.classList.remove('hidden'); setTimeout(async () => { await fetch(`/action/stop?peer_id=${myId}&clear_alert=true`); }, 10000); } else { box.classList.add('hidden'); }
                if(d.is_active) await fetch(`/action/${d.mode==='SHARING'?'share':'receive'}?peer_id=${myId}`);
            } catch(e) {} setTimeout(mainLoop, 1000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
