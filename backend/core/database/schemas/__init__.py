from typing import Optional

from pydantic.main import BaseModel


class Meta(BaseModel):
    version: Optional[str]
    build: Optional[str]
