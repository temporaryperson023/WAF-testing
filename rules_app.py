from flask import Blueprint, render_template, jsonify,request, redirect 
import requests
from flask import request, jsonify


rules_bp = Blueprint('rules', __name__, url_prefix='/rules')

# Dashboard
@rules_bp.route('/')
def rules_dashboard():
    return render_template('rules/dashboard.html')

# =========================
# ERROR RULES
# =========================
@rules_bp.route('/error')
def error_rules():
    return render_template('rules/error_rules.html')

@rules_bp.route('/error/test')
def error_test():
    ALLOWED_CODES = {
        400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413,
        414, 415, 416, 417, 418, 421, 422, 423, 424, 425, 426, 428, 429, 431,
        450, 451, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506,
        507, 508, 510, 511, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530
    }

    ERROR_MESSAGES = {
        400: "Bad Request", 401: "Unauthorized", 402: "Payment Required",
        403: "Forbidden", 404: "Not Found", 405: "Method Not Allowed",
        406: "Not Acceptable", 407: "Proxy Authentication Required",
        408: "Request Timeout", 409: "Conflict", 410: "Gone",
        411: "Length Required", 412: "Precondition Failed",
        413: "Content Too Large", 414: "URI Too Long",
        415: "Unsupported Media Type", 416: "Range Not Satisfiable",
        417: "Expectation Failed", 418: "I'm a Teapot",
        421: "Misdirected Request", 422: "Unprocessable Content",
        423: "Locked", 424: "Failed Dependency", 425: "Too Early",
        426: "Upgrade Required", 428: "Precondition Required",
        429: "Too Many Requests", 431: "Request Header Fields Too Large",
        450: "Blocked by Windows Parental Controls", 451: "Unavailable For Legal Reasons",
        495: "SSL Certificate Error", 496: "SSL Certificate Required",
        497: "HTTP Request Sent to HTTPS Port", 498: "Invalid Token",
        499: "Client Closed Request", 500: "Internal Server Error",
        501: "Not Implemented", 502: "Bad Gateway", 503: "Service Unavailable",
        504: "Gateway Timeout", 505: "HTTP Version Not Supported",
        506: "Variant Also Negotiates", 507: "Insufficient Storage",
        508: "Loop Detected", 510: "Not Extended",
        511: "Network Authentication Required", 520: "Web Server Unknown Error",
        521: "Web Server Is Down", 522: "Connection Timed Out",
        523: "Origin Is Unreachable", 524: "A Timeout Occurred",
        525: "SSL Handshake Failed", 526: "Invalid SSL Certificate",
        527: "Railgun Listener Error", 528: "Site Is Overloaded",
        529: "Site Is About To Be Throttled", 530: "Origin DNS Error"
    }

    try:
        code = int(request.args.get('code', 404))
    except (ValueError, TypeError):
        code = 404

    if code not in ALLOWED_CODES:
        return jsonify({
            "status": 400,
            "error": "Invalid error code",
            "message": f"Code {code} is not a supported error code"
        }), 400

    message = ERROR_MESSAGES.get(code, "Error")
    return jsonify({
        "status": code,
        "error": message,
        "message": f"This is a simulated {code} {message} error response"
    }), code


# =========================
# HEADER RULES
# =========================
@rules_bp.route('/header')
def header_rules():
    return render_template('rules/header_rules.html')


@rules_bp.route('/header/test')
def header_test():
    # Capture request headers
    req_headers = dict(request.headers)

    response = {
        "message": "Header test endpoint",
        "status": "ok",
        "request_headers": req_headers
    }

    return jsonify(response)


# =========================
# REDIRECT RULES
# =========================
@rules_bp.route('/redirect')
def redirect_rules():
    return render_template('rules/redirect_rules.html')


@rules_bp.route('/redirect/test')
def redirect_test():
    # Normal response (no redirect)
    return {
        "message": "No redirect applied",
        "status": "ok"
    }

# Target page (for testing)
@rules_bp.route('/redirect/target')
def redirect_target():
    return "<h1>Redirect Target Page</h1>"


# =========================
# VARIABLE RULES
# =========================
from flask import request, jsonify

@rules_bp.route('/variable')
def variable_rules():
    return render_template('rules/variable_rules.html')


@rules_bp.route('/variable/test')
def variable_test():
    user = request.args.get('user', '')
    role = request.args.get('role', '')

    return jsonify({
        "received_user": user,
        "received_role": role
    })



# =========================
# TRANSFORM RULES
# =========================
@rules_bp.route('/transform')
def transform_rules():
    return render_template('rules/transform_rules.html')


@rules_bp.route('/transform/test')
def transform_test():
    # Raw response
    return """
    <h2>Welcome User</h2>
    <p>This is a normal response from backend.</p>
    """



# =========================
# FORWARDER RULES
# =========================
@rules_bp.route('/forwarder')
def forwarder_rules():
    return render_template('rules/forwarder_rules.html')


@rules_bp.route('/forwarder/test')
def forwarder_test():
    # Normal response
    return {
        "backend": "primary",
        "message": "Response from main backend"
    }


# Simulated second backend
@rules_bp.route('/forwarder/alt')
def forwarder_alt():
    return {
        "backend": "secondary",
        "message": "Response from alternate backend"
    }



# =========================
# CAPTURE RULES
# =========================
@rules_bp.route('/capture')
def capture_rules():
    return render_template('rules/capture_rules.html')


@rules_bp.route('/capture/test')
def capture_test():
    user = request.args.get('user', '')
    agent = request.headers.get('User-Agent')

    return jsonify({
        "message": "Request received",
        "user": user,
        "user_agent": agent
    })




# =========================
# UPSTREAM RULES
# =========================
@rules_bp.route('/upstream')
def upstream_rules():
    return render_template('rules/upstream_rules.html')


@rules_bp.route('/upstream/test')
def upstream_test():
    return {
        "upstream": "main-server",
        "message": "Handled by primary upstream"
    }


# Simulated alternate upstream
@rules_bp.route('/upstream/alt')
def upstream_alt():
    return {
        "upstream": "alternate-server",
        "message": "Handled by alternate upstream"
    }