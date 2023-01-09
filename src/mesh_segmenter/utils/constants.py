from dataclasses import dataclass, field
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

    def __str__(self) -> str:
        return f"{self.r} {self.g} {self.b}"


COLOUR_RED = Colour(255, 0, 0)
COLOUR_GREEN = Colour(0, 255, 0)
COLOUR_BLUE = Colour(0, 0, 255)
COLOUR_BLACK = Colour(0, 0, 0)
COLOUR_WHITE = Colour(255, 255, 255)

EPSILON = 0.0001
CONVEX_LIMIT = 3.14159265  # > 180 degree => convex
DELTA = 0.5
