#!/bin/env python3
import sys
from pathlib import Path
from typing import Literal

import logging
import textwrap
from pprint import pprint
from typing import List, Union
from datetime import datetime
import pprint
import yaml
import json
import requests
from pprint import pprint
import stat

import os
from argparse import ArgumentParser
from vkd_client import YamlProcessor
from vkd_client import queue_tools
import jinja2


from cyclopts import App
app = App()


def _process_form_template(template: str, **kwargs):
    processor = YamlProcessor()
    with open(os.path.join(os.path.dirname(__file__), 'templates', f'{template}.yaml')) as template_file:
        template = jinja2.Environment().from_string(template_file.read())
    return processor.process(template.render(**kwargs))


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
    pprint(_process_form_template('jobs', user=user, queue=queue))

@app.command
def logs(job: str, index: Union[int, None] = None, container: Union[str, None] = None):
    """
    Retrieve and display the output of a job

    Parameters
    ----------
    job
        full name of the job
    index
        Optional, job completion index to display the output of a single iteration
    container
        Optional, the name of the container to display if not the main one
    """
    logs = _process_form_template('logs', job=job, index=index, container=container)
    for pod_name, log in logs.items():
        print(f"\n### Job Pod: {pod_name}")
        print(log)

@app.command
def queues():
    """
    Retrieve and diplay the queues, or updates the configuration of the queues.
    """
    if stat.S_ISREG(os.fstat(0).st_mode):       # vkd queues < some_input.csv
        queue_tools.update_queues(''.join(sys.stdin))
    else:
        raw_queues = _process_form_template('queues')
        print (queue_tools.format_queues(raw_queues))

@app.default
def vkd():
    print(textwrap.dedent(r"""
     __   ___  __     _ 
     \ \ / / |/ /  __| |
      \ V /| ' <  / _` |
       \_/ |_|\_\ \__,_|   Virtual Kubelet Dispatcher. (c) INFN 2024.
    
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
