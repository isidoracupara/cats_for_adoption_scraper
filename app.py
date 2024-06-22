from flask import Flask, request, jsonify
import asyncio
from scraper import get_breeds_and_scrape, scrape_breeds

app = Flask(__name__)

@app.route('/scrape_breeds', methods=['GET'])
async def get_breeds():
    base_url = 'https://www.adopteereendier.be/katten?ras='
    try:
        breeds = await scrape_breeds(base_url + 'europese-korthaar')
        return jsonify({'breeds': breeds})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scrape', methods=['POST'])
async def scrape():
    data = request.json
    exclude_breeds = data.get('exclude_breeds', [])
    base_url = 'https://www.adopteereendier.be/katten?ras='

    try:
        results = await get_breeds_and_scrape(base_url, exclude_breeds)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
