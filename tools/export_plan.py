"""Export planning views from the canonical chapter manifest; never generate chapter prose."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT/'chapter-manifest.json').read_text(encoding='utf-8'))
    chapters = manifest['chapters']
    lines = ['# Human Physiology: chapter and visual plan', '',
             'The official60-lecture sequence is the coverage spine. The supplied playlist is reordered and omits lecture20; the recovered recording is included. The short course introduction is supplementary.', '',
             'Status: independently reviewed plan with targeted repairs. Manuscript, scientific source disposition, source-visual review and asset acceptance remain in progress. All graphics listed below are plans, not completed assets.', '']
    results = []
    visual_rows = []
    for chapter in chapters:
        n = chapter['number']
        lines += [f"## {n}. {chapter['title']}", '',
                  f"**Recordings:** {', '.join(map(str, chapter['recordings']))} · {chapter['recording_seconds']/3600:.2f} source hours.",
                  f"**Purpose:** {chapter['purpose']}",
                  f"**Scientific prerequisites:** {chapter['prerequisites']}. **Reading previous:** {chapter['reading_previous']}.",
                  '', '### Sections and central statements', '']
        for i, section in enumerate(chapter['sections']):
            lines.append(f"- **{section['id']} — {section['title']}.** {section['result_statement']}")
            cues = section.get('caption_cues', [])
            if cues:
                anchors = '; '.join(f"L{cue['lecture']} {cue['anchor']}" for cue in cues)
                lines.append(f'  Caption navigation anchors: {anchors}.')
            results.append({'id': section['id'], 'kind': 'empirical/model claim; classify in section evidence ledger',
                            'statement': section['result_statement'], 'planned_chapter': n,
                            'depends_on': [chapter['sections'][i-1]['id']] if i else [],
                            'prerequisite_chapters': chapter['prerequisites'],
                            'status': 'section-specific evidence and numerical/causal checks pending',
                            'source_recordings': section.get('source_recordings', chapter['recordings'])})
        lines += ['', '### Primary dynamic explanations', '']
        for asset in chapter['animations']:
            lines.append(f"- **{asset['id']}:** {asset['description']}.")
            visual_rows.append([n, asset['id'], 'animation', asset['status'], asset['description']])
        lines += ['', '### Anatomical and comparison views', '']
        for asset in chapter['illustrations']:
            lines.append(f"- **{asset['id']}:** {asset['description']}.")
            visual_rows.append([n, asset['id'], 'illustration', asset['status'], asset['description']])
        req = chapter['asset_requirements']
        lines += [f"- **Required visible structures:** {'; '.join(req['required_structures'])}.",
                  f"- **Actual acquisition status:** {req['status']}.", f"- **Fallback:** {req['fallback']}",
                  '', '### Worked investigation and exercises', '',
                  f"- **Question:** {chapter['lab']['question']}",
                  f"- **Investigation:** {chapter['lab']['description']}.",
                  f"- **Simulation mandatory:** {chapter['lab']['simulation_required']}; use causal/data interpretation where a defensible numerical model adds no value.",
                  '- **Exercises:** about six fully worked tasks, with flexible conceptual, derivational and computational/data-interpretation roles.',
                  f"- **High-priority source issues:** {', '.join(chapter['scientific_issue_ids']) or 'see the per-lecture source ledger'}.", '']
    lines += ['## Coverage, review and release', '',
              'All60official lecture numbers occur once in order. Reading progression is separate from actual prerequisites. Indispensable early cardiac/muscle bridges are explained locally and revisited later at greater depth.', '',
              'The precise topic-to-section navigation map is plan/topic-coverage.json; complete source excerpts and audits remain private. Caption locators are not proof of biological truth or visual verification.', '',
              'Animation is primary for temporal mechanisms. Each asset needs evidence for geometry, appearance and behavior, orientation/scale/time labels, sampled phase checks and accessible/print alternatives. An organ surface cannot establish its uninspected internals.', '',
              'Two actual independent digest-bound chapter reviews precede acceptance. Targeted repair checks follow blockers without endless full review loops. Completion requires all chapters/assets, verified computations, source and browser checks, and an inspected GitHub push/live reader. A plan or scaffold is not completion.']
    (ROOT/'plan'/'outline.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    (ROOT/'plan'/'results.yaml').write_text(json.dumps({'results': results}, indent=2)+'\n', encoding='utf-8')
    with (ROOT/'plan'/'visual-plan.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['chapter', 'id', 'type', 'status', 'description'])
        writer.writerows(visual_rows)
    architecture = ['# Chapter architecture', '', 'Scientific dependencies point backward and are distinct from reading progression.', '']
    architecture += [f"- **{c['number']}. {c['title']}:** lectures{c['recordings']}; scientific prerequisites{c['prerequisites']}; {c['purpose']}" for c in chapters]
    (ROOT/'plan'/'architecture.md').write_text('\n'.join(architecture)+'\n', encoding='utf-8')
    assigned = [n for c in chapters for n in c['recordings']]
    assert assigned == list(range(1, 61)), assigned
    print(f'Exported {len(chapters)} chapters, {len(results)} section nodes and {len(visual_rows)} planned visual records; official coverage1–60 verified.')


if __name__ == '__main__':
    main()
