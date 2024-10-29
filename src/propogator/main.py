import argparse
import json
import requests
import random
import time
import logging

from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    # Set the minimum log level
    level=logging.INFO,
    # Custom format for log messages
    format="%(asctime)s [%(levelname)s] %(message)s",
    # Date format
    datefmt="%Y/%m/%d %H:%M:%S",
)


def load_events(event_file):
    """
    Load events from a specified JSON file.

    Args:
        event_file (str): Path to the JSON file containing events.

    Raises:
        ValueError: If the JSON file is invalid or cannot be parsed.
        FileNotFoundError: If the specified file does not exist.
    
    Returns:
        list: A list of events loaded from the file.
    """
    try:
        with open(event_file, 'r') as file:
            events = json.load(file)
        logging.info(f'Successfully loaded {len(events)} events')
        return events
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON file format: {e}")
    except FileNotFoundError:
        raise ValueError(f"File not found: {event_file}")


def send_event(api_address, event_payload):
    """
    Send an event payload to the specified API endpoint.
    Logs success or failure of the HTTP POST request.

    Args:
        api_address (str): The address of the API endpoint.
        event_payload (dict): The event data to be sent.
    """
    try:
        response = requests.post(urljoin(api_address, "/event"),
                                 json=event_payload)
        response.raise_for_status()
        logging.info(f"Event sent successfully: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending event: {e}")


def main():
    parser = argparse.ArgumentParser(description='Event Propagator')
    parser.add_argument('--event_file', type=str, required=True,
                        help='Path to event file')
    parser.add_argument('--api_address', type=str, required=True,
                        help='Consumer API address')
    parser.add_argument('--period', type=int, default=3,
                        help='Time between each event being sent (seconds)')

    args = parser.parse_args()

    # Validate the period argument.
    if args.period < 1:
        raise ValueError("Period must be a positive integer")

    events = load_events(args.event_file)

    # Use a ThreadPoolExecutor to handle asynchronous event sending,
    # else the main thread would be blocked until a response is received.
    with ThreadPoolExecutor() as executor:
        while True:
            # Randomly select an event to send.
            event = random.choice(events)
            logging.info(f"Sending event: {event}")

            # Submit the send_event task to the executor to run asynchronously.
            executor.submit(send_event, args.api_address, event)

            time.sleep(args.period)


if __name__ == "__main__":
    main()
