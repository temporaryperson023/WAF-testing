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








# The below given code to remove the caching of the web pages in the browser, so that the latest version of the page is always loaded when accessed. and the css caching 304 error code can also be resolved.


# from flask import Flask, render_template
# from vuln_app import vuln_bp
# from rules_app import rules_bp

# app = Flask(__name__)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# @app.after_request
# def add_no_cache_headers(response):
#     response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '0'
#     return response

# # Register Blueprint
# app.register_blueprint(vuln_bp)
# app.register_blueprint(rules_bp)

# # Homepage
# @app.route('/')
# def home():
#     return render_template('index.html')

# if __name__ == '__main__':
#     print("\nStarting WAF Test Lab...")
#     print("Open: http://localhost:5600\n")
#     app.run(host='0.0.0.0', port=5600, debug=True)