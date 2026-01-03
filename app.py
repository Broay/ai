from flask import Flask, render_template_string, jsonify, request, send_file
import time, io, os, requests, threading, base64

app = Flask(__name__)

# --- EXECUTIVE CONFIG ---
VERSION = "v91.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "bartiinss/ai" # Senin repon

state = {
    "total_mb": 0,
    "active_mentor": "CORE 0",
    "last_action": "Sistem başlatıldı, emir bekleniyor.",
    "network_health": "96 Mbps Stabil",
    "hardware": "Casper S100 Safe"
}

# 1MB Tünel Paketi
TUNNEL_DATA = b"S" * (1024 * 1024)

def mentor_audit():
    """Mentor AI'ların otonom denetim döngüsü"""
    while True:
        time.sleep(3600) # Saatlik otonom kontrol
        prompt = f"NetSwap v91.0 Analizi: {state['network_health']} altında {state['total_mb']} MB işlendi. İyileştirme öner."
        for key in KEYS:
            if not key: continue
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
                if res.status_code == 200:
                    state["last_action"] = "Mentor AI: " + res.json()['candidates'][0]['content']['parts'][0]['text'][:50] + "..."
                    break
            except: continue

threading.Thread(target=mentor_audit, daemon=True).start()

@app.route('/download')
def download():
    state["total_mb"] += 1
    return send_file(io.BytesIO(TUNNEL_DATA), mimetype='application/octet-stream')

@app.route('/api/status')
def get_status():
    return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sovereign Executive</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4">
    <div class="text-center mb-6">
        <h1 class="text-2xl font-black italic">OVERLORD v91.0</h1>
        <p class="text-[10px] text-blue-400">PAU LAB | CASPER S100 PROTECTION ACTIVE</p>
    </div>

    <div class="border-2 border-green-500 p-4 rounded-lg mb-6 bg-black shadow-[0_0_15px_rgba(0,255,65,0.3)]">
        <h2 class="text-xs font-bold mb-2 uppercase text-gray-400 underline">Otonom Rapor</h2>
        <div id="report" class="text-sm font-bold leading-tight">İkiziniz rapor hazırlıyor...</div>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="border border-green-900 p-3 rounded bg-[#050505]">
            <span class="text-[9px] block">TOPLAM VERİ</span>
            <div id="data_val" class="text-3xl font-bold">0</div><span class="text-xs">MB</span>
        </div>
        <div class="border border-green-900 p-3 rounded bg-[#050505]">
            <span class="text-[9px] block">AĞ SAĞLIĞI</span>
            <div class="text-sm font-bold text-blue-400">96 MBPS</div>
        </div>
    </div>

    <button onclick="ignite()" id="btn" class="w-full py-5 bg-green-600 text-black font-black uppercase rounded active:scale-95 transition">SİSTEMİ ATEŞLE</button>

    <script>
        let active = false;
        function speak(t) { 
            const s = new SpeechSynthesisUtterance(t); s.lang = 'tr-TR'; 
            window.speechSynthesis.speak(s); 
        }

        async function ignite() {
            if(active) return; active = true;
            document.getElementById('btn').innerText = "ÇALIŞIYOR...";
            speak("Overlord v91.0 aktif. Ali Yiğit, tüm yetki ikizinde.");
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
                
                if(data.total_mb % 20 === 0 && navigator.vibrate) navigator.vibrate([30, 30]);
                setTimeout(loop, 150);
            } catch(e) {}
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)