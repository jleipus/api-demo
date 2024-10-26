import argparse
import json
import requests
import random
import time
import logging

from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

# Configure logging with timestamp and severity level for easy debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
)

def load_events(event_file):
    """
    Load events from a specified JSON file.

    Parameters:
    event_file (str): Path to the JSON file containing events.

    Returns:
    list: A list of events loaded from the file.

    Raises:
    ValueError: If the JSON file is invalid or cannot be parsed.
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

def send_event(api_endpoint, event_payload):
    """
    Send an event payload to the specified API endpoint.

    Parameters:
    api_endpoint (str): The URL of the API endpoint to send the event to.
    event_payload (dict): The event data to be sent.

    Logs success or failure of the HTTP POST request.
    """
    
    api_endpoint = urljoin(api_endpoint, "/event")
    
    try:
        response = requests.post(api_endpoint, json=event_payload)
        response.raise_for_status()
        logging.info(f"Event sent successfully: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending event: {e}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Event Propagator')
    parser.add_argument('--event_file', type=str, required=True, help='Path to event file')
    parser.add_argument('--api_address', type=str, required=True, help='Consumer API address')
    parser.add_argument('--period', type=int, default=3, help='Time between each event in seconds')
    
    args = parser.parse_args()
    
    if args.period < 1:
        raise ValueError("Period must be a positive integer")
    
    # Load events from the specified file
    events = load_events(args.event_file)

    # Use a ThreadPoolExecutor to handle asynchronous event sending
    with ThreadPoolExecutor() as executor:
        while True:
            # Randomly select an event to send
            event = random.choice(events)
            logging.info(f"Sending event: {event}")
            
            # Submit the send_event task to the executor to run asynchronously
            executor.submit(send_event, args.api_address, event)
            
            time.sleep(args.period)

    logging.info("Service stopped.")


if __name__ == "__main__":
    main()
