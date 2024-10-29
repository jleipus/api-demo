import argparse
import logging
import sqlite3
import os

from flask import Flask, request, jsonify, g

logging.basicConfig(
    # Set the minimum log level
    level=logging.INFO,
    # Custom format for log messages
    format="%(asctime)s [%(levelname)s] %(message)s",
    # Date format
    datefmt="%Y/%m/%d %H:%M:%S",
)

app = Flask(__name__)

database_path = None


def get_db():
    """
    Creates a database connection if it doesn't already exist

    Returns:
        sqlite3.Connection: The database connection object.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database_path)
    return db


def init_db():
    """
    Initializes the database by executing the SQL schema script.

    This function opens the SQL schema file, reads its contents, and executes
    the script on the database. The schema file is expected to be located in
    the same directory as this script.

    Raises:
        - FileNotFoundError: If the schema file is not found.
        - Exception: If there is an error executing the SQL script.

    """
    with app.app_context():
        db = get_db()
        real_path = os.path.realpath(__file__)
        schema_path = real_path.replace('main.py', 'schema.sql')
        try:
            with open(schema_path, 'r') as f:
                db.executescript(f.read())
            db.commit()
        except FileNotFoundError:
            logging.error(f"Schema file not found: {schema_path}")
            raise
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise


@app.teardown_appcontext
def close_connection(exception):
    """
    Close the database connection when the app context ends.

    Args:
        exception (Exception): An exception object representing any errors.

    Returns:
        None
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/events', methods=['GET'])
def list_events():
    """
    Handles the GET request to '/events' endpoint and returns a list of events.

    Args:
        count (int): The maximum number of events to retrieve.
            If not provided, all events will be retrieved.

    Returns:
        list: A list of events from the database, represented as dictionaries.
    """
    count = request.args.get('count', default=None, type=int)
    db = get_db()
    if count is not None:
        cur = db.execute('SELECT * FROM events LIMIT ?', (count,))
    else:
        cur = db.execute('SELECT * FROM events')
    rows = cur.fetchall()

    events = []
    for row in rows:
        event = {
            'id': row[0],
            'type': row[1],
            'payload': row[2],
            'created_at': row[3]
        }
        events.append(event)

    return jsonify(events)


@app.route('/event', methods=['POST'])
def consume_event():
    """
    Handles the POST request to '/event' endpoint and consumes an event by
    inserting it into the database.

    Returns:
        A JSON response indicating the status of the event consumption.
    """
    data = request.get_json()
    logging.info(f"Received JSON: {data}")

    event_type = data.get('event_type')
    event_payload = data.get('event_payload')

    # Validate the input data
    if not isinstance(event_type, str) or not isinstance(event_payload, str):
        return jsonify({"error": "Invalid data format"}), 400

    db = get_db()
    db.execute('INSERT INTO events (type, payload) VALUES (?, ?)',
               (event_type, event_payload))
    db.commit()

    return jsonify({"status": "received"}), 200


def main():
    parser = argparse.ArgumentParser(description='Event Consumer')
    parser.add_argument('--api_address', type=str, default='127.0.0.1',
                        help='Address for the consumer API')
    parser.add_argument('--api_port', type=int, required=True,
                        help='Port for the consumer API')
    parser.add_argument('--database_path', type=str, required=True,
                        help='Path to the SQLite database')

    args = parser.parse_args()

    global database_path
    database_path = args.database_path

    logging.info("Initializing database...")
    init_db()

    logging.info("Starting Flask app...")
    app.run(host=args.api_address, port=args.api_port)


if __name__ == '__main__':
    main()
