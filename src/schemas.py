from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from pydantic import BaseModel, Field, field_validator, validator
else:  # pragma: no cover - runtime fallback
    try:
        from pydantic import Field  # type: ignore[attr-defined]
        from pydantic import BaseModel, field_validator, validator
    except Exception:  # pragma: no cover - pydantic is unavailable

        class BaseModelMeta(type):
            def __new__(
                mcls, name: str, bases: tuple[type, ...], ns: dict
            ) -> "BaseModelMeta":
                annotations = ns.get("__annotations__", {})
                fields: dict[str, dict[str, Any]] = {}
                for attr in annotations:
                    value = ns.get(attr, None)
                    if isinstance(value, dict) and "_field_info" in value:
                        fields[attr] = value["_field_info"]
                        ns[attr] = None
                    else:
                        fields[attr] = {"default": value, "default_factory": None}
                ns["_fields_info"] = fields
                return super().__new__(mcls, name, bases, ns)

        class BaseModel(metaclass=BaseModelMeta):
            """Very small subset of :class:`pydantic.BaseModel`."""

            _fields_info: dict[str, dict[str, Any]]

            def __init__(self, **data: Any) -> None:
                for name, info in self._fields_info.items():
                    alias = info.get("alias")
                    if alias and alias in data:
                        value = data[alias]
                    elif name in data:
                        value = data[name]
                    else:
                        factory = info.get("default_factory")
                        if factory is not None:
                            value = factory()
                        else:
                            value = info.get("default")
                    setattr(self, name, value)

        def Field(
            default: Any = None,
            *,
            default_factory: Callable[[], Any] | None = None,
            alias: str | None = None,
            **_: Any,
        ) -> Any:
            return {
                "_field_info": {
                    "default": default,
                    "default_factory": default_factory,
                    "alias": alias,
                }
            }

        def validator(
            *_: str, **__: Any
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                return func

            return decorator

        # ``field_validator`` was introduced in pydantic v2. When running with
        # pydantic v1 or when pydantic is entirely unavailable we simply alias it
        # to ``validator`` which provides similar behaviour for the use cases in
        # this project.
        field_validator = validator
from typing import Optional


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
    link_to: Optional[str] = None
    link_type: str = "references"  # Default link type

    @field_validator("type_")
    @classmethod
    def validate_type(cls, v):
        if v not in ["t", "l", "r", "th"]:
            raise ValueError(
                "Type must be 't' (task), 'l' (learning), 'r' (research), or 'th' (thought)"
            )
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        if v.upper() not in ["LOW", "MED", "HI"]:
            raise ValueError("Priority must be LOW, MED, or HI")
        return v.upper()

    @field_validator("link_type")
    @classmethod
    def validate_link_type(cls, v):
        valid_link_types = ["references", "evolves-from", "inspired-by", "parent-child"]
        if v not in valid_link_types:
            raise ValueError(f"Link type must be one of: {', '.join(valid_link_types)}")
        return v

    @classmethod
    def parse_input(cls, input_str: str) -> "AddItemInput":
        # First, check if there are any optional parameters
        main_part = input_str
        link_to = None
        link_type = "references"  # Default link type

        # Extract optional parameters if present
        if " --link-to " in input_str:
            parts = input_str.split(" --link-to ", 1)
            main_part = parts[0]

            # Check if there's also a link type specified
            if " --link-type " in parts[1]:
                link_parts = parts[1].strip().split(" --link-type ", 1)
                link_to = link_parts[0].strip()
                link_type = link_parts[1].strip()
            else:
                link_to = parts[1].strip()

        # Parse the main parts as before
        parts = main_part.split("-", 4)
        if len(parts) < 5:
            raise ValueError(
                "Format: goal-type-priority-title-description [--link-to item_id] [--link-type type]"
            )

        obj = cls(
            goal=parts[0].strip(),
            type=parts[1].strip(),
            priority=parts[2].strip(),
            title=parts[3].strip(),
            description=parts[4].strip(),
            link_to=link_to,
            link_type=link_type,
        )

        # Manual validation when ``pydantic`` is unavailable
        obj.type_ = cls.validate_type(obj.type_)
        obj.priority = cls.validate_priority(obj.priority)
        obj.link_type = cls.validate_link_type(obj.link_type)
        return obj


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
        parts = input_str.split("-")
        if len(parts) < 3:
            raise ValueError("Format: update-id-status or update-id-field-value")

        if len(parts) == 3:
            return cls(item_id=parts[1].strip(), value=parts[2].strip())
        return cls(
            item_id=parts[1].strip(), field=parts[2].strip(), value=parts[3].strip()
        )


class AddThoughtInput(CommandInput):
    goal: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    parent_id: Optional[str] = None
    link_type: str = "evolves-from"

    @field_validator("link_type")
    @classmethod
    def validate_link_type(cls, v):
        valid_link_types = ["evolves-from", "references", "inspired-by", "parent-child"]
        if v not in valid_link_types:
            raise ValueError(f"Link type must be one of: {', '.join(valid_link_types)}")
        return v

    @classmethod
    def parse_input(cls, input_str: str) -> "AddThoughtInput":
        # Split for the required parameters
        parts = input_str.split("-", 2)

        if len(parts) < 3:
            raise ValueError(
                "Format: goal-title-description [--parent parent_id] [--link link_type]"
            )

        goal = parts[0].strip()
        title = parts[1].strip()

        # Process the description and optional parameters
        remaining = parts[2]

        # Check for optional parameters
        parent_id = None
        link_type = "evolves-from"

        # Look for --parent and --link parameters
        if " --parent " in remaining:
            desc_parts = remaining.split(" --parent ", 1)
            description = desc_parts[0].strip()

            # Check if there's also a link type
            parent_parts = desc_parts[1].strip().split(" --link ", 1)
            parent_id = parent_parts[0].strip()

            if len(parent_parts) > 1:
                link_type = parent_parts[1].strip()
        elif " --link " in remaining:
            # This should not normally happen as link requires a parent
            # But handle it gracefully
            raise ValueError("--link parameter requires --parent to be specified first")
        else:
            description = remaining.strip()

        obj = cls(
            goal=goal,
            title=title,
            description=description,
            parent_id=parent_id,
            link_type=link_type,
        )

        obj.link_type = cls.validate_link_type(obj.link_type)
        return obj
