from dataclasses import dataclass, field
from typing import Union
from enum import Enum


class DecompositionTypes(Enum):
    binary = "binary"
    k_way = "k_way"

    def __str__(self):
        return self.value


@dataclass(frozen=True)
class Colour:
    r: int
    g: int
    b: int


COLOUR_RED = Colour(255, 0, 0)
COLOUR_GREEN = Colour(0, 255, 0)
COLOUR_BLUE = Colour(0, 0, 255)
COLOUR_BLACK = Colour(0, 0, 0)


@dataclass(frozen=True)
class Vertex:
    x: float
    y: float
    z: float

    def __add__(self, other: Union[type["Vertex"], int]) -> type["Vertex"]:
        if isinstance(other, int):
            return Vertex(
                self.x + other,
                self.y + other,
                self.z + other,
            )
        else:
            return Vertex(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z,
            )

    def __truediv__(self, other: int) -> type["Vertex"]:
        return Vertex(
            self.x / other,
            self.y / other,
            self.z / other,
        )


@dataclass(frozen=True)
class Face:
    vertex_one: Vertex
    vertex_two: Vertex
    vertex_three: Vertex
    colour: Colour = COLOUR_BLACK


@dataclass
class Mesh:
    vertices: list[Vertex] = field(default_factory=list)
    faces: list[Face] = field(default_factory=list)
