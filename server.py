from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data.get('message', '')
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Format the message with a timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_message = f"[{timestamp}] {message}"
    
    return jsonify({'message': formatted_message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)