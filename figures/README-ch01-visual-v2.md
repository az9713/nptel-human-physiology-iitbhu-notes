# Rebuilding the Chapter 1 hierarchy and sketched plane lesson

Run `python -X utf8 figures/ch01_visual_v2.py` from the repository root.
Python's standard library is sufficient. The command reads the editable hierarchy
template, embeds the two retained PNG sketches in SVG plates and writes the
interactive hierarchy and three static plane views. It does not regenerate the
PNG artwork, edit its pixels, download anything or restore the retired unclothed
human photographs.

- `ch01_sketch_hierarchy.template.html`: editable cards, native controls, print,
  accessibility and explanation source; inline SVG placeholders are expanded by
  `ch01_planes_v2.py`.
- `assets/ch01-body-sketch-anterior.png` and `ch01-body-sketch-lateral.png`:
  original generated clothed line drawings, retained at 1024 by 1536 pixels.
- `assets/ch01-body-sketch-provenance.json`: exact generation prompts, hashes,
  source definitions, display geometry and limits.
- `assets/ch01-v2-plane-credits.html`: reader-facing credits and full-size sketches.
- Skin close-up, histology and fibroblast sources retain their own attribution
  in `assets/ch01-v2-provenance.json`; CT/MRI, microscopy and isolated organ
  specimens are outside this replacement request.

The plane traces are qualitative geometric guides. A shifted trace does not
expose an internal section, locate a measured displacement or establish
registration between the front and lateral illustrations. Broader visual
acceptance remains pending; this replacement does not reuse old scientific
review approvals for new artwork. Chapter prose and metadata are edited and
reviewed separately from this figure builder.
