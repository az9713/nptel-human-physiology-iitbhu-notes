# Acceptance evidence

The JSON files under `acceptance/` are portable producer attestations for accepted
chapter snapshots. They record manuscript and scientific-asset hashes, bounded
source-audit scope, two actual AI full-review identities and report hashes,
separately attributed targeted checks, and actual production-inspection scope.
They are not human expert certification or proof of scientific truth. Raw
captions, private reviews and browser proofs are excluded from the public reader.

Readers can check the portable records and local reader integrity offline:

```sh
python -X utf8 tools/validate_book.py --public
```

Development success permits explicitly pending work. A full-course release also
requires every chapter, planned visual, lab and source audit to be complete:

```sh
python -X utf8 tools/validate_book.py --public --release
```

The producer keeps the actual private reports and runs both independent modes:

```sh
python -X utf8 tools/validate_book.py --producer --release
python -X utf8 tools/export_acceptance.py
python -X utf8 tools/validate_book.py --public --release
```

Exporting verifies existing acceptance; it does not accept a chapter. A changed
body, asset, attribution, source audit or inspection scope invalidates its public
record. Public mode never falls back to private reports, and producer mode never
falls back to portable attestations. The records may cover an accepted subset
while the remaining course is still in progress.
