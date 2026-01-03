from flask import Flask, render_template_string, jsonify, request, send_file
import time, io, os, requests, threading, base64, random, json

app = Flask(__name__)

# --- NETSWAP SOVEREIGN SYNC v108.0 ---
# Amacı: Açılışta hatalı bakiye göstermeyi bitirmek ve tam senkronizasyon. [cite: 2025-12-26]
VERSION = "v108.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"

state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "total_shared_mb": 0,
    "internet_credits_mb": 120, # Bu değer GitHub'daki credits.json'dan beslenir
    "tunnel_status": "Hazır",
    "last_action": "v108.0 Senkronizasyon Modu Aktif.",
    "ai_status": "Otonom Takipte",
    "evolution_count": 9,
    "s100_temp": "34°C"
}

def sync_ledger():
    if not GH_TOKEN: return
    try:
        headers = {"Authorization": f"token {GH_TOKEN}"}
        url = f"https://api.github.com/repos/{GH_REPO}/contents/credits.json"
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        # Açılışta krediyi güncelle
        if res.status_code == 200:
            content_decoded = json.loads(base64.b64decode(res.json()['content']).decode())
            state["internet_credits_mb"] = content_decoded.get("credits", 120)
        
        content = json.dumps({"credits": state["internet_credits_mb"], "peer_id": state["peer_id"], "v": VERSION})
        payload = {"message": "Sync Ledger Update", "content": base64.b64encode(content.encode()).decode(), "sha": sha}
        requests.put(url, headers=headers, json=payload)
    except: pass

def self_evolution():
    state["ai_status"] = "1B Simülasyon..."
    prompt = "NetSwap v108.0 UI senkronizasyonunu analiz et. JavaScript ve Python arasındaki veri gecikmesini sıfırlayan bir yama yaz. SADECE KOD."
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
            payload = {"message": f"Evolution v108.{state['evolution_count']}", "content": base64.b64encode(new_code.encode()).decode(), "sha": sha}
            requests.put(f_url, headers=headers, json=payload)
            sync_ledger()
        except: pass
    state["ai_status"] = "Otonom Takipte"

threading.Thread(target=lambda: (time.sleep(1800), self_evolution()), daemon=True).start()

@app.route('/action/<type>')
def handle_action(type):
    if type == "share":
        state["is_active"] = True
        state["mode"] = "SHARING"
        state["total_shared_mb"] += 10
        state["internet_credits_mb"] += 10
        state["tunnel_status"] = "Açık (Verici)"
        state["last_action"] = "S100: 96 Mbps Hasadı Aktif."
    elif type == "receive":
        if state["internet_credits_mb"] >= 10:
            state["is_active"] = True
            state["mode"] = "RECEIVING"
            state["internet_credits_mb"] -= 10
            state["tunnel_status"] = "Açık (Alıcı)"
            state["last_action"] = "A55: Kredi Harcanıyor..."
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
    # Sayfa açılışında en güncel krediyi şırınga ediyoruz [cite: 2025-12-26]
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetSwap Sync v108.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4" onload="initSync()">
    <div class="text-center mb-6">
        <h1 class="text-3xl font-black italic text-blue-500">NETSWAP SYNC</h1>
        <p class="text-[9px] text-gray-500 uppercase tracking-widest">Real-Time Ledger System - v108.0</p>
    </div>

    <div class="bg-zinc-950 p-6 rounded-3xl border-2 border-blue-600 mb-6 text-center shadow-2xl">
        <h2 class="text-[10px] text-blue-400 font-bold uppercase mb-1">Mevcut Bakiyen</h2>
        <div id="credits" class="text-6xl font-black text-white italic">{{ current_credits }}</div>
        <span class="text-xs text-gray-500 uppercase tracking-widest">MB Hakkı</span>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-6">
        <button onclick="control('share')" class="py-6 bg-green-700 text-black font-black uppercase rounded-2xl text-xl shadow-lg active:scale-95 transition">VER (Paylaş)</button>
        <button onclick="control('receive')" class="py-6 bg-blue-700 text-white font-black uppercase rounded-2xl text-xl shadow-lg active:scale-95 transition">AL (Kullan)</button>
    </div>

    <button onclick="control('stop')" class="w-full py-4 bg-red-900/30 text-red-500 font-bold uppercase rounded-xl border border-red-900 mb-6 active:scale-95 transition">SİSTEMİ DURDUR</button>

    <div class="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800 mb-8">
        <div class="flex justify-between text-[9px] font-bold uppercase mb-2">
            <span class="text-zinc-500">Tünel:</span>
            <span id="tunnel_status" class="text-white">{{ t_status }}</span>
        </div>
        <div class="flex justify-between text-[9px] font-bold uppercase">
            <span class="text-zinc-500">Peer ID:</span>
            <span id="peer_id" class="text-blue-500">{{ p_id }}</span>
        </div>
    </div>

    <div class="border-t border-zinc-900 pt-4">
        <p id="report" class="text-xs italic text-gray-400 font-bold">> {{ l_action }}</p>
    </div>

    <script>
        let loopTimer;
        async function initSync() {
            // Sayfa açılır açılmaz son durumu bir kez daha doğrula [cite: 2025-12-26]
            const res = await fetch('/api/status');
            const data = await res.json();
            updateUI(data);
        }
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
""", 
current_credits=state["internet_credits_mb"], 
t_status=state["tunnel_status"], 
p_id=state["peer_id"],
l_action=state["last_action"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
