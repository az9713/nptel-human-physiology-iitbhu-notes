# Human Physiology

**[Read the live textbook](https://az9713.github.io/nptel-human-physiology-iitbhu-notes/)** · [Source map](https://az9713.github.io/nptel-human-physiology-iitbhu-notes/source-map.html) · [Code lab](https://az9713.github.io/nptel-human-physiology-iitbhu-notes/code-lab.html)

**Visual revision in progress (2026-11-10).** This is a development edition, published at the author's explicit request. Previous visual acceptance is withdrawn. All 25 chapters are being audited against the [physiological illustration rubric](spec/physiology-visual-rubric.md); completion will not be claimed while any applicable item is unverified.

Latest nervous-system references: [brain surfaces and fixed reconstruction](assets/ch22-v2-brain-surfaces.html), [spinal roots](assets/ch22-v2-spinal-roots.html), [human cord histology](assets/ch22-v2-cord-histology.html), [observed axonal transport](assets/ch23-v2-axonal-transport.html), [ribbon-synapse observations](assets/ch24-v2-ribbon-observed.html), and [capillary ultrastructure](assets/ch25-v2-barrier-observed.html). Source/preparation/time/licence limits are stated with each figure. These additions have not received final visual acceptance.

Independent study notes following **Prof. Sudip Mukherjee, IIT (BHU) Varanasi**, [NPTEL course 102106670](https://nptel.ac.in/courses/102106670).

[Chapter index](index.html) · [Source map](source-map.html) · [Code lab](code-lab.html)

The current revision is published in the existing course repository and GitHub Pages reader; see the [publication verification](publication-validation.json). Publication does not confer final visual acceptance; current manuscript availability, source checks and unfinished reviews remain separate.

The book contains 25 chapters with retained scientific review history and reopened visual acceptance covering the official 60-lecture sequence, with worked problems, controlled animations, static print alternatives and reproducible teaching calculations. Every chapter received two actual independent AI scientific/editorial full reviews, necessary targeted repairs and separate bounded browser/print checks. These checks are not human expert certification or clinical validation.

The supplied [YouTube playlist](https://www.youtube.com/playlist?list=PLyqSpQzTE6M_4jmZrdBaHSQyViWt4w0S5) is out of order and omits official lecture 20; the inventory includes its recovered recording and lists the short introduction separately. The official recordings total about 29.3 hours. Complete publisher captions and bounded visual audits cover all 60 recordings; 3,548 sampled frames were acquired. This is not a claim of continuous audio/video viewing.

The visual plan records 73 animations and 36 supporting illustrations across 101 section nodes. The rebuild replaces inadequate anatomical drawings with verified photographs, microscopy, scans or source-grounded realistic reconstructions. Temporal explanations require animations with controlled playback; species, preparation, scale and timing limits must remain explicit. A still image does not establish physiological kinetics.

## Current visual previews

These views have bounded source, native-image, browser or print evidence; they are not book-wide acceptance. Remaining rubric items and broader mechanisms stay pending.

- Observed structure: [fixed human heart](assets/ch05-v2-structural-heart-reference.html), [human lung lobes](assets/ch07-v2-gross-lung-reference.html), [vessel microscopy](assets/ch06-v2-vessel-observed-reference.html), [thyroid follicles](assets/ch11-v2-follicle-observed-reference.html).
- Observed motion: [pig airway mucus bundles](assets/ch07-v2-mucus-bos2023-reference.html), [human cardiac MRI](assets/ch05-v2-cardiac-observed-reference.html), [forced-expiration MRI](assets/ch07-v2-breathing-observed-reference.html).
- Quantitative explorers: [lung volumes](assets/ch08-lung-volumes.html) and [oxygen accounting](assets/ch08-oxygen-accounting.html).

## Read the chapters

| Chapter | Topic |
| --- | --- |
| 1 | [From cells to organ systems](chapter-01-cells-to-organ-systems.html) |
| 2 | [Membrane transport and homeostasis](chapter-02-membrane-transport-homeostasis.html) |
| 3 | [Blood, hemostasis and anticoagulation](chapter-03-blood-hemostasis-anticoagulation.html) |
| 4 | [Blood groups, lymph and immune defense](chapter-04-blood-groups-lymph-immunity.html) |
| 5 | [The heart as an electrical and mechanical pump](chapter-05-heart-electrical-mechanical-pump.html) |
| 6 | [Blood vessels and microvascular exchange](chapter-06-vessels-microvascular-exchange.html) |
| 7 | [Airways, ventilation and hemoglobin](chapter-07-airways-ventilation-hemoglobin.html) |
| 8 | [Oxygen delivery, lung volumes and measurement](chapter-08-oxygen-delivery-lung-volumes.html) |
| 9 | [Endocrine signaling and glucose homeostasis](chapter-09-endocrine-signaling-glucose.html) |
| 10 | [Diabetes technologies and experimental cell therapy](chapter-10-diabetes-technologies-cell-therapy.html) |
| 11 | [Thyroid and endocrine disorders](chapter-11-thyroid-endocrine-disorders.html) |
| 12 | [Digestive organization and carbohydrate absorption](chapter-12-digestion-carbohydrate-absorption.html) |
| 13 | [Protein and lipid absorption; digestive dysfunction](chapter-13-protein-lipid-digestion.html) |
| 14 | [Bones, joints and connective tissues](chapter-14-bones-joints-connective-tissue.html) |
| 15 | [Muscle contraction and neuromuscular transmission](chapter-15-muscle-neuromuscular-transmission.html) |
| 16 | [Kidney organization and glomerular filtration](chapter-16-kidney-glomerular-filtration.html) |
| 17 | [Tubular transport, renal regulation and disease](chapter-17-nephron-transport-pressure.html) |
| 18 | [Male reproduction and spermatogenesis](chapter-18-male-reproduction-spermatogenesis.html) |
| 19 | [Female anatomy, ovarian cycles and lactation](chapter-19-female-reproduction-ovarian-cycle.html) |
| 20 | [Menstrual regulation, fertilization and pregnancy](chapter-20-menstrual-cycle-pregnancy.html) |
| 21 | [Contraception, assisted reproduction and reproductive health](chapter-21-reproductive-health-technologies.html) |
| 22 | [Nervous-system organization: brain, spinal cord and nerves](chapter-22-nervous-system-organization.html) |
| 23 | [Neurons, axonal transport and nerve repair](chapter-23-neurons-axonal-transport-repair.html) |
| 24 | [Membrane excitability and synaptic transmission](chapter-24-membrane-excitability-synapses.html) |
| 25 | [Glia, sensory systems and neurological dysfunction](chapter-25-glia-barriers-sensation.html) |

## Run locally

Use **Python 3.10+**. The 25 declared chapter calculation labs use the standard library. After a fresh clone, restore the two oversized lossless videos from their checksum-pinned GitHub release assets:

~~~sh
python -X utf8 tools/prepare_pages.py
~~~

Their exact hashes and sizes are recorded in [publication-media.json](publication-media.json). GitHub Pages assembles the same files at their existing reader URLs; no video recompression is performed. Other reader files remain in the Git tree. Serve the reader over loopback HTTP so data/geometry panels can load:

~~~sh
python -X utf8 tools/preview_public.py --port 8765
~~~

Open the printed local URL. Reader scripts, MathJax and displayed data are bundled; external source links require internet access. Run a chapter lab using its command in [Code lab](code-lab.html).

## Rebuild and validate

~~~sh
python -X utf8 tools/export_plan.py
python -X utf8 tools/build_book.py
python -X utf8 tools/validate_book.py --public
~~~

Development integrity permits explicitly pending work. Final release validation (`python -X utf8 tools/validate_book.py --public --release`) remains blocked until all applicable rubric items pass. The retained [producer attestations](validation/README.md) describe historical review evidence; they do not approve changed visuals. `tools/verify_visual_rubric.py` is a producer-side check requiring private visual evidence, which is excluded from the public repository. The author explicitly authorized publication of this unfinished revision on 10 November 2026.

| Optional task | Additional requirements |
| --- | --- |
| JavaScript calculation checks | Modern Node.js; tested with 22.22.0 |
| Source-based knee reference projection | NumPy and Pillow; [reproduction scope](assets/ch14-knee-reproduction.md) |
| Retained anatomical render sources | Blender, applicable MPFB/HRA assets and separately acquired inputs described in source headers |
| Historical scaffold browser harness | Playwright and compatible browser; tests scaffold/pilot only, not final chapter acceptance |

In the previous release audit, the 25 labs, 11 public JavaScript check scripts and the chapter 15 static validator passed; 32 intercepted numerical/static outputs matched the bundled bytes. Optional upstream asset reacquisition and full Blender/knee repacking are separate workflows, with their input limits documented.

## Sources, rights and evidence

- [Observed macrophage phagocytosis](assets/ch04-v2-phagocytosis-observed.html) — cultured mouse cell-line time-lapse; source/native checks completed, browser/print acceptance pending.
- [Lecture inventory](lecture-inventory.csv) and [references](references.html)
- [Asset credits and licences](assets/ATTRIBUTION.md), including individual image/geometry notices
- [Visual-resource research](research/VISUAL_RESOURCES.md) and [production workflow](WORKFLOW.md)
- [Chapter/visual plan](plan/outline.md) and [completion record](completion.json)

Raw captions, lecture videos/slides, private reviews, browser proofs, credentials and personal absolute paths are excluded from publication. No original lecture artwork is relicensed by this repository. Third-party assets/dependencies retain their own notices, including the applicable GSAP licence; no blanket licence overrides them.
