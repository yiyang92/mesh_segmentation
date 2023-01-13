import logging

from mesh_segmenter.graph import DualGraph
from mesh_segmenter.utils.mesh import Mesh, Face
from mesh_segmenter.utils.constants import NUM_ITERS


class BinarySegmenter:
    """Segments a mesh into 2 segments."""

    def __init__(self, mesh: Mesh, dual_graph: DualGraph, num_iters: int = NUM_ITERS):
        self._dual_graph = dual_graph
        self._mesh = mesh
        self._num_iters = num_iters
        self._form_clusters()
    
    def get_distance(self, face_one: Face, face_two: Face):
        return self._dual_graph.get_distance(face_one, face_two)
    
    def _init_reprs(self) -> list[Face]:
        # For binary case
        # Choose a pair of nodes with highest distances
        max_dist = 0
        repr = (self._mesh.faces[0], self._mesh.faces[0])
        for i, face_one in enumerate(self._mesh.faces):
            for j in range(i + 1, self._mesh.num_faces):
                if (dist := self.get_distance(face_one, self._mesh.faces[j])) > max_dist:
                    max_dist = dist
                    repr = (face_one, self._mesh.faces[j])

        return repr
    
    def _update_probs(self, reprs: tuple[Face, Face], probs: dict[Face, list[float]]) -> None:
        """Updates in-place probabilities of belongings to the REPa or REPb."""
        for face in self._mesh.faces:
            # If distance is closer to other repr - probability of beloning lower
            # Update and normalize
            probs[face][0] = self.get_distance(face, reprs[1])
            probs[face][0] /= (self.get_distance(face, reprs[0]) + self.get_distance(face, reprs[1]))

            probs[face][1] = self.get_distance(face, reprs[0])
            probs[face][1] /= (self.get_distance(face, reprs[0]) + self.get_distance(face, reprs[1]))

    def _prob_dist_sum(self, face: Face, reprs: list[Face], update_idx: int) -> float:
        return 0.0

    def _update_reprs(self, reprs: list[Face]) -> list[Face]:
        min_prob_a_dist = float('inf')
        min_prob_b_dist = float('inf')
        for face in self._mesh.faces:
            pa_dist_sum = self._prob_dist_sum(
                face=face, reprs=reprs, update_idx=0)
            pb_dist_sum = self._prob_dist_sum(
                face=face, reprs=reprs, update_idx=1)

            # Choose a new repr set
            if pa_dist_sum < min_prob_a_dist:
                min_prob_a_dist = pa_dist_sum
                reprs = [face, reprs[1]]

            if pb_dist_sum < min_prob_b_dist:
                min_prob_b_dist = min_prob_b_dist
                reprs = [reprs[0], face]

        return reprs

    def _form_clusters(self):
        # Initial probabilistic representative of patches
        logging.info("Forming initial coarse clusters.")
        reprs = self._init_reprs()
        logging.info("Initial clusters were formed.")
        assert len(reprs) == 2,"Binary segmentation."
        probs = {face: [0.0, 0.0] for face in self._mesh.faces}
        
        logging.info("Iteratively update memeberships, get fuzzy decompose.")
        # Iteratively update list of probabilities of belonging in clusters
        for _ in range(self._num_iters):
            cur_rep_a, cur_rep_b = reprs
            self._update_probs(
                reprs=reprs,
                probs=probs,
            )
            reprs = self._update_reprs(reprs)
            # If no changes
            if cur_rep_a == reprs[0] and cur_rep_b == reprs[1]:
                break

        logging.info("Fuzzy segmentation mmebership updated, get fuzzy decompose.")
