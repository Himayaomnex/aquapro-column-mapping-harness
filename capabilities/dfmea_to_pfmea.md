# Capability: dfmea_to_pfmea

## Consumer

Simultaneous Engineering teams, Manufacturing Launch Engineers, and APQP Quality Leads bridging Product Design FMEA outputs into manufacturing Process FMEA risk analysis.

## Purpose

Establishes the engineering linkage between Design and Process FMEA (APQP Phase 2 to Phase 3 handoff):
- **Inherits Special Characteristics:** Carries Critical and Special Characteristics (CC/SC) identified in DFMEA directly into the PFMEA process spine.
- **Translates Design Causes into Process Failure Modes:** Maps design failure mechanisms (e.g. *"insufficient bolt clamp load under vibration"*) into assembly line failure modes (e.g. *"Station 30: Operator applies insufficient or excessive torque"*).
- **Mandates Error-Proofing (Poka-Yoke):** Enforces automated containment or error-proofing whenever design severity $S \ge 8$.

## Inputs (Strictly 2 Scenarios)

The agent picks exactly one path based on user input:

- **Scenario 1 — Document Provided (File upload):** `file_path` — uploaded DFMEA `.xlsx` workbook.
- **Scenario 2 — No Document Provided (RAG):** `production_item_name` — queried from historical DFMEA/PFMEA records via RAG.

## Tool hints

Pick the retrieval skill matching the input scenario, then assemble and validate:

- **Scenario 1:** `parse_pfmea_workbook(file_path)` (or workbook parser).
- **Scenario 2:** `retrieve_from_rag(production_item_name)`.

After retrieval: `excel_builder(mapped_context, draft_fields, document_type="dfmea_to_pfmea")` to assemble rows, then `validator`, then `excel_exporter`.

## Default budget

40,000 tokens · 5 tool calls

## Output schema

```json
[
  {
    "dfmea_part_name":                   "string",
    "design_characteristic":             "string",
    "dfmea_severity_rating":             "integer",
    "special_characteristic_class":      "CC | SC | null",
    "dfmea_failure_effect":              "string",
    "dfmea_design_cause":                "string",
    "pfmea_operation_number":            "string",
    "pfmea_operation_name":              "string",
    "pfmea_process_failure_mode":        "string",
    "pfmea_process_failure_cause":       "string",
    "error_proofing_poka_yoke":          "string | null",
    "recommended_process_control":       "string | null",
    "recommended_detection_method":      "string | null"
  }
]
```

## Abstention

Fields that **must remain blank** when not found in source evidence:
- Machine serial numbers, tooling IDs, operator badge IDs — never fabricate manufacturing shop-floor assets.
- Process parameters not stated in assembly routing — never invent speeds, feeds, or pressures.

## Verification rules

| # | Rule | On fail | Description |
|---|---|---|---|
| V1 | Traceability Coverage | reject_document | Every critical DFMEA characteristic must link to at least one PFMEA operation |
| V2 | Mandatory Error-Proofing | reject_row | For design severity $S \ge 8$, `error_proofing_poka_yoke` must be flagged |
| V3 | Special Characteristic Preservation | reject_row | Special characteristics (CC/SC) from DFMEA must be preserved; severity cannot be downgraded |
| V4 | Causal Traceability | reject_row | Process failure mode must logically prevent or detect the design root cause |
| V5 | Zero Hallucination | reject_row | No invented tooling IDs or machine model numbers |\n