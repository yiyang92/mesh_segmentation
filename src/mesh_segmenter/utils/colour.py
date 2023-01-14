from dataclasses import dataclass
from typing import Union


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

    def __radd__(self, other: Union[type["Colour"], int]) -> type["Colour"]:
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
