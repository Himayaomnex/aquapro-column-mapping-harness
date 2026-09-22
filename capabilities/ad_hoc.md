# Capability Contract: ad_hoc

## Consumer
Quality engineers, APQP managers, process auditors, and engineering team members asking ad-hoc analytical questions across any FMEA or APQP documents (PFMEA, DFMEA, Control Plan, or Cross-document linkages).

## Purpose
Answer targeted analytical questions about product/process risk, failure modes, special characteristics, controls, and APQP traceability without generating a complete spreadsheet document.
Examples:
- *"Which operations have severity >= 8 but lack error-proofing or detective controls?"*
- *"List all Critical and Special Characteristics (CC/SC) identified across this design."*
- *"What are the high Action Priority (AP=H) items in this PFMEA?"*
- *"Trace DFMEA characteristic 'clamp force' to its corresponding PFMEA assembly operation."*

Ground every claim strictly in verified evidence extracted from workbooks or RAG knowledge. Never hallucinate engineering metrics or ratings.

## Applicable Methodology Skills
- `skills/source_preservation.md` — Claims must be supported by exact, verifiable citations from the source evidence.
- `skills/vda_framework.md` — Interpreting Action Priority (AP) and 7-Step failure nets.

## Operational Scenarios
- **Scenario 1 — Document Provided (File Upload):** File uploaded; questions answered by querying parsed rows.
- **Scenario 2 — Greenfield / Reference Item (RAG):** Production item queried from historical vector store.

## Output Schema

```json
{
  "question": "string",
  "answer": "string",
  "claims": [
    {
      "claim": "string",
      "evidence_ids": ["string"]
    }
  ],
  "operations_analyzed": ["string"],
  "uncertainty": "string | null"
}
```

## Abstention & Uncertainty
If the requested information is absent from the workbook or database:
- State what was checked and what was missing in `uncertainty`.
- Do not fabricate severity ratings, failure causes, or control mechanisms.

## Verification & Acceptance Criteria

| # | Rule | Enforcement | Description |
|---|---|---|---|
| V1 | Claim Grounding | reject_claim | Every claim must cite specific source row IDs or operation numbers |
| V2 | No Hallucination | reject_claim | Unverified ratings or non-existent controls must not be fabricated |
| V3 | Explicit Uncertainty | reject_claim | If data is partial or absent, uncertainty must be clearly declared |