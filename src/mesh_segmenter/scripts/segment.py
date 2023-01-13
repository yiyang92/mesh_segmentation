import argparse
from pathlib import Path
import logging

from mesh_segmenter.utils.utils import parse_ply, write_ply
from mesh_segmenter.graph import DualGraph
from mesh_segmenter.segmenter import BinarySegmenter


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
        "-m",
        "--decompose_mode",
        type=Path,
        default=Path("TODO"),
    )
    parser.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        choices=["INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    logging.basicConfig(level=logging.getLevelName(args.log_level))

    # Parse ply file, form Mesh
    mesh = parse_ply(ply_path=args.input_file)
    dual_graph = DualGraph(mesh)
    segmenter = BinarySegmenter(mesh=mesh, dual_graph=dual_graph)

    write_ply(mesh=mesh, out_path=args.output_file)


if __name__ == "__main__":
    main()
