from flask import Flask, request, jsonify
from functools import wraps
import requests
from bs4 import BeautifulSoup
import json
import os

app = Flask(__name__)

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = os.environ.get("AUTH_TOKEN", "default_token")
        auth_header = request.headers.get('Authorization')
        if auth_header != f'Bearer {auth_token}':
            return jsonify({"error": "Unauthorized access"}), 401
        return f(*args, **kwargs)
    return decorated

def get_page_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.text, None
        else:
            return None, "Non-successful status code returned."
    except requests.RequestException as e:
        return None, str(e)

def extract_main_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    for script in soup(["script", "style", "header", "footer", "nav"]):
        script.extract()

    text = soup.get_text()
    words = text.split()
    return ' '.join(words[:500])

@app.route('/scrape')
@auth_required
def scrape_web_page():
    url = request.args.get('url')

    if not url.startswith("http"):
        url = "https://" + url

    html_content, error = get_page_content(url)

    if html_content is None:
        return jsonify({
            "error": "ERROR: this page can't be accessed. Reason: " + error
        })

    main_text = extract_main_text(html_content)
    return jsonify({"text": main_text})

if __name__ == "__main__":
    app.run(debug=True)
