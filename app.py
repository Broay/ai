from flask import Flask, render_template_string, jsonify, request, send_file
import time, io, os, requests, threading, base64, random, json, traceback

app = Flask(__name__)

# --- NETSWAP SOVEREIGN LOGIC-HUNTER v118.0 ---
# Vizyon: Mantık hatalarını avlayan ve ayrı dosyaya mühürleyen otonom zeka. [cite: 2025-12-26]
VERSION = "v118.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"

state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "internet_credits_mb": 0,
    "last_action": "v118.0 Logic-Hunter Aktif.",
    "ai_status": "Mantık Avlanıyor",
    "logic_report": "Mantık Stabil",
    "evolution_count": 19,
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

def autonomous_logic_hunter():
    """Saniyede 1 kez koddaki mantıksal tutarsızlıkları avlar [cite: 2025-12-26]"""
    prev_credits = 0
    while True:
        try:
            time.sleep(1)
            current_credits = state["internet_credits_mb"]
            logic_issue = None

            if state["is_active"]:
                # --- MANTIK AVI 1: TERS İŞLEM DENETİMİ ---
                if state["mode"] == "RECEIVING" and current_credits > prev_credits:
                    logic_issue = "KRİTİK: AL modunda kredi artıyor!"
                elif state["mode"] == "SHARING" and current_credits < prev_credits:
                    logic_issue = "KRİTİK: VER modunda kredi azalıyor!"
                
                # --- MANTIK AVI 2: HIZ DENETİMİ ---
                if abs(current_credits - prev_credits) > 10:
                    logic_issue = "HATA: Beklenmedik Sıçrama Algılandı."
            else:
                # --- MANTIK AVI 3: HAYALET İŞLEM ---
                if current_credits != prev_credits:
                    logic_issue = "HATA: Sistem durmuşken bakiye değişiyor."

            if logic_issue:
                state["logic_report"] = logic_issue
                github_seal("logic_errors.json", {"issue": logic_issue, "ts": time.ctime(), "v": VERSION}, "Logic Error Captured")
            else:
                state["logic_report"] = "Mantık Stabil (OK)"

            prev_credits = current_credits
            
        except Exception as e:
            github_seal("debug_report.json", {"crash": str(e)}, "Logic Hunter Crash")

threading.Thread(target=autonomous_logic_hunter, daemon=True).start()

@app.route('/action/<type>')
def handle_action(type):
    if type == "share":
        state["is_active"] = True
        state["mode"] = "SHARING"
        state["internet_credits_mb"] += 10
        state["last_action"] = "Veriliyor (+)"
    elif type == "receive":
        if state["internet_credits_mb"] >= 10:
            state["is_active"] = True
            state["mode"] = "RECEIVING"
            state["internet_credits_mb"] -= 10
            state["last_action"] = "Alınıyor (-)"
        else: state["last_action"] = "Bakiye Yetersiz!"
    elif type == "stop":
        state["is_active"] = False
        state["mode"] = "IDLE"
        state["last_action"] = "Durduruldu."
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
    <title>NetSwap Logic-Hunter v118</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4" onload="updateLoop()">
    <div class="text-center mb-6">
        <h1 class="text-3xl font-black italic text-orange-500 uppercase">Logic Hunter</h1>
        <p class="text-[9px] text-gray-500 uppercase tracking-widest">Autonomous Logic Debugger - v118.0</p>
    </div>

    <div class="bg-zinc-950 p-6 rounded-3xl border-2 border-orange-900 mb-6 text-center">
        <h2 class="text-[9px] text-orange-500 font-bold mb-1 uppercase tracking-widest">Twin Logic Report (1s)</h2>
        <div id="logic_report" class="text-xs text-white font-bold italic">Taranıyor...</div>
    </div>

    <div class="bg-zinc-950 p-8 rounded-3xl border border-zinc-800 mb-6 text-center shadow-2xl">
        <div id="credits" class="text-7xl font-black text-white italic">0</div>
        <span class="text-[10px] text-gray-600 uppercase">NetSwap MB Credits</span>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-6">
        <button onclick="control('share')" class="py-6 bg-green-700 text-black font-black rounded-2xl text-xl shadow-lg transition active:scale-95">VER</button>
        <button onclick="control('receive')" class="py-6 bg-blue-700 text-white font-black rounded-2xl text-xl shadow-lg transition active:scale-95">AL</button>
    </div>

    <button onclick="control('stop')" class="w-full py-4 bg-zinc-900 text-red-500 font-bold rounded-xl border border-zinc-800 mb-8 active:scale-95 transition text-[10px]">SİSTEMİ KİLİTLE</button>

    <div class="flex justify-between items-center text-[9px] font-bold border-t border-zinc-900 pt-4">
        <span class="text-yellow-600 uppercase">1B Simülasyon Takipte</span>
        <span id="peer_id" class="text-zinc-700">ID: NS-0000</span>
    </div>

    <script>
        async function control(type) {
            const res = await fetch('/action/' + type);
            const data = await res.json();
            updateUI(data);
        }
        function updateUI(data) {
            document.getElementById('credits').innerText = data.internet_credits_mb;
            document.getElementById('logic_report').innerText = data.logic_report;
            document.getElementById('peer_id').innerText = "ID: " + data.peer_id;
        }
        async function updateLoop() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                updateUI(data);
                if(data.is_active) await fetch('/action/' + (data.mode === 'SHARING' ? 'share' : 'receive'));
            } catch(e) {}
            setTimeout(updateLoop, 1000);
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
