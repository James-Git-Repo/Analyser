# Startup Evaluator 360 (Market & Investor Readiness)

Tool LLM che valuta startup con priorità su:
1. **Market readiness**
2. **Investor readiness**

L’analisi prodotto è trattata come supporto backend: confronto col mercato, tipo prodotto e attrattività (IP intensity, scalabilità, contesto normativo/economico), con focus operativo su **Svizzera**.

## Input richiesto
JSON con:
- `website_url`: URL del sito della startup
- `answers`: risposte a criteri/claim chiave
- `verification_context`: benchmark e regole di qualità per validare i claim

Esempio: `examples/startup_input.example.json`.

## Setup API

```bash
export LLM_API_KEY="<your_api_key>"
export LLM_MODEL="gpt-4o-mini"
export LLM_API_BASE="https://api.openai.com/v1"
```

## Esecuzione

```bash
python3 startup_evaluator.py --input examples/startup_input.example.json
```

Output:
- `evaluation_report.json`
- `evaluation_report.md`

## Cosa trovi nel report
- Score su 35 criteri
- `market_readiness_score` e `investor_readiness_score`
- `product_backend_support_score`
- Analisi attrattività prodotto (IP intensity, scalability, regulatory/economic tailwind)
- Relative analysis vs alternative di mercato
- Bloccanti e next steps per investor/commercial readiness in Svizzera

## Opzioni utili

```bash
python3 startup_evaluator.py --input my_input.json --output out.json --markdown out.md
python3 startup_evaluator.py --input my_input.json --max-website-chars 15000
python3 startup_evaluator.py --input my_input.json --dry-run
```
