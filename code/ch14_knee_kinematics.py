"""Decode acquired Open Knee(s) oks003 rigid logs, without running FEBio.

Run: python -X utf8 code/ch14_knee_kinematics.py
Writes PRIVATE records only under work/ch14-knee-kinematics/. Standard library.
The model time coordinate is a quasi-static load parameter, not seconds of gait.
Only physical rigid bones are exported; no soft-tissue deformation is inferred.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'work/ch14-knee-motion'
OUTPUT = ROOT / 'work/ch14-knee-kinematics'
BONES = {1: 'PTB', 2: 'FBB', 3: 'TBB', 4: 'FMB'}
DATA_COLUMNS = {'center_of_mass': 3, 'rotation_quaternion': 4,
                'Reaction_Forces': 3, 'Reaction_Torques': 3,
                'Rigid_Connector_Force': 3, 'Rigid_Connector_Moment': 3}
QUAT_NORM_TOL = 2e-6  # Conservative tolerance for approximately six-digit logs.
BLOCK = re.compile(r'Data Record #(\d+)\s*\n=+\s*\n'
                   r'Step = (\d+)\s*\nTime = ([^\n]+)\n'
                   r'Data = ([^\n]+)\n((?:\d+ [^\n]+\n)+)')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite(values):
    values = tuple(float(v) for v in values)
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Nonfinite numerical input')
    return values


def safe_xml(raw):
    if re.search(br'<!\s*(DOCTYPE|ENTITY)\b', raw, re.I):
        raise ValueError('DTD/entity declarations are forbidden')
    return ET.fromstring(raw)


def vector(text):
    values = finite(text.split(','))
    if len(values) != 3:
        raise ValueError('Expected a three-vector')
    return values


def norm(v):
    return math.sqrt(sum(x*x for x in v))


def distance(a, b):
    return norm([x-y for x, y in zip(a, b)])


def rotation(q):
    """Active reference-to-current rotation, column vectors; q=(x,y,z,w).

    Reject nonunit input beyond documented log rounding, then normalize it.
    Matrix rows follow FEBio's quatd::RotationMatrix, not Euler-angle recipes.
    """
    if len(q) != 4:
        raise ValueError('Expected quaternion x,y,z,w')
    q = finite(q)
    size = norm(q)
    if abs(size-1) > QUAT_NORM_TOL:
        raise ValueError('Quaternion outside printed-unit precision')
    x, y, z, w = (v/size for v in q)
    return ((1-2*(y*y+z*z), 2*(x*y-w*z), 2*(x*z+w*y)),
            (2*(x*y+w*z), 1-2*(x*x+z*z), 2*(y*z-w*x)),
            (2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x*x+y*y)))


def matvec(matrix, v):
    return tuple(sum(a*b for a, b in zip(row, v)) for row in matrix)


def transform(point, initial_center, current_center, q):
    """x(t)=c(t)+R(q(t)) @ (x0-c0), in the native model reference frame."""
    if any(len(v) != 3 for v in (point, initial_center, current_center)):
        raise ValueError('Expected three-dimensional point and centers')
    local = tuple(a-b for a, b in zip(finite(point), finite(initial_center)))
    return tuple(a+b for a, b in zip(finite(current_center),
                                   matvec(rotation(q), local)))


def parse_log(text):
    """Strictly collect every requested data block; reject partial/duplicates."""
    matches = list(BLOCK.finditer(text))
    if len(matches) != text.count('Data Record #'):
        raise ValueError('Incomplete or malformed log record')
    frames = {}
    for match in matches:
        _, step, timestamp, name, rows = match.groups()
        step, timestamp = int(step), finite([timestamp])[0]
        if name not in DATA_COLUMNS:
            raise ValueError('Unexpected log data name: '+name)
        values = {}
        for row in rows.splitlines():
            fields = row.split()
            body = int(fields[0])
            numbers = finite(fields[1:])
            if body in values or len(numbers) != DATA_COLUMNS[name]:
                raise ValueError('Duplicate body or wrong log column count')
            values[body] = numbers
        frame = frames.setdefault(step, {'time': timestamp, 'data': {}})
        if frame['time'] != timestamp or name in frame['data']:
            raise ValueError('Duplicate record or mismatched step time')
        frame['data'][name] = values
    if not frames:
        raise ValueError('No rigid records')
    ordered = sorted(frames.items())
    if [s for s, _ in ordered] != list(range(1, len(ordered)+1)):
        raise ValueError('Missing/nonsequential log step')
    if any(f['time'] <= 0 or set(f['data']) != set(DATA_COLUMNS)
           for _, f in ordered):
        raise ValueError('Missing complete requested records')
    if any(a[1]['time'] >= b[1]['time'] for a, b in zip(ordered, ordered[1:])):
        raise ValueError('Nonincreasing log times')
    return ordered


def csv_table(path):
    rows = list(csv.reader(path.open(encoding='utf-8')))
    columns = [c.strip().lstrip('#').strip() for c in rows[0] if c.strip()]
    values = [finite(row) for row in rows[1:] if row]
    if any(len(row) != len(columns) for row in values):
        raise ValueError('CSV column mismatch')
    if any(a[0] >= b[0] for a, b in zip(values, values[1:])):
        raise ValueError('Nonincreasing CSV times')
    return {'columns': columns, 'values': values}


def stl_points(path):
    """Inspect every binary STL coordinate; return sparse deterministic samples."""
    raw = path.read_bytes()
    count = struct.unpack_from('<I', raw, 80)[0]
    if len(raw) != 84+50*count or count < 1:
        raise ValueError('Invalid binary STL')
    samples = []
    for i in range(count):
        values = finite(struct.unpack_from('<12f', raw, 84+50*i))
        if i in {0, count//4, count//2, 3*count//4, count-1}:
            samples.extend([values[j:j+3] for j in (3, 6, 9)])
    return samples


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    audit = json.loads((INPUT/'audit.json').read_text())
    for item in audit['files']:
        path = INPUT/Path(item['archive_path']).name
        if sha(path) != item['sha256']:
            raise ValueError('Changed native motion input: '+path.name)
    root = safe_xml((INPUT/'FeBio_custom.feb').read_bytes())
    props = safe_xml((INPUT/'ModelProperties.xml').read_bytes())
    materials = {int(m.get('id')): {
        'name': m.get('name'), 'c0_mm': vector(m.findtext('center_of_mass'))}
        for m in root.findall('Material/material') if m.get('type') == 'rigid body'}
    if any(materials[k]['name'] != v for k, v in BONES.items()):
        raise ValueError('Unexpected native material mapping')
    step = root.findall('Step')
    if len(step) != 1 or step[0].find('Control/analysis').get('type') != 'static':
        raise ValueError('Expected one quasi-static load step')
    fixes = {int(x.get('mat')): {b.get('bc'): float(b.text)
             for b in x.findall('prescribed')}
             for x in step[0].findall('Boundary/rigid_body')}
    for body in (2, 3):
        if fixes.get(body) != dict.fromkeys(('x', 'y', 'z', 'Rx', 'Ry', 'Rz'), 0.):
            raise ValueError('Tibia/fibula fixity differs')
    requests = {x.get('name'): x.get('data') for x in root.findall('Output/logfile/*')}
    if (requests.get('center_of_mass') != 'x;y;z' or
            requests.get('rotation_quaternion') != 'qx;qy;qz;qw'):
        raise ValueError('Unexpected native output component order')
    curves = {x.get('name'): [vector2.text for vector2 in x.findall('point')]
              for x in root.findall('LoadData/loadcurve')}
    if curves.get('Loading_Curve') != ['0,0', '1,0', '2,1']:
        raise ValueError('Unexpected flexion load curve')
    log_text = (INPUT/'FeBio_custom.log').read_text()
    if 'N O R M A L   T E R M I N A T I O N' not in log_text:
        raise ValueError('Native log lacks normal termination')
    initial_logged = {}
    header = log_text.split('Data Record #')[0]
    for match in re.finditer(r'(?m)^\s*(\d+) - (\w+) \(type: rigid body\)'
                            r'([\s\S]*?)center_of_mass [ .]*: ([^\n]+)', header):
        k, name, _, com = match.groups()
        initial_logged[int(k)] = {'name': name, 'c0_mm': vector(com)}
    if set(initial_logged) != set(materials) or any(
            initial_logged[k]['name'] != m['name'] or
            distance(initial_logged[k]['c0_mm'], m['c0_mm']) > 1e-4
            for k, m in materials.items()):
        raise ValueError('Input versus log-header initial references mismatch')
    if root.find('Initial') is not None:
        raise ValueError('Initial conditions require separate orientation audit')
    native = parse_log(log_text)
    tables = {p.name: csv_table(p) for p in sorted(INPUT.glob('*.csv'))}
    times = [0.]+[f['time'] for _, f in native]
    for table in tables.values():
        if len(times) != len(table['values']) or any(
                abs(t-row[0]) > 1e-10 for t, row in zip(times, table['values'])):
            raise ValueError('Processed CSV and native log time grids differ')
    source = json.loads((ROOT/'assets/ch14-knee-source.json').read_text())
    points, geometry_hashes = {}, {}
    for item in source['archive']['contents']:
        if item['structure'] not in BONES.values():
            continue
        path = ROOT/'work/ch14-knee-source'/Path(item['path']).name
        if sha(path) != item['sha256']:
            raise ValueError('Changed native bone geometry')
        points[item['structure']] = stl_points(path)
        geometry_hashes[item['structure']] = sha(path)
    checks = {'native_frames': len(native), 'constructed_t0': True,
              'initial_input_log_header_agree_within_mm': 1e-4,
              'max_raw_quaternion_norm_error': 0., 'max_rotation_orthogonality_error': 0.,
              'max_rotation_determinant_error': 0., 'max_pair_distance_error_mm': 0.,
              'max_pivot_mapping_error_mm': 0., 'fixed_body_max_displacement_mm': 0.,
              'fixed_body_max_quaternion_change': 0.}
    frames = [{'model_time': 0., 'native_step': None,
               'origin': 'constructed input reference, NOT a logged state',
               'poses': {name: {'c_mm': materials[k]['c0_mm'], 'q_xyzw': [0., 0., 0., 1.]}
                         for k, name in BONES.items()}}]
    for number, frame in native:
        data = frame['data']
        for key in ('center_of_mass', 'rotation_quaternion'):
            if set(data[key]) != set(materials):
                raise ValueError('Native rigid material IDs differ')
        # Check all nine native bodies, not only the four physical bone outputs.
        for k, rawq in data['rotation_quaternion'].items():
            err = abs(norm(rawq)-1)
            checks['max_raw_quaternion_norm_error'] = max(
                checks['max_raw_quaternion_norm_error'], err)
            r = rotation(rawq)
            orth = max(abs(sum(r[j][a]*r[j][b] for j in range(3))-(a == b))
                       for a in range(3) for b in range(3))
            det = sum(r[0][i]*(r[1][(i+1)%3]*r[2][(i+2)%3]-
                              r[1][(i+2)%3]*r[2][(i+1)%3]) for i in range(3))
            checks['max_rotation_orthogonality_error'] = max(
                checks['max_rotation_orthogonality_error'], orth)
            checks['max_rotation_determinant_error'] = max(
                checks['max_rotation_determinant_error'], abs(det-1))
        poses = {}
        for k, name in BONES.items():
            center, rawq = data['center_of_mass'][k], data['rotation_quaternion'][k]
            c0 = materials[k]['c0_mm']
            pivot = transform(c0, c0, center, rawq)
            checks['max_pivot_mapping_error_mm'] = max(
                checks['max_pivot_mapping_error_mm'], distance(pivot, center))
            moved = [transform(p, c0, center, rawq) for p in points[name]]
            for i, j in itertools.combinations(range(len(moved)), 2):
                checks['max_pair_distance_error_mm'] = max(
                    checks['max_pair_distance_error_mm'],
                    abs(distance(moved[i], moved[j])-distance(points[name][i], points[name][j])))
            if k in (2, 3):
                checks['fixed_body_max_displacement_mm'] = max(
                    checks['fixed_body_max_displacement_mm'], distance(center, c0))
                checks['fixed_body_max_quaternion_change'] = max(
                    checks['fixed_body_max_quaternion_change'], distance(rawq, (0, 0, 0, 1)))
            poses[name] = {'c_mm': center,
                           'q_xyzw': [v/norm(rawq) for v in rawq]}
        frames.append({'model_time': frame['time'], 'native_step': number,
                       'origin': 'native printed COM/quaternion log', 'poses': poses})
    if (checks['fixed_body_max_displacement_mm'] > 1e-10 or
            checks['fixed_body_max_quaternion_change'] > 1e-12 or
            checks['max_pair_distance_error_mm'] > 1e-9 or
            checks['max_rotation_determinant_error'] > 1e-12):
        raise ValueError('Rigid motion checks failed')
    series = [{'model_time': t,
               'reported_tf_flexion_deg': tables['Tibiofemoral_Kinematics.csv']['values'][j][4],
               'reported_tf_flexion_moment_Nmm': tables['Tibiofemoral_Kinetics.csv']['values'][j][4],
               'reported_pf_flexion_deg': tables['Patellofemoral_Kinematics.csv']['values'][j][4]}
              for j, t in enumerate(times)]
    result = {'schema': 'oks003-private-rigid-poses-v1',
              'transform': 'x(t)=c(t)+R(q_xyzw(t))*(x0-c0); active column-vector rotation',
              'coordinate_frame': 'native FEBio global reference axes; millimetres; anatomical world signs NOT inferred',
              'time_axis': 'quasi-static model load parameter; 0..1 prestrain, 1..2 flexion; NOT gait seconds',
              'initial_centers_mm': {v: materials[k]['c0_mm'] for k, v in BONES.items()},
              'center_definition': 'Input-defined rigid reference/pivot named center_of_mass; not independently measured anatomical mass centroid (fibula explicitly uses zero).',
              'quaternion_policy': 'qx,qy,qz,qw; normalize rounded printed quaternion; reject norm error >2e-6',
              'frames': frames, 'time_matched_reported_csv_series': series,
              'limits': ['T0 constructed from input COM and reference identity, not logged.',
                         'JCS CSV rotations are reported quantities, not world Euler angles.',
                         'Tibia_Translation.csv is not absolute world tibia motion: native tibia is fixed.',
                         'No soft tissue deformation/contact/photorealistic appearance/experimental validation.',
                         'Geometry_custom.feb is not acquired; exact volume-mesh to smoothed-STL registration not independently established.',
                         'Exact FEBio2.9.1 source/binary not acquired; source convention checked against owning manual and v3.0 source.']}
    provenance = {'input_hashes': {p.name: sha(p) for p in sorted(INPUT.iterdir()) if p.is_file()},
                  'bone_stl_sha256': geometry_hashes, 'materials': materials,
                  'requests': requests, 'zero_prescribed_dofs': fixes,
                  'load_curves': curves,
                  'prescribed_flexion': [ET.tostring(x, encoding='unicode') for x in
                      step[0].findall("Constraints/constraint[@name='Extension_Flexion']")],
                  'landmarks_reference_only': {x.tag: x.text for x in props.find('Landmarks')
                                               if isinstance(x.tag, str)},
                  'geometry_external_dependency': 'Geometry_custom.feb: NOT acquired; local absolute source path not copied',
                  'checks': checks,
                  'sources': [
                      'https://febiosoftware.github.io/febio-docs/theory/chapter6/6.3-rigid-body-dynamics/',
                      'https://github.com/febiosoftware/FEBio/blob/47746329aea1ec32201ba556afe4da863357efad/FEBioMech/FEBioMechData.cpp',
                      'https://github.com/febiosoftware/FEBio/blob/47746329aea1ec32201ba556afe4da863357efad/FEBioMech/FERigidBody.h',
                      'https://github.com/febiosoftware/FEBio/blob/47746329aea1ec32201ba556afe4da863357efad/FECore/quatd.h',
                      'https://pmc.ncbi.nlm.nih.gov/articles/PMC9832097/'],
                  'source_access': 'Owning FEBio manual/v3.0 source and owning paper text read. Appendix PDF retrieval failed; units/source-coordinate provenance inherited from root source record, not independently reread PDF.'}
    for name, obj in [('poses.json', result), ('provenance-checks.json', provenance)]:
        (OUTPUT/name).write_text(json.dumps(obj, separators=(',', ':'), allow_nan=False)+'\n')
    print(json.dumps(checks, indent=2))
    print('PRIVATE outputs:', OUTPUT.relative_to(ROOT))


if __name__ == '__main__':
    main()
