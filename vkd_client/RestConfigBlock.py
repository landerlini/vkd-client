import json
from typing import List, Dict, Union, Any, Literal, Optional
from pydantic import BaseModel, Field

GenericData = Union[str, List[Any], Dict[str, Any], None]


class RestConfigBlock(BaseModel):

    class Config:
        extra = 'forbid'

    method: Literal['GET', 'POST', 'DELETE']
    resource: str
    title: Optional[str] = None
    select: Union[Dict[str, Dict[Literal['field', 'default'], Any]], None] = None
    where: Union[List[str], None] = None
    data: GenericData = None

    def json_data(self) -> Union[str, None]:
        if self.data is None:
            return None

        if isinstance(self.data, str):
            return self.data

        return json.dumps(self.data)

