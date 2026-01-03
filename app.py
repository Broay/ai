from flask import Flask, render_template_string, jsonify, request, Response
import time, io, os, requests, threading, base64, random, json, traceback
from threading import Lock
from urllib.parse import urljoin

app = Flask(__name__)

# --- NETSWAP SOVEREIGN COMMAND CENTER v136.1 ---
# Vizyon: Önceki tüm özelliklerin (Proxy, Cloak, Vault) yeni Command Center ile birleşimi. [cite: 2025-12-26, 2026-01-03]
VERSION = "v136.1"
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = "Broay/ai"
ADMIN_KEY = "ali_yigit_overlord_A55" 
ADMIN_PIN = "1907" 

# Vodafone Maskeleme İmzası
MOBILE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-A556B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36",
    "X-Requested-With": "com.android.chrome"
}

transaction_lock = Lock()
state = {
    "is_active": False,
    "mode": "IDLE",
    "peer_id": f"NS-{random.randint(1000, 9999)}",
    "internet_credits_mb": 120.0,
    "actual_mbps": 0.0,
    "last_op_time": time.perf_counter(),
    "global_lock": False,
    "evolution_count": 37,
    "s100_temp": "34°C",
    "banned_peers": [],
    "user_registry": {} 
}

# --- YENİDEN YAZIM MOTORU (v127'den mühürlü) [cite: 2026-01-03] ---
def rewrite_links(content, base_url):
    if isinstance(content, bytes):
        try: content = content.decode('utf-8')
        except: return content
    tags = ['href="', 'src="', 'action="']
    for tag in tags:
        start_idx = 0
        while True:
            start_idx = content.find(tag, start_idx)
            if start_idx == -1: break
            quote = tag[-1]
            end_idx = content.find(quote, start_idx + len(tag))
            if end_idx == -1: break
            original_url = content[start_idx + len(tag):end_idx]
            if original_url and not original_url.startswith(('data:', 'javascript:', '#')):
                absolute_url = urljoin(base_url, original_url)
                new_url = f"/tunnel_fetch?url={absolute_url}"
                content = content[:start_idx + len(tag)] + new_url + content[end_idx:]
                start_idx += len(new_url) + len(tag)
            else: start_idx = end_idx + 1
    return content

def github_seal(filename, data, message):
    if not GH_TOKEN: return
    try:
        headers = {"Authorization": f"token {GH_TOKEN}"}
        url = f"https://api.github.com/repos/{GH_REPO}/contents/{filename}"
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        payload = {"message": message, "content": base64.b64encode(json.dumps(data, indent=4).encode()).decode(), "sha": sha}
        requests.put(url, headers=headers, json=payload)
    except: pass

def check_admin_auth(req):
    ua = req.headers.get('User-Agent', '').upper()
    key = req.args.get('key')
    pin = req.args.get('pin', '').strip()
    is_a55 = "437F" in ua or "SM-A55" in ua or "MOBILE" in ua or "ANDROID" in ua
    if key == ADMIN_KEY and pin == ADMIN_PIN and is_a55: return True
    return False

# --- SOVEREIGN COMMAND API ---
@app.route('/overlord_api/<action>')
def admin_api(action):
    if not check_admin_auth(request): return "ERİŞİM REDDEDİLDİ", 403
    target = request.args.get('target_peer')
    with transaction_lock:
        if action == "lock": state["global_lock"] = not state["global_lock"]
        elif action == "gift": state["internet_credits_mb"] += 100.0
        elif action == "kick" and target:
            if target in state["user_registry"]: state["user_registry"][target]["status"] = "KICKED"
        elif action == "ban" and target:
            if target not in state["banned_peers"]: state["banned_peers"].append(target)
    return jsonify(state)

@app.route('/overlord')
def overlord_panel():
    if not check_admin_auth(request): return "<h1>YETKİSİZ ERİŞİM</h1>", 403
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><title>Command Center v136</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-white p-4 font-mono">
    <div class="border-b border-red-900 pb-4 mb-6 flex justify-between items-center">
        <div><h1 class="text-xl font-black text-red-600 italic uppercase">Command Center</h1>
        <p class="text-[8px] text-zinc-500 uppercase tracking-widest">S100: {{ temp }} | {{ peer_id }}</p></div>
        <button onclick="f('lock')" class="px-4 py-2 bg-red-900 text-[10px] font-bold rounded">GLOBAL KİLİT</button>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 text-center">
        <div class="bg-zinc-950 p-4 border border-zinc-900 rounded-2xl">
            <p class="text-[9px] text-zinc-600 uppercase">Rezerv</p><div id="c" class="text-4xl font-black italic">...</div>
            <button onclick="f('gift')" class="text-[8px] text-green-500 underline uppercase">100 MB Ekle</button>
        </div>
        <div class="bg-zinc-950 p-4 border border-zinc-900 rounded-2xl">
            <p class="text-[9px] text-zinc-600 uppercase">Yük</p><div id="speed" class="text-4xl font-black italic text-blue-500">...</div>
        </div>
        <div class="bg-zinc-950 p-4 border border-zinc-900 rounded-2xl">
            <p class="text-[9px] text-zinc-600 uppercase">Düğümler</p><div id="nodes" class="text-4xl font-black italic text-yellow-500">0</div>
        </div>
    </div>
    <div class="bg-zinc-950 rounded-2xl border border-zinc-900 overflow-hidden">
        <div class="p-3 bg-zinc-900/50 text-[10px] font-bold text-red-500 uppercase">Canlı Takip & Müdahale</div>
        <table class="w-full text-[9px] text-left">
            <thead class="text-zinc-600 border-b border-zinc-900"><tr><th class="p-3">ID</th><th>SON GÖRÜLEN</th><th>TRAFİK</th><th>DURUM</th><th>EYLEM</th></tr></thead>
            <tbody id="userTable"></tbody>
        </table>
    </div>
    <script>
        const k="{{a_key}}", p="{{a_pin}}";
        async function f(a, t=""){ await fetch(`/overlord_api/${a}?key=${k}&pin=${p}&target_peer=${t}`); }
        async function u(){
            const r=await fetch('/api/status'), d=await r.json();
            document.getElementById('c').innerText = d.internet_credits_mb.toFixed(2);
            document.getElementById('speed').innerText = d.actual_mbps.toFixed(1) + " Mbps";
            document.getElementById('nodes').innerText = Object.keys(d.user_registry).length;
            let html="";
            for(let id in d.user_registry){
                let user = d.user_registry[id];
                html += `<tr class="border-b border-zinc-900">
                    <td class="p-3 font-bold text-white">${id}</td>
                    <td>${user.last_seen}</td>
                    <td>${user.received.toFixed(1)}/${user.sent.toFixed(1)} MB</td>
                    <td class="${user.status=='ACTIVE'?'text-green-500':'text-red-500'}">${user.status}</td>
                    <td><button onclick="f('kick','${id}')" class="text-yellow-600 mr-2">KICK</button>
                    <button onclick="f('ban','${id}')" class="text-red-600">BAN</button></td></tr>`;
            }
            document.getElementById('userTable').innerHTML = html; setTimeout(u, 1000);
        } u();
    </script>
</body></html>
""", a_key=ADMIN_KEY, a_pin=ADMIN_PIN, temp=state["s100_temp"], peer_id=state["peer_id"])

@app.route('/tunnel_fetch')
def tunnel_fetch():
    target_url = request.args.get('url')
    if not target_url: return "URL?", 400
    with transaction_lock:
        if state["global_lock"]: return "LOCKED", 423
        if state["internet_credits_mb"] <= 0: return "Yetersiz Kredi", 403
    try:
        resp = requests.get(target_url, headers=MOBILE_HEADERS, timeout=15)
        state["internet_credits_mb"] = max(0, round(state["internet_credits_mb"] - (len(resp.content)/1048576), 6))
        if "text/html" in resp.headers.get("Content-Type", ""):
            return Response(rewrite_links(resp.content, target_url), mimetype=resp.headers.get('Content-Type'))
        return Response(resp.content, mimetype=resp.headers.get('Content-Type'))
    except: return "Proxy Hatası", 500

@app.route('/action/<type>')
def handle_action(type):
    now = time.perf_counter()
    p_id = request.args.get('peer_id', 'GUEST')
    with transaction_lock:
        if p_id in state["banned_peers"]: return jsonify({"error": "BANNED"}), 403
        if state["global_lock"] and type != "stop": return jsonify({"error": "LOCKED"}), 423
        if p_id not in state["user_registry"]:
            state["user_registry"][p_id] = {"received": 0, "sent": 0, "status": "ACTIVE", "last_seen": ""}
        state["user_registry"][p_id]["last_seen"] = time.strftime('%H:%M:%S')
        dt, state["last_op_time"] = now - state["last_op_time"], now
        state["actual_mbps"] = round(random.uniform(5.0, 98.0), 2)
        mb = (state["actual_mbps"]/8)*dt
        if type == "share":
            state["is_active"], state["mode"] = True, "SHARING"
            state["internet_credits_mb"] += round(mb, 6)
            state["user_registry"][p_id]["sent"] += mb
        elif type == "receive":
            if state["user_registry"][p_id]["status"] == "KICKED": return jsonify({"error": "KICKED"}), 401
            state["is_active"], state["mode"] = True, "RECEIVING"
            state["internet_credits_mb"] = max(0, round(state["internet_credits_mb"] - mb, 6))
            state["user_registry"][p_id]["received"] += mb
        elif type == "stop":
            state["is_active"], state["mode"] = False, "IDLE"
            github_seal("credits.json", {"credits": state["internet_credits_mb"]}, "Final Audit v136")
    return jsonify(state)

@app.route('/api/status')
def get_status(): return jsonify(state)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NetSwap Hub</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-green-500 font-mono p-4" onload="mainLoop()">
    <div class="text-center mb-10"><h1 class="text-3xl font-black text-blue-600 uppercase italic">NETSWAP HUB</h1><p class="text-[9px] text-zinc-600">v136.1 Command Ready</p></div>
    <div class="bg-zinc-950 p-12 rounded-[40px] border-2 border-zinc-900 mb-10 text-center shadow-2xl">
        <div id="credits" class="text-7xl font-black text-white italic">0.00</div><span class="text-[10px] text-zinc-700 uppercase mt-4 block">MB REZERV</span>
    </div>
    <div class="grid grid-cols-2 gap-4"><button onclick="control('share')" class="py-10 bg-green-700 text-black font-black rounded-3xl text-3xl transition active:scale-90">VER</button>
    <button onclick="control('receive')" class="py-10 bg-blue-700 text-white font-black rounded-3xl text-3xl transition active:scale-90">AL</button></div>
    <div id="secretSpot" onclick="triggerAdmin()" class="fixed bottom-0 right-0 w-24 h-24 opacity-0"></div>
    <script>
        let myId = "NS-" + Math.floor(1000 + Math.random() * 9000);
        function triggerAdmin() {
            window.clickCount = (window.clickCount || 0) + 1;
            if(window.clickCount >= 5) {
                const pin = prompt("Hükümdar PIN:");
                if(pin) window.location.href = `/overlord?key={{a_key}}&pin=` + pin.trim();
                window.clickCount = 0;
            }
            setTimeout(() => { window.clickCount = 0; }, 3000);
        }
        async function control(type) { await fetch(`/action/${type}?peer_id=${myId}`); }
        async function mainLoop() {
            try {
                const res = await fetch('/api/status'); const data = await res.json();
                document.getElementById('credits').innerText = data.internet_credits_mb.toFixed(2);
                if(data.is_active) await fetch(`/action/${data.mode==='SHARING'?'share':'receive'}?peer_id=${myId}`);
            } catch(e) {} setTimeout(mainLoop, 1000);
        }
    </script>
</body></html>
""", a_key=ADMIN_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
