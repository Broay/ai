from flask import Flask, render_template_string, jsonify, request, send_file
import time, io, os, requests, threading, base64, random, json, traceback

app = Flask(__name__)

# --- NETSWAP SOVEREIGN THROTTLE v116.0 ---
# Amacı: Seri tıklama ile bakiye şişirmeyi (Spam) engellemek ve tam denetim. [cite: 2025-12-26]
VERSION = "v116.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"

state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "internet_credits_mb": 0,
    "last_action": "v116.0 Throttle Aktif.",
    "ai_status": "Rate Limit Uygulanıyor",
    "last_op_time": 0, # Son işlem zamanı (Saniyelik kontrol için)
    "evolution_count": 17,
    "s100_temp": "34°C"
}

def load_credits():
    """GitHub'dan krediyi güvenli yükle"""
    if not GH_TOKEN: return
    try:
        headers = {"Authorization": f"token {GH_TOKEN}"}
        url = f"https://api.github.com/repos/{GH_REPO}/contents/credits.json"
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = json.loads(base64.decodebytes(res.json()['content'].encode()).decode())
            state["internet_credits_mb"] = data.get("credits", 0)
    except: pass

def save_credits():
    """Krediyi GitHub'a mühürle"""
    if not GH_TOKEN: return
    try:
        headers = {"Authorization": f"token {GH_TOKEN}"}
        url = f"https://api.github.com/repos/{GH_REPO}/contents/credits.json"
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        content = json.dumps({"credits": state["internet_credits_mb"], "ts": time.time()})
        payload = {"message": f"Security Seal v116", "content": base64.b64encode(content.encode()).decode(), "sha": sha}
        requests.put(url, headers=headers, json=payload)
    except: pass

@app.route('/action/<type>')
def handle_action(type):
    current_time = time.time()
    
    # 1 SANİYE KURALI: Seri tıklamayı sunucu tarafında reddet [cite: 2025-12-26]
    if type != "stop" and (current_time - state["last_op_time"]) < 1.0:
        return jsonify({"error": "Çok hızlı işlem!", "credits": state["internet_credits_mb"]}), 429
    
    state["last_op_time"] = current_time

    if type == "share":
        state["is_active"] = True
        state["mode"] = "SHARING"
        state["internet_credits_mb"] += 10 # VER (+)
        state["last_action"] = "Veri Paylaşıldı (+10 MB)"
    elif type == "receive":
        if state["internet_credits_mb"] >= 10:
            state["is_active"] = True
            state["mode"] = "RECEIVING"
            state["internet_credits_mb"] -= 10 # AL (-)
            state["last_action"] = "Veri Alındı (-10 MB)"
        else:
            state["is_active"] = False
            state["mode"] = "IDLE"
            state["last_action"] = "Yetersiz Bakiye!"
    elif type == "stop":
        state["is_active"] = False
        state["mode"] = "IDLE"
        state["last_action"] = "Sistem Durduruldu."
        save_credits()
        
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
    <title>NetSwap Throttle v116.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #000; color: #00ff41; font-family: monospace; }
        .btn-lock { opacity: 0.5; pointer-events: none; filter: grayscale(1); }
    </style>
</head>
<body class="p-4" onload="init()">
    <div class="text-center mb-6">
        <h1 class="text-3xl font-black italic text-blue-500 uppercase">Sovereign Throttle</h1>
        <p class="text-[9px] text-gray-500 uppercase tracking-widest">Spam Protection Engine - v116.0</p>
    </div>

    <div class="bg-zinc-950 p-8 rounded-3xl border-2 border-zinc-800 mb-8 text-center">
        <h2 class="text-[11px] text-zinc-500 font-bold mb-1 uppercase tracking-widest">Güvenli Bakiye</h2>
        <div id="credits" class="text-7xl font-black text-white italic">0</div>
        <span class="text-xs text-zinc-700 font-bold uppercase">MegaByte (MB)</span>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-6">
        <button id="btn-share" onclick="sendAction('share')" class="py-8 bg-green-700 text-black font-black uppercase rounded-2xl text-2xl shadow-lg active:scale-95 transition">VER (+)</button>
        <button id="btn-receive" onclick="sendAction('receive')" class="py-8 bg-blue-700 text-white font-black uppercase rounded-2xl text-2xl shadow-lg active:scale-95 transition">AL (-)</button>
    </div>

    <button id="btn-stop" onclick="sendAction('stop')" class="w-full py-4 bg-zinc-900 text-red-500 font-bold uppercase rounded-xl border border-zinc-800 mb-8 active:scale-95 transition">DURDUR</button>

    <div class="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800 mb-4">
        <p id="report" class="text-[10px] italic text-gray-400 font-bold text-center uppercase">> {{ l_action }}</p>
    </div>

    <div class="flex justify-between items-center text-[9px] font-bold border-t border-zinc-900 pt-4">
        <span class="text-yellow-600 uppercase">Anti-Spam Kilidi Aktif</span>
        <span id="peer_id" class="text-zinc-700">ID: NS-0000</span>
    </div>

    <script>
        let isThrottled = false;

        async function init() {
            const res = await fetch('/api/status');
            const data = await res.json();
            updateUI(data);
            setInterval(updateLoop, 1000); // Otomatik mod saniyede 1 çalışır
        }

        async function sendAction(type) {
            if (isThrottled && type !== 'stop') return;
            isThrottled = true;
            
            // UI Kilidi: Butonları saniyede bir kez tıklanabilir yap [cite: 2025-12-26]
            document.getElementById('btn-share').classList.add('btn-lock');
            document.getElementById('btn-receive').classList.add('btn-lock');

            try {
                const res = await fetch('/action/' + type);
                const data = await res.json();
                updateUI(data);
            } catch(e) {
                console.error("Hız limiti aşıldı.");
            } finally {
                setTimeout(() => {
                    document.getElementById('btn-share').classList.remove('btn-lock');
                    document.getElementById('btn-receive').classList.remove('btn-lock');
                    isThrottled = false;
                }, 1000); // 1 Saniye Cooldown [cite: 2025-12-26]
            }
        }

        function updateUI(data) {
            document.getElementById('credits').innerText = data.internet_credits_mb;
            document.getElementById('report').innerText = "> " + (data.last_action || "Bekleniyor");
            document.getElementById('peer_id').innerText = "ID: " + data.peer_id;
        }

        async function updateLoop() {
            if (isThrottled) return;
            const res = await fetch('/api/status');
            const data = await res.json();
            if(data.is_active) {
                await sendAction(data.mode === 'SHARING' ? 'share' : 'receive');
            }
        }
    </script>
</body></html>
""", l_action=state["last_action"])

load_credits()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
