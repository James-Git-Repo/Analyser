# Startup Evaluator 360 (LLM API + Website Analysis)

Questo tool usa un **modello LLM via API** per valutare una startup su 35 criteri (score 1-10), partendo da:
- **contenuto del sito web** della startup,
- **risposte ai criteri** che fornisci in input,
- **benchmark/regole di verifica**.

In output ottieni anche una **relative analysis** (confronto con soluzioni esistenti) e una stima di **investor/commercial readiness per la Svizzera**.

## Input richiesto
Il file JSON deve includere:
- `website_url`: URL del sito da analizzare.
- `answers`: dizionario con risposte qualitative/quantitative ai criteri.
- `verification_context`: benchmark references + quality rules + info addizionali.

Esempio pronto: `examples/startup_input.example.json`.

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

## Opzioni utili

```bash
python3 startup_evaluator.py --input my_input.json --output out.json --markdown out.md
python3 startup_evaluator.py --input my_input.json --max-website-chars 15000
python3 startup_evaluator.py --input my_input.json --dry-run
```

- `--max-website-chars`: limita il testo estratto dal sito prima della valutazione.
- `--dry-run`: stampa il payload completo inviato al modello (debug).

## Note pratiche
- Se il fetch del sito fallisce, il processo continua usando comunque le risposte e il contesto forniti.
- La qualità della valutazione dipende dalla qualità delle fonti/benchmark inseriti in `verification_context`.
