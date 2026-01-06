from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import time

class Incident(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    status: str
    service: str
    timestamp: float = time.time()
    context: List[str] = []
    mitigation_plan: Optional[str] = None
    
    def to_dict(self):
        return self.model_dump()

class LogEntry(BaseModel):
    service: str
    level: str
    message: str
    timestamp: float
