# Third-party visual and reader components

This register describes the current development assets. It does not certify scientific or visual acceptance. Original schematics and explanatory text are separate from the referenced photographs and geometry.

## Primary human fibroblast

- Public file: `ch01-cell-reference.jpg`, an unmodified 760 × 492 pixel JPEG.
- Matthew Daniels / University of Oxford; Wellcome Collection, accession B0007852.
- [Owning record](https://wellcomecollection.org/works/fmsmxyyh). [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Confocal micrograph of a stained primary human fibroblast: mitochondria red, nucleus yellow. The archive does not supply physical calibration, dye identities, culture protocol or live/fixed status in the checked record. These colors are image signals, not natural tissue appearance.
- SHA-256: `b91b04039956a7763c044386ce64d7b94b1a52cc959817877130bdec6a5696c7`.

## Human skin histology

- Public file: `ch01-cell-tissue-reference.jpg`, unmodified full-field JPEG.
- Kevin Mackenzie / University of Aberdeen; Wellcome Collection, accession B0009427.
- [Owning record](https://wellcomecollection.org/works/pbfv4uhw). [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Aldehyde fuchsin, Orange G and Light Green staining; archive identifies elastic fibres as purple and collagen as green to yellow. Full-field width is 400 micrometres. Body site, donor, fixation, section thickness, objective and instrument are not established by the checked record.
- SHA-256: `3179080646bbeaa391234196628efddcaa0b5d9ade8fc85b55faa326aa63f85c`.

The cell and tissue images are different specimens. They are not registered views of the same anatomical object at different magnifications. Machine-readable details are in [ch01-cell-reference.json](ch01-cell-reference.json).

## Generic exterior body

- Public renders: `ch01-body-front.png`, `ch01-body-side.png`, embedded in `ch01-body-orientation.svg`.
- MPFB 2.0.18 core basemesh and macro targets, rendered in Blender 5.2.1 LTS. MPFB core graphics are [CC0](https://static.makehumancommunity.org/about/license.html); the software license is distinct from the generated graphics. [MPFB licensing explanation](https://static.makehumancommunity.org/mpfb/faq/can_i_sell_models.html).
- Modifications: macro shaping, rigged anatomical pose, camera and lighting setup, explicit Blender material translation and separate vector annotations. This is a generic parametric male exterior, not a patient scan or population average. No internal organ geometry is inferred from it.
- Source: `figures/ch01_body_orientation.py` in the repository. Current appearance is illustrative and has not met the photorealism requirement. The [official MakeHuman system pack inventory](https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html) identifies the applied middleage_asian_male skin, brown eye texture and low-poly eye mesh as CC0. Asset headers also declare CC0, crediting Data Collection AB, Joel Palmius and Jonas Hauquier. The native UV atlas, MPFB attachment/fitting and Blender material translation were used; no measured roughness or displacement maps were supplied. Skin source SHA-256: `e897c4cc1b6ad5d10a7d2b2be92402feda4e772e6582dfaf0a1e8fc4621d8097`; eye texture SHA-256: `4659691c7295ad6206c78b003e5fd0e5f91dcd53032fa914a229bb48cabe424b`; eye OBJ SHA-256: `783fe1e6331162c876520b4c2bed7a8ca06354ca15497e8ebd68bb1b59f4d3de`. No clothing or organ meshes are incorporated. Catalogue labels do not establish specimen ancestry, age or photographic acquisition provenance.
- The accompanying cavity SVG is an original schematic construction; it is not a measured section through this exterior.

## MathJax

Local MathJax 3.2.2 TeX/SVG components retain their [Apache 2.0 license](mathjax/LICENSE). Component hashes are retained with the local distribution.

Animation libraries will be listed here if incorporated. Consulting the animate-libs repository does not transfer the license of any bundled library to this project.

## Anterior human photographs

- Public file: `ch01-anatomical-photo.jpg`, unmodified full composition (4089 × 4334 pixels).
- Actual studio photographs at City Studios, Stockholm, 29 September 2011, with KYO assistance; uploaded by Mikael Häggström. [Owning Commons record](https://commons.wikimedia.org/wiki/File:Anterior_view_of_human_female_and_male,_without_labels.jpg), [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). The owning record states both adult models agreed to the license and Wikipedia use; no separate release was independently obtained. No model endorsement is implied.
- The current archive derivative has a 2013 brightness correction; this project makes no JPEG modification. Both models show anterior palms and lateral thumbs; their feet turn outward slightly. Their appearance and stance are individual, with no population-normal or metric-calibration claim. The photograph is separate from the parametric 3D exterior and is not registered to any section or micrograph.
- SHA-256: `1b91adc388d3c8c1a5f3ae38b1742533e0642e26847e9b84793a976755d22cd2`. Machine-readable details: [ch01-anatomical-photo.json](ch01-anatomical-photo.json).
