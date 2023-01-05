from pathlib import Path

from mesh_segmenter.utils.constants import Vertex, Face, Mesh

HEADER_START = "ply"
HEADER_END = "end_header"
OUT_COMMENT = "mesh segmenter output for Nikolai Zakharov"
ELEMENT_VERTEX = "element vertex"
ELEMENT_FACE = "element face"


def parse_ply(ply_path: Path) -> Mesh:
    if not ply_path.exists():
        raise FileNotFoundError(f"{str(ply_path)} file does not exist.")

    if ply_path.suffix != ".ply":
        raise ValueError("Input file should have .ply extension")
    
    with ply_path.open("r") as input_file:
        input_lines = input_file.readlines()

    out_mesh = Mesh()
    n_vertices = 0
    n_faces = 0
    start_idx = 0
    # Parse header (TODO: more property parsing)
    for idx, line in enumerate(input_lines):
        if idx == 0 and line.strip() != HEADER_START:
            raise ValueError("Invalid ply")
        
        if ELEMENT_VERTEX in line:
            n_vertices = int(line.strip().split()[-1])
        
        if ELEMENT_FACE in line:
            n_faces = int(line.strip().split()[-1])
        
        if HEADER_END in line:
            start_idx = idx + 1
            break
    
    # Parse vertices
    for idx in range(start_idx, start_idx + n_vertices):
        line = input_lines[idx]
        out_mesh.vertices.append(
            Vertex(*[float(i) for i in line.strip().split()[:3]])
        )
    
    start_idx += n_vertices
    # Parse faces
    for idx in range(start_idx, start_idx + n_faces):
        line = input_lines[idx]
        
        # Assume triangles
        _, v1_idx, v2_idx, v3_idx = line.strip().split()

        v1 = out_mesh.vertices[int(v1_idx)]
        v2 = out_mesh.vertices[int(v2_idx)]
        v3 = out_mesh.vertices[int(v3_idx)]

        face = Face(
            vertex_one=v1,
            vertex_two=v2,
            vertex_three=v3
        )
        out_mesh.faces.append(face)
    
    # TODO: check why can happen such cases?
    # Filter out non-unique faces
    out_mesh.faces = list(set(out_mesh.faces))
    return out_mesh


def write_ply(input_mesh: Mesh, out_path: Path):
    # TODO: write ply file. vertices + vertex_indices and colours
    ...
