# Lost Deal Analyzer

Identify recorded reasons opportunities fail using a deterministic Python CLI.
For Henry's technical outbound operation. No network, model, GPU, or database.

Hypothesis: explicit inputs, planted ground truth and named failure modes make
recorded loss analysis trustworthy. This build tests aggregation accuracy, not
whether recorded explanations establish causality or improve outreach revenue.

## Quickstart

Python 3.10 or later and setuptools are required. Runtime has no dependencies.
Install locally without contacting a package index:

```powershell
python -m pip install --no-deps --no-build-isolation -e .
lda fixtures --out demo
lda run --input demo
lda report --format md
python -m pytest -q
```

If Windows installs the user script directory outside PATH, enable it for the
current PowerShell session before using `lda`:

```powershell
$scriptsPath = python -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
$env:PATH = "$scriptsPath;$env:PATH"
```

Alternatively, replace `lda` with `python -m lost_deal_analyzer.cli`.

pytest is a development prerequisite. JSON is the only supported input format.
The fixture has 200 synthetic records: 120 lost, 40 won, 40 open, each with
10000 GBP minor units of opportunity value. Six loss groups each contain 20
records and 200000 minor units. Total value is 2000000 and lost value 1200000.
These are invented test values, never Henry's measured business results.

## Input reference

Place JSON documents in one directory. Each document uses exactly these fields:

```json
{
  "synthetic": false,
  "provenance": "Henry's own data, entered by him",
  "as_of": "2026-09-30",
  "currency": "GBP",
  "records": [
    {"id": "deal-1", "name": "Example only", "status": "lost",
     "reason": "budget", "amount_minor": 10000, "closed_on": "2026-09-29"}
  ]
}
```

The example above is illustrative schema documentation, not real trial data.
Use `synthetic: false` only for Henry's own hand-entered records. Invented data
must use `synthetic: true` and `provenance: "synthetic fixture"`.
Actual trial data and results are kept outside the committed repository.

Statuses: `lost`, `won`, `open`. A lost record requires one recorded reason:
`budget`, `timing`, `competitor`, `no_fit`, `no_response`, or `unknown`.
Choose `unknown` when evidence is missing. Won and open records require null
reason. Closed outcomes require a valid ISO date no later than the document's
explicit `as_of` date; open records require null `closed_on`.
The observation date is supplied by the user, not derived from the system clock.

IDs must be unique across all files. IDs and names allow Unicode and Windows
paths, up to 10000 characters, without control characters or em dash characters.
Amounts must be integers between 0 and 1000000000000000 inclusive in currency
minor units. Booleans, negative amounts, unknown fields and mixed currencies
are rejected. Currency must be three uppercase letters; no conversion occurs.
Zero is permitted but cannot distinguish a missing amount from an actual zero.

Empty directories produce zero reports. Every top-level file is input except
`expectations.json` and `SYNTHETIC.md`, reserved fixture metadata filenames.
Subdirectories are ignored. Unsupported formats fail explicitly.

## Subcommands

| Command | Example | Result |
| --- | --- | --- |
| fixtures | `lda fixtures --out demo` | Labelled synthetic set and independent expectations |
| run | `lda run --input demo --state .lda/result.json` | Validates, computes, saves result and prints JSON |
| report | `lda report --format json --out report.json` | Renders last saved result with provenance |
| reasons | `lda reasons --input demo` | Computes recorded reason counts, values and supporting IDs |
| audit | `lda audit --input demo` | Validates all input and prints reconciled computed totals |

Each command supports `--help` with an example. Report supports `md` and `json`.
Input errors return exit code 2. Parse errors name file and line; schema errors
name file, record and offending field. Missing input includes a usage hint.
Output replacement is atomic; write failures retain the old destination and
remove temporary files. The output directory must exist for report output.
A failed run retains the previous saved result; its provenance identifies its
original source files. Rerun successfully before treating it as current data.

## Architecture

```text
fixtures.py -> labelled JSON + independent expectations
input directory -> cli.py (parse) -> core.py (validate + aggregate)
                                -> atomic .lda/result.json
saved result -> report.py -> markdown / JSON with provenance
```

Core logic has no I/O. Aggregation uses exact integers. Reason totals reconcile
to lost counts and values; all status counts reconcile to total records.
Source names, observation dates and IDs make figures traceable to inputs.
Output has no timestamps or randomness. No seed is needed. The same input and
filenames produce byte-identical output, regardless of directory enumeration.

## Honesty boundary and fixture labels

The tool computes from explicit inputs. It does not discover, predict or estimate
causes. Recorded labels can be wrong. No response is an observed outcome, not
proof of disinterest. Opportunity value is not lost revenue or money saved.
Time saved and money saved are unmeasured and refused by omission with an
explicit statement in every report. No hypothetical benefit is reported.
Mixed real and synthetic files are identified individually in the banner.

JSON has no comments, so every generated JSON file contains `synthetic: true`
and a textual synthetic label. The companion Markdown starts with a synthetic
header comment. Every report repeats source provenance, including empty input.
The expectations file is independent of engine output. Corrupting a planted
record changes report figures, demonstrating that totals are computed.

## Evidence and two-week improvement hook

Acceptance: all tests green, exact planted counts and IDs with zero false
positives, exact amount reconciliation, and the full fixture demo under 5 seconds.
See EVIDENCE.md for local results. Synthetic accuracy does not establish real
world accuracy or actual usage. There has been no real-data trial in this build.

After two weeks of real use, hand-check a sample of recorded loss classifications
against Henry's underlying evidence. Record sample size, disagreements, error
rate (disagreements / sample size), days used, run count and the top failure cause
in a private trial log. If error exceeds 10 percent, fix that cause and recheck
or kill with a recorded reason. If unused, record why and kill. Zero sample size
means accuracy is unmeasured, never zero error. Optional time savings require
timed baseline and tool runs on the same task; otherwise remain unmeasured.

Verdict is pending the two-week evidence window, not invented at build time.
Record one of: expand for daily use or revenue; integrate for substantial sibling
overlap; commercialise for a buyer willing to pay as-is; maintain as portfolio
evidence otherwise; kill for no use or unmet acceptance criteria. Include the
reason and measured evidence. No publication is performed by this build.
