# Capability: control_plan_from_pfmea

## Consumer

A quality engineer generating or updating a Control Plan from an approved PFMEA workbook,
for AIAG 4th Edition PPAP submission.

## Purpose

Produce a 16-column AIAG-compliant Control Plan document from PFMEA evidence.
Answer: **given this PFMEA source, what is the correct Control Plan — and what must remain blank?**

## Inputs (Strictly 2 Scenarios)

The agent picks exactly one path based on user input:

- **Scenario 1 — Document Provided (File upload):** `file_path` — uploaded PFMEA `.xlsx` workbook.
- **Scenario 2 — No Document Provided (RAG):** `production_item_name` — user specifies a part name; the agent queries historical PFMEA records via RAG.

## Tool hints

Pick the retrieval skill matching the input scenario, then assemble and validate:

- **Scenario 1:** `parse_pfmea_workbook(file_path)` — parses the uploaded `.xlsx`, maps headers to canonical fields.
- **Scenario 2:** `retrieve_from_rag(production_item_name)` — queries historical records from local and knowledge repositories.

After retrieval: `excel_builder(mapped_context, draft_fields, document_type="control_plan_from_pfmea")` to assemble rows, then `validator`, then `excel_exporter`.
`excel_exporter` must never run before `validator` returns an empty violation list.

## Default budget

40,000 tokens · 5 tool calls

## Output schema

```json
[
  {
    "production_item_name":              "string",
    "process_segment_name":              "string | null",
    "operation_number":                  "string",
    "operation_name":                    "string",
    "product_characteristic":            "string | null",
    "process_characteristic":            "string | null",
    "special_characteristic_class":      "CC | SC | null",
    "specification_tolerance":           "string | null",
    "evaluation_measurement_technique":  "string | null",
    "tool_number":                       "string | null",
    "tool_name":                         "string | null",
    "gage_number":                       "string | null",
    "control_method":                    "string | null",
    "sample_size":                       "string | null",
    "sample_frequency":                  "string | null",
    "reaction_plan":                     "string | null"
  }
]
```

## Abstention

Fields that **must remain blank** when not found in the source PFMEA:
- `specification_tolerance` — never author without an engineering drawing
- `tool_number`, `tool_name` — never fabricate tooling identifiers
- `gage_number` — never invent gage IDs
- `sample_size`, `sample_frequency` — never assume sampling plans

A Control Plan with honest blanks in these columns is compliant with AIAG PPAP 4th Edition.
A Control Plan with invented values will fail a customer PPAP audit.

## Verification rules

| # | Rule | On fail | Description |
|---|---|---|---|
| V1 | Schema Completeness | reject_row | All 16 canonical keys present per row with valid scalar types and CC/SC classification format |
| V2 | Operation Set Equality | reject_document | 100% operation fidelity: every operation present in source PFMEA must exist in output Control Plan |
| V3 | Mandatory Abstention | reject_row | Zero Hallucination: tooling, gage, and sample fields must remain blank on new import |
| V4 | Evidence Traceability | reject_row | Control methods and evaluation techniques must be grounded in source PFMEA evidence |
| V5 | Quality Interlocks | reject_row | Reaction plan permitted only when a detective control exists in source evidence |\n