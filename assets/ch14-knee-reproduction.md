# Knee visualization reproduction

The interactive viewer reads the published geometry binary, geometry JSON and
saved-pose JSON locally. Serve the repository with an HTTP server; opening the
HTML with a `file:` URL may block its data requests.

To regenerate the printed reference projection, install NumPy and Pillow and run
`python -X utf8 figures/ch14_knee_reference.py`. This reads only published assets,
checks the binary digest and uses the shared deterministic software painter in
`figures/ch14_knee_pack.py`. It preserves source coordinates and draws artificial
structure colors. It performs no finite-element simulation or contact analysis.

The full source-packing command in `figures/ch14_knee_pack.py` is a separate
producer workflow. It requires the acquired geometry archive and private native
motion inputs/audit records. `code/ch14_knee_kinematics.py` documents the decoder.
The raw compact motion download is not redistributed here: its model/log files
include upstream absolute filesystem paths. Thus a clean public checkout can
replay the published saved states and regenerate the reference still; it cannot
independently recreate the native-log audit without reacquiring those inputs.

The missing original volume mesh and the native FEBio 2.9.1 versus checked v3
convention boundary prevent a claim of exact simulation reproduction. Source
coordinates, saved poses and reported joint-coordinate scalars remain distinct
from experimentally verified knee motion. Preserve both dataset notices in
`ch14-knee-viewer-LICENSE.txt`, the separate MRI attribution/license, and the
osteocyte image provenance.
