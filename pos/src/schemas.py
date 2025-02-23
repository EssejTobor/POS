from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional
from enum import Enum

class CommandInput(BaseModel):
    """Base model for command input validation"""
    @classmethod
    def parse_input(cls, input_str: str) -> "CommandInput":
        """Parse and validate input string"""
        raise NotImplementedError

class AddItemInput(CommandInput):
    goal: str = Field(..., min_length=1, max_length=50)
    type_: str = Field(..., alias="type")
    priority: str
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)

    @field_validator("type_")
    @classmethod
    def validate_type(cls, v):
        if v not in ["t", "l", "r"]:
            raise ValueError("Type must be 't' (task), 'l' (learning), or 'r' (research)")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        if v.upper() not in ["LOW", "MED", "HI"]:
            raise ValueError("Priority must be LOW, MED, or HI")
        return v.upper()

    @classmethod
    def parse_input(cls, input_str: str) -> "AddItemInput":
        parts = input_str.split('-', 4)
        if len(parts) < 5:
            raise ValueError("Format: goal-type-priority-title-description")
        return cls(
            goal=parts[0].strip(),
            type=parts[1].strip(),
            priority=parts[2].strip(),
            title=parts[3].strip(),
            description=parts[4].strip()
        )

class UpdateItemInput(CommandInput):
    item_id: str = Field(..., min_length=1)
    field: Optional[str] = None
    value: str = Field(..., min_length=1)

    @field_validator("field")
    @classmethod
    def validate_field(cls, v):
        if v and v not in ["status", "priority"]:
            raise ValueError("Field must be 'status' or 'priority'")
        return v

    @classmethod
    def parse_input(cls, input_str: str) -> "UpdateItemInput":
        parts = input_str.split('-')
        if len(parts) < 3:
            raise ValueError("Format: update-id-status or update-id-field-value")
        
        if len(parts) == 3:
            return cls(item_id=parts[1].strip(), value=parts[2].strip())
        return cls(
            item_id=parts[1].strip(),
            field=parts[2].strip(),
            value=parts[3].strip()
        ) 