import logging
from collections import defaultdict
from dataclasses import dataclass

import tqdm

from mesh_segmenter.utils.mesh import Mesh, Face
from mesh_segmenter.utils.utils import angular_distance, geodesic_distance
from mesh_segmenter.utils.constants import DELTA


@dataclass
class GraphEdge:
    ang_distance: float
    geod_distance: float
    weight: float


class DualGraph:
    """Graph definition - adjacency list between centers of faces."""

    def __init__(self, mesh: Mesh) -> None:
        # Vertices and neighbours
        # Weighted graph of connected faces
        self._graph: dict[Face, dict[Face, GraphEdge]] = defaultdict(dict)
        # Keep track for weight
        self._ang_dists: list[float] = []
        self._geod_dists: list[float] = []
        # Distances between all faces (TODO: is it needed here?)
        self._distances: dict[Face, Face] = {}
        self._mesh: Mesh = mesh
        self._create_graph()
        self._calculate_weights()

    def _create_graph(self):
        # Find adjacent faces - 2 common vertices
        faces = self._mesh.faces

        logging.info("Creating a dual graph, calculating angular and geodesic distances.")
        for i, face_one in tqdm.tqdm(enumerate(faces), total=len(faces)):
            for j, face_two in enumerate(faces):
                if i == j:
                    continue

                # Check if they have 2 common vertices => common edge
                vts_one = {
                    face_one.vertex_one,
                    face_one.vertex_two,
                    face_two.vertex_three
                }
                vts_two = {
                    face_two.vertex_one,
                    face_two.vertex_two,
                    face_two.vertex_three
                }
                common = list(vts_one.intersection(vts_two))
                if len(common) == 2:
                    # Define connections (weights calculated later)
                    ang_distance = angular_distance(face_one, face_two)
                    geod_distance = geodesic_distance(
                        face_one=face_one,
                        face_two=face_two,
                        common_one=common[0],
                        common_two=common[1],
                    )
                    self._ang_dists.append(ang_distance)
                    self._geod_dists.append(geod_distance)
                    # Add arcs
                    self._graph[face_one][face_two] = GraphEdge(
                        ang_distance=ang_distance,
                        geod_distance=geod_distance,
                        weight=None,
                    )
                    self._graph[face_two][face_one] = GraphEdge(
                        ang_distance=ang_distance,
                        geod_distance=geod_distance,
                        weight=None,
                    )
        logging.info("Dual graph created")

    def _calculate_weights(self):
        logging.info("Calculating weights for dual graph arcs")
        
        # Calculate average
        average_angular = sum(self._ang_dists) / len(self._ang_dists)
        average_geod = sum(self._geod_dists) / len(self._geod_dists)
        
        # Caclulate weights for arcs
        for face_one in self._graph:
            for face_two in self._graph[face_one]:
                edge = self._graph[face_one][face_two]
                if edge.weight is not None:
                    continue

                ang = (1 - DELTA) * edge.ang_distance / average_angular
                geod = DELTA * edge.geod_distance / average_geod
                edge.weight = ang + geod
        logging.info("Dual graph weights were calculated")
