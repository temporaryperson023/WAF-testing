from flask import Blueprint, render_template, request
import sqlite3
import subprocess
import requests

vuln_bp = Blueprint('vuln', __name__, url_prefix='/vuln')

# =========================
# DATABASE SETUP
# =========================
def get_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # Create tables
    conn.executescript("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT,
        email TEXT
    );

    INSERT INTO users VALUES
    (1,'admin','supersecret123','admin','admin@waflab.local'),
    (2,'alice','password123','user','alice@waflab.local'),
    (3,'bob','letmein','user','bob@waflab.local'),
    (4,'charlie','qwerty','user','charlie@waflab.local');
    """)

    return conn

db = get_db()

# =========================
# ROUTES
# =========================

@vuln_bp.route('/')
def vuln_dashboard():
    return render_template('vuln/dashboard.html')


# =========================
# XSS
# =========================
@vuln_bp.route('/xss')
def xss():
    query = request.args.get('q', '')
    return render_template('vuln/xss.html', query=query)


# =========================
# FILE UPLOAD
# =========================
@vuln_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    uploaded_file = None
    message = None

    if request.method == 'POST':
        file = request.files.get('file')

        if file:
            filename = file.filename

            # ❌ NO VALIDATION (INTENTIONALLY VULNERABLE)
            file.save(f"uploads/{filename}")

            uploaded_file = filename
            message = "File uploaded successfully!"

    return render_template('vuln/upload.html', uploaded_file=uploaded_file, message=message)


# =========================
# COMMAND INJECTION
# =========================
@vuln_bp.route('/cmdi', methods=['GET', 'POST'])
def cmdi():
    output = None
    command_shown = ""

    if request.method == 'POST':
        ip = request.form.get('ip', '')

        # ❌ VULNERABLE COMMAND
        command = f"ping -c 2 {ip}"
        command_shown = command

        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            output = result.decode()
        except Exception as e:
            output = str(e)

    return render_template('vuln/cmdi.html', output=output, command_shown=command_shown)

# =========================
# BROKEN ACCESS CONTROL
# =========================
@vuln_bp.route('/admin')
def admin():
    # ❌ NO AUTH CHECK
    return render_template('vuln/admin.html')


@vuln_bp.route('/admin/panel')
def admin_panel():
    # ❌ DIRECT ACCESS
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template('vuln/admin_panel.html', users=users)


# =========================
# SSRF
# =========================
@vuln_bp.route('/ssrf', methods=['GET', 'POST'])
def ssrf():
    response_text = None
    target_url = ""

    if request.method == 'POST':
        target_url = request.form.get('url', '')

        try:
            # ❌ NO VALIDATION
            r = requests.get(target_url, timeout=3)
            response_text = r.text[:500]  # limit output
        except Exception as e:
            response_text = str(e)

    return render_template('vuln/ssrf.html', response=response_text, url=target_url)

# =========================
# SQL INJECTION
# =========================
@vuln_bp.route('/sqli', methods=['GET', 'POST'])
def sqli():
    result = None
    query_shown = ""

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # ❌ INTENTIONALLY VULNERABLE
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        query_shown = query

        try:
            rows = db.execute(query).fetchall()

            if rows:
                result = {
                    "status": "success",
                    "message": "Login successful!",
                    "rows": rows
                }
            else:
                result = {
                    "status": "fail",
                    "message": "Invalid credentials",
                    "rows": []
                }

        except Exception as e:
            result = {
                "status": "error",
                "message": str(e),
                "rows": []
            }

    return render_template('vuln/sqli.html', result=result, query_shown=query_shown)