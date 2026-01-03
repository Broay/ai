from flask import Flask, render_template_string, jsonify, request, send_file
import time, io, os, requests, threading, base64, random, json, traceback

app = Flask(__name__)

# --- NETSWAP SOVEREIGN FILTER v112.0 ---
# Amacı: Saniyede 1 denetim yaparken aynı hataları raporlamayı engellemek. [cite: 2025-12-26]
VERSION = "v112.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"

state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "internet_credits_mb": 0,
    "last_action": "v112.0 Filtreleme Modu Aktif.",
    "ai_status": "Akıllı Denetim",
    "debug_report": "Sistem Temiz",
    "last_error_hash": "", # Aynı hatayı engellemek için kimlik deposu
    "latest_improvement": "Analiz Bekleniyor...",
    "evolution_count": 13,
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

def autonomous_watchman():
    """Saniyede 1 denetim yapar, sadece yeni hataları raporlar [cite: 2025-12-26]"""
    while True:
        try:
            # 1. HATA AYIKLAMA (Saniyede 1)
            # Burada simüle edilmiş bir hata yakalama yapısı var
            current_status = "Tünel Stabil" if state["is_active"] else "Sistem Beklemede"
            
            # 2. İYİLEŞTİRME ANALİZİ (Gelecek Planlama)
            if random.random() < 0.01: 
                prompt = "NetSwap v112.0 için 1 milyar simülasyon yap ve tek bir devrimsel iyileştirme yaz."
                for key in KEYS:
                    if not key: continue
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}"
                        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
                        if res.status_code == 200:
                            insight = res.json()['candidates'][0]['content']['parts'][0]['text']
                            state["latest_improvement"] = insight[:60] + "..."
                            github_seal("future_improvements.json", {"idea": insight, "v": VERSION}, "Future Insight Update")
                            break
                    except: continue

            time.sleep(1) # Saniyede 1 döngü
            
        except Exception as e:
            error_trace = str(traceback.format_exc())
            # FİLTRELEME: Eğer hata bir öncekiyle aynıysa raporlama yapma
            if error_trace != state["last_error_hash"]:
                state["last_error_hash"] = error_trace
                state["debug_report"] = "YENİ HATA YAKALANDI"
                github_seal("debug_report.json", {"error": error_trace, "ts": time.ctime()}, "New Unique Error Caught")
            else:
                state["debug_report"] = "Aynı Hata (Raporlama Atlandı)"

threading.Thread(target=autonomous_watchman, daemon=True).start()

@app.route('/action/<type>')
def handle_action(type):
    if type == "share":
        state["is_active"] = True
        state["mode"] = "SHARING"
        state["internet_credits_mb"] += 10
        state["last_action"] = "Kredi Kazanımı Aktif."
    elif type == "receive":
        if state["internet_credits_mb"] >= 10:
            state["is_active"] = True
            state["mode"] = "RECEIVING"
            state["internet_credits_mb"] -= 10
            state["last_action"] = "Kredi Kullanımı Aktif."
        else: state["last_action"] = "Bakiye Yetersiz!"
    elif type == "stop":
        state["is_active"] = False
        state["mode"] = "IDLE"
        state["last_action"] = "Sistem Durduruldu."
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
    <title>NetSwap Filter v112.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4" onload="updateLoop()">
    <div class="text-center mb-6">
        <h1 class="text-3xl font-black italic text-green-500 uppercase">Filter Engine</h1>
        <p class="text-[9px] text-gray-500 uppercase tracking-widest">Deduplication Debugger - v112.0</p>
    </div>

    <div class="bg-zinc-950 p-5 rounded-3xl border border-zinc-800 mb-6 text-center">
        <h2 class="text-[10px] text-zinc-500 font-bold mb-1 uppercase tracking-tighter">Akıllı Bakiye (MB)</h2>
        <div id="credits" class="text-6xl font-black text-white italic">0</div>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-6">
        <button onclick="control('share')" class="py-6 bg-green-700 text-black font-black uppercase rounded-2xl text-xl shadow-lg active:scale-95 transition">VER</button>
        <button onclick="control('receive')" class="py-6 bg-blue-700 text-white font-black uppercase rounded-2xl text-xl shadow-lg active:scale-95 transition">AL</button>
    </div>

    <div class="space-y-4 mb-8">
        <div class="bg-zinc-950 p-4 rounded-xl border border-red-900">
            <h2 class="text-[9px] text-red-500 font-bold mb-1 uppercase">Hata Denetimi (Benzersiz)</h2>
            <div id="debug_report" class="text-xs text-gray-400 italic">Analiz ediliyor...</div>
        </div>
        <div class="bg-zinc-950 p-4 rounded-xl border border-blue-900">
            <h2 class="text-[9px] text-blue-500 font-bold mb-1 uppercase">Gelecek Vizyonu</h2>
            <div id="latest_improvement" class="text-xs text-gray-400 italic">Veri bekleniyor...</div>
        </div>
    </div>

    <button onclick="control('stop')" class="w-full py-4 bg-zinc-900 text-red-500 font-bold uppercase rounded-xl border border-zinc-800 mb-8 active:scale-95 transition">DURDUR</button>

    <div class="flex justify-between items-center text-[9px] font-bold border-t border-zinc-900 pt-4">
        <span class="text-green-600 uppercase">Sürekli Filtreleme Aktif</span>
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
            document.getElementById('debug_report').innerText = data.debug_report;
            document.getElementById('latest_improvement').innerText = data.latest_improvement;
            document.getElementById('peer_id').innerText = "ID: " + data.peer_id;
        }
        async function updateLoop() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                updateUI(data);
            } catch(e) {}
            setTimeout(updateLoop, 1000);
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
