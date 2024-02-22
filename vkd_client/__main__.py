#!/bin/env python3
import sys
from pathlib import Path
from typing import Literal
import time

import logging
import textwrap
from pprint import pprint
from typing import List, Union
from datetime import datetime
import yaml
import json
import requests
from pprint import pprint, pformat
import stat

import os
import re
from argparse import ArgumentParser
from vkd_client import YamlProcessor
from vkd_client import queue_tools
from vkd_client.utils import (
    process_form_template, 
    get_snakemake_job_properties, 
    get_nfs_volumes_from_filenames
)
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
def jobs(queue: str = None, user: str = os.environ.get('JUPYTERHUB_USER')):
    """
    List the jobs

    Parameters
    ----------
    user
        restrict list to a single username
    queue
        restrict list to a single queue
    """
    pprint(process_form_template('jobs', user=user, queue=queue))

@app.command
def kill(jobnames: List[str]):
    """
    Delete jobs from the queue.

    Parameters
    ----------
    jobname
        list of jobs to be removed
    """
    if len(jobnames):
        pprint(process_form_template('kill', jobnames=jobnames))

@app.command
def killall(queue: str = None, user: str = os.environ.get('JUPYTERHUB_USER')):
    """
    Delete all jobs from a queue.

    Parameters
    ----------
    user
        restrict list to a single username
    queue
        restrict list to a single queue
    """
    jobs = process_form_template('jobs', user=user, queue=queue)
    pprint(process_form_template('kill', jobnames=jobs.df.name))

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
    logs = process_form_template('logs', job=job, index=index, container=container)
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
        raw_queues = process_form_template('queues')
        print (queue_tools.format_queues(raw_queues))

@app.command
def from_snakemake(jobscript: str, queue: str, priority: str = "lowest"):
    """
    Thin wrapper to enable submitting jobs via Snakemake
    """
    logging.debug(f"from_snakemake invoked with script: {jobscript}")
    properties = get_snakemake_job_properties(jobscript)
    logging.debug(pformat(properties))
    nfs_volumes = get_nfs_volumes_from_filenames(
        sum([properties[category] for category in ('input', 'output', 'log')], [])
        )

    jobnames = process_form_template(
        'from_snakemake', 
        queue=queue, 
        priority=priority, 
        jobscript=open(jobscript).read(), 
        snakemake=properties,
        nfs_volumes=nfs_volumes,
    )

    while True:
        time.sleep(3)
        jobs = process_form_template('jobs', user=None, queue=queue).df
        if all([jobname in jobs.query('succeeded == total').name.values for jobname in jobnames]):
            logging.debug(f"User command has been executed. Returning control to Snakemake.")
            return 0
        if any([jobname in jobs.query('failed > 0').name.values for jobname in jobnames]):
            logging.error(f"Failure executing job {properties['rule']}")
            logging.error(f"Check logs with `vkd logs {jobname}`")
            raise RuntimeError(f"VKD failed processing rule {properties['rule']}")
        

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
        level=logging.DEBUG if 'VKD_DEBUG' in os.environ else logging.WARNING,
    )

    app()


if __name__ == '__main__':
    main()
