# Security Policy

## Scope
File Integrity Checker hashes local files and reads/writes baseline metadata. It does not require network access, credentials, or elevated privileges.

## Reporting
Please report security concerns privately to the maintainer through an appropriate private GitHub contact channel when available; do not publish exploit details before a fix can be prepared.

## Security model
- Treat baseline JSON files as trusted security metadata and protect them from unauthorized modification.
- The tool never follows symbolic links during directory scanning.
- Baseline replacement requires explicit `--overwrite`.
- Baseline files are written through a temporary file and atomically replaced on supported filesystems.
- Do not run the tool with more filesystem privilege than required.

SHA-256 comparison establishes content equality against the supplied baseline; it does not authenticate that baseline, scan malware, or prove file origin.

Maintainer: **Radwan Abdulhadi Ahmed / @rad03i2**
