from pydantic import BaseModel
from typing import Literal


class JobConfig(BaseModel):
    class Config:
        extra = 'forbid'



