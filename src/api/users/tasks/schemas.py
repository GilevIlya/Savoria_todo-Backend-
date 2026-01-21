from fastapi import Form
from pydantic import BaseModel, ConfigDict
from typing import Optional

class TaskBase(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
    priority: Optional[str]
    deadline: Optional[str]

    model_config = ConfigDict(extra='forbid')


class TaskCreate(TaskBase):

    @classmethod
    def get_tasks_fields(
            cls,
            title: str = Form(..., min_length=1, max_length=100),
            description: str = Form(..., min_length=1, max_length=500),
            status: str = Form(...),
            priority: str = Form(...),
            deadline: str = Form(...)
    ):
        return cls(
            title=title,
            description=description,
            status=status,
            priority=priority,
            deadline=deadline,
        )


class TaskEdit(TaskBase):
    @classmethod
    def get_optional_tasks_fields(
            cls,
            title: Optional[str] = Form(None, min_length=1, max_length=100),
            description: Optional[str] = Form(None, min_length=1, max_length=500),
            status: Optional[str] = Form(None),
            priority: Optional[str] = Form(None),
            deadline: Optional[str] = Form(None),
    ):
        return cls(
            title=title,
            description=description,
            status=status,
            priority=priority,
            deadline=deadline,
        )