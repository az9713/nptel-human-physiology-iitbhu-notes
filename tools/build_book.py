"""Generate offline reader indices without altering manuscripts or acceptance.

Run with Python 3.10+. Only the four root navigation pages are written.
"""
from __future__ import annotations

from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('index.html', 'source-map.html', 'references.html', 'code-lab.html')


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def chapter_path(chapter):
    import re
    name = chapter['file']
    if not isinstance(name, str) or not re.fullmatch(r'chapter-\d{2}-[a-z0-9-]+\.html', name):
        raise ValueError('Invalid chapter filename')
    path = ROOT / name
    if path.is_symlink() or path.resolve().parent != ROOT:
        raise ValueError('Chapter must be an ordinary root file')
    return path


def chapter_label(c):
    label = f'{c["number"]:02d}. {escape(c["title"])}'
    return (f'<a href="{escape(c["file"], quote=True)}">{label}</a>'
            if chapter_path(c).is_file() else f'<span aria-disabled="true">{label}</span>')


def wrap(title, body, course):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light"><title>{escape(title)} · Human Physiology</title>
<link rel="stylesheet" href="assets/book.css"><script defer src="assets/mathjax/tex-svg.js"></script>
<script defer src="assets/book.js"></script></head><body>
<a class="skip" href="#main">Skip to content</a><header class="site-header">
<a class="brand" href="index.html">Human Physiology</a><nav class="course-nav" aria-label="Book">
<a href="index.html">Chapters</a><a href="source-map.html">Source map</a><a href="references.html">References</a><a href="code-lab.html">Code lab</a></nav></header>
<div class="layout no-toc"><main id="main"><div class="reading-tools" aria-label="Reading controls">
<button id="theme-toggle" aria-pressed="false">Light theme</button><button id="text-toggle" aria-pressed="false">Larger text</button>
<button id="solutions-toggle" aria-pressed="false">Expand solutions</button><button id="print-page">Print with solutions</button></div>
<article id="chapter-content">{body}</article></main></div>
<footer class="site-footer">Independent study edition, not an official NPTEL or IIT publication. NPTEL course {escape(course['nptel_course'])},
Sudip Mukherjee, IIT (BHU) Varanasi. Educational material; examples and models require their stated physiological assumptions.
Raw captions and private working records are excluded from this reader.</footer></body></html>'''


def main():
    manifest, sources = load('chapter-manifest.json'), load('source-manifest.json')
    chapters, records = manifest['chapters'], sources['recordings']
    mapping = {}
    for c in chapters:
        chapter_path(c)
        for number in c['recordings']:
            if number in mapping:
                raise ValueError(f'Duplicate official lecture assignment: {number}')
            mapping[number] = c
    numbers = [r['number'] for r in records]
    if sorted(numbers) != list(range(1, 61)) or set(mapping) != set(numbers):
        raise ValueError('Official lectures 1–60 must each have one source and chapter assignment')
    written = sum(chapter_path(c).is_file() for c in chapters)
    # An index does not independently attest that a declared accepted status is valid.
    accepted = sum(c['status'] == 'accepted' for c in chapters)
    body = f'''<h1>Human Physiology</h1><p class="lead">An independent study edition following the official NPTEL lecture sequence.</p>
<p>Sudip Mukherjee · IIT (BHU) Varanasi · NPTEL 102106670.</p>
<p>{len(records)} official lectures · {len(chapters)} chapters · {written} manuscript files · {accepted} accepted chapter records (subject to evidence validation).</p>
<div class="warning"><strong>{'Reviewed study edition.' if accepted == len(chapters) else 'Development edition.'}</strong> Visual revisions are in progress and final visual acceptance remains pending. Each chapter record identifies its current status. Manuscript availability, source acquisition, scientific review and actual reader verification are distinct. Source-video audits use bounded sampling and do not claim continuous viewing.</div>
<h2 id="route">Learning route</h2><p>Follow the numbered chapters. The progression connects cells and homeostasis to transport, signaling and integrated organ-system physiology. Chapter records below identify prerequisites by chapter number. Quantitative models will state their assumptions, units and limits.</p>
<div class="search-tools"><label class="search-label" for="lecture-search">Search chapters, topics, or official lecture numbers</label><input id="lecture-search" type="search" autocomplete="off" placeholder="For example: membrane or lecture 20"><p id="search-status" role="status" aria-live="polite">{len(chapters)} chapters shown</p></div><ol class="lecture-list">'''
    for c in chapters:
        lectures = ', '.join(f'lecture {n}' for n in c['recordings'])
        availability = 'manuscript present' if chapter_path(c).is_file() else 'manuscript not written'
        prerequisites = ', '.join(str(n) for n in c.get('prerequisites', [])) or 'none specified'
        body += f'<li data-lecture="{c["number"]}" id="chapter-{c["number"]}"><h2>{chapter_label(c)}</h2><p>{escape(c["purpose"])}</p><p class="lecture-meta">{escape(lectures)} · {escape(c["status"])} · {availability}<br>Prerequisite chapters: {escape(prerequisites)}</p></li>'
    body += '</ol>'
    outputs = {'index.html': ('Chapters', body)}
    body = '''<h1>Source map</h1><p>The sequence uses <strong>official NPTEL lecture numbers</strong>, not supplied playlist positions. The playlist is reordered; official lecture 20 is absent from it. Its separately located official recording remains part of the course. The short course introduction is supplementary and is not counted as lecture 61.</p>
<p>“Acquired” refers to captions only. Caption authorship and anatomical, visual and scientific correctness require separate checks. Chapter timestamps locate the lecture spine. The recorded visual audits are bounded samples, not continuous video or audio review.</p>
<table><thead><tr><th>Official lecture / week</th><th>Recording</th><th>Playlist position</th><th>Chapter</th><th>Evidence</th></tr></thead><tbody>'''
    for r in sorted(records, key=lambda item: item['number']):
        position = str(r['playlist_index']) if r.get('in_supplied_playlist') else 'Absent from supplied playlist'
        body += f'<tr id="lecture-{r["number"]}"><td>{r["number"]} / {r["week"]}</td><td><a href="{escape(r["url"], quote=True)}">{escape(r["title"])}</a><br>{r["duration_seconds"] // 60}:{r["duration_seconds"] % 60:02d}</td><td>{position}</td><td>{chapter_label(mapping[r["number"]])}</td><td>Captions: {escape(r["caption_status"])}<br>Visuals: {escape(r["visual_coverage"])}</td></tr>'
    body += '</tbody></table><h2 id="supplementary">Supplementary entries</h2><ul>'
    for r in sources.get('supplementary_entries', []):
        body += f'<li><a href="{escape(r["url"], quote=True)}">{escape(r["title"])}</a> · playlist position {r["playlist_index"]} · {escape(r["role"])}</li>'
    body += '</ul><p>Metadata retrieved: ' + escape(sources['retrieved_at_utc']) + '.</p>'
    outputs['source-map.html'] = ('Source map', body)
    course = sources['course']
    body = f'''<h1>References and evidence</h1><h2 id="course">Course sources</h2><ul><li><a href="{escape(course['official_url'], quote=True)}">Official NPTEL Human Physiology course 102106670</a> — course identity and official sequence.</li><li><a href="{escape(course['supplied_playlist'], quote=True)}">Supplied NPTEL-NOC IITM playlist</a> — reordered playlist, with the discrepancy recorded in the <a href="source-map.html">source map</a>.</li></ul>
<h2 id="claims">Claim-level references</h2><p>References accompany the chapter claims they support. The chapters distinguish lecture statements, researched corrections, original teaching constructions and source-access limits. Consult each chapter's evidence section and current review status; a linked source alone does not establish that every claim has been verified.</p>
<h2 id="provenance">Evidence policy</h2><p>Separate lecture statements, independently researched corrections and original teaching constructions. Caption hashes are recorded in the source manifest; those hashes establish identity, not correctness. Review acceptance requires two independent full scientific reviews bound to the current manuscript and its assets. A static development check cannot replace scientific or browser review.</p>
<h2 id="assets">Visual sources and licenses</h2><p>Photographs and external body geometry retain their original creator, accession, license and modification records in the <a href="assets/ATTRIBUTION.md">asset attribution register</a>. Modality colors, specimen differences and calibration limits are stated beside the figures.</p>
<h2 id="reader">Offline reader components</h2><p>Navigation, search and reader controls use local files. External source links need network access when followed. Mathematical typesetting uses the locally bundled MathJax distribution; see its <a href="assets/mathjax/LICENSE">license</a>.</p>'''
    outputs['references.html'] = ('References', body)
    body = '<h1>Code lab and visual index</h1><p>Original teaching models and visual explanations, with their current evidence status. Runnable source links appear where the files exist. Mathematical checks establish properties of the stated model; they do not validate an anatomical or clinical prediction.</p><table><thead><tr><th>Chapter</th><th>Model / lab</th><th>Visuals and status</th></tr></thead><tbody>'
    for c in chapters:
        lab = c['lab']
        import re
        name = lab.get('path', '')
        download = ''
        if isinstance(name, str) and re.fullmatch(r'code/ch\d{2}_[a-z0-9_]+\.py', name):
            path = ROOT / name
            if path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT.resolve()):
                download = f'<p><a href="{escape(name, quote=True)}">Runnable Python source</a></p>'
        visuals = ''.join(f'<li>{escape(v["description"])} — {escape(v["status"])}</li>' for v in c['animations'] + c['illustrations'])
        body += f'<tr><td>{chapter_label(c)}</td><td>{escape(lab["description"])}<br><span class="status">{escape(lab["status"])}</span>{download}<p>{escape(lab["evidence"])}</p></td><td><ul>{visuals}</ul></td></tr>'
    outputs['code-lab.html'] = ('Code lab', body + '</tbody></table>')
    for filename, (title, content) in outputs.items():
        (ROOT / filename).write_text(wrap(title, content, course), encoding='utf-8', newline='\n')
    print(f'Generated {len(outputs)} reader pages; {written}/{len(chapters)} manuscript files. No statuses changed.')


if __name__ == '__main__':
    main()
