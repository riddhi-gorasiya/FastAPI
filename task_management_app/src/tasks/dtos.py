from pydantic import BaseModel
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"

class TaskSchema(BaseModel):
    title:str
    description:str
    is_completed:bool=False
    status:TaskStatus=TaskStatus.pending


class TaskResponseSchema(BaseModel):
    id:int
    title:str
    description:str
    is_completed:bool
    status:TaskStatus
    user_id:int | None = 0