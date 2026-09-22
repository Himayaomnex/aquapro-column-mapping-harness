# Ad-Hoc Analysis

## Purpose
Answer targeted analytical questions about risk, failure modes, special characteristics, controls, and APQP traceability across FMEA documents.

The output answers: **What does the evidence say — and what does it not say?** Every claim must cite a specific source row or operation. Nothing is fabricated.

## Methodology Skills
- `source_preservation` — All claims must be grounded in verifiable source evidence.

## Output Contract

```json
{
  "question": "string",
  "answer": "string",
  "claims": [
    {
      "claim": "string",
      "evidence_source": "string — operation number, row ID, or source column"
    }
  ],
  "operations_analysed": ["string"],
  "uncertainty": "string | null — explicitly declared when data is missing or partial"
}
```

## Acceptance Criteria

| Rule | Enforcement | Requirement |
|---|---|---|
| V1 | reject_claim | Every stated claim cites a specific source row, operation, or column |
| V2 | reject_claim | No severity ratings, failure causes, or control descriptions may be fabricated |
| V3 | reject_claim | Absence of information must be explicitly declared in `uncertainty`, not omitted |