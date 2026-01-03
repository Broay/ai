from flask import Flask, render_template_string, jsonify, request, Response
import time, io, os, requests, threading, base64, random, json, traceback
from threading import Lock

app = Flask(__name__)

# --- NETSWAP SOVEREIGN OVERLORD-FIX v129.0 ---
# Amacı: 404 hatasını gidermek ve Bakiye Borsası'nı aktif etmek. [cite: 2025-12-26]
VERSION = "v129.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"
ADMIN_KEY = "ali_yigit_overlord_A55" # Senin özel erişim anahtarın

transaction_lock = Lock()
state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "internet_credits_mb": 120.0, # Mevcut bakiyen korundu
    "actual_mbps": 0.0,
    "last_op_time": time.perf_counter(),
    "ai_status": "Overlord Denetiminde",
    "global_lock": False,
    "banned_peers": [],
    "user_registry": {} # Diğer kullanıcılar buraya düşecek
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

# --- OVERLORD YÖNETİCİ KONTROLLERİ ---
@app.route('/overlord_api/<action>')
def admin_api(action):
    if request.args.get('key') != ADMIN_KEY: return "ERİŞİM REDDEDİLDİ", 403
    
    target_peer = request.args.get('peer_id')
    with transaction_lock:
        if action == "ban" and target_peer: state["banned_peers"].append(target_peer)
        elif action == "lock": state["global_lock"] = not state["global_lock"]
        elif action == "gift": state["internet_credits_mb"] += 100.0
    return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if request.args.get('key') != ADMIN_KEY: return "Sovereign Access Required", 403
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"><title>NetSwap Overlord</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #ff0000; font-family: monospace; }</style>
</head>
<body class="p-4" onload="updatePanel()">
    <div class="border-2 border-red-900 p-4 mb-6 rounded-2xl bg-red-950/10 text-center">
        <h1 class="text-xl font-black uppercase">Sovereign Overlord v129</h1>
        <p class="text-[8px] text-zinc-500">PAÜ - Bilgisayar Programcılığı / Ali Yiğit Bartın</p>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-6">
        <div class="bg-zinc-900 p-4 rounded-xl border border-zinc-800 text-center">
            <span class="text-[8px] text-zinc-500 uppercase">Aktif Kredi</span>
            <div id="admCred" class="text-2xl font-black text-white">0.00</div>
            <button onclick="adminCall('gift')" class="mt-2 text-[8px] text-green-500 underline uppercase">100 MB Hediye Et</button>
        </div>
        <div class="bg-zinc-900 p-4 rounded-xl border border-zinc-800 text-center">
            <span class="text-[8px] text-zinc-500 uppercase">Global Kilit</span>
            <div id="lockStat" class="text-xs font-bold text-red-500 mt-1">AÇIK</div>
            <button onclick="adminCall('lock')" class="mt-2 text-[8px] text-red-500 underline uppercase">Tetikle</button>
        </div>
    </div>

    <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-900 mb-6">
        <h2 class="text-[10px] text-yellow-600 font-bold mb-3 uppercase tracking-widest text-center italic">Bakiye Borsası</h2>
        <table class="w-full text-[9px] text-left">
            <thead><tr class="text-zinc-600 border-b border-zinc-900"><th>PEER ID</th><th>BAKİYE</th><th>EYLEM</th></tr></thead>
            <tbody id="userTable">
                <tr><td>{{ p_id }} (Siz)</td><td id="myCred">0 MB</td><td>-</td></tr>
            </tbody>
        </table>
    </div>

    <script>
        const key = "{{ a_key }}";
        async function adminCall(act) { await fetch(`/overlord_api/${act}?key=${key}`); }
        async function updatePanel() {
            const res = await fetch('/api/status');
            const data = await res.json();
            document.getElementById('admCred').innerText = data.internet_credits_mb.toFixed(2);
            document.getElementById('myCred').innerText = data.internet_credits_mb.toFixed(2) + " MB";
            document.getElementById('lockStat').innerText = data.global_lock ? "KİLİTLİ" : "AÇIK";
            setTimeout(updatePanel, 2000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY, p_id=state["peer_id"])

# --- MEVCUT SİSTEM ÇEKİRDEĞİ ---
@app.route('/action/<type>')
def handle_action(type):
    now = time.perf_counter()
    with transaction_lock:
        if state["global_lock"] and type != "stop": return jsonify({"error": "Global Lock"}), 423
        dt = now - state["last_op_time"]
        state["last_op_time"] = now
        state["actual_mbps"] = round(random.uniform(1.0, 98.0), 2)
        if type == "share":
            state["is_active"], state["mode"] = True, "SHARING"
            state["internet_credits_mb"] += round((state["actual_mbps"]/8)*dt, 6)
        elif type == "receive":
            state["is_active"], state["mode"] = True, "RECEIVING"
            state["internet_credits_mb"] = max(0, round(state["internet_credits_mb"] - (state["actual_mbps"]/8)*dt, 6))
        elif type == "stop":
            state["is_active"], state["mode"] = False, "IDLE"
            github_seal("credits.json", {"credits": state["internet_credits_mb"]}, "Seal v129")
    return jsonify(state)

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"><title>NetSwap Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4" onload="mainLoop()">
    <div class="text-center mb-6">
        <h1 class="text-2xl font-black italic text-blue-500">NETSWAP HUB</h1>
        <p class="text-[8px] text-zinc-500">PAÜ Programcılık Node - v129</p>
    </div>
    <div class="bg-zinc-950 p-6 rounded-3xl border-2 border-zinc-900 mb-6 text-center">
        <div id="credits" class="text-6xl font-black text-white italic">0.00</div>
        <span class="text-[8px] text-zinc-700 uppercase">Doğrulanmış Rezerv</span>
    </div>
    <div class="grid grid-cols-2 gap-4">
        <button onclick="control('share')" class="py-6 bg-green-700 text-black font-black rounded-2xl">VER</button>
        <button onclick="control('receive')" class="py-6 bg-blue-700 text-white font-black rounded-2xl">AL</button>
    </div>
    <script>
        async function control(type) { await fetch('/action/' + type); }
        async function mainLoop() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('credits').innerText = data.internet_credits_mb.toFixed(2);
                if(data.is_active) await fetch('/action/' + (data.mode === 'SHARING' ? 'share' : 'receive'));
            } catch(e) {}
            setTimeout(mainLoop, 1000);
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
