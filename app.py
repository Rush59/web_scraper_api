from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

def get_page_content(url):
    try:
        # Add 'https://' if not present in the url
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

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

@app.route('/scrape', methods=['GET'])
def scrape_web_page():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is missing."}), 400
    html_content, error = get_page_content(url)
    if html_content is None:
        return jsonify({
            "error": "ERROR: this page can't be accessed. Reason: " + error
        }), 500
    main_text = extract_main_text(html_content)
    return jsonify({"text": main_text})

if __name__ == "__main__":
    app.run()
