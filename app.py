from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

def get_page_content(url):
    try:
        # Sending a request to the URL with a user-agent and timeout
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        # Checking if the request was successful
        if response.status_code == 200:
            return response.text, None
        else:
            return None, "Non-successful status code returned."
    except requests.RequestException as e:
        # Return None and the error if there is an exception
        return None, str(e)


def extract_main_text(html_content):
    # Parsing the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Removing unwanted sections
    for script in soup(["script", "style", "header", "footer", "nav"]):
        script.extract()

    # Extracting text and breaking into words
    text = soup.get_text()
    words = text.split()

    # Return first 500 words
    return ' '.join(words[:500])


def scrape_web_page(url):
    # Getting the page content and an error message if applicable
    html_content, error = get_page_content(url)

    # Checking if the page content is None
    if html_content is None:
        return jsonify({"error": "ERROR: this page can't be accessed. Reason: " + error}), 500

    # Extracting main text
    main_text = extract_main_text(html_content)
    return jsonify({"text": main_text}), 200


@app.route('/scrape', methods=['GET'])
def scrape():
    # Check for the correct authentication header
    auth_header = request.headers.get('Authorization')
    if auth_header != 'Bearer Fda512sE1xWTIlF':
        return jsonify({"error": "Unauthorized access"}), 401
    
    # Check if a URL is provided as a parameter
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    # Fetch the content and return it
    return scrape_web_page(url)


if __name__ == "__main__":
    app.run(debug=True)
