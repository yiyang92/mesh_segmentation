import math
from dataclasses import dataclass
from typing import Union

from mesh_segmenter.utils.constants import Colour, COLOUR_WHITE


@dataclass(frozen=True)
class Vertex:
    x: float
    y: float
    z: float

    @property
    def length(self) -> float:
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    @property
    def components(self) -> list[float]:
        return [self.x, self.y, self.z]

    @property
    def out_properties(self) -> str:
        """Return properties, defined in the vertex."""
        return """property float x\nproperty float y\nproperty float z"""

    def __add__(
        self, other: Union[type["Vertex"], int, float]
    ) -> type["Vertex"]:
        if isinstance(other, int) or isinstance(other, float):
            return Vertex(
                self.x + other,
                self.y + other,
                self.z + other,
            )
        return Vertex(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def __radd__(
        self, other: Union[type["Vertex"], int, float]
    ) -> type["Vertex"]:
        if isinstance(other, int) or isinstance(other, float):
            return Vertex(
                self.x + other,
                self.y + other,
                self.z + other,
            )
        return Vertex(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def __sub__(
        self, other: Union[type["Vertex"], int, float]
    ) -> type["Vertex"]:
        if isinstance(other, int) or isinstance(other, float):
            return Vertex(
                self.x - other,
                self.y - other,
                self.z - other,
            )
        return Vertex(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
        )

    def __mul__(
        self, other: Union[type["Vertex"], int, float]
    ) -> type["Vertex"]:
        if isinstance(other, int) or isinstance(other, float):
            return Vertex(
                self.x * other,
                self.y * other,
                self.z * other,
            )
        return Vertex(
            self.x * other.x,
            self.y * other.y,
            self.z * other.z,
        )

    def __truediv__(self, other: int) -> type["Vertex"]:
        return Vertex(
            self.x / other,
            self.y / other,
            self.z / other,
        )

    def cross(self, other: type["Vertex"]) -> type["Vertex"]:
        """Calculate a cross product."""
        return Vertex(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def dot(self, other: type["Vertex"]) -> float:
        """Calculates dot product between vectors, pointed to vertices."""
        return sum([x * y for x, y in zip(self.components, other.components)])

    def cos_angle(self, other: type["Vertex"]) -> float:
        """Calculates a cosine of angel between two vectors, pointed to vertices."""
        return self.dot(other) / (self.length + other.length)

    def angle(self, other: type["Vertex"]) -> float:
        """Calculates an angel between two vectors, pointed to vertices."""
        return math.acos(self.cos_angle(other))

    def __str__(self) -> str:
        return f"{self.x} {self.y} {self.z}"


@dataclass(frozen=True)
class Face:
    vertex_one: Vertex
    vertex_two: Vertex
    vertex_three: Vertex
    colour: Colour = COLOUR_WHITE

    def set_colour(self, colour: Colour) -> None:
        """Setter for colour."""
        # NOTE: not the best way maybe, but want to protect other fields
        object.__setattr__(self, "colour", colour)

    @property
    def out_properties(self) -> str:
        return "property uint8 red\nproperty uint8 green\nproperty uint8 blue"

    @property
    def properties_str(self) -> str:
        """Output string representation of properties"""
        return str(self.colour)

    @property
    def vertices(self) -> list[Vertex]:
        return [self.vertex_one, self.vertex_two, self.vertex_three]

    @property
    def center(self) -> Vertex:
        return sum(self.vertices) / 3.0

    @property
    def normal(self) -> Vertex:
        # Find 2 edge vectors
        edge_one = self.vertex_one - self.vertex_two
        edge_two = self.vertex_one - self.vertex_three

        # Find cross product to get a vector, pointing as normal
        normal = edge_one.cross(edge_two)
        normal /= normal.length  # Normalize for unit length
        return normal


class Mesh:
    def __init__(self, vertices: list[Vertex], faces: list[Face]) -> None:
        self.vertices = vertices
        self.faces = faces

        # Used for .ply outputs
        self.id_to_vertex = {id_: vtx for id_, vtx in enumerate(self.vertices)}
        self.vertex_to_id = {vtx: id_ for id_, vtx in enumerate(self.vertices)}

    def get_vertex(self, id: int) -> Vertex:
        return self.id_to_vertex[id]

    def get_vertex_id(self, vertex: Vertex) -> int:
        return self.vertex_to_id[vertex]

    @property
    def num_faces(self) -> int:
        return len(self.faces)

    @property
    def num_vertices(self) -> int:
        return len(self.vertices)
