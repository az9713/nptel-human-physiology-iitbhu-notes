"""Portable acceptance records; hash bindings are not scientific certification."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
import re

SCHEMA = 'physiology-acceptance-v1'
LIMITS = ('AI scientific/editorial review records, not human expert certification. '
          'Hashes bind the producer attestation to this snapshot; they do not '
          'prove scientific truth, actual viewing or reviewer independence.')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_path(root, name, *, base=None, required=True):
    """Reject links (including Windows junctions) before resolving or writing."""
    if (not isinstance(name, str) or not name or '\\' in name
            or Path(name).is_absolute() or re.match(r'^[a-zA-Z]:', name)
            or '..' in Path(name).parts):
        raise ValueError('invalid evidence path')
    root = root.resolve()
    path = root / name
    for item in (path, *path.parents):
        if item == root:
            break
        if item.is_symlink() or getattr(item, 'is_junction', lambda: False)():
            raise ValueError('linked evidence path is forbidden')
    boundary = root / base if base else root
    if (not path.resolve().is_relative_to(boundary.resolve())
            or (required and not path.is_file())):
        raise ValueError('missing or out-of-scope evidence path')
    return path


def private_proof(root, name, expected, *, base='work'):
    if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
        raise ValueError('actual private proof SHA-256 required')
    path = checked_path(root, name, base=base)
    if digest(path) != expected:
        raise ValueError('stale actual private proof')
    return path


def atomic_writes(root, files):
    """Preflight every destination before touching either existing output."""
    paths = {name: checked_path(root, name, required=False) for name in files}
    staged = {}
    try:
        for name, path in paths.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            checked_path(root, name, required=False)
            fd, temporary = tempfile.mkstemp(prefix='.acceptance-', dir=path.parent)
            staged[name] = Path(temporary)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(files[name])
        for name in paths:
            checked_path(root, name, required=False)
        for name, path in paths.items():
            checked_path(root, name, required=False)
            os.replace(staged[name], path)
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


def check_review_shape(review):
    if not isinstance(review, dict):
        raise ValueError('review record must be an object')
    if 'targeted_reviewer_id' in review:
        if (not isinstance(review['targeted_reviewer_id'], str)
                or not review['targeted_reviewer_id'].strip()
                or (review.get('targeted_checker_is_separate') is True
                    and review['targeted_reviewer_id'] == review.get('reviewer_id'))):
            raise ValueError('invalid separate targeted checker identity')
    for value in review.values():
        if isinstance(value, dict) and 'reviewer_id' in value:
            if (not isinstance(value['reviewer_id'], str) or not value['reviewer_id'].strip()
                    or not isinstance(value.get('scope'), str) or not value['scope'].strip()
                    or not isinstance(value.get('report_sha256'), str)
                    or not re.fullmatch(r'[0-9a-f]{64}', value['report_sha256'])):
                raise ValueError('invalid separately attributed checker record')


def validate_review_proofs(root, review, aggregate):
    check_review_shape(review)
    text = aggregate.read_text(encoding='utf-8')
    # Older aggregates embed the exact original/target text, binding those
    # named files without falsely assigning the latest snapshot to each one.
    for key in ('original_full_report', 'targeted_report'):
        if key in review:
            proof = checked_path(root, review[key], base='work/reviews')
            content = proof.read_text(encoding='utf-8').strip()
            if not content or content not in text:
                raise ValueError('named historical review not bound by aggregate')
    if 'targeted_reviewer_id' in review and not review.get('targeted_report'):
        raise ValueError('separate targeted checker needs its named proof')
    for value in review.values():
        if isinstance(value, dict) and ('report_path' in value or 'reviewer_id' in value):
            proof = private_proof(root, value.get('report_path'), value.get('report_sha256'),
                                  base='work/reviews')
            content = proof.read_text(encoding='utf-8')
            declared = value.get('body_sha256')
            if declared is not None and (not isinstance(declared, str)
                    or not re.fullmatch(r'[0-9a-f]{64}', declared) or declared not in content):
                raise ValueError('historical checker snapshot mismatch')


def validate_production(root, chapter, meta, body, artifacts):
    info = meta.get('production_validation', {})
    if not isinstance(info.get('scope'), str) or not info['scope'].strip():
        raise ValueError('actual production inspection scope required')
    proof = private_proof(root, info.get('report_path'), info.get('report_sha256'))
    report = json.loads(proof.read_text(encoding='utf-8'))
    if not isinstance(report, dict):
        raise ValueError('production report must be an object')
    if 'chapters' in report and not isinstance(report['chapters'], dict):
        raise ValueError('production chapter mapping must be an object')
    selected = report.get('chapters', {}).get(str(chapter['number'])) if 'chapters' in report else report
    if not isinstance(selected, dict):
        raise ValueError('production report does not cover this chapter')
    number = selected.get('chapter', chapter['number'] if 'chapters' in report else None)
    if (number != chapter['number']
            or selected.get('body_sha256', selected.get('final_body_sha256')) != body
            or selected.get('artifact_sha256') != artifacts):
        raise ValueError('production report must bind chapter, current body and artifact map')
    if report.get('schema') == 'physiology-production-bridge-v1':
        # A new bounded inspection records its own scope and limits. The old
        # report is retained as historical evidence, never relabelled current.
        for key in ('prior_production', 'artifact_identity', 'current_reader_inspection'):
            item = report.get(key, {})
            if (not isinstance(item, dict) or not isinstance(item.get('scope'), str)
                    or not item['scope'].strip() or not isinstance(item.get('limits'), str)
                    or not item['limits'].strip()):
                raise ValueError('scoped production bridge evidence and limits required')
            bound = private_proof(root, item.get('report_path'), item.get('report_sha256'))
            if key != 'prior_production':
                content = bound.read_text(encoding='utf-8')
                if not all(value in content for value in (body, *artifacts.values())):
                    raise ValueError('bridge current verification must bind this snapshot')


def modality(gate):
    """Retain the declared modality and evidence, without private report paths."""
    keys = ('status', 'mode', 'scene_family', 'rationale', 'appearance_references',
            'mechanism_files', 'no_anatomical_appearance_claim',
            'representative_still', 'motion_preview', 'source_files',
            'report_sha256')
    return {key: gate[key] for key in keys if key in gate}


def safe_record(record):
    raw = json.dumps(record, ensure_ascii=False)
    if re.search(r'(?i)((?<![a-z0-9])[a-z]:[\\/]|file://|bearer\s|[?&]token=)', raw):
        raise ValueError('local path or credential-shaped value in public record')
    def inspect(value, key=''):
        if isinstance(value, dict):
            for name, item in value.items():
                inspect(item, name)
        elif isinstance(value, list):
            for item in value:
                inspect(item, key)
        elif isinstance(value, str) and key not in ('reviewer_id', 'targeted_reviewer_id'):
            if re.search(r'(?i)(?<![a-z0-9])(?:(?:work|sources|research|spec|plan)/|/(?:home|Users|tmp|private|mnt|Volumes)/)', value):
                raise ValueError('private filesystem path in public record')
    inspect(record)


def review_record(original):
    check_review_shape(original)
    keys = ('reviewer_id', 'reviewer_model', 'reasoning_effort', 'independent',
            'full_scientific_review', 'verdict', 'blocking_findings',
            'report_sha256', 'review_basis', 'targeted_reviewer_id',
            'targeted_reviewer_model', 'targeted_checker_is_separate',
            'original_full_review_body_sha256')
    result = {key: original[key] for key in keys if key in original}
    checks = {}
    for key, value in original.items():
        if isinstance(value, dict) and 'reviewer_id' in value:
            checks[key] = {k: value[k] for k in
                           ('reviewer_id', 'reviewer_model', 'reasoning_effort',
                            'scope', 'report_sha256') if k in value}
    if checks:
        result['separately_attributed_checks'] = checks
    return result


def source_evidence(root, chapter):
    rows = json.loads((root / 'source-manifest.json').read_text(encoding='utf-8'))['recordings']
    result = []
    for number in chapter['recordings']:
        matches = [row for row in rows if row['number'] == number]
        if len(matches) != 1:
            raise ValueError('unique source recording required')
        row = matches[0]
        audit = row.get('bounded_visual_audit', {})
        if (row.get('caption_status') != 'acquired'
                or not re.fullmatch(r'[0-9a-f]{64}', row.get('caption_sha256', ''))
                or audit.get('status') != 'complete for stated still-sampling task'
                or audit.get('continuous_video_review') is not False
                or any(type(audit.get(k)) is not int or audit[k] <= 0
                       for k in ('contact_sheets', 'sampled_stills'))
                or type(audit.get('native_still_views')) is not int
                or audit['native_still_views'] < 0
                or not re.fullmatch(r'[0-9a-f]{64}', audit.get('report_sha256', ''))
                or not row.get('visual_review_scope')):
            raise ValueError('acquired captions and completed bounded source audit required')
        keys = ('number', 'video_id', 'url', 'caption_status', 'caption_type',
                'caption_sha256', 'caption_cues', 'visual_coverage',
                'sampled_frame_count', 'bounded_visual_audit', 'visual_review_scope')
        projected = {key: row[key] for key in keys if key in row}
        audit_keys = ('status', 'continuous_video_review', 'contact_sheets',
                      'sampled_stills', 'native_still_views', 'report_sha256')
        projected['bounded_visual_audit'] = {key: audit[key] for key in audit_keys}
        result.append(projected)
    return result


def validate_attestation(root, chapter, meta, body, artifacts):
    binding = meta.get('public_acceptance', {})
    name = binding.get('path')
    expected = f'validation/acceptance/chapter-{chapter["number"]:02d}.json'
    if name != expected:
        raise ValueError('missing canonical public acceptance record')
    path = checked_path(root, name)
    if (not path.is_file() or path.is_symlink()
            or any(p.is_symlink() for p in path.parents
                   if p.is_relative_to(root))
            or not path.resolve().is_relative_to(root.resolve())
            or digest(path) != binding.get('sha256')):
        raise ValueError('missing or stale public acceptance record')
    record = json.loads(path.read_text(encoding='utf-8'))
    safe_record(record)
    if (record.get('schema') != SCHEMA
            or record.get('chapter') != chapter['number']
            or record.get('manuscript') != chapter['file']
            or record.get('body_sha256') != body
            or record.get('artifact_sha256') != artifacts
            or record.get('coverage_complete') is not True
            or record.get('limits') != LIMITS):
        raise ValueError('public acceptance snapshot or evidence limits mismatch')
    if (record.get('coverage_basis') != meta.get('coverage_basis')
            or record.get('source_recordings') != chapter['recordings']
            or record.get('source_evidence') != source_evidence(root, chapter)):
        raise ValueError('public source-coverage attestation mismatch')
    reviews = record.get('reviews', [])
    if (not isinstance(reviews, list) or any(not isinstance(r, dict) for r in reviews)
            or len(reviews) != 2
            or len({r.get('reviewer_id') for r in reviews}) != 2
            or len({r.get('report_sha256') for r in reviews}) != 2):
        raise ValueError('two distinct actual full-review identities required')
    actual = meta.get('reviews', [])
    if len(actual) != 2:
        raise ValueError('two producer full-review records required')
    for review, original in zip(reviews, actual):
        if review != review_record(original):
            raise ValueError('public full-review attribution mismatch')
        if (not isinstance(review.get('reviewer_id'), str)
                or not review['reviewer_id'].strip()
                or review.get('independent') is not True
                or review.get('full_scientific_review') is not True
                or review.get('verdict') != 'yes'
                or type(review.get('blocking_findings')) is not int
                or review['blocking_findings'] != 0
                or not re.fullmatch(r'[0-9a-f]{64}', review.get('report_sha256', ''))
                or original.get('body_sha256') != body
                or original.get('artifact_sha256') != artifacts):
            raise ValueError('current public full-review approval required')
    production = record.get('production', {})
    original = meta.get('production_validation', {})
    if (not production.get('scope')
            or production.get('scope') != original.get('scope')
            or production.get('report_sha256') != original.get('report_sha256')
            or not re.fullmatch(r'[0-9a-f]{64}', production.get('report_sha256', ''))):
        raise ValueError('public production evidence mismatch')
    if record.get('visual_modality') != modality(meta.get('realistic_asset_gate', {})):
        raise ValueError('public visual-modality evidence mismatch')
    return record
