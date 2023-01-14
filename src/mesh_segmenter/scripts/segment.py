import argparse
import multiprocessing
from pathlib import Path
import logging

from mesh_segmenter.utils.constants import SegmenterType
from mesh_segmenter.utils.utils import parse_ply, write_ply, random_colours
from mesh_segmenter.graph import DualGraph
from mesh_segmenter.segmenters import BinaryRecursive, BinarySegmenter


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-i",
        "--input_file",
        type=Path,
        required=True,
        help="Input .ply file path",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=Path,
        default=Path("output_decompose.ply"),
        help="Output .ply filename",
    )
    parser.add_argument(
        "-s",
        "--segmenter",
        type=str,
        default=SegmenterType.binary,
        choices=list(SegmenterType),
    )
    parser.add_argument(
        "-k",
        "--num_levels",
        type=int,
        default=1,
        help="Number of segmentation levels for the binary segmenter.",
    )
    parser.add_argument(
        "-t",
        "--num_threads",
        type=int,
        default=multiprocessing.cpu_count(),
    )
    parser.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        choices=["INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    # TODO: add some validation fof arguments
    return parser.parse_args()


def main():
    args = _parse_args()
    logging.basicConfig(level=logging.getLevelName(args.log_level))

    # Parse ply file, form Mesh
    mesh = parse_ply(ply_path=args.input_file)
    dual_graph = DualGraph(mesh)

    # Choose segmenter
    if args.segmenter == SegmenterType.binary:
        if args.num_levels == 1:
            # Binary
            segmenter = BinarySegmenter(num_workers=args.num_threads)
        else:
            # Binary recursive
            segmenter = BinaryRecursive(
                num_levels=args.num_levels,
                num_workers=args.num_threads,
            )

    # Segment
    out_mesh = segmenter(mesh=mesh, dual_graph=dual_graph)

    # Output results
    write_ply(mesh=out_mesh, out_path=args.output_file)


if __name__ == "__main__":
    main()
