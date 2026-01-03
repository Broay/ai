from flask import Flask, render_template_string, jsonify, request, send_file
import time, io, os, requests, threading, base64, random

app = Flask(__name__)

# --- SOVEREIGN SILENT v98.1 ---
VERSION = "v98.1"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"

state = {
    "total_mb": 0,
    "last_action": "Sessiz Mod Aktif. Bildirimler Devre Dışı.",
    "ai_status": "Otonom Takipte",
    "evolution_count": 0,
    "s100_temp": "36°C",
    "security_breach": "0",
    "latest_apk_link": f"https://github.com/{GH_REPO}/releases"
}

TUNNEL_DATA = b"S" * (1024 * 1024)

def self_evolve_silent():
    """Gelişimi GitHub'a iter, bildirim göndermez."""
    while True:
        time.sleep(3600)
        prompt = "v98.1 kodunu analiz et ve ağ hızını artıracak sessiz bir iyileştirme yap. SADECE kodun tamamını ver."
        
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
                sha = requests.get(f"https://api.github.com/repos/{GH_REPO}/contents/app.py", headers=headers).json().get('sha')
                payload = {"message": f"Silent Evolution v98.{state['evolution_count']}", "content": base64.b64encode(new_code.encode()).decode(), "sha": sha}
                requests.put(f"https://api.github.com/repos/{GH_REPO}/contents/app.py", headers=headers, json=payload)
                state["last_action"] = f"v98.{state['evolution_count']} mühürlendi. Senkronizasyon başarılı."
            except: pass

threading.Thread(target=self_evolve_silent, daemon=True).start()

@app.route('/download')
def download():
    state["total_mb"] += 1
    return send_file(io.BytesIO(TUNNEL_DATA), mimetype='application/octet-stream')

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sovereign Silent v98.1</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4">
    <div class="text-center mb-8 border-b border-zinc-800 pb-4">
        <h1 class="text-3xl font-black italic text-zinc-400">SILENT v98.1</h1>
        <p class="text-[9px] text-zinc-600 uppercase tracking-widest">Notification Engine: DISABLED</p>
    </div>

    <div class="border-2 border-zinc-700 p-4 rounded-lg mb-6 bg-black">
        <h2 class="text-[10px] text-zinc-500 uppercase font-bold mb-1">Rapor Paneli</h2>
        <div id="report" class="text-sm font-bold text-zinc-300">Sistem sessiz modda çalışıyor.</div>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-8">
        <div class="bg-zinc-950 p-4 rounded border border-green-900 text-center">
            <span class="text-[8px] block text-zinc-500 uppercase">Tünel Verisi</span>
            <div id="data_val" class="text-4xl font-black">0</div><span class="text-[10px]">MB</span>
        </div>
        <div class="bg-zinc-950 p-4 rounded border border-zinc-800 text-center">
            <span class="text-[8px] block text-zinc-500 uppercase">S100 Durum</span>
            <div id="temp" class="text-xl font-bold mt-1">36°C</div>
        </div>
    </div>

    <button onclick="ignite()" id="btn" class="w-full py-8 bg-zinc-800 text-zinc-300 font-black uppercase rounded-2xl shadow-xl transition active:scale-95">SİSTEMİ ATEŞLE</button>

    <div class="mt-8 text-center">
        <a href="{{ apk_link }}" target="_blank" class="text-xs text-zinc-500 underline font-bold uppercase tracking-tighter">Otonom APK Merkezi</a>
    </div>

    <script>
        let active = false;
        async function ignite() { 
            if(active) return; active = true; 
            document.getElementById('btn').innerText = "SILENT ACTIVE";
            loop(); 
        }
        async function loop() {
            if(!active) return;
            try {
                await fetch('/download');
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('data_val').innerText = data.total_mb;
                document.getElementById('report').innerText = "> " + data.last_action;
                document.getElementById('temp').innerText = data.s100_temp;
                if(data.total_mb % 100 === 0 && navigator.vibrate) navigator.vibrate(20);
                setTimeout(loop, 110);
            } catch(e) {}
        }
    </script>
</body></html>
""", apk_link=state["latest_apk_link"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
