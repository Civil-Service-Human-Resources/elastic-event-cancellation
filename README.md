# Elastic event cancellation script

A script to align the Elasticsearch event database with the learner record event database

## Prerequisites

- Python 3.x
- MySQL Connector/Python (`mysql-connector-python`)
- `requests` library

As always, first install requirements with `pip install -r requirements.txt`

## Environment variables

- ELASTIC_REPO_ENDPOINT: The endpoint URL of the Elasticsearch repository.
- ELASTIC_REPO_USERNAME: The username for Elasticsearch authentication.
- ELASTIC_REPO_PASSWORD: The password for Elasticsearch authentication.
- MYSQL_HOST: The hostname of the MySQL server.
- MYSQL_USER: The username for MySQL authentication.
- MYSQL_PASSWORD: The password for MySQL authentication.

## Running

Run the script with `python event_script.py`


The script will:
1. Fetch all cancelled events/cancellation reasons from the `event` table in `learner_record`
2. Fetch those events from Elasticsearch
3. Check to see if the events are cancelled with a reason
  4. If not, update accordingly
