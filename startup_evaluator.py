#!/usr/bin/env python3
"""Valutatore startup a 360° con scoring eseguito da LLM via API."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from html import unescape
from typing import Any
from urllib import error, request


@dataclass
class Criterion:
    id: str
    category: str
    question: str


CRITERIA = [
    Criterion("problem_solution", "Problema & Soluzione", "Problema che affronta e soluzione che presenta"),
    Criterion("competition_innovation", "Competizione & Innovazione", "Competizione (quanto innovativo e più efficace è rispetto a soluzioni simili)"),
    Criterion("impact_1y_5y", "Impatto", "What 1-year and 5-year impact do you hope to accomplish, including the benefit to society?"),
    Criterion("impact_metrics", "Impatto", "What measures will you use to track impact, such as revenue, profit, CO2/emissions removed, or lives saved?"),
    Criterion("roadmap_5y", "Roadmap", "What is your 5-year roadmap, including major phases, milestones, and scale targets?"),
    Criterion("market_definition", "Mercato", "How would you define your potential market?"),
    Criterion("tam", "Mercato", "What is the total addressable market size?"),
    Criterion("traction", "Traction", "What traction have you achieved to date in terms of market validation?"),
    Criterion("prototype_evidence", "Traction", "What evidence do you have that your prototype or solution works?"),
    Criterion("demo_available", "Traction", "Is a live demonstration, virtual demo, site visit, or product video available?"),
    Criterion("value_proposition", "Go-To-Market", "What is your value proposition to customers?"),
    Criterion("marketing_message", "Go-To-Market", "What will your core marketing message be to users and customers?"),
    Criterion("message_spread", "Go-To-Market", "How do you plan to spread that message?"),
    Criterion("channels", "Go-To-Market", "Which sales, distribution, or partnership channels will you use to reach customers?"),
    Criterion("current_competitors", "Competitor Landscape", "Which organizations compete with your current value offering?"),
    Criterion("future_competitors", "Competitor Landscape", "Which organizations might compete with you in the future?"),
    Criterion("complements", "Ecosistema", "Which organizations or products complement your offering in the market?"),
    Criterion("value_chain_partners", "Ecosistema", "What value chain partners do you already know of or anticipate?"),
    Criterion("advantages", "Moat", "What are your primary advantages relative to existing or potential competitors?"),
    Criterion("win_reason", "Moat", "Why will you win in the market?"),
    Criterion("economics_drivers", "Economics", "What are the key drivers of your business economics, such as price points, margins, and cost structure?"),
    Criterion("energy_economics", "Economics", "How does energy consumption affect your business economics?"),
    Criterion("modular_scalability", "Tecnologia & Scalabilità", "How does your modular architecture support scalability and economics?"),
    Criterion("on_site_installation", "Tecnologia & Scalabilità", "How does on-site installation improve cost, efficiency, or customer value?"),
    Criterion("lead_time_deployment", "Tecnologia & Scalabilità", "How do lead time and plug-and-play deployment affect the business model?"),
    Criterion("ip_existing", "IP", "What intellectual property exists for your business or in your industry?"),
    Criterion("ip_protection", "IP", "How is your core technology or know-how protected?"),
    Criterion("ip_strategy", "IP", "What is your current or planned IP strategy?"),
    Criterion("regulatory_requirements", "Regolatorio", "What regulatory requirements apply to your business or industry?"),
    Criterion("regulatory_compliance", "Regolatorio", "How will you ensure compliance with production, certification, safety, and permitting requirements?"),
    Criterion("team_background", "Team", "What are the backgrounds of your team members?"),
    Criterion("team_fit", "Team", "What makes your team uniquely qualified to succeed?"),
    Criterion("advisors", "Network", "What current or anticipated advisors support the venture?"),
    Criterion("investors", "Network", "What current or anticipated investors support the venture?"),
    Criterion("funding_milestones", "Funding", "What funding milestones, strategic partnerships, or investor discussions are currently in progress?"),
]

SYSTEM_PROMPT = """You are a venture evaluation analyst.
Output MUST be valid JSON only, without markdown fences.
You evaluate startup quality on each criterion from 1-10 using evidence provided.
If evidence is weak, score lower and explicitly explain what is missing.
Perform relative analysis against existing and adjacent competing solutions.
Assess if the company is investor-ready and commercial-ready specifically for Switzerland.
Use concise, concrete rationales.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valuta startup via LLM API su framework 35 criteri.")
    parser.add_argument("--input", required=True, help="Path JSON con website URL, risposte ai criteri e benchmark.")
    parser.add_argument("--output", default="evaluation_report.json", help="File JSON output.")
    parser.add_argument("--markdown", default="evaluation_report.md", help="File Markdown output.")
    parser.add_argument("--model", default=os.getenv("LLM_MODEL", "gpt-4o-mini"), help="Nome modello API.")
    parser.add_argument("--api-base", default=os.getenv("LLM_API_BASE", "https://api.openai.com/v1"), help="Base URL API compatibile OpenAI.")
    parser.add_argument("--api-key", default=os.getenv("LLM_API_KEY"), help="API key. In alternativa usare env LLM_API_KEY.")
    parser.add_argument("--max-website-chars", type=int, default=12000, help="Numero massimo di caratteri da estrarre dal sito web.")
    parser.add_argument("--dry-run", action="store_true", help="Stampa payload senza chiamare API.")
    return parser.parse_args()


def clean_html(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_website_text(url: str, max_chars: int) -> str:
    req = request.Request(url, headers={"User-Agent": "StartupEvaluator/1.0"}, method="GET")
    with request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="ignore")
    return clean_html(raw)[:max_chars]


def load_input(path: str, max_website_chars: int) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required = ["website_url", "answers", "verification_context"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Campi obbligatori mancanti in input JSON: {', '.join(missing)}")

    website_text = ""
    website_error = None
    try:
        website_text = fetch_website_text(data["website_url"], max_chars=max_website_chars)
    except Exception as exc:  # network/website issues should not block run
        website_error = str(exc)

    data["website_content"] = {
        "url": data["website_url"],
        "text_excerpt": website_text,
        "fetch_error": website_error,
    }
    return data


def build_user_prompt(data: dict[str, Any]) -> str:
    schema = {
        "scores": [
            {
                "criterion_id": "string",
                "question": "string",
                "category": "string",
                "score": "int 1-10",
                "rationale": "string (max 50 words)",
                "evidence_strength": "low|medium|high",
                "verification_checks": ["string"],
                "benchmark_comparison": "string (max 40 words)",
            }
        ],
        "relative_analysis": {
            "existing_alternatives": ["string"],
            "functional_gap_vs_market": "string",
            "differentiation_score": "int 1-10",
        },
        "switzerland_readiness": {
            "investor_ready_score": "int 1-10",
            "commercial_ready_score": "int 1-10",
            "top_blockers": ["string"],
            "recommended_next_steps": ["string"],
            "swiss_regulatory_notes": ["string"],
        },
        "overall_score": "float 1-10",
        "brief_report_it": "string in Italian, max 200 words",
        "priority_actions": ["string", "string", "string"],
    }
    prompt_payload = {
        "criteria": [asdict(c) for c in CRITERIA],
        "website_content": data["website_content"],
        "answers_to_criteria": data["answers"],
        "verification_context": data["verification_context"],
        "target_market_focus": "Switzerland",
        "output_schema": schema,
        "instructions": [
            "Use website content + provided answers + verification references.",
            "Do not invent customers, revenues, patents, or regulatory approvals.",
            "If uncertain, state uncertainty and reduce score accordingly.",
            "Ensure every criterion_id appears exactly once.",
            "Relative analysis must compare against known solution categories and direct alternatives.",
            "Swiss readiness must include practical investor/commercial blockers and next 90-day actions.",
        ],
    }
    return json.dumps(prompt_payload, ensure_ascii=False)


def call_llm(*, api_base: str, api_key: str, model: str, user_prompt: str) -> dict[str, Any]:
    if not api_key:
        raise ValueError("API key mancante. Usa --api-key o env LLM_API_KEY.")
    url = api_base.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as e:
        details = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Errore HTTP API ({e.code}): {details}") from e

    content = body["choices"][0]["message"]["content"]
    return json.loads(content)


def normalize_result(result: dict[str, Any]) -> dict[str, Any]:
    by_id = {c.id: c for c in CRITERIA}
    id_order = {c.id: i for i, c in enumerate(CRITERIA)}
    seen = set()
    normalized_scores = []

    for item in result.get("scores", []):
        cid = item.get("criterion_id")
        if cid not in by_id or cid in seen:
            continue
        seen.add(cid)
        score = item.get("score", 1)
        if not isinstance(score, int):
            try:
                score = int(round(float(score)))
            except Exception:
                score = 1
        score = max(1, min(10, score))
        crit = by_id[cid]
        normalized_scores.append(
            {
                "criterion_id": cid,
                "question": crit.question,
                "category": crit.category,
                "score": score,
                "rationale": item.get("rationale", ""),
                "evidence_strength": item.get("evidence_strength", "unknown"),
                "verification_checks": item.get("verification_checks", []),
                "benchmark_comparison": item.get("benchmark_comparison", ""),
            }
        )

    for cid in [c.id for c in CRITERIA if c.id not in seen]:
        crit = by_id[cid]
        normalized_scores.append(
            {
                "criterion_id": cid,
                "question": crit.question,
                "category": crit.category,
                "score": 1,
                "rationale": "Criterio non valutato dal modello.",
                "evidence_strength": "low",
                "verification_checks": ["Completare dati in input."],
                "benchmark_comparison": "N/A",
            }
        )

    normalized_scores.sort(key=lambda x: id_order[x["criterion_id"]])
    overall = round(sum(s["score"] for s in normalized_scores) / len(normalized_scores), 2)
    report = str(result.get("brief_report_it", "")).strip()
    if len(report.split()) > 200:
        report = " ".join(report.split()[:200])

    swiss = result.get("switzerland_readiness", {})
    relative = result.get("relative_analysis", {})

    return {
        "scores": normalized_scores,
        "overall_score": overall,
        "brief_report_it": report,
        "priority_actions": result.get("priority_actions", [])[:3],
        "relative_analysis": {
            "existing_alternatives": relative.get("existing_alternatives", []),
            "functional_gap_vs_market": relative.get("functional_gap_vs_market", ""),
            "differentiation_score": max(1, min(10, int(relative.get("differentiation_score", 1) or 1))),
        },
        "switzerland_readiness": {
            "investor_ready_score": max(1, min(10, int(swiss.get("investor_ready_score", 1) or 1))),
            "commercial_ready_score": max(1, min(10, int(swiss.get("commercial_ready_score", 1) or 1))),
            "top_blockers": swiss.get("top_blockers", []),
            "recommended_next_steps": swiss.get("recommended_next_steps", []),
            "swiss_regulatory_notes": swiss.get("swiss_regulatory_notes", []),
        },
    }


def write_markdown(path: str, final: dict[str, Any]) -> None:
    lines = [
        "# Startup Evaluation Report",
        "",
        f"**Overall score:** {final['overall_score']}/10",
        f"**Differentiation score:** {final['relative_analysis']['differentiation_score']}/10",
        f"**Switzerland investor-ready:** {final['switzerland_readiness']['investor_ready_score']}/10",
        f"**Switzerland commercial-ready:** {final['switzerland_readiness']['commercial_ready_score']}/10",
        "",
        "## Scores by Criterion",
        "",
        "| # | Category | Question | Score | Evidence |",
        "|---|---|---|---:|---|",
    ]
    for i, s in enumerate(final["scores"], start=1):
        lines.append(f"| {i} | {s['category']} | {s['question']} | {s['score']} | {s['evidence_strength']} |")

    lines.extend(["", "## Relative analysis", ""])
    for alt in final["relative_analysis"].get("existing_alternatives", []):
        lines.append(f"- Alternative: {alt}")
    gap = final["relative_analysis"].get("functional_gap_vs_market", "")
    if gap:
        lines.extend(["", f"Gap vs market: {gap}"])

    lines.extend(["", "## Switzerland readiness", "", "### Top blockers"])
    for blocker in final["switzerland_readiness"].get("top_blockers", []):
        lines.append(f"- {blocker}")
    lines.extend(["", "### Recommended next steps"])
    for step in final["switzerland_readiness"].get("recommended_next_steps", []):
        lines.append(f"- {step}")
    lines.extend(["", "### Swiss regulatory notes"])
    for note in final["switzerland_readiness"].get("swiss_regulatory_notes", []):
        lines.append(f"- {note}")

    lines.extend(["", "## Priority actions", ""])
    for action in final.get("priority_actions", []):
        lines.append(f"- {action}")

    lines.extend(["", "## Brief report (IT)", "", final.get("brief_report_it", "")])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    args = parse_args()
    data = load_input(args.input, max_website_chars=args.max_website_chars)
    user_prompt = build_user_prompt(data)

    if args.dry_run:
        print(user_prompt)
        return 0

    raw = call_llm(api_base=args.api_base, api_key=args.api_key, model=args.model, user_prompt=user_prompt)
    final = normalize_result(raw)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)
    write_markdown(args.markdown, final)

    print(f"Report JSON: {args.output}")
    print(f"Report MD: {args.markdown}")
    print(f"Overall score: {final['overall_score']}/10")
    return 0


if __name__ == "__main__":
    sys.exit(main())
