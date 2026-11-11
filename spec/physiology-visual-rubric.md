# Physiological illustration and animation acceptance rubric

> **User-directed human-figure exception — 9 November 2026:** Replace photorealistic unclothed external human figures with anatomical sketches. Assess those figures for sketch quality, anatomy, reference directions and teaching clarity; their non-photographic appearance is intentional. CT/MRI, microscopy and isolated organ specimens retain their existing modality requirements. This exception does not waive accuracy, usability, provenance or other applicable checks.

Version 2.0 — 2026-11-08. This replaces the earlier visual acceptance standard.

The user rejected the published symbolic body/skin/tissue/cell drawings. They do
not satisfy the requested accurate, photorealistic textbook illustrations.
Working controls, mathematical checks, disclaimers and a photograph elsewhere in
the chapter cannot establish the quality of the illustration being assessed.

## Scope and decision rule

Inspect every displayed illustration, anatomical overlay, animation mode, inset,
thumbnail, enlarged view, video poster, static fallback and print figure. Reused
files need a review of every materially different crop, annotation and context.
An external link does not count as a delivered figure.

Each item below receives PASS, FAIL, PENDING or a specifically permitted N/A,
with evidence, the actual reviewer, date and exact delivered-file hashes. All
applicable items must PASS. There is no averaged score and no trade of realism
against accuracy. A missing proof is PENDING. FAIL or PENDING blocks completion.
An automated check can verify file integrity; it cannot certify photorealism.

Anatomy must be represented by a verified photograph/micrograph/scan or by a
source-grounded, professionally rendered anatomical reconstruction. Stick
figures, blobs, generic ellipses, block organs, floating labels and rectangles
connected by arrows are not substitutes for anatomical illustrations. Existing
microscopy is assessed too; it receives no automatic exemption.

For atomic-scale subjects, do not imply that a colored molecular rendering is a
visible-light photograph. Use experimentally supported coordinates and explicitly
defined representation conventions (assembly, atom selection, surface algorithm,
radii/probe, missing regions and illustrative colors). V05 still applies to the
quality and fidelity of the delivered molecular reconstruction: professional
surface detail, spatial readability and honest material/lighting conventions,
without invented tissue texture or a cartoon substitute for the actual fold.
Experimental resolution is distinct from render pixel resolution. A static
structure supplies neither a transport trajectory nor a kinetic rate.

Only a genuinely quantitative graph without anatomical imagery may mark the
photographic-appearance requirement N/A. It must instead meet the graph criteria.
An organ, membrane, cell or anatomical pathway cannot be relabelled a diagram to
evade the appearance requirement. Clear vector labels and arrows may accompany
realistic imagery. Microscopy colors must be identified as staining or modality
colors, rather than presented as natural tissue colors.

## Required checks

| ID | Criterion | Evidence required for PASS |
| --- | --- | --- |
| V01 | Teaching purpose | State the physiological question and the structures/relationships the figure must show; check against its paragraph and caption. |
| V02 | Anatomical authority | Name the owning atlas/dataset/paper, accession/version and relevant section/figure. Inspect the source itself. State human/animal, specimen, preparation and normal/pathological context. |
| V03 | Correct geometry | Check every named structure, topology, attachment, compartment, relative position, vessel/duct continuity, lumen and wall. A plausible silhouette is insufficient. Record a structure-by-structure comparison. |
| V04 | Orientation and scale | Verify side, view, axes, section plane and units. Use a justified scale bar or explicitly nonmetric reconstruction; never invent a measured scale or register unrelated specimens. |
| V05 | Photorealistic appearance | At native resolution and the intended reading size, compare to appropriate observed references. Check tissue-specific color, surface/microstructure, roughness, scattering, fluid/air interfaces and natural variation. No toy/plastic, low-poly or cartoon appearance. Record actual compared crops. For microscopy, verify preparation/optical appearance and preserve diagnostic detail. |
| V06 | Meaningful detail | Required physiological structures are visible and distinguishable. No decorative texture substituting for anatomy, invented pores, repeated generic cells, false internal cutaway or absent structure hidden by camera/lighting. |
| V07 | Physiological mechanism | Check direction, causal order, active/passive transport, energy coupling, pressure/current/sign conventions and source/destination compartments. A moving token does not by itself illustrate a mechanism. |
| V08 | Time representation | Use animation when the explanation requires evolution over time. Identify biological/model/presentation time and any speed changes. A montage or cross-fade is not a physiological simulation. N/A only for a static reference with no temporal teaching claim. |
| V09 | Motion and state consistency | Inspect beginning, middle, end and every distinct phase/transition. Geometry, labels, cursor, plots and readouts agree. Check contacts, intersections, membrane crossings, registration, jitter, flicker and loop seams. N/A only for static images. |
| V10 | Visual hierarchy and composition | Main subject and mechanism are immediately clear; useful close-ups and a coherent gross-to-micro route. No clutter, wasted empty card, decorative metaphor or misleading cinematic focus. |
| V11 | Labels and nomenclature | Correct terms and unambiguous leader endpoints; sufficient contrast and consistent color keys. Check actual effective label size at desktop/tablet/phone, enlarged view and print. Target at least 14 px at intended web reading size and 9 pt in print, or provide a tested accessible enlargement/pan view. |
| V12 | Resolution and image integrity | Native source resolution supports the delivery size. Aim for 300 ppi at intended print size; document a source-limited exception with a smaller figure rather than hallucinated upscaling. No compression artifacts, clipped anatomy or denoising that removes important detail. |
| V13 | Graph accuracy | For each plot, verify units, scales, ticks, legends, data/curve alignment and calculations. A graph should remain a precise graph, not a photorealistic decoration. N/A only when no graph is present. |
| V14 | Playback and access | Test play/pause, replay, seeking/stepping and speed as applicable, keyboard access, focus visibility, reduced motion and a useful still/text equivalent. A static photograph needs meaningful alt text and full-size access where detail matters. |
| V15 | Actual delivered layouts | Inspect the real page at desktop, 650 px and 390 px, plus the actual print/PDF output. No tiny unreadable labels, hidden required image, overflow without accessible panning, detached credit or clipped figure. Inspect native-size images as well as contact sheets. |
| V16 | Provenance and rights | Retain exact source URLs, creator, licence/notice, modifications, source hashes and attribution beside or directly linked from the image. Software licensing does not license a model or source image. No copied tutorial/video artwork without verified reuse rights. |
| V17 | Reproducibility | Keep editable scene/code, source-asset manifest, pinned tools, parameters, coordinate/unit transforms and deterministic seeds. Document separately acquired inputs honestly. Generated anatomy is not accepted solely on a model's verbal claim. |
| V18 | Evidence and claim alignment | Caption accurately describes what is observed, reconstructed, measured, hypothetical or synthetic. No inferred live dynamics from a still; no animal-to-human substitution or fictitious continuous zoom. A caveat does not excuse a visually inadequate figure. |
| V19 | Recorded critical review | Perform and record distinct anatomical/mechanism and appearance/teaching review passes on the exact final files. Name actual reviewers and scope; preserve defects and repairs. No fabricated expert approval, unseen-frame claims or acceptance inferred from test counts. |
| V20 | Complete coverage and delivery | Inventory every planned visual and every actual reachable visual surface, including nested runtime/print material. Bind all PASS evidence to current hashes; no unclassified or unreviewed item remains. Verify that the final local delivery bytes match the accepted files. Publication is a separate action and requires the user's explicit request; if authorized later, verify those published bytes too. |

## Per-visual record

Use `validation/visuals/records/<visual-id>.json` with: id, chapter/use locations,
visual class, teaching brief, required structures, geometry/appearance/behavior
sources separately, current artifact hashes, V01–V20 results and specific
evidence/reviewer/date, linked proof hashes, defects/repairs, and final status.
Allowed N/A is limited to the conditions in this table. Every result starts
PENDING. Classifying a file is not accepting it.

## Production procedure

1. Inventory and inspect the current delivery; identify rejected material.
2. Write a source-grounded anatomical and appearance brief before creating art.
3. Build a representative final-resolution still and motion sequence for each
   genuinely new visual family. Compare it to observed references. Do not scale
   an inadequate style over the whole book.
4. Prefer high-quality licensed photographs, microscopy and image-derived/atlas
   geometry. Use Blender for rendered anatomy and spatial motion; use SVG/JS for
   crisp overlays, exact plots and controls. Keep photographic detail underneath.
5. Review each final visual and its actual reader/print/motion presentation.
6. Resolve every applicable rubric item before declaring the book complete.

The Omi/Zack D. Films references guide surface craft, camera and rendering; they
are not anatomy authorities or evidence of physiological timing. Procedural skin
detail, subsurface scattering and postprocessing must match the chosen tissue
and scale, not be copied as universal biological parameters. No paid skill is
claimed to have been used.

## Methodological references

- [Animation Lab collaboration methods](https://animationlab.utah.edu/collaborate): integrate structure, localization, binding, stoichiometry and dynamics.
- [Liu et al., PLOS Biology (2022)](https://doi.org/10.1371/journal.pbio.3001731): annotate the evidence and uncertainty behind scientific animations.
- [Blender Principled BSDF](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html): tissue-material rendering tools; optical rendering is distinct from anatomical validation.
- [animate-libs](https://github.com/az9713/animate-libs): deterministic playback and review infrastructure; individual library licences remain applicable.

These sources inform the process, not certification of this book's figures.
