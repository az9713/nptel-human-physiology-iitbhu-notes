# Human Physiology

Independent study notes following **Prof. Sudip Mukherjee, IIT (BHU) Varanasi**, [NPTEL course 102106670](https://nptel.ac.in/courses/102106670).

[Online reader (publication pending)](https://az9713.github.io/nptel-human-physiology-iitbhu-notes/) · [Chapter index](index.html) · [Source map](source-map.html) · [Code lab](code-lab.html)

The book contains 25 accepted chapters covering the official 60-lecture sequence, with worked problems, controlled animations, static print alternatives and reproducible teaching calculations. Every chapter received two actual independent AI scientific/editorial full reviews, necessary targeted repairs and separate bounded browser/print checks. These checks are not human expert certification or clinical validation.

The supplied [YouTube playlist](https://www.youtube.com/playlist?list=PLyqSpQzTE6M_4jmZrdBaHSQyViWt4w0S5) is out of order and omits official lecture 20; the inventory includes its recovered recording and lists the short introduction separately. The official recordings total about 29.3 hours. Complete publisher captions and bounded visual audits cover all 60 recordings; 3,548 sampled frames were acquired. This is not a claim of continuous audio/video viewing.

The visual plan records 73 animations and 35 supporting illustrations across 101 section nodes. Time-evolving mechanisms use controlled playback, seeking and explanations, with plots where useful. Verified microscopy/imaging supplies observed tissue appearance; original diagrams and selected source-based 3D explain topology and movement. Species, preparation, scale, artificial timing and model limits are stated at point of use. A still image does not establish physiological kinetics.

## Run locally

Use **Python 3.10+**. The 25 declared chapter calculation labs use the standard library. Serve the reader over loopback HTTP so data/geometry panels can load:

~~~sh
python -X utf8 tools/preview_public.py --port 8765
~~~

Open the printed local URL. Reader scripts, MathJax and displayed data are bundled; external source links require internet access. Run a chapter lab using its command in [Code lab](code-lab.html).

## Rebuild and validate

~~~sh
python -X utf8 tools/export_plan.py
python -X utf8 tools/build_book.py
python -X utf8 tools/validate_book.py --public --release
~~~

Public validation checks all 25 current accepted snapshots against sanitized [producer attestations](validation/README.md). It does not reconstruct private reviews or certify biological truth. The producer separately validates actual private reports and exports the portable records; those private tools/evidence are deliberately excluded.

| Optional task | Additional requirements |
| --- | --- |
| JavaScript calculation checks | Modern Node.js; tested with 22.22.0 |
| Source-based knee reference projection | NumPy and Pillow; [reproduction scope](assets/ch14-knee-reproduction.md) |
| Retained anatomical render sources | Blender, applicable MPFB/HRA assets and separately acquired inputs described in source headers |
| Historical scaffold browser harness | Playwright and compatible browser; tests scaffold/pilot only, not final chapter acceptance |

The 25 labs, 11 public JavaScript check scripts and the chapter 15 static validator passed the release reproduction audit; 32 intercepted numerical/static outputs matched the bundled bytes. Optional upstream asset reacquisition and full Blender/knee repacking are separate workflows, with their input limits documented.

## Sources, rights and evidence

- [Lecture inventory](lecture-inventory.csv) and [references](references.html)
- [Asset credits and licences](assets/ATTRIBUTION.md), including individual image/geometry notices
- [Visual-resource research](research/VISUAL_RESOURCES.md) and [production workflow](WORKFLOW.md)
- [Chapter/visual plan](plan/outline.md) and [completion record](completion.json)

Raw captions, lecture videos/slides, private reviews, browser proofs, credentials and personal absolute paths are excluded from publication. No original lecture artwork is relicensed by this repository. Third-party assets/dependencies retain their own notices, including the applicable GSAP licence; no blanket licence overrides them.
