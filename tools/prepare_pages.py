"""Restore checksum-pinned large media, optionally assemble the tracked public site.

python tools/prepare_pages.py                       # restore media in a fresh clone
python tools/prepare_pages.py --output build/pages  # assemble the Pages artifact
Only missing media require network access. No acceptance state is modified.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = {'work', 'sources', '.git', '.venv', 'node_modules', '.ignore'}


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def restore_media(destination):
    manifest = json.loads((ROOT / 'publication-media.json').read_text(encoding='utf-8'))
    assert manifest['repository'] == 'az9713/nptel-human-physiology-iitbhu-notes'
    assert manifest['release_tag'] == 'visual-v2-media-2026-11-10'
    for entry in manifest['assets']:
        relative = Path(entry['path'])
        if relative.is_absolute() or '..' in relative.parts or relative.parts[0] != 'assets':
            raise ValueError('Unsafe media path')
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            raise ValueError('Media must be an ordinary file')
        if target.is_file():
            if target.stat().st_size != entry['bytes'] or sha(target) != entry['sha256']:
                raise ValueError('Existing media differs: ' + entry['path'])
            continue
        local = ROOT / relative
        with tempfile.TemporaryDirectory(prefix='pages-media-', dir=target.parent) as temporary:
            candidate = Path(temporary) / target.name
            if local.is_file():
                shutil.copyfile(local, candidate)
            else:
                url = (f"https://github.com/{manifest['repository']}/releases/download/"
                       f"{manifest['release_tag']}/{target.name}")
                with urlopen(Request(url, headers={'User-Agent': 'physiology-notes-pages'}), timeout=120) as response:
                    with candidate.open('wb') as output:
                        shutil.copyfileobj(response, output)
            if candidate.stat().st_size != entry['bytes'] or sha(candidate) != entry['sha256']:
                raise ValueError('Media download/copy failed checksum: ' + entry['path'])
            candidate.replace(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', help='Empty directory under build/ for the Pages artifact')
    args = parser.parse_args()
    destination = ROOT
    if args.output:
        destination = (ROOT / args.output).resolve()
        if not destination.is_relative_to((ROOT / 'build').resolve()) or destination == (ROOT / 'build').resolve():
            raise ValueError('Output must be a child directory under build/')
        if destination.exists() and any(destination.iterdir()):
            raise ValueError('Output must be empty; choose a new build directory')
        destination.mkdir(parents=True, exist_ok=True)
        tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        for name in filter(None, tracked):
            relative = Path(name)
            if relative.parts[0] in PRIVATE or relative.name in {'HANDOFF.md', 'AGENTS.md', 'README.txt'} or name.startswith('validation/visuals/'):
                raise ValueError('Private file is tracked: ' + name)
            if name.startswith('.') and name != '.nojekyll':
                continue
            source = ROOT / relative
            if source.is_symlink() or not source.is_file():
                raise ValueError('Not an ordinary tracked file: ' + name)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    restore_media(destination)
    if args.output:
        files = [p for p in destination.rglob('*') if p.is_file()]
        total = sum(p.stat().st_size for p in files)
        if total >= 1_000_000_000:
            raise ValueError('Published site exceeds the 1 GB budget')
        print(f'PAGES_READY: {len(files)} files; {total} bytes; media checksums match; visual acceptance unchanged')
    else:
        print('MEDIA_READY: checksum-pinned release media restored; visual acceptance unchanged')


if __name__ == '__main__':
    main()
