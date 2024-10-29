# API Demo application

This is a simple API demo application that implementas an event propogater and consumer. The application is written in Python and uses the Flask framework. Dependecies are managed using Poetry.
The application consists of two services: the event propogator and the event consumer. The event propogator is responsible for sending events to the event consumer. The event consumer is responsible for receiving events from the event propogator and storing them in a SQLite database.

## Installation

To install the application, clone the repository and run the following commands:

```bash
poetry install
```

## Running the application

The application can be run either directly using Poetry or using Docker.

### Arguments

#### Event Propogator

The propogator service accepts the following arguments:

- `--event_file` Path to event file
- `--api_address` Consumer API address
- `--period` Time between each event being sent (seconds)

#### Event Consumer

The consumer service accepts the following arguments:

- `--api_address` Address for the consumer API
- `--api_port` Port for the consumer API
- `--database_path` Path to the SQLite database

### Poetry

To run the application using Poetry, the two services must be run in separate terminal windows.
To run the propogator service, run the following command:

```bash
poetry run propogator
```

To run the consumer service, run the following command:

```bash
poetry run producer
```

### Docker

To run the application using Docker, run the following command:

```bash
docker-compose up --build -d
```

## API

The consumer service exposes the following endpoints:

- `GET /events`: Returns a list of all events stored in the database.
- `POST /event`: Creates a new event in the database. The request body should be a JSON object with the following
    properties:
  - `event_type`: The type of the event.
  - `event_payload`: The associated payload of the event.
