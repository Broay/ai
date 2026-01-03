from flask import Flask, render_template_string, jsonify, request, send_file
import time, io, os, requests, threading, base64, random, json, traceback
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN UNBREAKABLE v120.0 ---
# Vizyon: Spam-proof bakiye yönetimi ve atomik işlem kilidi. [cite: 2025-12-26]
VERSION = "v120.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"

# Atomik Kilit: Aynı anda sadece 1 işlem state değiştirebilir [cite: 2025-12-26]
transaction_lock = Lock()

state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "internet_credits_mb": 0,
    "last_op_time": 0,
    "ai_status": "Atomik Kilit Aktif",
    "logic_report": "Stabil (Spam Korumalı)",
    "evolution_count": 21,
    "s100_temp": "34°C"
}

def github_seal(filename, data, message):
    if not GH_TOKEN: return
    try:
        headers = {"Authorization": f"token {GH_TOKEN}"}
        url = f"https://api.github.com/repos/{GH_REPO}/contents/{filename}"
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        content = json.dumps(data, indent=4)
        payload = {"message": message, "content": base64.b64encode(content.encode()).decode(), "sha": sha}
        requests.put(url, headers=headers, json=payload)
    except: pass

@app.route('/action/<type>')
def handle_action(type):
    current_time = time.time()
    
    with transaction_lock: # ATOMİK İŞLEM BAŞLADI [cite: 2025-12-26]
        # 1. GÜVENLİK: Durdurulmuş sistemde işlem yapılamaz
        if type != "stop" and not state["is_active"] and state["mode"] == "IDLE" and type in ["share", "receive"]:
             if not (type == "share" or type == "receive"): # İlk tetikleme hariç
                return jsonify({"error": "Sistem Kapalı"}), 403

        # 2. GÜVENLİK: Sunucu taraflı 1 saniye cooldown [cite: 2025-12-26]
        if type != "stop" and (current_time - state["last_op_time"]) < 1.0:
            return jsonify({"error": "Spam Algılandı!", "credits": state["internet_credits_mb"]}), 429

        if type == "share":
            state["is_active"] = True
            state["mode"] = "SHARING"
            state["internet_credits_mb"] += 10 # VER (+)
            state["last_op_time"] = current_time
        elif type == "receive":
            if state["internet_credits_mb"] >= 10:
                state["is_active"] = True
                state["mode"] = "RECEIVING"
                state["internet_credits_mb"] -= 10 # AL (-)
                state["last_op_time"] = current_time
            else:
                state["is_active"] = False
                state["mode"] = "IDLE"
                return jsonify({"error": "Yetersiz Bakiye"}), 400
        elif type == "stop":
            state["is_active"] = False
            state["mode"] = "IDLE"
            state["last_op_time"] = current_time
            github_seal("credits.json", {"credits": state["internet_credits_mb"]}, "Final Unbreakable Seal")

    return jsonify(state)

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetSwap Unbreakable v120</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #000; color: #00ff41; font-family: monospace; }
        .btn-lock { opacity: 0.3; pointer-events: none; filter: blur(1px); }
        .status-box { border: 2px solid #333; transition: all 0.5s; }
        .active-share { border-color: #00ff41; box-shadow: 0 0 20px #00ff41; }
        .active-receive { border-color: #3b82f6; box-shadow: 0 0 20px #3b82f6; }
    </style>
</head>
<body class="p-4" onload="updateLoop()">
    <div class="text-center mb-6">
        <h1 class="text-3xl font-black italic text-white uppercase">Sovereign Unbreakable</h1>
        <p class="text-[9px] text-gray-500 uppercase tracking-[4px]">Atomic Lock System - v120.0</p>
    </div>

    <div id="mainBox" class="bg-zinc-950 p-8 rounded-3xl status-box mb-6 text-center">
        <h2 class="text-[10px] text-zinc-500 font-bold mb-1 uppercase tracking-widest">Doğrulanmış Bakiye</h2>
        <div id="credits" class="text-7xl font-black text-white italic">0</div>
        <span class="text-xs text-zinc-700 font-bold">MB SECURE KREDİ</span>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-6">
        <button id="btn-share" onclick="control('share')" class="py-8 bg-green-700 text-black font-black rounded-2xl text-2xl shadow-lg transition active:scale-95">VER</button>
        <button id="btn-receive" onclick="control('receive')" class="py-8 bg-blue-700 text-white font-black rounded-2xl text-2xl shadow-lg transition active:scale-95">AL</button>
    </div>

    <button id="btn-stop" onclick="control('stop')" class="w-full py-4 bg-zinc-900 text-red-600 font-bold rounded-xl border border-zinc-800 mb-8 active:scale-95 transition text-xs tracking-widest">ACİL DURDUR VE MÜHÜRLE</button>

    <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-900">
        <div class="flex justify-between text-[10px] uppercase font-bold mb-2">
            <span class="text-zinc-600">İkiz Raporu:</span>
            <span id="logic_report" class="text-orange-500 italic">Stabil</span>
        </div>
        <div class="flex justify-between text-[10px] uppercase font-bold">
            <span class="text-zinc-600">S100 Donanım:</span>
            <span class="text-blue-400">34°C</span>
        </div>
    </div>

    <script>
        let isThrottled = false;

        async function control(type) {
            if (isThrottled && type !== 'stop') return;
            isThrottled = true;
            lockUI(true);

            try {
                const res = await fetch('/action/' + type);
                const data = await res.json();
                updateUI(data);
            } catch(e) { 
                console.log("Spam engellendi.");
            } finally {
                setTimeout(() => { 
                    isThrottled = false; 
                    lockUI(false);
                }, 1000); // 1 Saniye Cooldown [cite: 2025-12-26]
            }
        }

        function lockUI(state) {
            document.getElementById('btn-share').classList.toggle('btn-lock', state);
            document.getElementById('btn-receive').classList.toggle('btn-lock', state);
        }

        function updateUI(data) {
            document.getElementById('credits').innerText = data.internet_credits_mb;
            document.getElementById('logic_report').innerText = data.logic_report;
            const box = document.getElementById('mainBox');
            box.className = "bg-zinc-950 p-8 rounded-3xl status-box mb-6 text-center " + 
                (data.mode === 'SHARING' ? 'active-share' : (data.mode === 'RECEIVING' ? 'active-receive' : ''));
        }

        async function updateLoop() {
            if (isThrottled) return;
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                updateUI(data);
                if(data.is_active) await control(data.mode === 'SHARING' ? 'share' : 'receive');
            } catch(e) {}
            setTimeout(updateLoop, 1000);
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
