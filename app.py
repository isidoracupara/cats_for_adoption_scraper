from flask import Flask, request, jsonify
import asyncio
from scraper import get_breeds_and_scrape, scrape_breeds, build_url, DEFAULT_FILTERS

app = Flask(__name__)

@app.route('/scrape_breeds', methods=['GET'])
async def get_breeds():
    base_url = 'https://www.adopteereendier.be/katten'
    try:
        breeds = await scrape_breeds(base_url + '?ras=europese-korthaar')
        return jsonify({'breeds': breeds})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scrape', methods=['POST'])
async def scrape():
    try:
        if request.data:
            data = request.get_json(silent=True)
            if data is None:
                filters = DEFAULT_FILTERS
            else:
                filters = data.get('filters', DEFAULT_FILTERS)
        else:
            filters = DEFAULT_FILTERS

        base_url = 'https://www.adopteereendier.be/katten'
        url_with_filters = build_url(base_url, filters)
        await get_breeds_and_scrape(url_with_filters, filters)
        return jsonify({'message': 'Scraped hrefs saved as a text file.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
