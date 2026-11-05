# Human Physiology: production workflow

## Scope and current state
Independent study notes following [NPTEL102106670](https://nptel.ac.in/courses/102106670), Prof. Sudip Mukherjee, IIT (BHU) Varanasi. The NPTEL-NOC IITM channel hosts the videos. The supplied playlist is reordered, omits official lecture20 and includes a supplementary introduction. The official60-lecture order is canonical.

All25 chapters are accepted after exactly two actual independent full scientific/editorial reviews each, necessary bounded repairs and separate actual browser/print assessments. Complete publisher captions and bounded source-visual audits cover all60 recordings; no continuous viewing claim is made. The plan records25 chapters,101section nodes,73animations and35supporting illustrations. Final release validation and actual remote/live publication are recorded separately in completion.json.

The user authorized autonomous completion and GitHub publication using the established lecture-repository workflow. Do not invent author approval or claim a review happened when it did not.

## Skills and responsibilities
- **analyze-sources:** source identity, acquisition, provenance, partial-coverage labels and source/verification separation.
- **stem-textbook:** specification, dependencies, notation, architecture, state and book-level integrity.
- **transcript-grounded-textbook:** lecture-specific coverage maps and nine-pass chapter production, calibrated against completed reference chapters.
- **rigorous-explainer:** developed explanations, local definitions, derivations, worked cases, purposeful figures, exercises and HTML checks.
- **science-editor:** actual substantive reviews with located scientific/teaching defects and concrete repairs.
- **animate-libs:** appropriate deterministic animation, frame sampling, controls and export/review infrastructure.

Use task-sized models/effort. Routine acquisition, mapping and formatting use low effort; full chapter work and scientific checking ordinarily use a capable model at medium effort. Escalate only for a specific hard unresolved issue. Avoid duplicate work and endless full review loops.

## Source and planning process
1. Identify every recording from the owning course; preserve supplied playlist position separately.
2. Preserve captions/metadata privately with hashes. Publisher delivery does not establish human authorship. Never infer missing content or equate captions with slides/video.
3. Sample source video with actual timestamps, build contact sheets, and inspect relevant frames and notation. Track acquisition and review separately.
4. Map substantive source topics to chapter sections. Keep exact cue locators and uncertainty. False, irrelevant or unsupported assertions receive a reasoned disposition rather than uncritical repetition.
5. Prepare specification, notation, section statements, real prerequisites, source issues and per-chapter visual plans. Independently review the plan; perform targeted checks after repairs.
6. Produce and inspect one representative chapter/visual set before scaling production. Continue the full authorized objective; do not redefine completion as the pilot.

## Chapter construction
Author prose directly in root chapter-NN-slug.html files, with matching meta.json. Do not store manuscript prose in generator scripts. Draft one section at a time through coverage, prose, mathematics, research, implementation, exercises, prose editing, parity and validation passes.

Keep mutable production and acceptance status in sidecar metadata and reader indices, rather than manuscript prose. Scientific evidence limits and visual provenance remain in the reader.

Define every term/symbol/compartment before use. Start from a consequential case, explain mechanisms and assumptions, interpret equations, compute printed numerical examples, and state model boundaries. An empirical biological claim needs evidence; a mathematical model does not prove the biological mechanism. Preserve the lecture topic spine while writing independent original prose.

Place timestamps beside major headings. Distinguish lecture coverage, verified corrections, research extensions and original teaching constructions. Clinical/regulatory claims use current owning sources and dates. Never promote an anecdote to causal evidence, an animal result to a human cure, or a visual analogy to a measured mechanism.

Exercises have fully worked solutions. About six per chapter is a reference default, with a flexible mix of conceptual reasoning, meaningful derivations and computation/data interpretation. Do not invent simulations or proof quotas for descriptive biology.

## Visual policy
### Realistic visual production and new rendered styles
Record the visual modality and its evidence for Chapters9–25. Preserve the accepted scientific snapshots of Chapters1–8; any later visual replacement needs its own scoped checks. These are production procedures for implementing the user’s request, not a user-imposed quota of new 3D renders per chapter.

Before producing multiple assets in a new anatomical scene family or rendering style, build and inspect one representative realistic rendered sample and a short motion preview for a time-evolving phenomenon. Record the actual files inspected, source geometry/material references, observed defects, repairs and a separate visual verdict. Use appropriately sized models/effort. This is a production inspection gate, not an additional user-permission gate or another full scientific review.

The sample must demonstrate source-checked anatomy and spatial relationships, credible tissue materials/surface detail, lighting and depth at the intended reader size. Motion must preserve anatomical relationships and agree with the stated physiological model; inspect intermediate frames for intersections, implausible deformation and flicker. Where plots accompany motion, derive both from a consistent state and distinguish presentation time from physiological time. Label reconstructions and synthetic behavior honestly; visual realism does not establish biological accuracy.

The user explicitly selected verified microscopy with controlled mechanism animations, adding realistic3D where it adds spatial insight. Choose the modality for the scientific task. Directly relevant, source-checked photography or microscopy can supply the anatomical appearance reference, paired with controlled SVG/JavaScript mechanisms, overlays and plots. State preparation, stain, species, scale and inference limits; a prepared image does not establish natural living color or transport kinetics. This observed-reference approach does not require fabricating a new 3D cellular scene. Conceptual engineering proposals and quantitative plots may use an explicitly justified schematic treatment without an anatomical appearance claim. Flat SVG anatomy, basic shaded primitives, or an unrelated photograph alone do not fulfill a required realistic anatomical illustration. New rendered anatomical styles still require the representative still and motion inspection above before scaling; failed prototypes remain unaccepted. Prefer animation for time-evolving phenomena, with accessible static/reduced-motion and print alternatives.

Do not scale a failed style or accept a chapter's required realistic assets solely because science reviews, code checks or browser checks passed. Repair and inspect the representative sample first, then inspect each delivered asset. If geometry, appearance or motion remains inadequate, record the visual requirement as pending rather than declaring the chapter fully accepted. Preserve editable scene/code sources, licenses and reproducible render instructions. A realistic image alone does not satisfy the motion preview for a time-evolving scene.

**Animation is the default when the phenomenon evolves over time.** Use SVG/JavaScript for mechanism, transport, feedback, gating, waves and synchronized plots; use Blender for anatomically grounded spatial motion and realistic rendering. Provide play/pause, replay, speed control and seeking/phase stepping as appropriate.

Static views support nomenclature, comparison, anatomical reference, print and accessible/reduced-motion use. Give figure images intrinsic dimensions and load required print figures eagerly; an offscreen lazy image can be absent from a print proof. They do not replace the preferred dynamic explanation. Labels, scale/orientation cues and the physical/presentation time mapping remain legible during playback.

Specify evidence for **geometry, behavior and appearance separately**:
- Anatomy: species/specimen, normal/pathological state, required structures, orientation, compartments and scale.
- Behavior: causal sequence, transport direction, phase timing, model equations/parameters or observed trajectory.
- Appearance: modality/preparation, tissue surface/material reference, illustrative colors and optical settings.
- Provenance: creator, accession/DOI, version, source URL, license, modifications, source asset hashes and build instructions.

Inspect the actual contents of an atlas asset before planning cuts or motion. An external surface does not establish internal valves, chambers or microstructure. If required internals are absent, use an explicitly identified sectional reconstruction checked against authoritative anatomy. Separate scales rather than invent continuous photographic access from organ to molecule.

Blender realism uses correct geometry and scene scale, appropriate roughness/scattering/surface detail and controlled lighting. Camera polish, denoising and upscaling do not validate anatomy. Inspect close-ups and temporal transitions for intersections, seams, flicker and loss of small structures. Keep labels crisp, preferably as a separate vector/HTML layer.

The HRA heart pilot is geometry/material calibration only. It retains the original asset; its current tissue material has not met the photorealism requirement. Prototype success is not production acceptance.

## Animation and model checks
Use an explicit clock, seeded randomness, reproducible frame sampling and one shared biological state for geometry/plots. Model parameters require source support or explicit synthetic labels. Tweening and rigid-body libraries are presentation tools, not evidence of physiological dynamics.

Check initial/intermediate/final states, actual motion, timing changes, controls, keyboard access, reduced motion, text alternatives and print fallback. Do not imply that every schematic particle is an accurately counted molecule or that an interpolated protein transition is an experimental trajectory.

## Review and acceptance
Perform separate scientific and visual checks. Each chapter receives two actual independent full scientific/editorial reviews bound to body/code/asset digests. Repair blockers and run targeted changed-content checks; a changed argument may justify renewed full review. Do not fabricate reviewer identities, reports, verdicts, acceptance or hashes.

Use the local reader assets and MathJax. Check math, definitions, links, anchors, code outputs and source provenance. Inspect actual browser rendering at desktop,650px and390px, and print/reduced-motion behavior. Mechanical passes do not establish scientific or teaching quality.

## Files and reproducibility
- chapter-manifest.json: canonical chapter/section/visual plan and status.
- source-manifest.json and lecture-inventory.csv: official recording inventory and coverage metadata.
- plan/: derived outline, architecture, result/notation ledger, visual plan and caption navigation map.
- spec/: reader/scope/house-style/source specification.
- assets/, figures/, code/: shared reader, production visual sources and executable teaching work.
- tools/: planning export, reader build, source acquisition and validation.
- index.html, source-map.html, references.html, code-lab.html: generated reader indices.
- sources/ and work/: private ignored raw evidence, frame sheets, working reports, reviews and prototypes.

Regenerate planning views with `python -X utf8 tools/export_plan.py`, reader pages with `python -X utf8 tools/build_book.py`, and development integrity with `python -X utf8 tools/validate_book.py`. Development validation explicitly reports pending work. `--release` must fail until all required acceptance evidence is present. Browser interaction checks are separate.

## Release
Publish only accepted chapters/assets, their provenance/licenses, reproducible code, reader tools and truthful validation reports. Exclude raw captions/videos/slides, private work/reviews, local paths, credentials and unrelated files. Preserve every third-party asset/dependency license; the animate-libs repository license does not replace the custom GSAP license.

After full-course acceptance, inspect the staged diff, push to the intended course repository, and verify the actual remote commit and live reader. User authorization to publish does not justify claiming incomplete work is complete.

Portable acceptance records are exported with `python -X utf8 tools/export_acceptance.py` only after actual private producer checks pass. At release run both `tools/validate_book.py --producer --release` and `tools/validate_book.py --public --release`. Public mode checks the current files against sanitized records under validation/acceptance without claiming access to private reports; producer mode requires the actual private reports. Never fall back from either failed mode to the other. See validation/README.md for evidence limits and reader commands.
