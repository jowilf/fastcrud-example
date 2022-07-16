from typing import Any, Dict, Optional, Tuple, Type

from sqlmodel import SQLModel
from sqlmodel.main import SQLModelMetaclass


class _AllOptionalMeta(SQLModelMetaclass):
    def __new__(
        self,
        name: str,
        bases: Tuple[Type[Any], ...],
        class_dict: Dict[str, Any],
        **kwargs
    ):
        annotations: dict = class_dict.get("__annotations__", {})

        for base in bases:
            for base_ in base.__mro__:
                if base_ is SQLModel:
                    break

                annotations.update(base_.__annotations__)

        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]
        class_dict["__annotations__"] = annotations

        return super().__new__(self, name, bases, class_dict, **kwargs)
