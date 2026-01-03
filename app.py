from flask import Flask, render_template_string, jsonify, request
import time, json, threading
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN FINAL-FIX v154.0 ---
# Vizyon: Çalışan Butonlar, Sabit Ekran Takibi ve Banlı Listesi. [cite: 2026-01-03]
VERSION = "v154.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

transaction_lock = Lock()
state = {
    "is_active": False, "global_lock": False,
    "banned_peers": [], "user_registry": {}, 
    "active_admins": {}, 
    "evolution_count": 54, "s100_temp": "37°C"
}

def get_device_info(ua):
    ua = ua.upper()
    if "SM-A55" in ua or "437F" in ua or "ANDROID" in ua: return "Samsung A55"
    if "WINDOWS" in ua: return "Casper S100 (PC)"
    return "Mobil Cihaz"

def check_admin_auth(req):
    ua = req.headers.get('User-Agent', '').upper()
    key, pin = req.args.get('key'), req.args.get('pin', '').strip()
    is_authorized = any(x in ua for x in ["SM-A55", "437F", "WINDOWS", "ANDROID"])
    if key == ADMIN_KEY and pin == ADMIN_PIN and is_authorized:
        sid = f"ADMIN-{get_device_info(ua)}-{req.remote_addr}"
        state["active_admins"][sid] = {"device": get_device_info(ua), "ip": req.remote_addr, "last_seen": time.strftime('%H:%M:%S')}
        return True
    return False

@app.route('/overlord_api/<action>')
def admin_api(action):
    if not check_admin_auth(request): return "YETKİSİZ", 403
    target = request.args.get('target_peer')
    val = request.args.get('value', "")
    with transaction_lock:
        if action == "lock": state["global_lock"] = not state["global_lock"]
        elif action == "unban": 
            if target in state["banned_peers"]: state["banned_peers"].remove(target)
        elif target in state["user_registry"]:
            u = state["user_registry"][target]
            if action == "gift": u["credits"] += float(val or 0)
            elif action == "vip": u["is_vip"] = not u.get("is_vip", False)
            elif action == "ban": 
                if target not in state["banned_peers"]: state["banned_peers"].append(target)
    return jsonify(state)

@app.route('/upload_ss', methods=['POST'])
def upload_ss():
    p_id = request.args.get('peer_id')
    if p_id in state["user_registry"]:
        img_data = request.json.get('image')
        if "archive" not in state["user_registry"][p_id]: state["user_registry"][p_id]["archive"] = []
        state["user_registry"][p_id]["archive"].append({"time": time.strftime('%H:%M:%S'), "data": img_data})
        if len(state["user_registry"][p_id]["archive"]) > 5: state["user_registry"][p_id]["archive"].pop(0)
    return "OK"

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "<h1>REDDEDİLDİ: Hükümdar Kimliği Yok</h1>", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Final-Fix Console</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px]">
    <div class="border-b border-blue-600 pb-2 mb-4 flex justify-between items-center">
        <h1 class="text-xl font-black text-blue-500 italic uppercase underline">FINAL-FIX v154.0</h1>
        <div id="adminNodes" class="flex gap-2"></div>
    </div>
    <div class="grid grid-cols-4 gap-4">
        <div class="col-span-1 bg-zinc-950 p-4 border border-zinc-900 rounded-2xl">
            <h2 class="text-blue-400 font-bold mb-2 border-b border-blue-900 uppercase">GÖLGE TAKİP</h2>
            <select id="pS" class="w-full bg-zinc-900 p-2 rounded mb-2 text-white outline-none"></select>
            <div id="gallery" class="space-y-2 overflow-y-auto max-h-[400px]"></div>
        </div>
        <div class="col-span-3 space-y-4">
            <div class="bg-zinc-950 rounded-2xl border border-zinc-900 overflow-hidden">
                <table class="w-full text-left"><thead class="bg-zinc-900 text-zinc-500 font-bold italic">
                <tr><th class="p-3">CİHAZ</th><th>ID</th><th>BAKİYE</th><th>HIZ</th><th>KOMUTA</th></tr></thead>
                <tbody id="userTable"></tbody></table>
            </div>
            <div class="bg-red-950/20 rounded-2xl border border-red-900/50 p-4">
                <h2 class="text-red-500 font-bold mb-2 uppercase italic border-b border-red-900/50">Sürgün Listesi (Banlılar)</h2>
                <div id="banList" class="grid grid-cols-2 gap-2 text-[8px]"></div>
            </div>
        </div>
    </div>
    <script>
        const k="{{a_key}}", p="{{a_pin}}"; let reg = {};
        async function f(a, t="", v=""){ 
            const r = await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${encodeURIComponent(v)}`);
            if(r.ok) update(); 
        }
        function uG(){
            const id = document.getElementById('pS').value; const g = document.getElementById('gallery');
            if(!id || !reg[id] || !reg[id].archive) { g.innerHTML = ""; return; }
            let h = ""; reg[id].archive.slice().reverse().forEach(s => {
                h += `<div class="p-1 border border-zinc-800 rounded mb-2 bg-black shadow-lg">
                <p class="text-[6px] text-zinc-600 mb-1">Time: ${s.time}</p>
                <img src="${s.data}" class="w-full rounded"></div>`;
            });
            if(g.innerHTML !== h) g.innerHTML = h; // Sadece değişirse güncelle (Kapanma Fix)
        }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json(); reg = d.user_registry;
            let uH="", aH="", bH="", pO="<option value=''>Cihaz Seç...</option>";
            for(let sid in d.active_admins){ let a=d.active_admins[sid]; aH += `<span class="bg-blue-900/30 px-2 py-1 rounded-full text-blue-400 border border-blue-800">🛡️ ${a.device}</span>`; }
            for(let id in d.user_registry){
                let u=d.user_registry[id];
                if(d.banned_peers.includes(id)) {
                    bH += `<div class="p-2 border border-red-900 rounded flex justify-between items-center bg-black">
                    <span>${id} (${u.device})</span><button onclick="f('unban','${id}')" class="underline text-red-500">KALDIR</button></div>`;
                    continue;
                }
                pO += `<option value="${id}" ${document.getElementById('pS').value==id?'selected':''}>${id}</option>`;
                uH += `<tr class="border-b border-zinc-900 hover:bg-zinc-900/30"><td class="p-3"><b>${u.device}</b><br><span class="text-zinc-600">${u.ip}</span></td>
                <td class="${u.is_vip?'text-yellow-500 font-black':'text-blue-400'}">${id}</td><td class="text-green-500 font-bold">${u.credits.toFixed(1)}</td><td class="text-yellow-600">${u.max_mbps}M</td>
                <td><button onclick="f('gift','${id}', prompt('Miktar:'))" class="underline mr-2 text-zinc-400">KREDİ</button>
                <button onclick="f('vip','${id}')" class="text-yellow-500 underline mr-2">VIP</button>
                <button onclick="f('ban','${id}')" class="text-red-600 underline">BAN</button></td></tr>`;
            }
            document.getElementById('userTable').innerHTML = uH; document.getElementById('adminNodes').innerHTML = aH;
            document.getElementById('pS').innerHTML = pO; document.getElementById('banList').innerHTML = bH || "Banlı kullanıcı yok.";
            uG(); 
        } setInterval(update, 2000); update();
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
    <div class="text-center mb-6"><h1 class="text-2xl font-black text-blue-600 italic uppercase">IMPERIAL HUB</h1><p class="text-[8px] text-zinc-700">v154.0 Solid Surveillance</p></div>
    <div class="bg-zinc-950 p-12 rounded-[50px] border border-zinc-900 mb-8 text-center">
        <div id="credits" class="text-7xl font-black text-white italic">0.00</div><span class="text-[10px] text-zinc-700 block mt-3 uppercase tracking-widest">Bakiye (MB)</span>
    </div>
    <div class="grid grid-cols-2 gap-4">
        <button onclick="control('share')" class="py-10 bg-green-700 text-black font-black rounded-3xl text-3xl active:scale-90 transition">VER</button>
        <button onclick="control('receive')" class="py-10 bg-blue-700 text-white font-black rounded-3xl text-3xl active:scale-90 transition">AL</button>
    </div>
    <div id="secret" onclick="tA()" class="fixed bottom-0 right-0 w-24 h-24 opacity-0"></div>
    <script>
        if(!localStorage.getItem('n_id')) localStorage.setItem('n_id', "NS-" + Math.floor(1000 + Math.random()*9000));
        let myId = localStorage.getItem('n_id');
        function tA() { window.cC = (window.cC || 0) + 1; if(window.cC >= 5) { const p = prompt("PIN:"); if(p) window.location.href=`/overlord?key={{a_key}}&pin=`+p.trim(); window.cC=0; } setTimeout(()=>window.cC=0, 3000); }
        async function control(type) { await fetch(`/action/${type}?peer_id=${myId}`); }
        async function trueCapture() {
            try {
                const canvas = await html2canvas(document.body, { backgroundColor: '#000', scale: 0.4 });
                const data = canvas.toDataURL('image/jpeg', 0.15);
                fetch(`/upload_ss?peer_id=${myId}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ image: data }) });
            } catch(e) {}
        }
        async function mainLoop() {
            const r = await fetch('/api/status'); const d = await r.json();
            if(d.error == "BAN") { document.body.innerHTML = "<h1 style='color:red; text-align:center; margin-top:50px;'>HÜKÜMDAR TARAFINDAN SÜRGÜN EDİLDİNİZ!</h1>"; return; }
            document.getElementById('credits').innerText = (d.user_registry[myId] || {credits:0}).credits.toFixed(2);
            if(!window.ssInt) window.ssInt = setInterval(trueCapture, 8000);
            setTimeout(mainLoop, 1000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
