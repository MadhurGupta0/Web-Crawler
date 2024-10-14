from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def crawl(url, depth):
    if depth == 0:
        return []

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = set()

    for anchor in soup.find_all('a', href=True):
        link = anchor['href']
        full_url = urljoin(url, link)

        if urlparse(full_url).netloc == urlparse(url).netloc:
            links.add(full_url)

    crawled_links = []
    for link in links:
        if link in crawled_links:
            continue
        crawled_links.append(link)
        crawled_links.extend(crawl(link, depth - 1))
    return crawled_links




@app.route('/api/crawl', methods=['POST'])
def api_crawl():
    data = request.json
    root_url = data.get('root_url')
    depth = data.get('depth')

    if not root_url or not isinstance(depth, int) or depth < 0:
        return jsonify({'status': 'error', 'message': 'Invalid input parameters.'}), 400

    crawled_links=crawl(root_url, depth)
    return jsonify({'status': 'success', 'data': crawled_links})


if __name__ == '__main__':
    app.run(debug=True)


