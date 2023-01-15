import logging
import heapq
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from typing import Union, Type
from collections import defaultdict
from dataclasses import dataclass

import tqdm

from mesh_segmenter.utils.mesh import Mesh, Face
from mesh_segmenter.utils.utils import angular_distance, geodesic_distance
from mesh_segmenter.utils.constants import DELTA, DIST_N_SMALLEST


@dataclass
class GraphEdge:
    ang_distance: float
    geod_distance: float
    weight: float

    def __lt__(self, other: Type["GraphEdge"]) -> bool:
        if self.weight != other.weight:
            return self.weight < other.weight
        return False


@dataclass(frozen=True)
class HeapNode:
    distance: float
    face: Face

    def __lt__(self, other: Type["HeapNode"]) -> bool:
        if self.distance != other.distance:
            return self.distance < other.distance
        return False


class DualGraph:
    """Graph definition - adjacency list between centers of faces."""

    def __init__(
        self,
        mesh: Mesh,
        dist_n_smallest=DIST_N_SMALLEST,
        num_workers=multiprocessing.cpu_count(),
    ) -> None:
        # Vertices and neighbours
        self._num_workers = num_workers
        # Weighted graph of connected faces
        self._graph: dict[Face, dict[Face, GraphEdge]] = defaultdict(dict)
        # Keep track for weight
        self._ang_dists: list[float] = []
        self._geod_dists: list[float] = []
        self._mesh: Mesh = mesh
        # Distances
        self._dist_n_smallest: int = dist_n_smallest
        self._distance: dict[Face, Face] = {}
        self._create_graph()
        self._calculate_weights()
        self._calculate_distances()

    @property
    def graph(self) -> dict[Face, dict[Face, GraphEdge]]:
        return self._graph

    def get_distance(
        self, face_one: Face, face_two: Face
    ) -> Union[None, float]:
        if face_one not in self._distance:
            return None

        if face_two not in self._distance[face_one]:
            return float("infinity")

        return self._distance[face_one][face_two]

    def _create_graph(self) -> None:
        # Find adjacent faces - 2 common vertices
        faces = self._mesh.faces

        logging.info(
            "Creating a dual graph, calculating angular and geodesic distances."
        )
        for i, face_one in tqdm.tqdm(enumerate(faces), total=len(faces)):
            for j, face_two in enumerate(faces):
                if i == j:
                    continue

                # Check if they have 2 common vertices => common edge
                vts_one = {
                    face_one.vertex_one,
                    face_one.vertex_two,
                    face_two.vertex_three,
                }
                vts_two = {
                    face_two.vertex_one,
                    face_two.vertex_two,
                    face_two.vertex_three,
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

    def _calculate_weights(self) -> None:
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

    def _shortest_path_dijkstra(
        self,
        start: Face,
    ) -> tuple[Face, dict[GraphEdge, float]]:
        # Distances to nodes
        distances = {node: float("infinity") for node in self.graph}
        distances[start] = 0.0
        unvisited = [HeapNode(distance=distances[start], face=start)]
        heapq.heapify(unvisited)

        while unvisited:
            # The closest unvisited node, greedily look
            curr_node = heapq.heappop(unvisited)
            # Update distances of neighbors
            for neighbor, edge in heapq.nsmallest(
                n=self._dist_n_smallest,
                iterable=self.graph[curr_node.face].items(),
                key=lambda x: x[1],
            ):
                weight = edge.weight
                if weight + curr_node.distance < distances[neighbor]:
                    distances[neighbor] = weight + curr_node.distance
                    heapq.heappush(
                        unvisited,
                        HeapNode(distance=distances[neighbor], face=neighbor),
                    )

        return start, distances

    def _calculate_distances(self):
        logging.info("Calculating distances between faces")

        with ThreadPoolExecutor(max_workers=self._num_workers) as executor:
            results = tqdm.tqdm(
                executor.map(self._shortest_path_dijkstra, self._mesh.faces),
                total=self._mesh.num_faces,
            )
            for face, distances in results:
                self._distance[face] = distances

        logging.info("Distances calulated")
