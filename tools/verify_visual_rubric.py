"""Producer-side, fail-closed V01-V20 visual evidence gate.

This verifies coverage, file integrity and the presence of scoped review evidence.
It cannot determine whether an anatomical claim or a photograph is scientifically
correct. It deliberately emits no acceptance records or public export.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

MEDIA = {".svg", ".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".mp4", ".webm", ".mov", ".gif", ".glb", ".gltf"}
LAYOUTS = ("native", "desktop", "650px", "390px", "print")
CRITERIA = tuple(f"V{i:02d}" for i in range(1, 21))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SurfaceParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []
        self.counts = {}

    def handle_starttag(self, tag, attributes):
        if tag not in {"img", "svg", "canvas", "video", "iframe", "object"}:
            return
        attrs = dict(attributes)
        self.counts[tag] = self.counts.get(tag, 0) + 1
        self.items.append((attrs.get("id") or f"{tag}-{self.counts[tag]}"))


class SelectParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.select_id = None
        self.option_value = None
        self.option_text = None
        self.modes = {}

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "select":
            self.select_id = attrs.get("id", "unnamed-select")
            self.modes.setdefault(self.select_id, [])
        elif tag == "option" and self.select_id:
            self.option_value = attrs.get("value")
            self.option_text = ""

    def handle_data(self, data):
        if self.option_text is not None:
            self.option_text += data

    def handle_endtag(self, tag):
        if tag == "option" and self.option_text is not None:
            self.modes[self.select_id].append({"value": self.option_value, "label": self.option_text.strip()})
            self.option_value = self.option_text = None
        elif tag == "select":
            self.select_id = None


def current_inventory(root: Path):
    """Independent read-only scan matching the declared inventory's scope."""
    manifest = json.loads((root / "chapter-manifest.json").read_text(encoding="utf-8"))
    planned = {}
    for ch in manifest["chapters"]:
        for kind in ("illustrations", "animations"):
            for x in ch.get(kind, []):
                planned[x["id"]] = x.get("path")
    files = {root / c["file"] for c in manifest["chapters"]}
    files.update(p for p in (root / "assets").rglob("*") if p.is_file() and "__pycache__" not in p.parts and re.match(r"ch\d\d-", p.name))
    files.add(root / "assets" / "secretory-traffic-pilot.html")
    actual = {}
    for path in sorted(files):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        ext = path.suffix.lower()
        if ext in MEDIA:
            actual[rel] = sha(path)
        elif ext == ".html":
            parser = SurfaceParser()
            parser.feed(path.read_text(encoding="utf-8", errors="replace"))
            for name in parser.items:
                actual[f"{rel}#{name}"] = sha(path)
        elif ext == ".js":
            source = path.read_text(encoding="utf-8", errors="replace")
            if any(m in source for m in ("<svg", "<path", "<rect", "createElementNS", "getContext(", "WebGLRenderer")):
                actual[rel] = sha(path)
    return planned, actual


def file_proof(root: Path, obj, where: str, errors: list[str]):
    if not isinstance(obj, dict) or not isinstance(obj.get("path"), str) or not re.fullmatch(r"[0-9a-f]{64}", str(obj.get("sha256", ""))):
        errors.append(f"{where}: missing path/SHA-256 proof")
        return
    path = Path(obj["path"])
    if path.is_absolute() or ".." in path.parts:
        errors.append(f"{where}: proof path must stay relative to producer root")
        return
    full = root / path
    try:
        resolved = full.resolve(strict=True)
    except (OSError, RuntimeError):
        errors.append(f"{where}: proof file missing: {path.as_posix()}")
        return
    if not resolved.is_relative_to(root.resolve()):
        errors.append(f"{where}: proof path escapes producer root: {path.as_posix()}")
    elif not resolved.is_file():
        errors.append(f"{where}: proof file missing: {path.as_posix()}")
    elif resolved.stat().st_size == 0:
        errors.append(f"{where}: empty proof: {path.as_posix()}")
    elif sha(resolved) != obj["sha256"]:
        errors.append(f"{where}: stale proof SHA-256: {path.as_posix()}")


def review_units_for_surface(surface):
    ident = surface["id"]
    kind = surface.get("kind")
    if kind == "media-asset":
        return {f"asset::{ident}::native"}
    if kind == "drawing-code":
        return {f"producer::{ident}::source-review", f"producer::{ident}::generated-output-map"}
    return {f"surface::{ident}::{layout}" for layout in LAYOUTS}


def review_fields(obj, where: str, errors: list[str]):
    if not isinstance(obj, dict):
        errors.append(f"{where}: review object missing")
        return False
    for key in ("reviewer", "scope", "evidence"):
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            errors.append(f"{where}: {key} missing")
    try:
        date.fromisoformat(obj.get("date", ""))
    except (TypeError, ValueError):
        errors.append(f"{where}: date missing or malformed")
    return True


def validate(root: Path, inventory_path: Path, audit_path: Path, records_dir: Path):
    errors = []
    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        manifest_planned, scanned_actual = current_inventory(root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"status": "BLOCKED", "errors": [f"input unavailable or malformed: {exc}"], "counts": {}}

    planned = inventory.get("planned_uses", [])
    surfaces = inventory.get("actual_surfaces", [])
    planned_ids = [x.get("id") for x in planned]
    surface_ids = [x.get("id") for x in surfaces]
    if len(planned_ids) != len(set(planned_ids)) or set(planned_ids) != set(manifest_planned):
        errors.append("inventory planned IDs differ from current chapter manifest or contain duplicates")
    for x in planned:
        if x.get("id") in manifest_planned and x.get("path") != manifest_planned[x["id"]]:
            errors.append(f"inventory planned host path differs from current manifest: {x.get('id')}")
    if len(surface_ids) != len(set(surface_ids)) or set(surface_ids) != set(scanned_actual):
        errors.append("inventory actual surface IDs differ from current source scan or contain duplicates; nested/new render uncovered")
    for x in surfaces:
        ident = x.get("id")
        if ident in scanned_actual and x.get("file_sha256") != scanned_actual[ident]:
            errors.append(f"inventory surface file drift: {ident}")
    if audit.get("inventory_sha256") != sha(inventory_path):
        errors.append("audit-plan inventory digest stale")
    if {x.get("id") for x in audit.get("planned_uses", [])} != set(planned_ids) or {x.get("id") for x in audit.get("actual_surfaces", [])} != set(surface_ids):
        errors.append("audit-plan coverage IDs differ from inventory")

    # Every host must be bound to the current bytes; stale source-visible mode
    # extraction otherwise creates a route to miss a new mode.
    hosts = audit.get("runtime_hosts", [])
    actual_host_files = {p.relative_to(root).as_posix() for p in (root / "assets").glob("ch[0-9][0-9]-*.html")}
    if (root / "assets/secretory-traffic-pilot.html").is_file():
        actual_host_files.add("assets/secretory-traffic-pilot.html")
    if {x.get("file") for x in hosts} != actual_host_files:
        errors.append("audit-plan runtime host set differs from current HTML host set")
    for host in hosts:
        f = host.get("file")
        if not isinstance(f, str) or not (root / f).is_file():
            errors.append(f"runtime host missing: {f}")
        elif host.get("file_sha256") != sha(root / f):
            errors.append(f"runtime host digest stale: {f}")
        if isinstance(f, str) and (root / f).is_file():
            source = (root / f).read_text(encoding="utf-8", errors="replace")
            detected_temporal = bool(re.search(r'id=["\'](?:play|seek|phase)["\']|requestAnimationFrame', source, flags=re.I))
            if host.get("temporal") is not detected_temporal:
                errors.append(f"runtime host temporal classification stale: {f}")
            selections = SelectParser()
            selections.feed(source)
            detected_modes = {k: v for k, v in selections.modes.items() if k.lower() not in {"speed", "rate"} and v}
            if host.get("explicit_select_modes") != detected_modes:
                errors.append(f"runtime host source-visible mode list stale: {f}")
            detected_embeds = sorted({x.get("source") for x in surfaces if x.get("tag") == "iframe" and x.get("source") and x.get("source").split("?", 1)[0].lstrip("./") == f})
            if host.get("declared_embed_variants") != detected_embeds:
                errors.append(f"runtime host declared iframe variants stale: {f}")

    records = []
    for path in sorted(records_dir.glob("*.json")) if records_dir.is_dir() else []:
        try:
            records.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except (OSError, ValueError) as exc:
            errors.append(f"record unreadable {path.name}: {exc}")
    if not records:
        errors.append("no visual evidence records")
    covered_planned, covered_actual, covered_runtime = set(), set(), set()
    criterion_counts = {"PASS": 0, "N/A": 0, "PENDING": 0, "FAIL": 0, "INVALID": 0}
    planned_set, actual_set = set(planned_ids), set(surface_ids)
    by_surface = {x.get("id"): x for x in surfaces}
    by_planned = {x.get("id"): x for x in planned}
    rendered_source_text = {}
    for candidate in sorted({root / x.get("file") for x in surfaces if isinstance(x.get("file"), str)}):
        if candidate.suffix.lower() in {".html", ".js", ".css"} and candidate.is_file():
            rendered_source_text[candidate] = candidate.read_text(encoding="utf-8", errors="replace")
    for path, rec in records:
        rid = rec.get("id", path.stem)
        where = f"record {rid}"
        cls = rec.get("visual_class")
        if cls not in {"anatomical", "physiological", "mixed", "quantitative-plot", "static-reference"}:
            errors.append(f"{where}: visual_class missing or unknown")
        flags = rec.get("flags", {})
        if not isinstance(flags, dict) or not all(isinstance(flags.get(k), bool) for k in ("depicts_anatomy", "temporal_claim", "contains_graph")):
            errors.append(f"{where}: explicit anatomy/temporal/graph flags missing")
            flags = {}
        if cls == "quantitative-plot" and flags.get("depicts_anatomy") is not False:
            errors.append(f"{where}: quantitative plot cannot contain anatomy")
        if cls in {"anatomical", "physiological", "mixed", "static-reference"} and flags.get("depicts_anatomy") is not True:
            errors.append(f"{where}: biological visual class cannot declare anatomy absent")
        coverage = rec.get("coverage", {})
        pids = coverage.get("planned_use_ids", []) if isinstance(coverage, dict) else []
        aids = coverage.get("actual_surface_ids", []) if isinstance(coverage, dict) else []
        ruids = coverage.get("runtime_unit_ids", []) if isinstance(coverage, dict) else []
        if not pids and not aids:
            errors.append(f"{where}: at least one planned or actual coverage ID required")
        for ident in pids:
            if ident not in planned_set: errors.append(f"{where}: unknown planned ID {ident}")
            if ident in covered_planned: errors.append(f"{where}: duplicate planned ID {ident}")
            covered_planned.add(ident)
        for ident in aids:
            if ident not in actual_set: errors.append(f"{where}: unknown actual ID {ident}")
            if ident in covered_actual: errors.append(f"{where}: duplicate actual ID {ident}")
            covered_actual.add(ident)
        covered_runtime.update(ruids)

        artifacts = rec.get("artifacts", [])
        artifact_hashes = {}
        if not isinstance(artifacts, list) or not artifacts:
            errors.append(f"{where}: artifact SHA list missing")
        else:
            for i, item in enumerate(artifacts):
                file_proof(root, item, f"{where} artifact[{i}]", errors)
                if isinstance(item, dict): artifact_hashes[item.get("path")] = item.get("sha256")
        for ident in aids:
            surf = by_surface.get(ident)
            if surf and artifact_hashes.get(surf.get("file")) != surf.get("file_sha256"):
                errors.append(f"{where}: actual surface {ident} not bound to current artifact hash")
        for ident in pids:
            planned_use = by_planned.get(ident)
            host = (planned_use or {}).get("path")
            if isinstance(host, str):
                host = host.split("#", 1)[0].split("?", 1)[0]
                if not (root / host).is_file() or artifact_hashes.get(host) != sha(root / host):
                    errors.append(f"{where}: planned use {ident} host file not bound to current artifact hash")
        for ident in ruids:
            parts = ident.split("::")
            if len(parts) != 4 or parts[0] != "runtime":
                errors.append(f"{where}: malformed runtime unit {ident}")
            else:
                host = parts[1]
                if not (root / host).is_file() or artifact_hashes.get(host) != sha(root / host):
                    errors.append(f"{where}: runtime host {host} not bound to current artifact hash")

        links = coverage.get("render_host_links", []) if isinstance(coverage, dict) else []
        linked = {x.get("source_id"): x for x in links if isinstance(x, dict)} if isinstance(links, list) else {}
        for ident in aids:
            surf = by_surface.get(ident)
            if not surf or surf.get("kind") not in {"media-asset", "drawing-code"}:
                continue
            link = linked.get(ident)
            if not isinstance(link, dict):
                errors.append(f"{where}: missing typed render-host association for {ident}")
                continue
            review_fields(link, f"{where} render-link {ident}", errors)
            file_proof(root, link.get("proof"), f"{where} render-link {ident} proof", errors)
            host_ids = link.get("host_surface_ids", [])
            if host_ids:
                for host_id in host_ids:
                    host_surf = by_surface.get(host_id)
                    if not host_surf or host_surf.get("kind") != "display-surface" or host_id not in aids:
                        errors.append(f"{where}: render host {host_id} for {ident} must be a covered display surface")
                    elif artifact_hashes.get(host_surf.get("file")) != host_surf.get("file_sha256"):
                        errors.append(f"{where}: render host {host_id} artifact hash missing")
            elif not isinstance(link.get("unrendered_reason"), str) or not link["unrendered_reason"].strip():
                errors.append(f"{where}: source {ident} needs a rendered host or documented unrendered reason")
            elif any(Path(surf.get("file")).name in text for candidate, text in rendered_source_text.items() if candidate != root / surf.get("file")):
                errors.append(f"{where}: source {ident} appears in rendering source; cannot claim unrendered without host mapping")

        source_proofs = rec.get("source_proofs", [])
        roles = {x.get("role") for x in source_proofs if isinstance(x, dict)} if isinstance(source_proofs, list) else set()
        needed = {"mechanism"}
        if flags.get("depicts_anatomy"):
            needed |= {"anatomy", "appearance"}
        if not needed <= roles:
            errors.append(f"{where}: missing source proof roles: {sorted(needed - roles)}")
        for i, sp in enumerate(source_proofs if isinstance(source_proofs, list) else []):
            file_proof(root, sp, f"{where} source[{i}]", errors)
            for key in ("locator", "identity", "context"):
                if not isinstance(sp.get(key), str) or not sp[key].strip():
                    errors.append(f"{where} source[{i}]: {key} missing")

        criteria = rec.get("criteria", {})
        if not isinstance(criteria, dict) or set(criteria) != set(CRITERIA):
            errors.append(f"{where}: criterion set must contain exactly V01-V20")
        for key in CRITERIA:
            item = criteria.get(key, {}) if isinstance(criteria, dict) else {}
            status = item.get("status") if isinstance(item, dict) else None
            if status not in criterion_counts:
                criterion_counts["INVALID"] += 1
            else:
                criterion_counts[status] += 1
            if status == "PENDING":
                # A real review may be recorded incrementally. Pending cannot
                # release, but must not require invented reviewer/proof fields.
                errors.append(f"{where} {key}: PENDING blocks release")
                if isinstance(item.get("proofs"), list):
                    for i, proof in enumerate(item["proofs"]):
                        file_proof(root, proof, f"{where} {key} proof[{i}]", errors)
                if "artifact_hashes" in item and item["artifact_hashes"] != artifact_hashes:
                    errors.append(f"{where} {key}: pending artifact binding stale")
                continue
            if not review_fields(item, f"{where} {key}", errors):
                continue
            if status == "N/A":
                allowed = ((key == "V05" and cls == "quantitative-plot" and flags.get("depicts_anatomy") is False)
                           or (key in {"V08", "V09"} and flags.get("temporal_claim") is False and cls == "static-reference")
                           or (key == "V13" and flags.get("contains_graph") is False))
                if not allowed: errors.append(f"{where} {key}: N/A not permitted")
            elif status != "PASS":
                errors.append(f"{where} {key}: status {status!r} blocks release")
            proofs = item.get("proofs", [])
            if not isinstance(proofs, list) or not proofs:
                errors.append(f"{where} {key}: exact proof missing")
            else:
                for i, proof in enumerate(proofs): file_proof(root, proof, f"{where} {key} proof[{i}]", errors)
            if item.get("artifact_hashes") != artifact_hashes:
                errors.append(f"{where} {key}: review not bound to exact artifact hashes")

        passes = rec.get("critical_reviews", [])
        if not isinstance(passes, list) or {x.get("role") for x in passes if isinstance(x, dict)} != {"anatomy-mechanism", "appearance-teaching"}:
            errors.append(f"{where}: distinct anatomy/mechanism and appearance/teaching passes required")
        else:
            if len(passes) != 2 or passes[0].get("pass_id") == passes[1].get("pass_id"):
                errors.append(f"{where}: critical review passes must be distinct")
            reviewer_ids = [x.get("reviewer_id") for x in passes]
            if not all(isinstance(x, str) and x.strip() for x in reviewer_ids) or len(set(reviewer_ids)) != 2:
                errors.append(f"{where}: critical reviews need two distinct reviewer IDs")
            for i, item in enumerate(passes):
                review_fields(item, f"{where} critical[{i}]", errors)
                if item.get("artifact_hashes") != artifact_hashes:
                    errors.append(f"{where} critical[{i}]: stale artifact binding")
                file_proof(root, item.get("proof"), f"{where} critical[{i}] proof", errors)

        units = rec.get("review_units", [])
        unit_ids = {x.get("id") for x in units if isinstance(x, dict)} if isinstance(units, list) else set()
        required_units = set().union(*(review_units_for_surface(by_surface[ident]) for ident in aids if ident in by_surface))
        required_units |= set(ruids)
        for ident in sorted(required_units - unit_ids): errors.append(f"{where}: unreviewed unit {ident}")
        for i, unit in enumerate(units if isinstance(units, list) else []):
            review_fields(unit, f"{where} unit[{i}]", errors)
            if unit.get("artifact_hashes") != artifact_hashes:
                errors.append(f"{where} unit[{i}]: stale artifact binding")
            file_proof(root, unit.get("proof"), f"{where} unit[{i}] proof", errors)

    for ident in sorted(planned_set - covered_planned): errors.append(f"planned use uncovered: {ident}")
    for ident in sorted(actual_set - covered_actual): errors.append(f"actual surface uncovered: {ident}")

    # Source-visible host modes and all three temporal phase samples are required.
    required_runtime = set()
    for host in hosts:
        file = host.get("file")
        modes = {"default"}
        for options in host.get("explicit_select_modes", {}).values():
            modes.update(str(x.get("value") or x.get("label")) for x in options)
        modes.update(host.get("declared_embed_variants", []))
        phases = ("start", "middle", "end", "static", "print") if host.get("temporal") else ("static", "print")
        for mode in modes:
            required_runtime.update(f"runtime::{file}::{mode}::{phase}" for phase in phases)
    for ident in sorted(required_runtime - covered_runtime): errors.append(f"runtime mode/phase uncovered: {ident}")
    return {"status": "PASS" if not errors else "BLOCKED", "errors": errors,
            "counts": {"planned": len(planned_set), "actual": len(actual_set), "records": len(records), "required_runtime_units": len(required_runtime), "criterion_statuses": criterion_counts, "errors": len(errors)}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--audit-plan", type=Path)
    parser.add_argument("--records", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    result = validate(root, args.inventory or root / "validation/visuals/inventory.json", args.audit_plan or root / "validation/visuals/audit-plan.json", args.records or root / "validation/visuals/records")
    output = {"status": result["status"], "counts": result["counts"],
              "error_samples": result["errors"][:20], "more_errors": max(0, len(result["errors"]) - 20)}
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
