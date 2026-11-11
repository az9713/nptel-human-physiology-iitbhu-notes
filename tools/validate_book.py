"""Check offline reader integrity; --release also requires complete evidence.

Development success explicitly permits pending work, never acceptance. Acceptance
uses a .meta.json sidecar: current body_sha256, coverage_complete, reviewed_artifacts
(paths or {path, sha256} objects), and two distinct, independently attested full
reviews with current body/artifact digests and local hash-matching reports.
This validates evidence bindings, not scientific truth or reviewer independence.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from build_book import ROOT, PAGES, chapter_path, load
from public_acceptance import checked_path, private_proof, validate_review_proofs, validate_production

SHA = re.compile(r'[0-9a-f]{64}')
PRIVATE = {'sources', 'work', 'research', 'spec', 'plan', '.git', '.serena'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_file(name):
    if not isinstance(name, str) or '\\' in name:
        raise ValueError('invalid public artifact path')
    target = checked_path(ROOT, name)
    if {part.casefold() for part in Path(name).parts} & PRIVATE:
        raise ValueError(f'private public artifact: {name}')
    return target


def reader_link(source, name):
    """Resolve ordinary relative reader links without relaxing evidence paths."""
    if (not isinstance(name, str) or '\\' in name or Path(name).is_absolute()
            or re.match(r'^[a-zA-Z]:', name)):
        raise ValueError('invalid reader link')
    parts = list(source.parent.relative_to(ROOT).parts)
    for part in Path(name).parts:
        if part == '..':
            if not parts:
                raise ValueError('reader link escapes project')
            parts.pop()
        elif part != '.':
            if part.casefold() in PRIVATE:
                raise ValueError('private reader link')
            parts.append(part)
        candidate = ROOT.joinpath(*parts)
        if candidate.is_symlink() or getattr(candidate, 'is_junction', lambda: False)():
            raise ValueError('linked reader path is forbidden')
    return public_file('/'.join(parts))



class Page(HTMLParser):
    def __init__(self, path=None, *, text=None):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.duplicate_attributes = [], [], []
        self.feed(text if text is not None else path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        self.duplicate_attributes.extend(name for name, count in
                                         Counter(name for name, _ in attrs).items()
                                         if count > 1)
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for attribute in ('href', 'src', 'poster', 'data'):
            if attribute in attrs:
                self.links.append((attrs[attribute], attribute != 'href' or tag == 'link'))
        if 'srcset' in attrs:
            self.links.extend((entry.strip().split()[0], True) for entry in attrs['srcset'].split(',') if entry.strip())


def asset_file(name):
    """Resolve a public scientific asset, including a checked HTML/SVG fragment."""
    if not isinstance(name, str):
        raise ValueError("asset path must be a string")
    url = urlsplit(name)
    if url.scheme or url.netloc or url.query:
        raise ValueError("asset must be a local file with an optional fragment")
    filename, fragment = unquote(url.path), unquote(url.fragment)
    target = public_file(filename)
    if fragment and (target.suffix.lower() not in (".html", ".svg")
                     or fragment not in Page(target).ids):
        raise ValueError("scientific asset fragment is missing")
    return filename, target, fragment


def realistic_asset_evidence(c, meta, artifacts, public=False):
    """Bind the chosen visual modality; new rendered styles need a pilot.

    Observed microscopy can supply anatomical appearance while an explicitly
    schematic animation explains mechanism. This is not a per-chapter 3D quota.
    Evidence bindings cannot themselves judge scientific or visual quality.
    """
    if not 9 <= c['number'] <= 25:
        return
    gate = meta.get('realistic_asset_gate', {})
    if gate.get('status') != 'accepted':
        raise ValueError('chapter visual modality and production inspection pending')
    if not isinstance(gate.get('scene_family'), str) or not gate['scene_family'].strip():
        raise ValueError('visual scene family or subject required')
    mode = gate.get('mode', 'rendered-scene')
    if mode in ('observed-reference-plus-schematic', 'conceptual-quantitative'):
        required = gate.get('mechanism_files', [])
        if (not isinstance(required, list) or not required
                or not isinstance(gate.get('rationale'), str)
                or not gate['rationale'].strip()):
            raise ValueError('reviewed mechanisms and modality rationale required')
        if mode == 'observed-reference-plus-schematic':
            references = gate.get('appearance_references', [])
            if (not isinstance(references, list) or not references
                    or any(not isinstance(name, str) or Path(name).suffix.lower()
                           not in ('.png', '.jpg', '.jpeg', '.webp', '.mp4', '.webm')
                           for name in references)):
                raise ValueError('directly relevant observed appearance reference required')
            required = [*required, *references]
        elif gate.get('no_anatomical_appearance_claim') is not True:
            raise ValueError('conceptual exception must explicitly exclude anatomical appearance claims')
    elif mode == 'rendered-scene':
        required = [gate.get('representative_still'), gate.get('motion_preview')]
        sources = gate.get('source_files', [])
        if not isinstance(sources, list) or not sources:
            raise ValueError('editable rendered scene sources required')
        if (any(not isinstance(name, str) for name in required)
                or Path(required[0]).suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp')
                or Path(required[1]).suffix.lower() not in
                ('.mp4', '.webm', '.gif', '.html', '.glb', '.gltf')
                or required[0] == required[1]):
            raise ValueError('distinct realistic still and playable motion artifacts required')
        required = [*required, *sources]
    else:
        raise ValueError('unknown visual production modality')
    if any(not isinstance(name, str) or name not in artifacts for name in required):
        raise ValueError('visual modality evidence must name reviewed artifacts')
    if public:
        # The portable record must independently match this exact gate below.
        # Public validation never pretends to have read private inspection files.
        return
    report_name = gate.get('report_path', '')
    if not isinstance(report_name, str):
        raise ValueError('realistic inspection report path required')
    report = private_proof(ROOT, report_name, gate.get('report_sha256'))
    text = report.read_text(encoding='utf-8')
    if not all(artifacts[name] in text for name in required):
        raise ValueError('visual inspection must bind the delivered reference, mechanisms or rendered sources')


def accepted_evidence(c, public=False):
    if c.get('status') != 'accepted':
        raise ValueError('canonical manifest chapter is not accepted')
    path = chapter_path(c)
    meta_path = checked_path(ROOT, path.with_suffix('.meta.json').name)
    if not path.is_file() or not meta_path.is_file():
        raise ValueError('missing manuscript or review sidecar')
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    if meta.get('status') != 'accepted' or meta.get('coverage_complete') is not True:
        raise ValueError('accepted sidecar and complete source coverage required')
    raw = path.read_bytes()
    begin, end = b'<!-- BEGIN CHAPTER BODY -->', b'<!-- END CHAPTER BODY -->'
    if raw.count(begin) != 1 or raw.count(end) != 1 or raw.index(begin) >= raw.index(end):
        raise ValueError('one ordered pair of manuscript body markers required')
    body_bytes = raw.split(begin)[1].split(end)[0]
    body = hashlib.sha256(body_bytes).hexdigest()
    body_ids = set(Page(text=body_bytes.decode('utf-8')).ids)
    if meta.get('body_sha256') != body:
        raise ValueError('stale manuscript body digest')
    artifacts = {}
    for item in meta.get('reviewed_artifacts', []):
        name = item if isinstance(item, str) else item['path']
        if name in artifacts:
            raise ValueError('duplicate reviewed artifact')
        artifacts[name] = digest(public_file(name))
        if isinstance(item, dict) and item.get('sha256') != artifacts[name]:
            raise ValueError('stale reviewed artifact digest')
    for kind in ('animations', 'illustrations'):
        if not c.get(kind):
            raise ValueError(f'missing planned {kind}')
        for asset in c[kind]:
            if asset.get('status') not in ('accepted', 'validated'):
                raise ValueError(f'{kind} still incomplete')
            name, target, fragment = asset_file(asset.get('path') or asset.get('file'))
            if target == path:
                if not fragment or fragment not in body_ids:
                    raise ValueError('inline scientific asset must be inside the reviewed body')
            elif name not in artifacts:
                raise ValueError(f'{kind} must name its reviewed artifact path')
    lab = c.get('lab', {})
    if lab.get('status') not in ('accepted', 'validated') or (lab.get('path') or lab.get('file')) not in artifacts:
        raise ValueError('lab must be validated and bound to a reviewed artifact')
    if not artifacts:
        raise ValueError('reviewed scientific assets required')
    realistic_asset_evidence(c, meta, artifacts, public=public)
    if public:
        from public_acceptance import validate_attestation
        validate_attestation(ROOT, c, meta, body, artifacts)
        return
    validate_production(ROOT, c, meta, body, artifacts)
    if not isinstance(meta.get('reviews'), list) or len(meta['reviews']) != 2:
        raise ValueError('exactly two original full-review records required')
    identities, reports = set(), set()
    for review in meta.get('reviews', []):
        current = review.get('body_sha256') == body and review.get('artifact_sha256') == artifacts
        if current and review.get('blocking_findings', 0):
            raise ValueError('current review has blocking findings')
        if not (current and review.get('independent') is True
                and review.get('full_scientific_review') is True
                and review.get('verdict') == 'yes'
                and type(review.get('blocking_findings')) is int
                and review['blocking_findings'] == 0):
            continue
        reviewer = review.get('reviewer_id')
        report_sha = review.get('report_sha256', '')
        report_name = review.get('report_path', '')
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError('actual reviewer identity required')
        report = private_proof(ROOT, report_name, report_sha, base='work/reviews')
        validate_review_proofs(ROOT, review, report)
        text = report.read_text(encoding='utf-8')
        if not all(value in text for value in (body, *artifacts.values())):
            continue
        if reviewer not in identities and report_sha not in reports:
            identities.add(reviewer)
            reports.add(report_sha)
    if len(identities) < 2:
        raise ValueError('two distinct independent full approvals bound to current body, assets and reports required')


def validate(release=False, public=False):
    manifest, sources = load('chapter-manifest.json'), load('source-manifest.json')
    chapters, records = manifest['chapters'], sources['recordings']
    errors, pending = [], []
    source_numbers = [r['number'] for r in records]
    assigned = [n for c in chapters for n in c['recordings']]
    for label, numbers in [('source inventory', source_numbers), ('chapter mapping', assigned)]:
        if Counter(numbers) != Counter(range(1, 61)):
            errors.append(f'{label}: official lectures 1–60 must occur exactly once')
    if len({c['number'] for c in chapters}) != len(chapters) or len({c['file'] for c in chapters}) != len(chapters):
        errors.append('chapter numbers and filenames must be unique')
    for r in records:
        if r.get('caption_status') != 'acquired' or not SHA.fullmatch(r.get('caption_sha256', '')):
            errors.append(f'Lecture {r["number"]}: missing acquired-caption SHA-256 metadata')
        if type(r.get('caption_cues')) is not int or r['caption_cues'] <= 0:
            errors.append(f'Lecture {r["number"]}: missing positive caption cue count')
        audit = r.get('bounded_visual_audit', {})
        bounded = (
            audit.get('status') == 'complete for stated still-sampling task'
            and audit.get('continuous_video_review') is False
            and all(type(audit.get(key)) is int and audit[key] > 0
                    for key in ('contact_sheets', 'sampled_stills'))
            and type(audit.get('native_still_views')) is int
            and audit['native_still_views'] >= 0
            and isinstance(audit.get('report_sha256'), str)
            and SHA.fullmatch(audit['report_sha256'])
            and isinstance(r.get('visual_review_scope'), str)
            and bool(r['visual_review_scope'].strip())
        )
        if not bounded and r.get('visual_coverage') not in ('complete', 'verified', 'reviewed'):
            pending.append(f'Lecture {r["number"]}: bounded visual audit pending; '
                           f'visual coverage {r.get("visual_coverage", "missing")}')
    missing = sorted(r['number'] for r in records if not r.get('in_supplied_playlist'))
    if sources.get('discrepancies', {}).get('official_lectures_absent_from_supplied_playlist') != missing:
        errors.append('playlist absence discrepancy does not match source rows')
    paths = [ROOT / name for name in PAGES]
    # Standalone visual panels have their own local links and resources.
    paths.extend(sorted((ROOT / 'assets').glob('*.html')))
    paths.extend(sorted((ROOT / 'assets').glob('*.svg')))
    for c in chapters:
        path = chapter_path(c)
        status = c.get('status')
        exists = path.is_file()
        if status not in ('planned', 'draft', 'in-review', 'review', 'revised', 'accepted'):
            errors.append(f'Chapter {c["number"]}: unknown status {status}')
        if exists:
            paths.append(path)
        if (status == 'planned' and exists) or (status != 'planned' and not exists):
            errors.append(f'Chapter {c["number"]}: status {status} conflicts with manuscript existence')
        sidecar = path.with_suffix('.meta.json')
        if sidecar.exists() and load(sidecar.name).get('status') != status:
            errors.append(f'Chapter {c["number"]}: sidecar status differs from manifest')
        if status == 'accepted':
            try:
                accepted_evidence(c, public=public)
            except (ValueError, KeyError, TypeError, OSError) as error:
                errors.append(f'Chapter {c["number"]}: invalid acceptance: {error}')
        else:
            pending.append(f'Chapter {c["number"]}: {status}; manuscript {"present" if exists else "absent"}; review acceptance pending')
        for kind in ('animations', 'illustrations'):
            for asset in c.get(kind, []):
                if asset.get('status') not in ('accepted', 'validated'):
                    pending.append(f'Chapter {c["number"]}: {asset.get("id", kind)} {asset.get("status", "missing status")}')
                elif not (asset.get('path') or asset.get('file')):
                    errors.append(f'Chapter {c["number"]}: completed {kind} has no artifact path')
                else:
                    asset_file(asset.get('path') or asset.get('file'))
        if c.get('lab', {}).get('status') not in ('accepted', 'validated'):
            pending.append(f'Chapter {c["number"]}: lab pending')
    cache = {}
    def page_for(path):
        if path not in cache:
            cache[path] = Page(path)
        return cache[path]
    for path in paths:
        if not path.is_file():
            errors.append(f'Missing reader page: {path.name}')
            continue
        page = page_for(path)
        if page.duplicate_attributes:
            errors.append(f'{path.name}: duplicate HTML attributes {sorted(set(page.duplicate_attributes))}')
        if any(count > 1 for count in Counter(page.ids).values()):
            errors.append(f'{path.name}: duplicate HTML ids')
        for link, resource in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                if url.scheme not in ('https', 'http', 'mailto', 'tel', 'data'):
                    errors.append(f'{path.name}: unsupported URL scheme {link}')
                if resource and url.scheme != 'data':
                    errors.append(f'{path.name}: network-dependent embedded resource {link}')
                continue
            try:
                target = reader_link(path, unquote(url.path)) if url.path else path
                if url.fragment and target.suffix.lower() in ('.html', '.svg'):
                    if unquote(url.fragment) not in page_for(target).ids:
                        errors.append(f'{path.name}: missing local anchor {link}')
            except (ValueError, OSError) as error:
                errors.append(f'{path.name}: broken or private link {link}: {error}')
    # Visual v2 acceptance is an additional gate, not an inference from the
    # historical chapter reviews, functioning controls, or an old attestation.
    visual_revision = load('completion.json').get('visual_revision', {})
    if release and visual_revision.get('version') == 2:
        if public:
            errors.append('Release blocked: version-2 visual acceptance must be exported after all rubric checks pass')
        else:
            try:
                from verify_visual_rubric import validate as validate_visual_rubric
                visual_result = validate_visual_rubric(
                    ROOT, ROOT/'validation/visuals/inventory.json',
                    ROOT/'validation/visuals/audit-plan.json',
                    ROOT/'validation/visuals/records')
                if visual_result['status'] != 'PASS':
                    errors.append('Release blocked by visual V01-V20 rubric: '
                                  + str(len(visual_result['errors'])) + ' missing, pending or stale checks')
            except (ImportError, OSError, ValueError, KeyError, TypeError) as error:
                errors.append(f'Release blocked: visual rubric evidence unavailable: {error}')
    if release and pending:
        errors.append('Release blocked: incomplete chapters, visual coverage or assets remain')
    return errors, pending


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', action='store_true')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--public', action='store_true',
                      help='Check portable attestations; do not read private reports')
    mode.add_argument('--producer', action='store_true',
                      help='Require actual private producer reports (default)')
    args = parser.parse_args()
    try:
        errors, pending = validate(args.release, public=args.public)
    except (ValueError, KeyError, TypeError, OSError) as error:
        errors, pending = [f'Invalid project data: {error}'], []
    for error in errors:
        print('ERROR:', error)
    for item in pending:
        print('PENDING:', item)
    print(f'{"FAIL" if errors else "PASS"}: {"release" if args.release else "development integrity only"}; {len(errors)} errors; {len(pending)} pending items. Scientific acceptance is not inferred.')
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
