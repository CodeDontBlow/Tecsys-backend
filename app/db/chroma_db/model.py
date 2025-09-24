from dataclasses import dataclass

@dataclass
class NCMResult:
    ncm_code: str
    description:str
    distance:float

@dataclass
class Response:
    query:str
    result: NCMResult
    
