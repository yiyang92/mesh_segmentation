import logging
from collections import defaultdict
from dataclasses import dataclass

import tqdm

from mesh_segmenter.utils.mesh import Mesh, Vertex, Face


@dataclass(frozen=True)
class GraphNode:
    face: Face
    center: Vertex
    normal: Vertex


class DualGraph:
    """Graph definition - adjacency list between centers of faces."""

    def __init__(self, mesh: Mesh) -> None:
        # Vertices and neighbours
        self._graph = defaultdict(list)  # Graph of connected faces
        self._weights = {}  # Weight between all faces
        self._distances = {}  # Distances between all faces
        self._mesh = mesh
        self._create_graph()

    @staticmethod
    def _face_center(face: Face) -> Vertex:
        center = (face.vertex_one + face.vertex_three + face.vertex_three) / 3
        return center

    @staticmethod
    def _face_normal(face: Face) -> Vertex:
        # Find 2 edge vectors
        edge_one = face.vertex_one - face.vertex_two
        edge_two = face.vertex_one - face.vertex_three
        
        # Find cross product to get a vector, pointing as normal
        normal = edge_one.cross(edge_two)
        normal /= normal.length
        return normal
    
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
                        normal=self._face_normal(face_one),
                    )
                    node_two = GraphNode(
                        face=face_two,
                        center=self._face_center(face_two),
                        normal=self._face_normal(face_two),
                    )
                    self._graph[node_one].append(node_two)
                    self._graph[node_two].append(node_one)
        logging.info("Dual graph created")

    # def _calculate_weights(self):
    #     # Calclulate angular disctances

    #     # Calculate geodesic distances