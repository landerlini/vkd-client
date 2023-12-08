from .RestConfigBlock import RestConfigBlock, GenericData
import json
from typing import List, Dict, Union, Any, Literal, Optional
import logging
import requests
from pprint import pformat
import vkd_client.configuration as config
from pydantic import validate_call

from .Table import Table

class BaseProcessor:
    def __init__(self, api_url: str = config.VKD_API_URL):
        self._api_url = api_url

    @property
    def api_url(self):
        return self._api_url

    @staticmethod
    def _validate_response(url: str, response: requests.Response) -> Dict[str, Any]:
        if response.status_code // 100 == 2:
            return response.json()
        else:
            logging.error(f"Error {response.status_code} from {url}: {response.reason}.")
            try:
                logging.error(pformat(json.loads(response.content)))
            except json.JSONDecodeError:
                logging.error(f"Invalid json: {pformat(response.text)}")

    @validate_call
    def _get(self, resource: str, data: Optional[str] = None) -> Dict[str, Any]:
        logging.debug(f"HTTP request [GET {resource}] submitted")
        url = f"{self.api_url}/{resource}"
        response = requests.get(url, data=data)
        return self._validate_response(url, response)

    @validate_call
    def _post(self, resource: str, data: Optional[str] = None) -> Dict[str, Any]:
        logging.debug(f"HTTP request [POST {resource}] submitted")
        url = f"{self.api_url}/{resource}"
        response = requests.post(url, data=data)
        return self._validate_response(url, response)

    @validate_call
    def _delete(self, resource: str, data: Optional[str] = None) -> Dict[str, Any]:
        logging.debug(f"HTTP request [DELETE {resource}] submitted")
        url = f"{self.api_url}/{resource}"
        response = requests.delete(url, data=data)
        return self._validate_response(url, response)

    @staticmethod
    @validate_call
    def _extract_fields(raw_json: GenericData, field: List[str], default: Any = " "):
        if raw_json is None:
            return [default]
        elif isinstance(raw_json, list):
            return sum([BaseProcessor._extract_fields(sub_field, field, default) for sub_field in raw_json], [])
        elif isinstance(raw_json, dict):
            if len(field) == 1:  # leaf
                ret = raw_json.get(field[0], default)
                return ret if isinstance(ret, list) else [ret]
            else:  # branch
                return BaseProcessor._extract_fields(raw_json.get(field[0]), field[1:], default)

        logging.warning(f"Unexpectedly reached end of YamlProcessor._extract_fields()")
        return default

    @staticmethod
    def _retrieve_field(field) -> Union[List[str], None]:
        logging.info(field)
        if isinstance(field, str):
            return field.split('.')
        if isinstance(field, list):
            return field
        if isinstance(field, dict):
            return BaseProcessor._retrieve_field(field['field'])
        else:
            raise ValueError("Select statement does not include 'field' definition")

    @staticmethod
    def _retrieve_default(field):
        if isinstance(field, dict):
            return field.get('default', " ")
        return " "

    @validate_call
    def process(self, rest_blocks: Union[List[RestConfigBlock], RestConfigBlock]):
        ret = []
        for req in rest_blocks if isinstance(rest_blocks, list) else [rest_blocks]:
            logging.debug(f"Processing {req.title}")
            method = getattr(self, f'_{req.method.lower()}')

            try:
                raw_json = method(req.resource, req.json_data())
            except Exception:
                logging.critical(f"Failed HTTP request [{req.method} {req.resource}]")
                raise

            if req.select is None:
                ret.append(raw_json)
            else:
                ret.append(
                    Table(
                        title=req.title,
                        queries=req.where,
                        data={
                            field_name: self._extract_fields(
                                raw_json,
                                self._retrieve_field(attrs),
                                self._retrieve_default(attrs)
                            )
                            for field_name, attrs in req.select.items()
                        })
                )

        if isinstance(rest_blocks, list):
            return ret

        return ret.pop()
