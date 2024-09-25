from pydantic import BaseModel, Field, field_validator
from typing import List, Literal
import re

class Node(BaseModel):
    text: str
    id: str
    type: Literal["fact", "policy", "value"]

    # Custom field validator to ensure id starts with "N" followed by a number
    @field_validator('id')
    def id_must_start_with_n_and_number(cls, value):
        if not re.match(r'^N\d+$', value):
            raise ValueError('id must start with "N" and be followed by a number')
        return value

class Edge(BaseModel):
    label: Literal["support", "attack"]
    source: str
    target: str

    # Custom field validator to ensure source and target start with "N" followed by a number
    @field_validator('source', 'target')
    def source_target_must_start_with_n_and_number(cls, value):
        if not re.match(r'^N\d+$', value):
            raise ValueError('source and target must start with "N" and be followed by a number')
        return value

class GraphModel(BaseModel):
    nodes: List[Node]
    edges: List[Edge]