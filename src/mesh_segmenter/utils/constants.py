from dataclasses import dataclass
from typing import Union
from enum import Enum


class DecomposeMode(Enum):
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

    def __add__(self, other: Union[type["Colour"], int]) -> type["Colour"]:
        if isinstance(other, int):
            return Colour(
                r=max(255, self.r + other),
                g=max(255, self.g + other),
                b=max(255, self.b + other),
            )
        return Colour(
            r=max(255, self.r + other.r),
            g=max(255, self.g + other.g),
            b=max(255, self.b + other.b),
        )


COLOUR_RED = Colour(255, 0, 0)
COLOUR_GREEN = Colour(0, 255, 0)
COLOUR_BLUE = Colour(0, 0, 255)
COLOUR_BLACK = Colour(0, 0, 0)
COLOUR_WHITE = Colour(255, 255, 255)

ETA = 0.01
CONVEX_LIMIT = 3.14159265  # > 180 degree => convex
DELTA = 0.5  # Angular and geodesic distances weighting
DIST_N_SMALLEST = 5
NUM_ITERS = 10
