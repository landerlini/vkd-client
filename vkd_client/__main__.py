#!/bin/env python3
from pathlib import Path

import logging
import textwrap
from pprint import pprint
from typing import List
from datetime import datetime
import pprint
import yaml
import json
import requests
from pprint import pprint

import os
from argparse import ArgumentParser
from vkd_client import YamlProcessor
import jinja2

from cyclopts import App
app = App()

@app.command
def request(input_file: Path):
    """
    Submit a raw yaml request from a text file.

    Parameters
    ----------
    input_file
        input yaml_file with the script to execute
    """
    processor = YamlProcessor()
    result = processor.process(open(input_file).read())
    pprint(result)

@app.command
def jobs(user: str = os.environ.get('JUPYTERHUB_USER'), queue: str = None):
    """
    List the jobs

    Parameters
    ----------
    user
        restrict list to a single username
    queue
        restrict list to a single queue
    """
    processor = YamlProcessor()
    with open(os.path.join(os.path.dirname(__file__), 'templates', 'jobs.yaml')) as template_file:
        template = jinja2.Environment().from_string(template_file.read())
    result = processor.process(template.render(
        user=user,
        queue=queue,
    ))
    pprint(result)

@app.default
def splash():
    print(textwrap.dedent(r"""
        __      ,_      ,-. 
        \ \    / /    __| |
         \ \  / /    / _| |
          \ \/ / \  | |_| |
           \__/ \_\  \__|_|
    
    Virtual Kubelet Dispatcher. (c) INFN 2024.
    
    """))


def main():
    log_format = '%(asctime)-22s %(levelname)-8s %(message)-90s'
    logging.basicConfig(
        format=log_format,
        level=logging.DEBUG,
    )

    app()


if __name__ == '__main__':
    main()
