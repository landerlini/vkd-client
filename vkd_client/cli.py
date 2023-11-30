#!/bin/env python3

import logging
from typing import List
from datetime import datetime
import pprint
import yaml
import json
import requests
from pprint import pprint

import os
from argparse import ArgumentParser
API_URL = os.environ.get("VKD_API_URL", "http://localhost:8000/api/v1")


def process_file(filename: str):
    cmds = yaml.safe_load(open(filename))
    for cmd in cmds:
        logging.debug(f"Processing {cmd}")
        if "GET" in [k.upper() for k in cmd.keys()]:
            response = requests.get(
                f"{API_URL}/{cmd['GET']}",
                data=json.dumps(cmd.get('data', {}))
            )
            if response.status_code // 100 == 2:
                print(f"# GET {cmd['GET']} at {datetime.now()}")
                print(yaml.safe_dump(response.json()))
                print(f"###")

        elif "POST" in [k.upper() for k in cmd.keys()]:
            response = requests.post(
                f"{API_URL}/{cmd['POST']}",
                data=json.dumps(cmd.get('data', {}))
            )
        elif "DELETE" in [k.upper() for k in cmd.keys()]:
            response = requests.delete(
                f"{API_URL}/{cmd['DELETE']}",
                data=json.dumps(cmd.get('data', {}))
            )
        else:
            raise NotImplementedError("Cannot find HTTP mode in step")

        if response.status_code//100 != 2:
            try:
                pprint(json.loads(response.content))
            except json.JSONDecodeError:
                pprint(response.text)

        response.raise_for_status()


def main():
    parser = ArgumentParser()
    parser.add_argument("files", nargs="+",
                        help="YAML files defining REST queries")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enhance verbosity for debugging purpose")

    args = parser.parse_args()

    log_format = '%(asctime)-22s %(levelname)-8s %(message)-90s'
    logging.basicConfig(
            format=log_format,
            level=logging.DEBUG if args.verbose else logging.INFO
        )

    for file in files:
        logging.info(f"Processing file {file}")
        process_file(file)
        logging.info(f"File {file} processed.")

