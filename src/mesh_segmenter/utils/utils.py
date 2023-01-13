from pathlib import Path

from mesh_segmenter.utils.mesh import Vertex, Face, Mesh
from mesh_segmenter.utils.constants import CONVEX_LIMIT, EPSILON

HEADER_START = "ply"
FORMAT = "format ascii 1.0"
HEADER_END = "end_header"
OUT_COMMENT = "comment mesh segmenter output by Nikolai Zakharov"
ELEMENT_VERTEX = "element vertex"
ELEMENT_FACE = "element face"


def parse_ply(ply_path: Path) -> Mesh:
    if not ply_path.exists():
        raise FileNotFoundError(f"{str(ply_path)} file does not exist.")

    if ply_path.suffix != ".ply":
        raise ValueError("Input file should have .ply extension")

    with ply_path.open("r") as input_file:
        input_lines = input_file.readlines()

    out_mesh_vertices: list[Vertex] = []
    out_mesh_faces: list[Face] = []

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
        out_mesh_vertices.append(
            Vertex(*[float(i) for i in line.strip().split()[:3]])
        )

    start_idx += n_vertices
    # Parse faces
    for idx in range(start_idx, start_idx + n_faces):
        line = input_lines[idx]

        # Assume triangles
        _, v1_idx, v2_idx, v3_idx = line.strip().split()

        v1 = out_mesh_vertices[int(v1_idx)]
        v2 = out_mesh_vertices[int(v2_idx)]
        v3 = out_mesh_vertices[int(v3_idx)]

        face = Face(vertex_one=v1, vertex_two=v2, vertex_three=v3)
        out_mesh_faces.append(face)

    # TODO: check why can happen such cases?
    # Filter out non-unique faces
    out_mesh_faces = list(set(out_mesh_faces))
    out_mesh = Mesh(vertices=out_mesh_vertices, faces=out_mesh_faces)
    return out_mesh


def write_ply(mesh: Mesh, out_path: Path):
    """Write ply file with vertices + vertex_indices and colours."""
    header = f"""{HEADER_START}
{FORMAT}
{OUT_COMMENT}
{ELEMENT_VERTEX} {len(mesh.vertices)}
{mesh.vertices[0].out_properties}
{ELEMENT_FACE} {len(mesh.faces)}
property list uchar int vertex_indices
{mesh.faces[0].out_properties}
{HEADER_END}
"""
    vertices_str = "\n".join([str(vtx) for vtx in mesh.vertices])
    faces_str = []
    # 3 (num vertices) vertex_id_0 vertex_id_1 vertex_id_2
    for face in mesh.faces:
        vertice_ids = " ".join(
            [str(mesh.get_vertex_id(vtx)) for vtx in face.vertices]
        )
        faces_str.append(f"3 {vertice_ids} {face.properties_str}")

    with out_path.open("w") as f:
        f.writelines([header, vertices_str, "\n", "\n".join(faces_str), "\n"])


def angular_distance(face_one: Face, face_two: Face) -> float:
    """Computes angular distance between adjacent faces."""
    mu = 1.0

    normal_one = face_one.normal
    normal_two = face_two.normal

    if normal_one.angle(normal_two) > CONVEX_LIMIT:
        # Small positive
        mu = EPSILON

    return mu * (1 - normal_one.cos_angle(normal_two))


def geodesic_distance(
    face_one: Face,
    face_two: Face,
    common_one: Vertex,
    common_two: Vertex,
) -> float:
    """Find a geodesic distance between 2 adjacent faces.

    It is defined as a shotest path between their centers.
    """
    # TODO: check
    # 2 common points, find edge vector direction
    edge = common_one - common_two

    # Vectors from centers to the edge
    face_one_c_edge = face_one.center - common_one
    face_two_c_edge = face_two.center - common_one

    # Orthogonal vector
    face_one_c_orth = face_one_c_edge.cross(edge)
    face_two_c_orth = face_two_c_edge.cross(edge)

    # Find lengths and normalize
    line_one_len = face_one_c_orth.length() / edge.length()
    line_two_len = face_two_c_orth.length() / edge.length()
    line_three_len = (face_one_c_orth - face_two_c_orth).length()

    return line_one_len + line_two_len + line_three_len
