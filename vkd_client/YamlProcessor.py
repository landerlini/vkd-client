import logging
from typing import List, Dict, Union, Any, Literal, Optional
import json
from datetime import datetime
from pydantic import validate_call
from pprint import pformat
from .RestConfigBlock import RestConfigBlock

import yaml
import requests

import vkd_client.configuration as config
from .BaseProcessor import BaseProcessor


class YamlProcessor (BaseProcessor):
    @validate_call
    def process(self, yaml_string: str):
        cmd_or_cmds = yaml.safe_load(yaml_string)
        if isinstance(cmd_or_cmds, list):
            return BaseProcessor.process(self, [RestConfigBlock(**cmd) for cmd in cmd_or_cmds])

        return BaseProcessor.process(self, RestConfigBlock(**cmd_or_cmds))

