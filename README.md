# Startup Evaluator 360

Production-oriented CLI tool to evaluate a startup with an LLM, with primary focus on:

- **Market readiness**
- **Investor readiness**

The tool combines:
1. startup website analysis,
2. structured founder answers,
3. benchmark/verification context,

and returns a structured assessment with scoring, competitive positioning, product attractiveness, and Switzerland-specific commercialization/investor readiness insights.

---

## What this tool does

Given one input JSON, the evaluator:

- fetches and parses text from the startup website,
- sends all evidence to an LLM API (OpenAI-compatible),
- scores all 35 framework criteria,
- performs relative analysis vs existing alternatives,
- estimates readiness for the Swiss context,
- writes machine-readable and human-readable reports.

Output files:

- `evaluation_report.json`
- `evaluation_report.md`

---

## Requirements

- Python **3.10+**
- Network access to the configured LLM endpoint
- A valid API key for your model provider

No third-party Python dependencies are required (standard library only).

---

## Quick start

### 1) Configure environment variables

```bash
export LLM_API_KEY="<your_api_key>"
export LLM_MODEL="gpt-4o-mini"
export LLM_API_BASE="https://api.openai.com/v1"
```

### 2) Prepare input JSON

Use the template:

- `examples/startup_input.example.json`

### 3) Run evaluation

```bash
python3 startup_evaluator.py --input examples/startup_input.example.json
```

You should see output paths and overall weighted score in terminal.

---

## CLI reference

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

### Arguments

- `--input` (**required**): input JSON path.
- `--output`: JSON output file path (default `evaluation_report.json`).
- `--markdown`: Markdown output file path (default `evaluation_report.md`).
- `--model`: model name override (default from `LLM_MODEL`).
- `--api-base`: base URL override (default from `LLM_API_BASE`).
- `--api-key`: API key override (default from `LLM_API_KEY`).
- `--max-website-chars`: cap on extracted site text sent to model.
- `--dry-run`: prints final prompt payload (debug only), no API call.

---

## Input format

Top-level required keys:

- `website_url` (string)
- `answers` (object)
- `verification_context` (object)

### Minimal example

```json
{
  "website_url": "https://example.com",
  "answers": {
    "problem_solution": "What problem you solve and how",
    "traction": "Customers, pilots, retention, revenues",
    "economics_drivers": "Pricing, margins, CAC payback"
  },
  "verification_context": {
    "benchmark_references": ["source A", "source B"],
    "quality_rules": ["rule A", "rule B"],
    "additional_verification_info": "any extra validation guidance"
  }
}
```

Use richer evidence whenever available (unit economics, pipeline quality, deployment metrics, legal/IP status, compliance roadmap).

---


## Advanced: implement your full VC framework directly

You can encode your full methodology inside `verification_context.framework_config`:

- `pillar_weights` (Team/Market/Product/Traction/UnitEcon/DealRisk)
- `decision_thresholds` (`go_min_weighted`, `conditional_min_weighted`, fatal gates, min pillar scores)
- `required_evidence_by_pillar`
- `red_flags`
- `bias_checks`

The evaluator now:

1. passes this framework to the model in prompt context;
2. requests `pillar_scores_1_to_5` and `investment_decision`;
3. recomputes decision gates locally (`Go`, `Conditional Go`, `No-Go`) from your thresholds;
4. writes decision, conditions, and fatal flags into JSON/Markdown output.

See `examples/startup_input.example.json` for a complete template.

## Output structure (high level)

`evaluation_report.json` includes:

- `scores`: per-criterion scoring for all framework criteria
- `criteria_average_score`
- `overall_score` (weighted)
- `readiness_focus`
  - `market_readiness_score`
  - `investor_readiness_score`
  - `product_backend_support_score`
- `product_market_fit_analysis`
  - product type, attractiveness, IP intensity, scalability, regulatory/economic tailwind
- `relative_analysis`
- `switzerland_readiness`
- `priority_actions`
- `brief_report_it` (max 200 words)

`evaluation_report.md` presents the same in a readable report format.

---

## Scoring logic

The tool computes:

- `criteria_average_score`: mean of criterion scores
- `overall_score` (weighted):
  - 40% market readiness
  - 40% investor readiness
  - 20% criteria average

This keeps evaluation aligned with fundraising and commercialization readiness, while still grounding on full framework evidence.

---

## Practical guidance for better results

1. **Use auditable evidence**: customer references, contracts/LOIs, real KPI logs.
2. **Add benchmark quality**: public comparables, market studies, competitor matrices.
3. **Be explicit on risks**: what is validated vs assumptions.
4. **Include Swiss constraints**: certifications, procurement cycle, channel setup, legal/regulatory path.
5. **Keep claims measurable**: avoid generic statements without numbers.

---

## Troubleshooting

### `API key mancante`
Set `LLM_API_KEY` or pass `--api-key`.

### Website fetch fails
The script continues with provided answers/context. Check URL reachability and retry.

### HTTP API errors
Verify model name, endpoint, authentication, and provider quota limits.

### Low-quality output
Improve `verification_context` with stronger references and stricter quality rules.

---

## Repository files

- `startup_evaluator.py` — main CLI evaluator
- `examples/startup_input.example.json` — sample input template
- `README.md` — this documentation

---

## GitHub implementation (run in Actions)

This repository includes a ready-to-run GitHub Action:

- Workflow file: `.github/workflows/startup-evaluator.yml`
- Trigger: **Actions → Startup Evaluator → Run workflow**
- Input: path to your input JSON in repo
- Output: `evaluation_report.json` and `evaluation_report.md` as downloadable artifacts

### Required GitHub Secrets

Set these in **Settings → Secrets and variables → Actions**:

- `LLM_API_KEY` (**required**)
- `LLM_API_BASE` (optional, defaults to `https://api.openai.com/v1`)

Optional runtime input in workflow UI:

- `model` (default: `gpt-4o-mini`)
- `max_website_chars` (default: `12000`)
