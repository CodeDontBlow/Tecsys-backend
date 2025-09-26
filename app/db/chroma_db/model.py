from dataclasses import dataclass
from typing import List

@dataclass
class NCMResult:
    ncm_code: str
    description:str
    distance:float

@dataclass
class Response:
    query:str
    results: List[NCMResult]
    
