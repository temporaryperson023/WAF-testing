from flask import Blueprint, render_template, request, jsonify, session
import random
import time
import hashlib

slb_bp = Blueprint('slb', __name__, url_prefix='/slb')

# Simulated backend server pool
# In real Haltdos SLB, these would be your actual upstream servers
SERVERS = [
    {"id": "server-01", "ip": "10.0.0.1", "port": 8001, "weight": 3, "zone": "Zone-A", "healthy": True},
    {"id": "server-02", "ip": "10.0.0.2", "port": 8002, "weight": 2, "zone": "Zone-A", "healthy": True},
    {"id": "server-03", "ip": "10.0.0.3", "port": 8003, "weight": 1, "zone": "Zone-B", "healthy": True},
]

# Round-robin counter (shared state)
rr_counter = {"index": 0}

# Request counters per server (simulates Least Connections)
server_connections = {"server-01": 0, "server-02": 0, "server-03": 0}

# Failover state (which servers are manually downed)
downed_servers = set()


def get_healthy_servers():
    return [s for s in SERVERS if s["healthy"] and s["id"] not in downed_servers]


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
@slb_bp.route('/')
def dashboard():
    return render_template('slb/dashboard.html')


# ─────────────────────────────────────────────
# MODULE 1 — HEALTH MONITOR
# ─────────────────────────────────────────────
@slb_bp.route('/health', methods=['GET'])
def health():
    return render_template('slb/health.html')

@slb_bp.route('/health/probe', methods=['GET'])
def health_probe():
    """
    This is the actual endpoint Haltdos health monitor should point to.
    Returns 200 OK with JSON status if server is healthy.
    Haltdos marks a backend healthy after N successful probes.
    """
    return jsonify({
        "status": "healthy",
        "server": "WAF-Lab-Backend",
        "uptime": "simulated",
        "timestamp": time.time()
    }), 200


@slb_bp.route('/lb-algo', methods=['GET', 'POST'])
def lb_algo():
    result = None
    selected_algo = None

    if request.method == 'POST':
        algo = request.form.get('algorithm', 'round_robin')
        selected_algo = algo
        healthy = get_healthy_servers()

        if not healthy:
            result = {"error": "No healthy servers available"}
            return render_template('slb/lb_algo.html', result=result, selected_algo=selected_algo, servers=SERVERS)

        if algo == 'round_robin':
            server = healthy[rr_counter["index"] % len(healthy)]
            rr_counter["index"] += 1
            result = {
                "algorithm": "Round Robin",
                "selected": server,
                "reason": f"Request #{rr_counter['index']} — rotating sequentially across all healthy servers"
            }

        elif algo == 'least_connections':
            server = min(healthy, key=lambda s: server_connections.get(s["id"], 0))
            server_connections[server["id"]] = server_connections.get(server["id"], 0) + 1
            result = {
                "algorithm": "Least Connections",
                "selected": server,
                "reason": f"{server['id']} had the fewest active connections",
                "connections": dict(server_connections)
            }

        elif algo == 'ip_hash':
            client_ip = request.remote_addr or "127.0.0.1"
            hash_val = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
            server = healthy[hash_val % len(healthy)]
            result = {
                "algorithm": "IP Hash",
                "selected": server,
                "reason": f"Your IP ({client_ip}) always maps to this server — sticky by IP",
                "hash": hex(hash_val)[:18]
            }

        elif algo == 'weighted':
            pool = []
            for s in healthy:
                pool.extend([s] * s["weight"])
            server = random.choice(pool)
            result = {
                "algorithm": "Weighted Round Robin",
                "selected": server,
                "reason": f"{server['id']} has weight {server['weight']} — higher weight = more traffic share",
                "weights": {s["id"]: s["weight"] for s in healthy}
            }

        elif algo == 'random':
            server = random.choice(healthy)
            result = {
                "algorithm": "Random",
                "selected": server,
                "reason": "Server selected at random from healthy pool"
            }

    # ← this return was missing — every route MUST end with a return
    return render_template('slb/lb_algo.html', result=result, selected_algo=selected_algo, servers=SERVERS)
# ─────────────────────────────────────────────
# MODULE 3 — STICKY SESSIONS
# ─────────────────────────────────────────────
@slb_bp.route('/sticky', methods=['GET', 'POST'])
def sticky():
    result = None

    if request.method == 'POST':
        healthy = get_healthy_servers()

        if not healthy:
            result = {"error": "No healthy servers available"}
            return render_template('slb/sticky.html', result=result)

        # Check if session already has a pinned server
        pinned_id = session.get('pinned_server')
        pinned_server = next((s for s in healthy if s["id"] == pinned_id), None)

        if pinned_server:
            result = {
                "status": "existing_session",
                "selected": pinned_server,
                "session_id": session.get('session_id', 'N/A'),
                "reason": "You already have a session — Haltdos pinned you to this server"
            }
        else:
            # First request — assign a server and pin it
            server = random.choice(healthy)
            session['pinned_server'] = server["id"]
            session['session_id'] = hashlib.md5(
                str(time.time()).encode()
            ).hexdigest()[:12]
            result = {
                "status": "new_session",
                "selected": server,
                "session_id": session['session_id'],
                "reason": "New session created — you are now pinned to this server"
            }

    return render_template('slb/sticky.html', result=result)


@slb_bp.route('/sticky/clear', methods=['POST'])
def sticky_clear():
    session.clear()
    return jsonify({"status": "session cleared"})


# ─────────────────────────────────────────────
# MODULE 4 — FAILOVER SIMULATOR
# ─────────────────────────────────────────────
@slb_bp.route('/failover', methods=['GET', 'POST'])
def failover():
    result = None

    if request.method == 'POST':
        action = request.form.get('action')
        server_id = request.form.get('server_id')

        if action == 'down' and server_id:
            downed_servers.add(server_id)
            result = {
                "action": "Server taken DOWN",
                "server_id": server_id,
                "healthy_pool": [s["id"] for s in get_healthy_servers()],
                "message": f"{server_id} is now unavailable. Haltdos should route traffic to remaining healthy servers."
            }

        elif action == 'up' and server_id:
            downed_servers.discard(server_id)
            result = {
                "action": "Server brought UP",
                "server_id": server_id,
                "healthy_pool": [s["id"] for s in get_healthy_servers()],
                "message": f"{server_id} is back online. Haltdos should resume sending traffic after health check passes."
            }

        elif action == 'status':
            result = {
                "action": "Pool Status",
                "total_servers": len(SERVERS),
                "healthy_servers": [s["id"] for s in get_healthy_servers()],
                "downed_servers": list(downed_servers),
                "message": "Current state of your server pool"
            }

    return render_template('slb/failover.html', result=result, servers=SERVERS, downed_servers=downed_servers)


# ─────────────────────────────────────────────
# MODULE 5 — SERVER IDENTITY
# ─────────────────────────────────────────────
@slb_bp.route('/server-info', methods=['GET'])
def server_info():
    healthy = get_healthy_servers()

    # Simulate which server "served" this request
    simulated_server = healthy[rr_counter["index"] % len(healthy)] if healthy else None
    rr_counter["index"] += 1

    info = {
        "served_by": simulated_server["id"] if simulated_server else "None",
        "server_ip": simulated_server["ip"] if simulated_server else "N/A",
        "zone": simulated_server["zone"] if simulated_server else "N/A",
        "client_ip": request.remote_addr,
        "request_headers": dict(request.headers),
        "healthy_pool_size": len(healthy),
        "timestamp": time.time()
    }

    return render_template('slb/server_info.html', info=info)