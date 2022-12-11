from dataclasses import dataclass, field
from enum import Enum, auto


class DecompositionTypes(Enum):
    # TODO: to str
    binary = auto()


@dataclass(frozen=True)
class Colour:
    r: int
    g: int
    b: int


COLOUR_RED = Colour(255, 0, 0)
COLOUR_GREEN = Colour(0, 255, 0)
COLOUR_BLUE = Colour(0, 0, 255)
COLOUR_WHITE = Colour(255, 255, 255)


@dataclass(frozen=True)
class Vertex:
    x: float
    y: float
    z: float


class Face:

    def __init__(
        self,
        v1: Vertex,
        v2: Vertex,
        v3: Vertex,
        colour: Colour = COLOUR_WHITE,
    ):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.colour = colour


@dataclass
class Mesh:
    vertices: list[Vertex] = field(default_factory=list)
    faces: list[Face] = field(default_factory=list)
