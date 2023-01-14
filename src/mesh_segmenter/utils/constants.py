from enum import Enum

from mesh_segmenter.utils.colour import Colour


class SegmenterType(Enum):
    binary = "binary"

    def __str__(self):
        return self.value


ETA = 0.01
CONVEX_LIMIT = 3.14159265  # > 180 degree => convex
DELTA = 0.5  # Angular and geodesic distances weighting
DIST_N_SMALLEST = 5
MAX_NUM_ITERS = 10

COLOUR_RED = Colour(255, 0, 0)
COLOUR_GREEN = Colour(0, 255, 0)
COLOUR_BLUE = Colour(0, 0, 255)
COLOUR_BLACK = Colour(0, 0, 0)
COLOUR_WHITE = Colour(255, 255, 255)
