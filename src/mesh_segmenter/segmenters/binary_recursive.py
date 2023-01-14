from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import random
import multiprocessing
import logging

from mesh_segmenter.utils.mesh import Mesh, Face
from mesh_segmenter.graph import DualGraph
from mesh_segmenter.segmenters.binary import BinarySegmenter
from mesh_segmenter.utils.utils import random_colours


class BinaryRecursive:
    """Recursively call binary segmenter for more segments."""

    def __init__(
        self, num_levels: int, num_workers=multiprocessing.cpu_count()
    ):
        # Number of sub-clusters
        self._num_levels = num_levels
        self._num_workers = num_workers
        assert num_levels > 0

    def _divide_mesh(self, mesh: Mesh) -> tuple[Mesh, Mesh]:
        """Divide a mesh into 2 parts, based on colour."""
        # TODO: do I need to count like this? Better way?
        # Get colours
        colours_ctr: Counter[Face] = Counter()
        for face in mesh.faces:
            colours_ctr[face.colour] += 1

        common_colours = colours_ctr.most_common(2)
        assert len(common_colours) == 2, "Only one colour? Segment first"
        colour_one, colour_two = common_colours[0][0], common_colours[1][0]

        out_faces: list[list[Face]] = [[], []]
        for face in mesh.faces:
            if face.colour == colour_one:
                out_faces[0].append(face)
            elif face.colour == colour_two:
                out_faces[1].append(face)
            else:
                # Randomly put into 1 or 2
                out_faces[random.randint(0, 1)].append(face)

        return (
            Mesh(vertices=mesh.vertices, faces=out_faces[0]),
            Mesh(vertices=mesh.vertices, faces=out_faces[1]),
        )

    def _combine_meshes(self, meshes: list[Mesh]) -> Mesh:
        faces = []
        for mesh in meshes:
            faces.extend(mesh.faces)

        return Mesh(vertices=meshes[0].vertices, faces=faces)

    def __call__(self, mesh: Mesh, dual_graph: DualGraph) -> Mesh:
        """Recursively clusterize mesh."""
        logging.info(f"Segment into {self._num_levels} levels.")
        orig_num_faces = mesh.num_faces
        stack = [mesh]
        level = 0
        while stack:
            logging.info(f"Segmenting level {level + 1}")
            colours = random_colours(num_colours=(level + 1) * 2)
            output_meshes = []
            idx = 0
            # Segment submeshes of the original mesh
            while stack:
                mesh = stack.pop()
                segmenter = BinarySegmenter(
                    num_workers=self._num_workers,
                    cluster_colors=(colours[idx*2], colours[idx*2+1]),
                )
                output_meshes.append(
                    segmenter(
                        mesh=mesh,
                        dual_graph=dual_graph,
                    )
                )
                idx += 1

            logging.info(f"Level {level + 1} segmented")
            level += 1
            # If we want to segment more
            if level != self._num_levels:
                for mesh in output_meshes:
                    stack.extend(list(self._divide_mesh(mesh)))

        out_mesh = self._combine_meshes(output_meshes)
        if out_mesh.num_faces != orig_num_faces:
            raise ValueError(
                f"Incorrect resulted num faces,"
                f" expected: {orig_num_faces}, got: {out_mesh.num_faces}"
            )

        return out_mesh
