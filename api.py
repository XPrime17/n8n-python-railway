from flask import Flask, request, jsonify
import asyncio
import sys
import os

# Import your calendar extractor
sys.path.insert(0, '/home/node')
from extract_childcarecrm import CodeNinjasCalendarExtractor

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/extract-calendar', methods=['POST'])
def extract_calendar():
    try:
        data = request.get_json()
        calendar_url = data.get('calendar_url')
        location_id = data.get('location_id', 'WDM')
        
        if not calendar_url:
            return jsonify({'error': 'calendar_url required'}), 400
        
        # Run extraction
        extractor = CodeNinjasCalendarExtractor(calendar_url, location_id)
        result = asyncio.run(extractor.extract_all_weeks())
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```
