# Local build evidence

Measured on 2026-10-01 with Python 3.12.10 on this Windows CPU environment.

- `python -m pytest -q`: 25 passed in 0.26 seconds.
- Offline editable installation succeeded with no runtime dependencies.
- Installed executable demo: fixtures, run, markdown report completed in
  0.7763597 seconds combined, including three process startups and report output.
- Demo returned 200 records, 120 lost, 40 won, 40 open; total opportunity value
  2000000 and lost opportunity value 1200000 GBP minor units.
- All six reasons returned exactly 20 planted IDs and 200000 minor units each.
- Independent expectations tests found all planted IDs with zero false positives.
- Corrupting one planted reason and amount changed results as expected.
- Repeated runs and markdown writes were byte-identical.
- Source, tests and documentation were scanned for em dash characters: none.

These are synthetic test results and local runtime measurements, not real
business results. No savings baseline, real accuracy trial, adoption evidence
or buyer evidence has been measured. The verdict is pending the two-week trial.

The first executable attempt exposed a Windows user-install scripts directory
outside PATH. Adding that directory for the validation session resolved it;
README documents the same setup and the module invocation alternative.
