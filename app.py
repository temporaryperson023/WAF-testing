from flask import Flask, render_template
from vuln_app import vuln_bp
from rules_app import rules_bp

app = Flask(__name__)

# Register Blueprint
app.register_blueprint(vuln_bp)

app.register_blueprint(rules_bp)

# Homepage
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    print("\nStarting WAF Test Lab...")
    print("Open: http://localhost:5600\n")
    app.run(host='0.0.0.0', port=5600, debug=True)