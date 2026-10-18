# Security hardening review — 2026-10-16

Baseline: `e40a45ec2a074b90703b3b4b842c8a3adbd6ada3`.

## Follow-up privacy review — 2026-10-18

A real local HTTP request with a synthetic NETRC file demonstrated that account
searches automatically attached matching local credentials. Searches and
project-owned manifest/update downloads now use sessions with trust_env=False.
This blocks implicit netrc authentication, including requests redirect handling.
Explicit proxies remain supported; environment proxies and requests CA-bundle
variables are no longer inherited on these paths. TLS verification stays enabled.

The relevant suite passed 29 tests, including the new real-request credential
regression. Only a synthetic credential file was read by the pre-fix test, never
the user's real credentials. The Windows process still has the current user's
filesystem permissions; this hardening is not an OS sandbox.

## Fixes

Usernames such as `../outside` previously caused automatically named TXT, CSV and XLSX reports to be written outside the working/output directory. Three end-to-end CLI tests reproduced this with network calls mocked. Generated filenames now replace path separators, control characters and Windows-invalid characters, and guard reserved Windows device names. The search username and an explicitly requested `--output` path remain unchanged. Existing output overwrite behavior and possible sanitized-name collisions are unchanged.

CSV and XLSX exports previously accepted formula-looking untrusted values. Two additional CLI tests reproduced raw formula prefixes in CSV and formula cells in XLSX. Values are now written as text. XLSX URLs are plain strings instead of constructed HYPERLINK formulas; spreadsheet applications may still recognize URLs as links. The tests inspect files rather than launching Excel.

## Verification

Python 3.11 on Windows, with VIRTUAL_ENV and PATH set to the test environment:

```text
python -m pytest tests/test_report_paths.py tests/test_spreadsheet_security.py tests/test_version.py tests/test_unicode.py tests/test_probes.py tests/test_ux.py -q --basetemp=../pytest-sherlock-final2
```

**28 passed**, including the five newly added tests that failed before the relevant fixes. `git diff --check` passed. The final shared test environment dependency audit reported no known vulnerabilities; this is not a claim about every version allowed by the project's broad dependency constraints.

## Inspection and limitations

The main requests path does not disable TLS verification. The existing modified-target CI workflow already passes changed targets through an environment variable and disables checkout credential persistence, addressing the previously published interpolation flaw. No upstream CI workflows were executed by this local inspection.

The review covered request setup, report paths and exports, dynamic execution matches and CI configuration. It was not an exhaustive code/dependency audit or a public-site penetration test. Site manifests remain trusted configuration, network requests disclose query information to destinations, and matching usernames are not proof of a person's identity. Explicit output paths, filesystem symlink attacks by an already-local adversary, terminal escape sequences, and all possible spreadsheet re-import behaviors were not comprehensively hardened.
