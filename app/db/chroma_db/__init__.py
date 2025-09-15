from dataclasses import dataclass
from typing import List

@dataclass
class NCMResult:
    ncm_code: str
    description:str
    distance:float

class Response:
    query:str
    result: List[NCMResult]

