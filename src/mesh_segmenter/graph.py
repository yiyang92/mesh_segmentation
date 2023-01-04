import logging
from collections import defaultdict
from dataclasses import dataclass

import tqdm

from mesh_segmenter.utils.constants import Mesh, Vertex, Face


@dataclass(frozen=True)
class GraphNode:
    face: Face
    center: Vertex


class DualGraph:
    """Graph definition - adjacency list between centers of faces."""

    def __init__(self, mesh: Mesh) -> None:
        # Vertices and neighbours
        self._graph = defaultdict(list)
        self._mesh = mesh
        self._create_graph()
    
    @staticmethod
    def _face_center(face: Face) -> Vertex:
        center = face.vertex_one + face.vertex_three + face.vertex_three
        center /= 3
        return center
    
    def _create_graph(self):
        # Find adjacent faces - 2 common vertices
        faces = self._mesh.faces

        logging.info("Creating a dual graph")
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

                common = vts_one.intersection(vts_two)
                if len(common) == 2:
                    node_one = GraphNode(
                        face=face_one,
                        center=self._face_center(face_one),
                    )
                    node_two = GraphNode(
                        face=face_two,
                        center=self._face_center(face_two)
                    )
                    self._graph[node_one].append(node_two)
                    self._graph[node_two].append(node_one)
        logging.info("Dual graph created")
