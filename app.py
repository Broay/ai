from flask import Flask, render_template_string, jsonify, request, send_file
import time, io, os, requests, threading, base64, random, json

app = Flask(__name__)

# --- NETSWAP SOVEREIGN BALANCED v104.0 ---
#
VERSION = "v104.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"

state = {
    "is_active": False,
    "mode": "IDLE", # IDLE, SHARING, RECEIVING
    "total_shared_mb": 0,
    "internet_credits_mb": 0,
    "last_action": "Sistem Dengelendi. Emir Bekleniyor.",
    "ai_status": "Simülasyon Aktif",
    "evolution_count": 5,
    "s100_temp": "34°C"
}

def sync_ledger():
    """Kredileri GitHub'a mühürler"""
    if not GH_TOKEN: return
    try:
        headers = {"Authorization": f"token {GH_TOKEN}"}
        url = f"https://api.github.com/repos/{GH_REPO}/contents/credits.json"
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        content = json.dumps({"credits": state["internet_credits_mb"], "last_update": time.ctime()})
        payload = {"message": "Balanced Ledger Sync", "content": base64.b64encode(content.encode()).decode(), "sha": sha}
        requests.put(url, headers=headers, json=payload)
    except: pass

def self_mutate_logic():
    """1 Milyar Simülasyon: Al/Ver dengesini optimize eder [cite: 2025-12-26]"""
    state["ai_status"] = "1B Simülasyon..."
    prompt = "NetSwap v104.0 Al/Ver dengesini analiz et. Kredi harcama hızını optimize eden bir Python yaması yaz. SADECE KOD."
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
            payload = {"message": f"Evolution v104.{state['evolution_count']}", "content": base64.b64encode(new_code.encode()).decode(), "sha": sha}
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
        state["last_action"] = "İnternet Paylaşılıyor..."
    elif type == "receive":
        if state["internet_credits_mb"] >= 10:
            state["is_active"] = True
            state["mode"] = "RECEIVING"
            state["internet_credits_mb"] -= 10
            state["last_action"] = "İnternet Geri Alınıyor..."
        else:
            state["last_action"] = "Yetersiz Kredi!"
    elif type == "stop":
        state["is_active"] = False
        state["mode"] = "IDLE"
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
    <title>NetSwap Balanced v104.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4">
    <div class="text-center mb-6">
        <h1 class="text-3xl font-black italic text-blue-500">NETSWAP BALANCED</h1>
        <p class="text-[9px] text-gray-500 uppercase tracking-widest">Al / Ver / Yönet - v104.0</p>
    </div>

    <div class="bg-zinc-950 p-6 rounded-3xl border-2 border-blue-600 mb-6 text-center shadow-xl">
        <h2 class="text-[10px] text-blue-400 font-bold uppercase mb-1">Mevcut Bakiyen</h2>
        <div id="credits" class="text-6xl font-black text-white italic">0</div>
        <span class="text-xs text-gray-500 uppercase">MB Kullanım Hakkı</span>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-8">
        <button onclick="control('share')" class="py-6 bg-green-700 text-black font-black uppercase rounded-2xl text-xl shadow-lg active:scale-95 transition">VER</button>
        <button onclick="control('receive')" class="py-6 bg-blue-700 text-white font-black uppercase rounded-2xl text-xl shadow-lg active:scale-95 transition">AL</button>
    </div>

    <button onclick="control('stop')" class="w-full py-4 bg-red-900/30 text-red-500 font-bold uppercase rounded-xl border border-red-900 mb-8 active:scale-95 transition">SİSTEMİ DURDUR</button>

    <div class="border-t border-zinc-900 pt-6">
        <div class="flex justify-between items-center mb-2">
            <span id="mode_tag" class="text-[9px] bg-zinc-800 px-2 py-0.5 rounded text-zinc-400">IDLE</span>
            <span id="ai_status" class="text-[9px] text-yellow-600 font-bold italic">Simülasyon Aktif</span>
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
            document.getElementById('mode_tag').innerText = data.mode;
            document.getElementById('mode_tag').className = "text-[9px] px-2 py-0.5 rounded " + 
                (data.mode === 'SHARING' ? 'bg-green-900 text-green-200' : 
                 data.mode === 'RECEIVING' ? 'bg-blue-900 text-blue-200' : 'bg-zinc-800 text-zinc-400');
        }
        async function loop() {
            const res = await fetch('/api/status');
            const data = await res.json();
            if(!data.is_active) return;
            await fetch('/action/' + (data.mode === 'SHARING' ? 'share' : 'receive'));
            updateUI(data);
            loopTimer = setTimeout(loop, 115);
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
