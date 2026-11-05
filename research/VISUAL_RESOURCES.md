# Physiology visualization: researched resource catalog

Checked 2026-11-04 (America/Los_Angeles). This is a candidate catalog, not a downloaded asset library or validation of a particular anatomical model. Verify each chosen entry, release, license, and software compatibility before production.

## Anatomy, tissues, and scientific illustrations

| Resource | Role in this project | Evidence and selection notes |
| --- | --- | --- |
| [Human Reference Atlas: 3D Reference Object Library](https://humanatlas.io/3d-reference-library) | Strong first candidate for reference organs, anatomical identifiers, and GLB geometry | The project describes specialist-created, organ-expert-approved objects and releases its reference objects under CC BY 4.0. Its stated source specimens also illustrate why an atlas model is a reference rather than a representation of every person. Inspect internal anatomy and resolution for the actual lesson. |
| [HRA digital visual assets](https://docs.humanatlas.io/visual-assets) | Bridge organ anatomy to functional tissue units | The catalog points to 2D functional tissue-unit illustrations, 3D functional tissue units, reference objects, and landmarks through the HRA Knowledge Graph Explorer and NIH services. Read the selected object's metadata and license. |
| [BodyParts3D / Anatomography license](https://lifesciencedb.jp/bp3d/info_en/license/index.html) | Labeled anatomical structures, bones, spatial context | The owning site states CC BY-SA 2.1 Japan and required credit. Preserve source IDs and license details; inspect a selected mesh's geometry and relationships rather than assuming scientific sufficiency from the database name. |
| [Z-Anatomy application and model links](https://github.com/LluisV/Z-Anatomy) | Candidate for a convenient organized anatomy atlas and Blender access | The app README provides Blender/FBX model links and a CC BY-SA 4.0 statement; its [license](https://github.com/LluisV/Z-Anatomy/blob/PC-Version/LICENSE) points onward for model-specific information. Verify the actual downloaded model provenance. An old `Z-Anatomy/Models` route returned 404 during research; do not build on that route without checking it. |
| [NIH BioArt Source FAQ](https://bioart.niaid.nih.gov/faqs) | Professional scientific illustrations, anatomy, cell scenes, reusable vector reference material | NIH describes work by medical illustrators in collaboration with subject matter experts. Entry licenses can be public domain or attribution-based; check each entry. Example candidates: [blood-vessel cross section](https://bioart.niaid.nih.gov/bioart/55) and [venule cross section](https://bioart.niaid.nih.gov/bioart/539). The entry classification is not a substitute for checking detail against the chapter's objective. |
| [Servier Medical Art](https://smart.servier.com/how-to-cite-servier-medical-art/) | Editable teaching illustrations, mechanism building blocks, anatomical context | Medical illustrations are CC BY 4.0. The [format FAQ](https://smart.servier.com/using-smart-images-what-you-can-do/) says downloads are PPTX or PNG, not native SVG. Inspect any extracted or converted vector elements and retain attribution/change notices. Do not describe these drawings as photorealistic anatomy. |
| [3D Slicer segmentation documentation](https://slicer.readthedocs.io/en/5.8/user_guide/modules/segmentations.html) | Optional image-derived anatomy when an atlas surface is insufficient | Documents segmentation export to surface models, including STL/OBJ. A possible route is appropriately licensed CT/MRI -> segmentation -> reviewed mesh -> Blender. Image acquisition resolution and segmentation uncertainty limit the geometry. The software's license does not grant rights to an external image dataset. |
| [The Cell: An Image Library](https://www.cellimagelibrary.org/docs/cell_image_library_flyer.pdf) | Candidate microscopy and video references for real cellular appearance | The repository describes vetted, annotated images and videos across organisms and modalities. Specific downloadable entries and reuse terms have not yet been selected or verified here. Choose by species, preparation, stain, resolution, and license; a generic visually similar texture is not equivalent. |

## Molecular structures and dynamic behavior

| Resource | Role in this project | Evidence and selection notes |
| --- | --- | --- |
| [RCSB PDB usage policies](https://www.rcsb.org/pages/usage-policy) | Experimental structural coordinates for channels, receptors, proteins, and complexes | PDB archive data and RCSB API data are CC0. Cite structure authors and accession IDs as scientific practice. The site distinguishes its data from articles and other material. Check organism, assembly, state, missing residues, ligands, and experimental support before using a structure as a particular physiological state. |
| [EMDB](https://www.ebi.ac.uk/emdb/) and [EMBL-EBI archive access statement](https://www.ebi.ac.uk/pdbe/about/public-data-access-statement) | Cryo-EM volumes and tomograms for molecular/cellular structural context | The archive access statement covers PDBe, EMDB, and EMPIAR under CC0 and site terms. Retain entry IDs and underlying publications. Map resolution and interpretation constrain any rendered surface. |
| [Molecular Nodes](https://github.com/BradyAJohnston/MolecularNodes) and [documentation](https://bradyajohnston.github.io/MolecularNodes/) | Bring structures, MD trajectories, electron-density/EM data, and molecular ensembles into Blender | An open-source Geometry Nodes-based tool. The repository lists supported Blender versions and flags the scripting API as experimental. Pin compatible releases; do not copy old tutorial API examples without checking them. Test structure scale and trajectory-to-frame mapping. |
| [OpenCOR](https://opencor.ws/) | Candidate physiology-model workflow for quantitative state trajectories | Its official page identifies an open-source modeling environment and links interactive sinoatrial/ventricular examples. Select and reproduce a particular model before coupling it to animation; verify model-specific provenance and licensing. A published model still has a defined physiological scope and limitations. |

## Scientific-animation methods worth studying

- [Janet Iwasa's Animation Lab: collaboration methods](https://animationlab.utah.edu/collaborate) describes integrating structures, localization, stoichiometry, dynamics, and binding evidence. This is a useful scientific complement to a short-video style reference.
- [Animation Lab: visual hypotheses](https://animationlab.utah.edu/) frames animations as representations of current mechanistic hypotheses. Use that distinction when a mechanism contains inferred motion or uncertain intermediates.
- [Phase Separation 101](https://animationlab.utah.edu/phase-separation) explicitly distinguishes its educational animations from molecular simulations and explains that timescales were slowed for teaching. Adopt the practice of disclosing altered timing. The page was reviewed for methodology, not used here to establish physiology-course content.
- [Animation Lab projects](https://animationlab.utah.edu/projects) identifies ProteinBlender as another tool to investigate if molecular animation becomes central. Its actual install, license, and integration have not been evaluated in this project. Treat as a follow-up candidate.

## Rendering and web delivery

- [Blender subsurface scattering manual](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/sss.html?highlight=subsurface+scattering): skin/tissue optical appearance, scale/radius parameters, and the limitations of scattering on imperfect meshes. Do not reuse one tissue's material parameters as universal physiology constants.
- [Blender display transforms](https://docs.blender.org/manual/en/5.0/render/color_management/displays_views.html): AgX and Khronos PBR Neutral serve different rendering goals. Compare references and preserve the selected color workflow across output formats.
- [MPFB on Blender Extensions](https://extensions.blender.org/add-ons/mpfb/): an open-source human-character system with procedural skin, rigging, and human-shape controls, already used by the local Omi project. Suitable for outer body context; it does not supply validated internal physiology. Check each optional asset pack separately.
- [animate-libs](https://github.com/az9713/animate-libs): deterministic JavaScript animation and export/review infrastructure. [Vendored library notes](https://github.com/az9713/animate-libs/blob/main/plugins/animate-libs/skills/animate-libs/libs/README.md) document bundle contents, license distinctions, and historical demo checks.
- [Three.js AnimationMixer](https://github.com/mrdoob/three.js/blob/dev/docs/pages/AnimationMixer.html): reference for time-based clip evaluation. Current loader/mixer documentation was also retrieved through Context7 during research. A production viewer must be tested for the selected GLB and animations.
- [GSAP standard license](https://gsap.com/community/standard-license/): a custom no-charge license with restrictions. Do not label the entire vendored stack MIT or uniformly open source.

## Local Omi evidence and limits

Read-only source project: `the user's separate ultra-realistic Blender reference project`.

| Inspected item | What it contributed |
| --- | --- |
| `README.txt` | Zack D. Films channel and two reference-short URLs |
| `transcript.txt` | Saved transcript and URL for Omi's [ultra-realistic 3D tutorial](https://www.youtube.com/watch?v=_fIoJ_ywGfY); describes reference analysis, asset sourcing, realism work, and render optimization |
| `HANDOFF.md` | Decisions, historical production state, known defects, and an explicit statement that the paid skill was not used |
| `beats.md` | Measured camera/visual beats and a useful instance of checking measurements against a tutorial's claims |
| `tools/build_scene.py` | Relevant inspected code for procedural skin, scattering, shape keys, hair curves, camera/render configuration |
| `tools/post.py` | Resizing, blue-background composition, blur, glow, vignette, and grain |
| `build/compare_latest.png` | Four reference/render still pairs visually inspected; the handoff says this comparison predates some later scene edits |

The project was not changed. No render was started, resumed, or certified complete during this investigation. Its timing measurements were not rebenchmarked. The saved tutorial is a creator's description of a recreation workflow, not proof of the original Zack D. Films production tools or the accuracy of every biological claim.

## Selection rule

For each figure, seek three forms of support independently: evidence for the structure, evidence for the behavior, and evidence for the displayed appearance. A compelling material, a reputable mesh, and a smooth animation can each be good while still being mismatched to one another or to the lesson. The figure brief and acceptance record should expose those mismatches before release.

## OpenSim joint models — additional candidate

[Official OpenSim musculoskeletal model catalog](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090607/Mus) links geometry and explicit joint definitions. This may supply a stronger source for joint motion than an arbitrary hinge animation. Selected model files, revision and asset-specific license still require verification. [Gait2392 documentation](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53086215/Gait+2392+and+2354+Models) identifies a patella omission and the catalog warns about high-flexion accuracy. [Lower Limb Model2010](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53087777/Lower+Limb+Model+2010) is another candidate to inspect. These are model candidates, not validated complete joint anatomy, tissue appearance or cartilage-contact predictions.

## Thyroglobulin condensates — candidate observed dynamics

[Yao et al., Communications Biology8,466(2025)](https://www.nature.com/articles/s42003-025-07909-z) supplies in-vitro condensate experiments and fixed cultured mouse/human follicle imaging. The human material came from treated Graves disease, not a healthy living-tissue sample. Supplementary movies are listed; selected movie bytes and per-file credits have not been inspected. The article states CC BY4.0 with third-party exclusions; [Cambridge owning repository](https://www.repository.cam.ac.uk/items/c577e39f-0e70-496d-b7ec-45ffb6e24fdd) independently lists CC BY4.0. Main publisher HTML retrieval redirected to authentication; the publisher PDF and indexed Results/Methods and repository rights page were readable. One47.71MB supporting-file route timed out in web retrieval, and a separate HEAD request returned text/html rather than verified media. No movie was acquired, displayed or accepted. This is a possible source for an explicitly labeled research extension and appearance/behavior reference; it does not establish physiological timing or satisfy the pending realistic-scene gate.
