import argparse
import logging
from flask import Flask, request, jsonify

logging.basicConfig(
    level=logging.INFO,  # Set the minimum log level
    format="%(asctime)s [%(levelname)s] %(message)s",  # Custom format for log messages
    datefmt="%Y/%m/%d %H:%M:%S",  # Date format
)

app = Flask(__name__)

@app.route('/event', methods=['POST'])
def event():
    data = request.get_json()
    logging.info(f"Received JSON: {data}")
    return jsonify({"status": "received"}), 200

def main():
    parser = argparse.ArgumentParser(description='Event Consumer')
    parser.add_argument('--api_address', type=str, default='127.0.0.1', help='Address for the consumer API')
    parser.add_argument('--api_port', type=int, required=True, help='Port for the consumer API')
    
    args = parser.parse_args()
    
    logging.info("Starting Flask app...")
    app.run(host=args.api_address, port=args.api_port)

if __name__ == '__main__':
    main()