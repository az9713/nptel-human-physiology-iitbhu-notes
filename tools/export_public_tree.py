"""Export a byte-preserving, allowlisted public checkout (Python 3.10+).

Usage: python tools/export_public_tree.py --destination work/public-release-check
       python tools/export_public_tree.py --self-test
No release/status inference, network access, deletion, overwrite, or git action.

Policy: exact reader/docs/tool names below, manifest-named chapter HTML/sidecars,
production assets matching assets/chNN-* plus book assets, bundled MathJax,
and the historically named reviewed secretory-traffic-pilot.html mechanism,
chapter teaching code, five reviewed editable figure sources, exact plan/spec
products, and canonical validation/acceptance/chapter-NN.json attestations.
Unknown files are excluded, never followed as dependencies. A reviewed artifact
outside that allowlist is an error, not silently dropped evidence. Provenance,
licenses, sidecars and attestations are copied verbatim, not sanitized. Raw
sources/work, credentials, caches, HANDOFF/AGENTS/README.txt and prototypes never
enter the selection. Retained render sources may require separately licensed
private acquisition inputs; copying them does not assert full source rebuild.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import subprocess

ROOT_FILES = {
    'index.html', 'source-map.html', 'references.html', 'code-lab.html',
    'chapter-manifest.json', 'source-manifest.json', 'completion.json',
    'README.md', 'WORKFLOW.md', 'lecture-inventory.csv', '.nojekyll', '.gitattributes', 'LICENSE', 'LICENSE.md',
    'LICENSE.txt', 'NOTICE', '.gitignore',
}
TOOLS = {
    'build_book.py', 'export_plan.py', 'validate_book.py', 'public_acceptance.py',
    'check_reader_browser.py', 'preview_public.py', 'export_public_tree.py',
}
FIGURES = {
    'ch01_body_orientation.py', 'ch01_cell_panel.py', 'ch05_heart_render.py',
    'ch14_knee_pack.py', 'ch14_knee_reference.py',
}
PLAN = {'architecture.md', 'notation.md', 'outline.md', 'results.yaml',
        'topic-coverage.json', 'topic-subsections.md', 'visual-plan.csv'}
SPEC = {'book-spec.md', 'house-style.md', 'sources.yaml'}
ASSET_EXT = {'.html', '.svg', '.png', '.jpg', '.jpeg', '.tif', '.tiff', '.webp',
             '.js', '.css', '.json', '.md', '.txt', '.woff2', '.zip', '.bin',
             '.mp4', '.webm', '.gif', '.glb', '.gltf'}
DENIED_PARTS = {'sources', 'work', '.git', '.serena', '__pycache__', 'node_modules',
                '.venv', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.cache', '.ssh', '.aws'}
SELECTED_TREES = ('assets', 'code', 'figures', 'tools', 'plan', 'spec', 'validation')
MANIFEST_NAME = 'public-export-manifest.json'


def ordinary_chain(path: Path) -> None:
    """Check lexical components before resolve: includes Windows reparse points."""
    for part in reversed((path, *path.parents)):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError(f'Linked/reparse path forbidden: {part}')


def absolute(value) -> Path:
    return Path(os.path.abspath(os.fspath(value)))


def below(path: Path, ancestor: Path) -> bool:
    return path == ancestor or path.is_relative_to(ancestor)


def walk_plain(directory: Path):
    ordinary_chain(directory)
    if not directory.exists():
        return
    if not directory.is_dir():
        raise ValueError(f'Expected directory: {directory}')
    for entry in sorted(directory.iterdir()):
        ordinary_chain(entry)
        if entry.is_dir():
            if entry.name.casefold() not in DENIED_PARTS:
                yield from walk_plain(entry)
        elif entry.is_file():
            yield entry
        else:
            raise ValueError(f'Nonordinary source entry: {entry}')


def relative_name(name) -> str:
    if (not isinstance(name, str) or not name or '\\' in name
            or name.startswith('/') or re.match(r'^[A-Za-z]:', name)
            or any(p in ('..', '') for p in name.split('/'))):
        raise ValueError('Invalid selected relative path')
    if any(p.casefold() in DENIED_PARTS for p in name.split('/')):
        raise ValueError(f'Private source cannot be exported: {name}')
    return name


def select_files(source: Path) -> list[str]:
    ordinary_chain(source)
    if not source.is_dir():
        raise ValueError('Source must be an ordinary project directory')
    selected = set()
    def add(name, required=False):
        name = relative_name(name)
        file = source / name
        ordinary_chain(file)
        if file.is_file():
            if re.search(r'(?i)(?:^|[._-])(?:credentials?|passwords?)(?:[._-]|$)|^\.env(?:\.|$)|^id_(?:rsa|ed25519)$', file.name):
                raise ValueError(f'Credential-shaped filename forbidden: {name}')
            selected.add(name)
        elif required:
            raise ValueError(f'Missing required public product: {name}')
    for name in ROOT_FILES:
        add(name, required=name in {'chapter-manifest.json', 'source-manifest.json',
                                   'index.html', 'source-map.html', 'references.html', 'code-lab.html'})
    manifest = json.loads((source/'chapter-manifest.json').read_text(encoding='utf8'))
    sidecars = []
    for chapter in manifest['chapters']:
        name = chapter['file']
        if not re.fullmatch(r'chapter-\d{2}-[a-z0-9-]+\.html', name):
            raise ValueError('Invalid canonical chapter filename')
        add(name)
        meta = name.removesuffix('.html')+'.meta.json'
        add(meta)
        if meta in selected:
            sidecars.append(json.loads((source/meta).read_text(encoding='utf8')))
    for directory, names in [('tools', TOOLS), ('figures', FIGURES), ('plan', PLAN), ('spec', SPEC)]:
        for name in names:
            add(directory+'/'+name, required=directory=='tools' and name in {'build_book.py','validate_book.py','public_acceptance.py'})
    add('validation/README.md')
    add('research/VISUAL_RESOURCES.md')  # README-linked public resource catalogue only.
    for file in walk_plain(source/'validation'/'acceptance'):
        name = file.relative_to(source).as_posix()
        if re.fullmatch(r'validation/acceptance/chapter-\d{2}\.json', name):
            add(name)
    for file in walk_plain(source/'assets'):
        rel = file.relative_to(source).as_posix()
        local = file.relative_to(source/'assets').as_posix()
        if ((local.startswith('mathjax/') and (file.suffix.lower() in {'.js','.json','.map','.woff','.woff2','.ttf','.otf','.svg','.txt','.md'} or file.name in {'LICENSE','NOTICE'})) or local in {'book.css','book.js','ATTRIBUTION.md','secretory-traffic-pilot.html'}
                or re.fullmatch(r'ch\d{2}-[^/]+', local) and file.suffix.lower() in ASSET_EXT):
            add(rel)
    for file in walk_plain(source/'code'):
        local = file.relative_to(source/'code').as_posix()
        if re.fullmatch(r'ch\d{2}_[a-z0-9_]+\.(?:py|cjs|js)', local):
            add('code/'+local)
    # Preserve exact evidence maps: an omitted reviewed product is a hard error.
    for meta in sidecars:
        artifacts = list(meta.get('artifact_sha256', {}))
        for item in meta.get('reviewed_artifacts', []):
            artifacts.append(item if isinstance(item, str) else item['path'])
        for name in artifacts:
            if relative_name(name) not in selected:
                raise ValueError(f'Reviewed dependency outside public allowlist or absent: {name}')
    return sorted(selected)


def export_tree(source, destination) -> dict:
    source, destination = absolute(source), absolute(destination)
    ordinary_chain(source)
    ordinary_chain(destination)
    if below(source, destination) or destination == source:
        raise ValueError('Destination cannot equal or contain source root')
    if any(below(destination, source/tree) for tree in SELECTED_TREES):
        raise ValueError('Destination overlaps a selected source directory')
    names = select_files(source)
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError('Destination must be absent or an ordinary empty directory')
    # Preflight every source before creating any output.
    for name in names:
        ordinary_chain(source/name)
    destination.mkdir(parents=True, exist_ok=True)
    ordinary_chain(destination)
    records = {}
    for name in names:
        src, dst = source/name, destination/name
        ordinary_chain(src)
        body = src.read_bytes()
        ordinary_chain(src)
        ordinary_chain(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        ordinary_chain(dst)
        with dst.open('xb') as stream:  # exclusive creation; never overwrite
            stream.write(body)
        if src.read_bytes() != body or dst.read_bytes() != body:
            raise ValueError(f'Source changed during export or copy mismatch: {name}')
        records[name] = hashlib.sha256(body).hexdigest()
    record = {'schema': 'physiology-public-export-v1', 'policy_version': 1,
              'files_sha256': records, 'file_count': len(records),
              'limits': 'Byte identity and allowlist only; no release or scientific acceptance. '
                        'Private acquisition inputs and producer reports are excluded. '
                        'Retained rendering sources may require those separate inputs.'}
    ordinary_chain(destination/MANIFEST_NAME)
    with (destination/MANIFEST_NAME).open('x', encoding='utf8', newline='\n') as stream:
        stream.write(json.dumps(record, indent=2, ensure_ascii=False)+'\n')
    return record


def self_test() -> dict:
    """Small fixtures retained for inspection; no deletion/recursive move."""
    base = Path(tempfile.mkdtemp(prefix='physiology-export-fixture-'))
    src = base/'source'; src.mkdir()
    for name in ('index.html','source-map.html','references.html','code-lab.html'):
        (src/name).write_text('<p>fixture</p>', encoding='utf8')
    (src/'chapter-manifest.json').write_text('{"chapters":[]}', encoding='utf8')
    (src/'source-manifest.json').write_text('{}', encoding='utf8')
    for name in ('tools/build_book.py','tools/validate_book.py','tools/public_acceptance.py','work/private.txt','sources/raw.txt','assets/ch01-LICENSE.txt',
                 'assets/ch01-reference.jpg','assets/unreviewed-pilot.html',
                 'figures/ch11_follicle_realism.py','code/ch01_test.py'):
        file=src/name; file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(b'fixture')
    result=export_tree(src,base/'public')
    assert 'assets/ch01-LICENSE.txt' in result['files_sha256']
    assert 'code/ch01_test.py' in result['files_sha256']
    assert not any('pilot' in n or n.startswith(('sources/','work/')) for n in result['files_sha256'])
    tests=3
    for bad in ('assets\\bad.jpg','assets/../bad.jpg','/absolute','work/private.txt','assets/.cache/cached.js'):
        try: relative_name(bad)
        except ValueError: tests+=1
        else: raise AssertionError('unsafe relative path accepted')
    assert export_tree(src,src/'work'/'public-copy')['file_count']==result['file_count']
    tests+=1
    for dest in (base/'public', src, src/'assets'/'nested', src/'code'/'nested'):
        try: export_tree(src,dest)
        except ValueError: tests+=1
        else: raise AssertionError('unsafe destination accepted')
    # Deliberately unallowlisted reviewed artifact must not be silently dropped.
    (src/'chapter-manifest.json').write_text('{"chapters":[{"file":"chapter-01-test.html"}]}')
    (src/'chapter-01-test.meta.json').write_text('{"reviewed_artifacts":["work/private.txt"]}')
    try: export_tree(src,base/'missing-dependency')
    except ValueError: tests+=1
    else: raise AssertionError('private reviewed dependency silently dropped')
    (src/'chapter-manifest.json').write_text('{"chapters":[]}')
    links=[]
    try:
        (base/'linked').symlink_to(src,target_is_directory=True)
        for source,dest in ((base/'linked',base/'bad-source'),(src,base/'linked'/'out')):
            try: export_tree(source,dest)
            except ValueError: tests+=1
            else: raise AssertionError('linked ancestor accepted')
        (src/'assets'/'ch01-link.jpg').symlink_to(src/'assets'/'ch01-reference.jpg')
        try: export_tree(src,base/'bad-file')
        except ValueError: tests+=1
        else: raise AssertionError('linked selected source accepted')
        links=['source ancestor','destination ancestor','selected source file']
    except OSError as error:
        links=['symlink creation unavailable: '+str(error)]
    if os.name == 'nt':
        junction = base/'junction'
        made = subprocess.run(['cmd','/d','/c','mklink','/J',str(junction),str(src)],
                              capture_output=True, text=True)
        if made.returncode != 0:
            raise AssertionError('Windows junction fixture could not be created: '+made.stderr)
        for source,dest in ((junction,base/'bad-junction-source'),(src,junction/'out')):
            try: export_tree(source,dest)
            except ValueError: tests+=1
            else: raise AssertionError('junction ancestor accepted')
        links.append('Windows junction source/destination ancestors')
    return {'tests_passed': tests, 'link_tests': links, 'retained_fixture': str(base)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).absolute().parents[1])
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--self-test', action='store_true')
    args=parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(),indent=2));return
    if args.destination is None:
        parser.error('--destination is required (never selected implicitly)')
    try:
        record=export_tree(args.source,args.destination)
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as error:
        parser.exit(1,f'Export refused: {error}\n')
    print(json.dumps({'destination':str(absolute(args.destination)),
                      'file_count':record['file_count'],
                      'manifest':MANIFEST_NAME,'release_acceptance':False},indent=2))


if __name__ == '__main__':
    main()
