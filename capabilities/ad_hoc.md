# Capability: ad_hoc

## Consumer

Quality engineers, APQP managers, process auditors, and engineering team members asking ad-hoc analytical questions across any FMEA or APQP documents (PFMEA, DFMEA, Control Plan, or Cross-document linkages).

## Purpose

Answer targeted analytical questions about product/process risk, failure modes, special characteristics, controls, and APQP traceability without requiring the generation of a full 16-column spreadsheet document.
Examples:
- *"Which operations have severity >= 8 but lack error-proofing or detective controls?"*
- *"List all Critical and Special Characteristics (CC/SC) identified across this design."*
- *"What are the high Action Priority (AP=H) items in this PFMEA?"*
- *"Trace DFMEA characteristic 'clamp force' to its corresponding PFMEA assembly operation."*

Ground every claim strictly in verified evidence extracted from workbooks or RAG knowledge. Never hallucinate engineering metrics or ratings.

## When the agent should choose it

When the user request is an exploratory, analytical, or auditing query (Use Case 2) rather than a request to generate a complete document (Use Case 1: `control_plan_from_pfmea`, `pfmea_aiag_to_vda`, `dfmea_aiag_to_vda`, `dfmea_to_pfmea`).

## Inputs (Strictly 2 Scenarios)

- `task` (the user's natural language analytical question)
- Context matching one of the two input scenarios:
  1. **Document Provided:** `file_path` — user uploaded a PFMEA, DFMEA, or Control Plan `.xlsx` workbook.
  2. **No Document Provided (RAG):** `production_item_name` / `query` — user asks a question about a part or process without uploading a file; retrieved from historical RAG store.

## Tool hints

Depending on which of the 2 input scenarios is present:
- `parse_pfmea_workbook(file_path)` (or workbook parser) if a document is provided.
- `retrieve_from_rag(production_item_name)` if querying historical engineering records.

## Default budget

30,000 tokens · 6 tool calls

## Output schema

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

## Abstention

If the requested information is absent from the workbook or database:
- State what was checked and what was missing in `uncertainty`.
- Do not fabricate severity ratings, failure causes, or control mechanisms.
- An honest answer with `uncertainty` populated is 100% valid.

## Verification rules

| # | Rule | On fail |
|---|---|---|
| V1 | Output conforms strictly to JSON schema with all 5 top-level keys | reject_document |
| V2 | Every claim in `claims` cites at least one valid, verifiable `evidence_id` from the retrieved data | reject_row |
| V3 | Zero hallucinated ratings or characteristics — any stated metric must match source rows exactly | reject_row |
| V4 | If evidence store is empty (`found_nothing=true`), `claims` must be empty and `uncertainty` non-null | reject_document |\n