"""Host-Python atom-coordinate envelopes; no Blender or GPU dependency.

The surface is a union of elemental vdW spheres (vdw), or its external
probe-centre offset (sas). It is never a solvent-excluded/Connolly surface or
experimental density. Coordinates and exported meshes remain in Angstroms.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

import gemmi
import numpy as np
import scipy
from scipy import ndimage, sparse
from scipy.sparse.csgraph import connected_components
import skimage
from skimage.measure import marching_cubes, mesh_surface_area


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atoms_for_model(model):
    """Choose one residue-wide conformer, preserve common atoms, drop occ<=0."""
    rows, choices = [], []
    for chain in model:
        seen_residues = set()
        for residue in chain:
            residue_key = (str(residue.seqid), residue.name)
            if residue_key in seen_residues:
                raise ValueError(f"Repeated residue identity: {chain.name}/{residue_key}")
            seen_residues.add(residue_key)
            alts = {}
            for atom in residue:
                alt = atom.altloc.strip("\x00 ")
                if alt:
                    alts[alt] = alts.get(alt, 0.0) + max(0.0, atom.occ)
            selected = min(alts, key=lambda k: (-alts[k], k)) if alts else ""
            candidates = {}
            for atom in residue:
                alt = atom.altloc.strip("\x00 ")
                if alt not in ("", selected) or atom.occ <= 0:
                    continue
                if not np.isfinite(atom.occ) or atom.occ > 1.0001:
                    raise ValueError("Invalid atomic occupancy")
                if atom.element.is_hydrogen:
                    continue
                # A selected conformer wins over a duplicate common-atom name.
                score = (alt == selected and bool(alt), atom.occ)
                if atom.name not in candidates or score > candidates[atom.name][0]:
                    candidates[atom.name] = (score, atom)
            if alts:
                choices.append({"chain": chain.name, "residue": str(residue.seqid),
                                "name": residue.name, "chosen_altloc": selected,
                                "occupancy_sums": alts})
            for _, atom in candidates.values():
                pos = [atom.pos.x, atom.pos.y, atom.pos.z]
                radius = float(atom.element.vdw_r)
                if not np.isfinite(pos).all() or not np.isfinite(radius) or radius <= 0:
                    raise ValueError("Nonfinite coordinate or unsupported elemental radius")
                rows.append({"chain": chain.name, "label_asym_id": residue.subchain,
                             "entity_id": residue.entity_id,
                             "residue_id": str(residue.seqid), "residue": residue.name,
                             "atom": atom.name, "element": atom.element.name,
                             "occupancy": atom.occ, "altloc": atom.altloc.strip("\x00 "),
                             "b_iso": atom.b_iso, "vdw_radius_A": radius,
                             "polymer": residue.entity_type == gemmi.EntityType.Polymer,
                             "water": residue.is_water(), "xyz_A": pos})
    return rows, choices


def orient(rows, orientation_path, max_rmsd):
    ref = gemmi.read_structure(str(orientation_path))
    ref.setup_entities()  # OPM PDB lacks the official mmCIF entity annotations.
    ref_rows, _ = atoms_for_model(ref[0])
    key = lambda a: (a["chain"], a["residue_id"], a["residue"], a["atom"])
    target = {key(a): a for a in ref_rows if a["polymer"] and a["atom"] == "CA"}
    matched = [a for a in rows if a["polymer"] and a["atom"] == "CA" and key(a) in target]
    if len(matched) < 10:
        raise ValueError("Too few unambiguously matched CA atoms for rigid alignment")
    p = np.array([a["xyz_A"] for a in matched], dtype=np.float64)
    q = np.array([target[key(a)]["xyz_A"] for a in matched], dtype=np.float64)
    u, singular, vt = np.linalg.svd((p-p.mean(0)).T @ (q-q.mean(0)))
    if singular[-1] < 1e-7:
        raise ValueError("Degenerate CA alignment")
    rotation = u @ vt
    if np.linalg.det(rotation) < 0:
        u[:, -1] *= -1
        rotation = u @ vt
    translation = q.mean(0) - p.mean(0) @ rotation
    residual = np.linalg.norm(p @ rotation + translation - q, axis=1)
    rmsd = float(np.sqrt(np.mean(residual**2)))
    if rmsd > max_rmsd or residual.max() > 5*max_rmsd:
        raise ValueError(f"Orientation coordinates differ nonrigidly: RMSD={rmsd:.6g}, "
                         f"max={residual.max():.6g} A")
    if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-10):
        raise ValueError("Rotation is not orthogonal")
    if not np.isclose(np.linalg.det(rotation), 1, atol=1e-10):
        raise ValueError("Improper/reflected rotation")
    original = np.array([a["xyz_A"] for a in rows], dtype=np.float64)
    transformed = original @ rotation + translation
    # Reproducible all-adjacent-atom distance invariant, not just fitted CA atoms.
    distance_error = float(np.max(np.abs(np.linalg.norm(np.diff(original, axis=0), axis=1)
                            - np.linalg.norm(np.diff(transformed, axis=0), axis=1))))
    if distance_error > 1e-9:
        raise ValueError("Rigid transformation changed interatomic distances")
    for atom, xyz in zip(rows, transformed):
        atom["source_xyz_A"] = atom["xyz_A"]
        atom["xyz_A"] = xyz.tolist()
    dummies = []
    for line in Path(orientation_path).read_text().splitlines():
        if line.startswith(("ATOM", "HETATM")) and line[17:20] == "DUM":
            dummies.append(float(line[46:54]))
    return {"source": str(orientation_path), "sha256": digest(orientation_path),
            "operation": "row-vector xyz_A @ rotation + translation_A; rigid only",
            "rotation": rotation.tolist(), "translation_A": translation.tolist(),
            "determinant": float(np.linalg.det(rotation)), "matched_CA": len(matched),
            "CA_rmsd_A": rmsd, "maximum_CA_residual_A": float(residual.max()),
            "max_adjacent_pair_distance_error_A": distance_error,
            "computed_hydrophobic_boundary_z_A": sorted(set(dummies)),
            "boundary_limit": "OPM model boundaries, not measured complete bilayer leaflets"}


def sphere_field(atoms, spacing, probe, external_only, max_voxels):
    positions = np.array([a["xyz_A"] for a in atoms], dtype=np.float64)
    radii = np.array([a["vdw_radius_A"]+probe for a in atoms], dtype=np.float64)
    low = np.floor(np.min(positions-radii[:, None], axis=0)/spacing)*spacing - 3*spacing
    high = np.ceil(np.max(positions+radii[:, None], axis=0)/spacing)*spacing + 3*spacing
    shape = np.ceil((high-low)/spacing).astype(int)+1
    if int(np.prod(shape)) > max_voxels:
        raise ValueError(f"Requested grid {shape} exceeds --max-voxels")
    # A truncated signed min-distance field; truncation does not change zero set.
    field = np.full(tuple(shape), float(radii.max()+3*spacing), dtype=np.float32)
    for centre, radius in zip(positions, radii):
        reach = radius+2*spacing
        start = np.maximum(0, np.floor((centre-reach-low)/spacing).astype(int))
        end = np.minimum(shape, np.ceil((centre+reach-low)/spacing).astype(int)+1)
        axes = [(np.arange(start[d], end[d])*spacing+low[d]-centre[d]).astype(np.float32)
                for d in range(3)]
        distance = np.sqrt(axes[0][:, None, None]**2+axes[1][None, :, None]**2
                           + axes[2][None, None, :]**2)-radius
        sl = tuple(slice(start[d], end[d]) for d in range(3))
        np.minimum(field[sl], distance, out=field[sl])
    filled_voxels = 0
    if external_only:
        # Retain only bulk-reachable solvent at grid resolution. No morphological
        # smoothing/closing: connected channels stay open; enclosed voids fill.
        inside = field <= 0
        filled = ndimage.binary_fill_holes(inside, structure=ndimage.generate_binary_structure(3, 1))
        inaccessible = filled & ~inside
        filled_voxels = int(inaccessible.sum())
        field[inaccessible] = -spacing
    if not np.isfinite(field).all():
        raise ValueError("Nonfinite scalar field")
    vertices, faces, _, _ = marching_cubes(field, level=0, spacing=(spacing,)*3,
                                          gradient_direction="ascent", allow_degenerate=False)
    vertices = vertices.astype(np.float64)+low
    faces = faces.astype(np.int32)
    signed = np.einsum("ij,ij->i", vertices[faces[:, 0]],
                      np.cross(vertices[faces[:, 1]], vertices[faces[:, 2]])).sum()/6
    if signed < 0:
        faces = faces[:, [0, 2, 1]]
    return vertices, faces, {"origin_A": low.tolist(), "shape_xyz": shape.tolist(),
                             "spacing_A": spacing, "enclosed_solvent_voxels_filled": filled_voxels}


def topology(vertices, faces):
    if not np.isfinite(vertices).all() or faces.min() < 0 or faces.max() >= len(vertices):
        raise ValueError("Invalid mesh indices/coordinates")
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    unique, counts = np.unique(edges, axis=0, return_counts=True)
    graph = sparse.coo_matrix((np.ones(len(unique), dtype=np.uint8),
                              (unique[:, 0], unique[:, 1])), shape=(len(vertices),)*2).tocsr()
    ncomp, labels = connected_components(graph, directed=False)
    areas = np.linalg.norm(np.cross(vertices[faces[:, 1]]-vertices[faces[:, 0]],
                                   vertices[faces[:, 2]]-vertices[faces[:, 0]]), axis=1)/2
    volume = np.einsum("ij,ij->i", vertices[faces[:, 0]],
                       np.cross(vertices[faces[:, 1]], vertices[faces[:, 2]])).sum()/6
    result = {"vertices": len(vertices), "triangles": len(faces), "unique_edges": len(unique),
              "boundary_edges": int((counts == 1).sum()),
              "nonmanifold_edges": int((counts > 2).sum()), "components": int(ncomp),
              "component_vertex_counts": np.bincount(labels).tolist(),
              "component_area_A2": np.bincount(labels[faces[:, 0]], weights=areas).tolist(),
              "euler_characteristic": int(len(vertices)-len(unique)+len(faces)),
              "area_A2": float(mesh_surface_area(vertices, faces)),
              "signed_volume_A3": float(volume), "minimum_triangle_area_A2": float(areas.min()),
              "bounds_A": [vertices.min(0).tolist(), vertices.max(0).tolist()]}
    if result["boundary_edges"] or result["nonmanifold_edges"] or areas.min() <= 0 or volume <= 0:
        raise ValueError(f"Mesh failed closed-manifold/positive-area-volume audit: {result}")
    return result


def write_obj(path, vertices, faces, title):
    # No mesh smoothing, normal displacement or coordinate rescaling.
    with Path(path).open("w", newline="\n") as out:
        out.write(f"# {title}; coordinates Angstroms; no baked vertex normals\n")
        np.savetxt(out, vertices, fmt="v %.8f %.8f %.8f")
        np.savetxt(out, faces+1, fmt="f %d %d %d")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--assembly", default="1")
    parser.add_argument("--orientation-pdb", type=Path)
    parser.add_argument("--max-alignment-rmsd", type=float, default=.05)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--spacing", type=float, default=.4)
    parser.add_argument("--surface", choices=["vdw", "sas"], default="sas")
    parser.add_argument("--probe", type=float, default=1.4)
    parser.add_argument("--max-voxels", type=int, default=50_000_000)
    args = parser.parse_args()
    if not .35 <= args.spacing <= .5 or not np.isfinite(args.probe) or args.probe < 0:
        parser.error("Use finite 0.35–0.5 A spacing and nonnegative probe")
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out/"manifest.json").exists():
        parser.error("Output manifest exists; use a new output folder to preserve prior evidence")
    structure = gemmi.read_structure(str(args.source))
    if len(structure) != 1:
        raise ValueError("Multiple coordinate models require an explicit model selection policy")
    assembly = next(a for a in structure.assemblies if a.name == args.assembly)
    model = gemmi.make_assembly(assembly, structure[0], gemmi.HowToNameCopiedChain.Dup)
    if len({c.name for c in model}) != len(model):
        raise ValueError("Assembly repeats author chain names; unique-copy naming required")
    rows, choices = atoms_for_model(model)
    alignment = orient(rows, args.orientation_pdb, args.max_alignment_rmsd) if args.orientation_pdb else None
    probe = args.probe if args.surface == "sas" else 0.0
    external = args.surface == "sas"
    manifest = {"status": "PREPROCESSING AND TOPOLOGY AUDIT ONLY; no visual/anatomical acceptance",
                "source": str(args.source), "source_sha256": digest(args.source),
                "code_sha256": digest(__file__), "entry": structure.name,
                "assembly": args.assembly, "assembly_author_determined": assembly.author_determined,
                "units": "Angstroms; shared assembly frame; no independent chain recentering",
                "surface": args.surface, "probe_radius_A": probe,
                "chain_surface_scope": "Each chain is evaluated independently in the common assembly frame. "
                    "Buried inter-chain surfaces remain and inflated chain envelopes can overlap; "
                    "these are not a partition of the exposed surface of the combined complex.",
                "definition": "Zero set of min_i(distance(x,atom_i)-(elemental_vdW_radius_i+probe)); "
                              + ("enclosed solvent components filled at grid resolution; external probe-centre SAS."
                                 if external else "union of elemental vdW spheres; internal cavities retained."),
                "not_claimed": ["solvent-excluded/Connolly surface", "experimental electron density",
                                "complete missing loops", "native membrane bilayer", "dynamics/trajectory"],
                "radii": {a["element"]: a["vdw_radius_A"] for a in rows},
                "selection": "Heavy atoms with occupancy>0; residue-wide maximum-summed-occupancy "
                             "altloc, lexicographic ties; common atoms retained; no occupancy radius scaling",
                "altloc_choices": choices, "rigid_orientation": alignment,
                "environment": {"python": platform.python_version(), "gemmi": gemmi.__version__,
                                "numpy": np.__version__, "scipy": scipy.__version__,
                                "skimage": skimage.__version__}, "chains": []}
    entity_lengths = {e.name: len(e.full_sequence) for e in structure.entities}
    for chain in model:
        atoms = [a for a in rows if a["chain"] == chain.name and a["polymer"]]
        if not atoms:
            continue
        vertices, faces, grid = sphere_field(atoms, args.spacing, probe, external, args.max_voxels)
        audit = topology(vertices, faces)
        prefix = f"chain-{chain.name}"
        obj = args.out/(prefix+".obj")
        write_obj(obj, vertices, faces, f"{structure.name} assembly {args.assembly} author chain {chain.name}")
        npz = args.out/(prefix+".npz")
        np.savez_compressed(npz, vertices=vertices, faces=faces)
        identities = sorted(set((a["residue_id"], a["residue"]) for a in atoms))
        entity_ids = sorted({a["entity_id"] for a in atoms})
        manifest["chains"].append({"author_chain": chain.name,
            "label_asym_ids": sorted({a["label_asym_id"] for a in atoms}),
            "entity_ids": entity_ids, "selected_heavy_atoms": len(atoms),
            "modelled_residues": len(identities), "source_sequence_lengths": {e: entity_lengths[e] for e in entity_ids},
            "residues_present": identities, "grid": grid, "mesh_audit": audit,
            "obj": obj.name, "obj_sha256": digest(obj), "npz": npz.name, "npz_sha256": digest(npz)})
        print(f"{prefix}: {len(atoms)} atoms; {len(vertices)} vertices; {len(faces)} triangles; "
              f"{audit['components']} closed components", flush=True)
    atom_file = args.out/"atoms-and-ligands.json"
    atom_file.write_text(json.dumps({"units": "Angstroms", "atoms": rows,
        "rendering_note": "Protein meshes exclude ligands/water; ligand and source atom coordinates retained here.",
        "source_specific_note": "For 3WGU author A: Na 2005–2007 are the three clustered bound ions; "
                                "Na 2008 is distant. Deposited Na inventory is not transport stoichiometry."}, indent=2)+"\n")
    manifest["atoms_file"] = atom_file.name
    manifest["atoms_sha256"] = digest(atom_file)
    manifest["atom_counts"] = {"selected_heavy_total": len(rows),
        "polymer": sum(a["polymer"] for a in rows), "water": sum(a["water"] for a in rows),
        "nonpolymer_nonwater": sum(not a["polymer"] and not a["water"] for a in rows)}
    (args.out/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({"atom_counts": manifest["atom_counts"], "alignment": alignment}, indent=2))


if __name__ == "__main__":
    main()
