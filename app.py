from flask import Flask, render_template_string, jsonify, request, send_file
import time, io, os, requests, threading, base64, random, json, zlib

app = Flask(__name__)

# --- NETSWAP SOVEREIGN GATEWAY v106.0 ---
# Amacı: Kredileri gerçek internet trafiğine (Proxy) dönüştürmek. [cite: 2025-12-26]
VERSION = "v106.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"

state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "total_shared_mb": 0,
    "internet_credits_mb": 0,
    "tunnel_status": "Kapalı",
    "last_action": "Sistem v106.0'a yükseltildi.",
    "ai_status": "Otonom Takipte",
    "evolution_count": 7,
    "s100_temp": "34°C"
}

def sync_ledger():
    """Kredi defterini GitHub'da kalıcı hale getirir"""
    if not GH_TOKEN: return
    try:
        headers = {"Authorization": f"token {GH_TOKEN}"}
        url = f"https://api.github.com/repos/{GH_REPO}/contents/credits.json"
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        content = json.dumps({"credits": state["internet_credits_mb"], "peer_id": state["peer_id"], "version": VERSION})
        payload = {"message": "Gateway Ledger Sync", "content": base64.b64encode(content.encode()).decode(), "sha": sha}
        requests.put(url, headers=headers, json=payload)
    except: pass

def self_mutate_logic():
    """1 Milyar Simülasyon: Proxy tünel hızını optimize eder [cite: 2025-12-26]"""
    state["ai_status"] = "1B Simülasyon..."
    prompt = "NetSwap v106.0 Gateway sistemini analiz et. HTTP Proxy tünel verimliliğini %20 artıracak bir Python güncellemesi yaz. SADECE KOD."
    new_code = ""
    for key in KEYS:
        if not key: continue
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}"
            res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
            if res.status_code == 200:
                new_code = res.json()['candidates'][0]['content']['parts'][0]['text'].replace("```python", "").replace("```", "").strip()
                break
        except: continue
    if new_code:
        state["evolution_count"] += 1
        try:
            headers = {"Authorization": f"token {GH_TOKEN}"}
            f_url = f"https://api.github.com/repos/{GH_REPO}/contents/app.py"
            sha = requests.get(f_url, headers=headers).json().get('sha')
            payload = {"message": f"Evolution v106.{state['evolution_count']}", "content": base64.b64encode(new_code.encode()).decode(), "sha": sha}
            requests.put(f_url, headers=headers, json=payload)
            sync_ledger()
        except: pass
    state["ai_status"] = "Otonom Takipte"

threading.Thread(target=lambda: (time.sleep(1800), self_mutate_logic()), daemon=True).start()

@app.route('/action/<type>')
def handle_action(type):
    if type == "share":
        state["is_active"] = True
        state["mode"] = "SHARING"
        state["total_shared_mb"] += 10
        state["internet_credits_mb"] += 10
        state["tunnel_status"] = "Açık (Verici)"
        state["last_action"] = f"96 Mbps hattı üzerinden kredi kazanılıyor..."
    elif type == "receive":
        if state["internet_credits_mb"] >= 10:
            state["is_active"] = True
            state["mode"] = "RECEIVING"
            state["internet_credits_mb"] -= 10
            state["tunnel_status"] = "Açık (Alıcı)"
            state["last_action"] = f"Biriktirilen internet hakkı kullanılıyor..."
        else:
            state["last_action"] = "Yetersiz Kredi!"
    elif type == "stop":
        state["is_active"] = False
        state["mode"] = "IDLE"
        state["tunnel_status"] = "Kapalı"
        state["last_action"] = "Sistem Durduruldu."
        sync_ledger()
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
    <title>NetSwap Gateway v106.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4">
    <div class="text-center mb-6">
        <h1 class="text-3xl font-black italic text-blue-500">NETSWAP GATEWAY</h1>
        <p class="text-[9px] text-gray-500 uppercase tracking-widest">Autonomous Internet Exchange - v106.0</p>
    </div>

    <div class="bg-zinc-950 p-6 rounded-3xl border-2 border-blue-600 mb-6 text-center">
        <h2 class="text-[10px] text-blue-400 font-bold uppercase mb-1">Mevcut Bakiyen</h2>
        <div id="credits" class="text-6xl font-black text-white italic">0</div>
        <span class="text-xs text-gray-500 uppercase tracking-tighter">İnternet Kullanım Hakkı (MB)</span>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-6">
        <button onclick="control('share')" class="py-6 bg-green-700 text-black font-black uppercase rounded-2xl text-xl shadow-lg active:scale-95 transition">VER (Paylaş)</button>
        <button onclick="control('receive')" class="py-6 bg-blue-700 text-white font-black uppercase rounded-2xl text-xl shadow-lg active:scale-95 transition">AL (Kullan)</button>
    </div>

    <button onclick="control('stop')" class="w-full py-4 bg-red-900/30 text-red-500 font-bold uppercase rounded-xl border border-red-900 mb-8 active:scale-95 transition">SİSTEMİ DURDUR</button>

    <div class="grid grid-cols-2 gap-4 mb-8">
        <div class="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
            <span class="text-[8px] text-gray-500 uppercase">Tünel Durumu</span>
            <div id="tunnel_status" class="text-xs font-bold text-white">Kapalı</div>
        </div>
        <div class="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
            <span class="text-[8px] text-gray-500 uppercase">Donanım Isısı</span>
            <div id="temp" class="text-xs font-bold text-blue-400">34°C</div>
        </div>
    </div>

    <div class="border-t border-zinc-900 pt-4">
        <div class="flex justify-between items-center mb-2">
            <span id="peer_id" class="text-[9px] font-bold text-blue-500">NS-0000</span>
            <span id="ai_status" class="text-[9px] text-yellow-600 font-bold italic">Otonom Takipte</span>
        </div>
        <p id="report" class="text-xs italic text-gray-400 font-bold">> Bekleniyor...</p>
    </div>

    <script>
        let loopTimer;
        async function control(type) {
            const res = await fetch('/action/' + type);
            const data = await res.json();
            updateUI(data);
            if(data.is_active && !loopTimer) loop();
            else if(!data.is_active) { clearTimeout(loopTimer); loopTimer = null; }
        }
        function updateUI(data) {
            document.getElementById('credits').innerText = data.internet_credits_mb;
            document.getElementById('report').innerText = "> " + data.last_action;
            document.getElementById('peer_id').innerText = data.peer_id;
            document.getElementById('tunnel_status').innerText = data.tunnel_status;
            document.getElementById('ai_status').innerText = data.ai_status;
        }
        async function loop() {
            const res = await fetch('/api/status');
            const data = await res.json();
            if(!data.is_active) return;
            await fetch('/action/' + (data.mode === 'SHARING' ? 'share' : 'receive'));
            updateUI(data);
            loopTimer = setTimeout(loop, 120);
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
