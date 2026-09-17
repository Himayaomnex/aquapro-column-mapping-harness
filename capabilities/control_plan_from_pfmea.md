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

| # | Rule | On fail |
|---|---|---|
| V1 | Every row must have `operation_number` and `operation_name` populated | reject_row |
| V2 | No fabricated values in `tool_number`, `gage_number`, `sample_size`, `sample_frequency` | reject_row |
| V3 | Rows with `special_characteristic_class` in `[CC, SC]` must have a non-blank `control_method` | reject_row |
| V4 | `reaction_plan` must be present whenever a detective control was mapped | reject_row |
| V5 | Column headers must match the 16 canonical AIAG 4th Edition names in exact order | reject_document |
| V6 | Minimum operation count: generated control plan must have >= 5 operations | reject_document |\n