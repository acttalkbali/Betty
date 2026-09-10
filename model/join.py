from dataclasses import dataclass
from typing import Any

@dataclass
class Join:
    """Class for keeping track of join"""
    joined_cls: "Storable"
    src_field: "Field"
    target_col_name: str
    value: Any
    joined_col_names: list[str]