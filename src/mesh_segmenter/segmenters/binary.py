import logging
from copy import deepcopy
import multiprocessing
from functools import partial
from concurrent.futures import ThreadPoolExecutor

import tqdm

from mesh_segmenter.graph import DualGraph
from mesh_segmenter.utils.mesh import Mesh, Face
from mesh_segmenter.utils.constants import (
    MAX_NUM_ITERS,
    COLOUR_BLUE,
    COLOUR_RED,
)
from mesh_segmenter.utils.colour import Colour


class BinarySegmenter:
    """Segments a mesh into the 2 segments."""

    def __init__(
        self,
        num_workers: int = multiprocessing.cpu_count(),
        num_iters: int = MAX_NUM_ITERS,
        prob_threshold: float = 0.5,
        cluster_colors: tuple[Colour, Colour] = (COLOUR_BLUE, COLOUR_RED),
    ):
        self._num_workers = num_workers
        self._num_iters = num_iters
        self._cluster_colors = cluster_colors
        self._color_unsure = sum(cluster_colors)
        self._prob_threshold = prob_threshold

    def _init_reprs(self, mesh: Mesh, dual_graph: DualGraph) -> list[Face]:
        # For binary case
        # Choose a pair of nodes with highest distances
        max_dist = 0
        repr = [mesh.faces[0], mesh.faces[0]]

        for i, face_one in enumerate(mesh.faces):
            for j in range(i + 1, mesh.num_faces):
                if (
                    dist := dual_graph.get_distance(face_one, mesh.faces[j])
                ) > max_dist:
                    max_dist = dist
                    repr = [face_one, mesh.faces[j]]

        return repr

    def _update_probs(
        self,
        reprs: list[Face],
        probs: dict[Face, list[float]],
        dual_graph: DualGraph,
        mesh: Mesh,
    ) -> None:
        """Updates in-place probabilities of belongings to the REPa or REPb."""
        # TODO: parallelize, need to debug a closed context problem!
        for face in mesh.faces:
            # If distance is closer to other repr - probability of beloning lower
            # Update and normalize
            probs[face][0] = dual_graph.get_distance(face, reprs[1])
            probs[face][0] /= dual_graph.get_distance(
                face, reprs[0]
            ) + dual_graph.get_distance(face, reprs[1])

            probs[face][1] = dual_graph.get_distance(face, reprs[0])
            probs[face][1] /= dual_graph.get_distance(
                face, reprs[0]
            ) + dual_graph.get_distance(face, reprs[1])

    def _prob_dist_sum(
        self,
        face: Face,
        probs: dict[Face, list[float]],
        cluster_idx: int,
        mesh: Mesh,
        dual_graph: DualGraph,
    ) -> float:
        out_sum = 0
        for face_cur in mesh.faces:
            out_sum += probs[face_cur][cluster_idx] * dual_graph.get_distance(
                face_cur, face
            )

        return out_sum

    def _update_reprs(
        self,
        reprs: list[Face],
        probs: dict[Face, list[float]],
        mesh: Mesh,
        dual_graph: DualGraph,
    ) -> list[Face]:
        # TODO: parallelize
        min_prob_a_dist = float("inf")
        min_prob_b_dist = float("inf")
        for face in mesh.faces:
            pa_dist_sum = self._prob_dist_sum(
                face=face,
                probs=probs,
                cluster_idx=0,
                mesh=mesh,
                dual_graph=dual_graph,
            )
            pb_dist_sum = self._prob_dist_sum(
                face=face,
                probs=probs,
                cluster_idx=1,
                mesh=mesh,
                dual_graph=dual_graph,
            )
            # Choose a new repr set
            if pa_dist_sum < min_prob_a_dist:
                min_prob_a_dist = pa_dist_sum
                reprs = [face, reprs[1]]

            if pb_dist_sum < min_prob_b_dist:
                min_prob_b_dist = min_prob_b_dist
                reprs = [reprs[0], face]

        return reprs

    def _form_clusters(
        self, mesh: Mesh, dual_graph: DualGraph
    ) -> dict[Face, list[float]]:
        """Form segmentation clusters, output probabilities of memberships."""
        logging.info("Forming initial coarse clusters.")
        # Initial cluster centers, the 2 most further faces
        reprs: list[Face] = self._init_reprs(mesh=mesh, dual_graph=dual_graph)
        logging.info("Initial clusters were formed.")
        assert len(reprs) == 2, "Binary segmentation."

        logging.info("Iteratively update memberships, get fuzzy decompose.")
        probs = {face: [0.0, 0.0] for face in mesh.faces}
        # Iteratively update list of probabilities of belonging in clusters
        for _ in tqdm.trange(self._num_iters):
            cur_rep_a, cur_rep_b = reprs
            self._update_probs(
                reprs=reprs,
                probs=probs,
                mesh=mesh,
                dual_graph=dual_graph,
            )
            reprs = self._update_reprs(
                reprs=reprs,
                probs=probs,
                mesh=mesh,
                dual_graph=dual_graph,
            )
            # If no updates
            if cur_rep_a == reprs[0] and cur_rep_b == reprs[1]:
                break

        logging.info(
            "Fuzzy segmentation memberships updated, get fuzzy decompose."
        )
        return probs

    def _update_segment_colours(
        self, mesh: Mesh, probs: dict[Face, list[float]]
    ) -> None:
        """Update coulours according to probabilities."""
        logging.info("Updating face segment colours")
        for face in mesh.faces:
            if probs[face][0] > self._prob_threshold:
                face.set_colour(self._cluster_colors[0])
            elif probs[face][1] > self._prob_threshold:
                face.set_colour(self._cluster_colors[1])
            else:
                face.set_colour(self._color_unsure)

        # TODO: fuzziness on borders
        logging.info("Segment colours update completed.")

    def __call__(self, mesh: Mesh, dual_graph: DualGraph) -> Mesh:
        """Segmented mesh with coloured seg  ments."""
        mesh, dual_graph = deepcopy(mesh), deepcopy(dual_graph)
        probs = self._form_clusters(mesh=mesh, dual_graph=dual_graph)
        self._update_segment_colours(mesh=mesh, probs=probs)

        return mesh
