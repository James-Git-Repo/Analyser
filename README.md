# Startup Evaluator 360

A production-ready CLI that evaluates startups with an LLM using:
- website evidence,
- structured founder answers,
- a configurable due-diligence framework (`verification_context`).

It is optimized for **market readiness** and **investor readiness** decisions.

---

## What it does

The tool:
1. fetches and parses website text from `website_url`,
2. combines it with your `answers` + `verification_context`,
3. asks the LLM for structured scoring,
4. normalizes results and applies local decision gates,
5. outputs reports in JSON + Markdown.

Outputs:
- `evaluation_report.json`
- `evaluation_report.md`

---

## Local run (recommended)

### 1) Prerequisites
- Python 3.10+
- Internet access
- LLM API key (OpenAI-compatible endpoint)

### 2) Set environment variables

```bash
export LLM_API_KEY="<your_api_key>"
export LLM_MODEL="gpt-4o-mini"
export LLM_API_BASE="https://api.openai.com/v1"
```

### 3) Prepare input
Use:
- `examples/startup_input.example.json`

### 4) Run

```bash
python3 startup_evaluator.py --input examples/startup_input.example.json
```

### 5) Check outputs
- `evaluation_report.json`
- `evaluation_report.md`

---

## General usage

```bash
python3 startup_evaluator.py \
  --input <input.json> \
  [--output evaluation_report.json] \
  [--markdown evaluation_report.md] \
  [--model gpt-4o-mini] \
  [--api-base https://api.openai.com/v1] \
  [--api-key <key>] \
  [--max-website-chars 12000] \
  [--dry-run]
```

### Important flags
- `--input` required input file
- `--dry-run` prints model payload without API call
- `--max-website-chars` limits website text sent to the model

---

## Input format

Required top-level fields:
- `website_url` (string)
- `answers` (object)
- `verification_context` (object)

`verification_context` supports both:
1. **Framework policy** (`framework_config`) used by local decision gates.
2. **Methodology body** (`framework_document`) used by the LLM as evaluation doctrine.

See:
- `examples/startup_input.example.json`
- `examples/verification_context.framework.json`

---

## Implemented evaluation framework (your requested one)

The repository now includes a machine-usable implementation of the complete framework you provided (Kaplan OUTSIDE-IMPACTS + Qubit + Seraf + Chicago Booth) in:

- `examples/verification_context.framework.json`

It includes:
- philosophy and core assumptions,
- OUTSIDE-IMPACTS mapping,
- 6-pillar weighted scorecard,
- score scale 1–5,
- pillar-level red flags and verification checks,
- decision thresholds (`Go`, `Conditional Go`, `No-Go`),
- due-diligence phase checklist,
- bias mitigation controls,
- source references.

---

## Scoring and decision logic

The script computes:
- per-criterion scores (1–10)
- readiness scores (market/investor/product support)
- weighted overall 1–10:
  - 40% market readiness
  - 40% investor readiness
  - 20% criteria average

Additionally, it applies **framework-based local decision gates** from `framework_config` using pillar scores (1–5):
- weighted pillar score,
- recommendation: `Go` / `Conditional Go` / `No-Go`,
- fatal flags and conditions.

---

## Run in GitHub (Actions)

Workflow file:
- `.github/workflows/startup-evaluator.yml`

How:
1. Push repository to GitHub.
2. Set repo secrets:
   - `LLM_API_KEY` (required)
   - `LLM_API_BASE` (optional)
3. Go to **Actions → Startup Evaluator → Run workflow**.
4. Provide `input_json` path.
5. Download artifacts:
   - `evaluation_report.json`
   - `evaluation_report.md`

---

## Troubleshooting

### API key missing
Set `LLM_API_KEY` or use `--api-key`.

### Website fetch fails
The tool continues with provided answers/context.

### API HTTP errors
Check model name, endpoint, authentication, and quota.

### Weak recommendations
Improve `verification_context` evidence quality (benchmarks, verified metrics, references, risk map).

---

## Project files
- `startup_evaluator.py` — evaluator CLI
- `.github/workflows/startup-evaluator.yml` — GitHub Action
- `examples/startup_input.example.json` — ready input template
- `examples/verification_context.framework.json` — full framework implementation
