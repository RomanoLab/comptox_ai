from dataclasses import dataclass

@dataclass
class Node:
    """Representation of a graph database node."""
    uri: str
    neo4j_id: int
    common_name: str
    properties: dict = {}