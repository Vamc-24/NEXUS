from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add project root to path so we can import ai_module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.storage import get_storage
from ai_module.pipeline import run_pipeline

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

storage = get_storage()

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    record = storage.add_feedback(data)
    
    # In a real Cloud Function/Run event-driven architecture, 
    # the database write would trigger a Pub/Sub event.
    # Here we just save it. The processing is triggered manually or periodically.
    
    return jsonify({'status': 'success', 'id': record['id']}), 201

@app.route('/api/process', methods=['POST'])
def trigger_processing():
    """
    Manually trigger the AI pipeline.
    In production, this would be a Cloud Function triggered by Firestore events.
    """
    try:
        result = run_pipeline(storage)
        return jsonify({'status': 'success', 'result': result}), 200
    except Exception as e:
        print(f"Error in pipeline: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/results', methods=['GET'])
def get_results():
    results = storage.get_latest_results()
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
