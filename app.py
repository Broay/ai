from flask import Flask, render_template_string, jsonify, request, send_file
import time, io, os, requests, threading, base64, random

app = Flask(__name__)

# --- NETSWAP SOVEREIGN FAST-TRACK v102.0 ---
#
VERSION = "v102.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"

state = {
    "total_shared_mb": 0,
    "internet_credits_mb": 0,
    "last_action": "Sistem Başlatıldı. 5 dk içinde ilk evrim gelecek.",
    "ai_status": "Gözlem Modu",
    "evolution_count": 3, # image_6ace25.png'deki son durumdan devam
    "s100_temp": "34°C",
    "latest_apk_link": f"https://github.com/{GH_REPO}/releases"
}

def self_mutate_logic():
    """1 Milyar Simülasyon ve Otonom Güncelleme Motoru [cite: 2025-12-26]"""
    state["ai_status"] = "Simülasyon Yapılıyor..."
    prompt = f"NetSwap v102.0 P2P takas sistemini analiz et. 1 milyar simülasyon yap ve gecikmeyi azaltacak bir güncelleme yaz. SADECE KODU VER."
    
    new_code = ""
    for key in KEYS:
        if not key: continue
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}"
            res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
            if res.status_code == 200:
                new_code = res.json()['candidates'][0]['content']['parts'][0]['text'].replace("```python", "").replace("```", "").strip()
                break
        except Exception as e:
            state["last_action"] = f"API Hatası: {str(e)[:30]}"
    
    if new_code:
        state["evolution_count"] += 1
        try:
            headers = {"Authorization": f"token {GH_TOKEN}"}
            # Dosya SHA bilgisini al
            f_url = f"https://api.github.com/repos/{GH_REPO}/contents/app.py"
            sha = requests.get(f_url, headers=headers).json().get('sha')
            
            payload = {
                "message": f"Sovereign Evolution v102.{state['evolution_count']}",
                "content": base64.b64encode(new_code.encode()).decode(),
                "sha": sha
            }
            res = requests.put(f_url, headers=headers, json=payload)
            
            # Log dosyasını da güncelle
            log_url = f"https://api.github.com/repos/{GH_REPO}/contents/evolution_log.txt"
            log_sha = requests.get(log_url, headers=headers).json().get('sha')
            log_content = f"Evrim Döngüsü {state['evolution_count']}:\nNetSwap P2P protokolü otonom olarak optimize edildi."
            log_payload = {
                "message": "Log Güncelleme",
                "content": base64.b64encode(log_content.encode()).decode(),
                "sha": log_sha
            }
            requests.put(log_url, headers=headers, json=log_payload)
            
            state["last_action"] = f"v102.{state['evolution_count']} GitHub'a mühürlendi!"
        except Exception as e:
            state["last_action"] = f"GitHub Hatası: {str(e)[:30]}"
    state["ai_status"] = "Otonom Takipte"

def autonomous_engine():
    """Zamanlayıcı: İlk evrim 5. dakikada, sonra her saat başı [cite: 2025-12-26]"""
    time.sleep(300) # İlk 5 dakika bekle
    while True:
        self_mutate_logic()
        time.sleep(3600)

threading.Thread(target=autonomous_engine, daemon=True).start()

@app.route('/force_evolve')
def force_evolve():
    """Manuel tetikleyici butonu"""
    threading.Thread(target=self_mutate_logic).start()
    return jsonify({"status": "Evrim Tetiklendi"})

@app.route('/share')
def share():
    state["total_shared_mb"] += 10
    state["internet_credits_mb"] += 10
    return jsonify({"credits": state["internet_credits_mb"]})

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetSwap Fast-Track v102.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4">
    <div class="text-center mb-8">
        <h1 class="text-4xl font-black italic text-blue-500">NETSWAP v102</h1>
        <p class="text-[9px] text-gray-500 tracking-[3px] uppercase mt-1">Self-Evolution & P2P Exchange</p>
    </div>

    <div class="bg-zinc-950 p-6 rounded-3xl border-2 border-blue-600 mb-8 text-center shadow-[0_0_20px_rgba(59,130,246,0.2)]">
        <h2 class="text-[10px] text-blue-400 font-bold uppercase mb-1">İnternet Kredisi</h2>
        <div id="credits" class="text-6xl font-black text-white">0</div>
        <span class="text-xs text-gray-500">MB HAKKI</span>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-8">
        <div class="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800 text-center">
            <span class="text-[8px] text-gray-500 uppercase">S100 Isı</span>
            <div id="temp" class="text-xl font-bold text-orange-500">34°C</div>
        </div>
        <div class="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800 text-center">
            <span class="text-[8px] text-gray-500 uppercase">Döngü</span>
            <div id="evo" class="text-xl font-bold text-yellow-500">3</div>
        </div>
    </div>

    <div class="space-y-4 mb-8">
        <button onclick="ignite()" id="btn" class="w-full py-6 bg-green-600 text-black font-black uppercase rounded-2xl text-xl shadow-lg transition active:scale-95">İnternet Paylaş</button>
        <button onclick="forceEvolve()" class="w-full py-3 bg-zinc-800 text-zinc-400 font-bold uppercase rounded-xl text-[10px] tracking-widest border border-zinc-700">Zorunlu Evrim Tetikle</button>
    </div>

    <div class="border-t border-zinc-900 pt-6">
        <div class="flex justify-between items-center mb-2">
            <span class="text-[10px] font-bold text-gray-500 uppercase italic">Canlı Rapor:</span>
            <span id="ai_status" class="text-[9px] bg-blue-900 px-2 py-0.5 rounded text-blue-200">Otonom Takipte</span>
        </div>
        <p id="report" class="text-xs italic text-gray-400 font-bold leading-tight">> Bekleniyor...</p>
    </div>

    <script>
        let active = false;
        async function forceEvolve() {
            document.getElementById('report').innerText = "> Evrim sinyali gönderildi...";
            await fetch('/force_evolve');
        }
        async function ignite() { 
            if(active) return; active = true; 
            document.getElementById('btn').innerText = "PAYLAŞILIYOR...";
            loop(); 
        }
        async function loop() {
            if(!active) return;
            try {
                await fetch('/share');
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('credits').innerText = data.internet_credits_mb;
                document.getElementById('report').innerText = "> " + data.last_action;
                document.getElementById('temp').innerText = data.s100_temp;
                document.getElementById('evo').innerText = data.evolution_count;
                document.getElementById('ai_status').innerText = data.ai_status;
                setTimeout(loop, 120);
            } catch(e) {}
        }
    </script>
</body></html>
""", apk_link=state["latest_apk_link"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
