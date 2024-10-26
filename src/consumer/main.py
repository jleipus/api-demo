import argparse
import logging
import sqlite3
import os

from flask import Flask, request, jsonify, g

logging.basicConfig(
    level=logging.INFO,  # Set the minimum log level
    format="%(asctime)s [%(levelname)s] %(message)s",  # Custom format for log messages
    datefmt="%Y/%m/%d %H:%M:%S",  # Date format
)

app = Flask(__name__)

database_path = None

def get_db():
    # Create a database connection if it doesn't already exist
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database_path)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        schema_path = os.path.realpath(__file__).replace('main.py', 'schema.sql')
        with open(schema_path, 'r') as f:
            db.executescript(f.read())

@app.teardown_appcontext
def close_connection(exception):
    # Close the database connection when the app context ends
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/events', methods=['GET'])
def list_events():
    count = request.args.get('count', default=None, type=int)
    db = get_db()
    if count is not None:
        cur = db.execute('SELECT * FROM events LIMIT ?', (count,))
    else:
        cur = db.execute('SELECT * FROM events')
    rows = cur.fetchall()
    return str(rows)

@app.route('/event', methods=['POST'])
def consume_event():
    data = request.get_json()
    logging.info(f"Received JSON: {data}")
    
    event_type = data.get('event_type')
    event_payload = data.get('event_payload')
    
    if not isinstance(event_type, str) or not isinstance(event_payload, str):
        return jsonify({"error": "Invalid data format"}), 400
    
    db = get_db()
    db.execute('INSERT INTO events (type, payload) VALUES (?, ?)', (event_type, event_payload))
    db.commit()
    
    return jsonify({"status": "received"}), 200

def main():
    parser = argparse.ArgumentParser(description='Event Consumer')
    parser.add_argument('--api_address', type=str, default='127.0.0.1', help='Address for the consumer API')
    parser.add_argument('--api_port', type=int, required=True, help='Port for the consumer API')
    parser.add_argument('--database_path', type=str, required=True, help='Path to the SQLite database')
    
    args = parser.parse_args()
    
    global database_path
    database_path = args.database_path
    
    logging.info("Initializing database...")
    init_db()
    
    logging.info("Starting Flask app...")
    app.run(host=args.api_address, port=args.api_port)

if __name__ == '__main__':
    main()