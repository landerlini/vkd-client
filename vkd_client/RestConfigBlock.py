import json
from typing import List, Dict, Union, Any, Literal, Optional
from pydantic import BaseModel

GenericData = Union[str, List[Any], Dict[str, Any], None]


class RestConfigBlock(BaseModel):

    class Config:
        extra = 'forbid'

    method: Literal['GET', 'POST', 'DELETE']
    resource: str
    title: Optional[str] = None
    select: Dict[str, Dict[Literal['field', 'default'], Any]]
    data: GenericData = None

    def json_data(self) -> Union[str, None]:
        if self.data is None:
            return None

        if isinstance(self.data, str):
            return self.data

        return json.dumps(self.data)

