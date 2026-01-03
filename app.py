from flask import Flask, render_template_string, jsonify, request, Response, redirect
import time, io, os, requests, threading, base64, random, json, traceback
from threading import Lock
from urllib.parse import urljoin

app = Flask(__name__)

# --- NETSWAP SOVEREIGN OVERLORD v128.0 ---
# Vizyon: Bakiye Borsası + Yönetici Kilidi + Tam Otonom Denetim. [cite: 2025-12-26]
VERSION = "v128.0"
KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"
ADMIN_KEY = "ali_yigit_overlord_A55" # Senin gizli anahtarın

MOBILE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-A556B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36"
}

transaction_lock = Lock()
state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "internet_credits_mb": 0.0,
    "actual_mbps": 0.0,
    "last_op_time": time.perf_counter(),
    "logic_report": "Stabil",
    "evolution_count": 29,
    "s100_temp": "34°C",
    "global_lock": False, # Hükümdar Kilidi
    "banned_peers": [], # Kara Liste
    "user_registry": {} # Bakiye Borsası Verisi
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

# --- YÖNETİCİ MOTORU ---
@app.route('/overlord_api/<action>')
def admin_control(action):
    key = request.args.get('key')
    if key != ADMIN_KEY: return "ERİŞİM REDDEDİLDİ", 403
    
    target_peer = request.args.get('peer_id')
    with transaction_lock:
        if action == "ban":
            if target_peer and target_peer not in state["banned_peers"]:
                state["banned_peers"].append(target_peer)
        elif action == "unban":
            if target_peer in state["banned_peers"]:
                state["banned_peers"].remove(target_peer)
        elif action == "global_lock":
            state["global_lock"] = not state["global_lock"]
        elif action == "add_credit":
            if target_peer == state["peer_id"]:
                state["internet_credits_mb"] += 100
        elif action == "reset_credits":
             if target_peer == state["peer_id"]:
                state["internet_credits_mb"] = 0
    return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    """Hükümdar Paneli: Sadece A55 ve Sen [cite: 2025-12-26]"""
    key = request.args.get('key')
    if key != ADMIN_KEY: return "<h1>SOVEREIGN ACCESS DENIED</h1>", 403
    
    # Bakiye Borsası için kullanıcı listesini hazırla
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"><title>NetSwap Overlord Console</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #050505; color: #ff0000; font-family: monospace; }</style>
</head>
<body class="p-4" onload="adminLoop()">
    <div class="border-2 border-red-900 p-4 mb-6 text-center rounded-xl bg-red-950/10">
        <h1 class="text-2xl font-black italic uppercase tracking-tighter">Sovereign Overlord Console</h1>
        <p class="text-[9px] text-zinc-500 uppercase">A55 Authorized Hardware Access - v128.0</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div class="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
            <h2 class="text-xs font-bold text-red-500 mb-2 uppercase">Ağ Durumu</h2>
            <div class="text-[10px] space-y-1">
                <p>Global Kilit: <span id="gLock" class="font-bold">KAPALI</span></p>
                <p>Aktif Kullanıcı: <span id="uCount">1</span></p>
                <p>Yasaklı Sayısı: <span id="bCount">0</span></p>
            </div>
            <button onclick="adminAction('global_lock')" class="mt-4 w-full py-2 bg-red-900 text-white text-[10px] font-bold uppercase rounded">Global Kilit Tetikle</button>
        </div>
        <div class="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800 text-center">
            <h2 class="text-xs font-bold text-blue-500 mb-2 uppercase">Hükümdar Bakiyesi</h2>
            <div id="admCredits" class="text-3xl font-black text-white italic">0.00</div>
            <button onclick="adminAction('add_credit', '{{ p_id }}')" class="mt-2 text-[8px] text-green-500 font-bold uppercase underline">Hediye 100 MB Ekle</button>
        </div>
    </div>

    <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800">
        <h2 class="text-xs font-bold text-yellow-600 mb-4 uppercase text-center">Bakiye Borsası & Kullanıcı Listesi</h2>
        <div class="overflow-x-auto text-[9px] uppercase">
            <table class="w-full text-left">
                <thead><tr class="text-zinc-500 border-b border-zinc-900"><th>ID</th><th>Bakiye</th><th>Durum</th><th>Eylem</th></tr></thead>
                <tbody id="userTable">
                    <tr><td>{{ p_id }} (Siz)</td><td id="rowCred">0.00 MB</td><td class="text-green-500">AKTİF</td><td>-</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const key = "{{ a_key }}";
        const myId = "{{ p_id }}";
        async function adminAction(act, peer="") {
            await fetch(`/overlord_api/${act}?key=${key}&peer_id=${peer}`);
        }
        async function adminLoop() {
            const res = await fetch('/api/status');
            const data = await res.json();
            document.getElementById('admCredits').innerText = data.internet_credits_mb.toFixed(2);
            document.getElementById('rowCred').innerText = data.internet_credits_mb.toFixed(2) + " MB";
            document.getElementById('gLock').innerText = data.global_lock ? "AKTİF (KİLİTLİ)" : "KAPALI (AÇIK)";
            document.getElementById('bCount').innerText = data.banned_peers.length;
            setTimeout(adminLoop, 2000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY, p_id=state["peer_id"])

# --- TÜNEL VE AKSİYON MOTORLARI ---
@app.route('/tunnel_fetch')
def tunnel_fetch():
    target_url = request.args.get('url')
    with transaction_lock:
        if state["global_lock"]: return "SİSTEM HÜKÜMDAR TARAFINDAN KİLİTLENDİ", 423
        if state["peer_id"] in state["banned_peers"]: return "ERİŞİMİNİZ YASAKLANDI", 403
        if state["internet_credits_mb"] <= 0: return "Yetersiz Kredi", 403
        
    try:
        resp = requests.get(target_url, headers=MOBILE_HEADERS, timeout=15)
        state["internet_credits_mb"] = max(0, round(state["internet_credits_mb"] - (len(resp.content)/1048576), 6))
        return Response(resp.content, mimetype=resp.headers.get('Content-Type'))
    except: return "Hata", 500

@app.route('/action/<type>')
def handle_action(type):
    now = time.perf_counter()
    with transaction_lock:
        if state["global_lock"] and type != "stop": return jsonify({"error": "Sistem Kilitli"}), 423
        dt = now - state["last_op_time"]
        state["last_op_time"] = now
        state["actual_mbps"] = round(random.uniform(5.0, 98.0), 2)
        if type == "share":
            state["is_active"], state["mode"] = True, "SHARING"
            state["internet_credits_mb"] += round((state["actual_mbps"]/8)*dt, 6)
        elif type == "receive":
            state["is_active"], state["mode"] = True, "RECEIVING"
            state["internet_credits_mb"] = max(0, round(state["internet_credits_mb"] - (state["actual_mbps"]/8)*dt, 6))
        elif type == "stop":
            state["is_active"], state["mode"] = False, "IDLE"
            github_seal("credits.json", {"credits": state["internet_credits_mb"]}, "Overlord Seal")
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
    <title>NetSwap v128</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #000; color: #00ff41; font-family: monospace; }</style>
</head>
<body class="p-4" onload="mainLoop()">
    <div class="text-center mb-6">
        <h1 class="text-3xl font-black italic text-blue-500 uppercase">NetSwap Hub</h1>
        <p class="text-[9px] text-gray-500 uppercase">Sovereign Node - v128.0</p>
    </div>
    <div class="bg-zinc-950 p-8 rounded-3xl border-2 border-zinc-900 mb-6 text-center">
        <h2 class="text-[10px] text-zinc-500 font-bold mb-1 uppercase">Mevcut Bakiyen</h2>
        <div id="credits" class="text-6xl font-black text-white italic">0.000000</div>
    </div>
    <div class="grid grid-cols-2 gap-4 mb-6">
        <button onclick="control('share')" class="py-6 bg-green-700 text-black font-black rounded-2xl text-xl transition active:scale-95">VER</button>
        <button onclick="control('receive')" class="py-6 bg-blue-700 text-white font-black rounded-2xl text-xl transition active:scale-95">AL</button>
    </div>
    <button onclick="control('stop')" class="w-full py-4 bg-zinc-900 text-red-500 font-bold rounded-xl border border-zinc-800 transition text-[10px] uppercase">DURDUR</button>
    <script>
        async function control(type) { await fetch('/action/' + type); }
        async function mainLoop() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('credits').innerText = data.internet_credits_mb.toFixed(6);
                if(data.is_active) await fetch('/action/' + (data.mode === 'SHARING' ? 'share' : 'receive'));
            } catch(e) {}
            setTimeout(mainLoop, 1000);
        }
    </script>
</body></html>
""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
