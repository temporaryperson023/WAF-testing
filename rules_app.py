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
    # ❌ RAW ERROR RESPONSE
    return jsonify({
        "status": 404,
        "error": "Resource not found",
        "message": "This is a simulated backend error"
    }), 404


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