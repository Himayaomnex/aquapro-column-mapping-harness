# Capability: dfmea_aiag_to_vda

## Consumer

Product Design Engineers, Systems Engineering Leads, and Functional Safety Auditors harmonizing Design FMEAs to the AIAG-VDA 1st Edition standard.

## Purpose

Convert legacy AIAG Design FMEAs (DFMEA) into the AIAG-VDA 7-Step Design format:
- **Step 2 (Structure Analysis):** Higher Level Element (System), Focus Element (Subsystem), Lower Level Element (Component).
- **Step 3 (Function Analysis):** Functions and requirements of Higher Level, Focus Element, and Lower Level.
- **Step 4 (Failure Analysis):** Failure Effect (FE at vehicle/system level), Failure Mode (FM at focus subsystem level), Design Cause (FC at component/physical level).
- **Step 5 (Risk Analysis):** Prevention Controls, Severity (S), Occurrence (O), Detection Controls, Detection (D), Action Priority (AP: H, M, L).
- **Step 6 (Optimization):** Design improvements, FEA simulations, prototype testing, responsible engineer, completion date, status.
- **Step 7 (Results Documentation):** Traceability from product requirements to design verification.

## Inputs (Strictly 2 Scenarios)

The agent picks exactly one path based on user input:

- **Scenario 1 — Document Provided (File upload):** `file_path` — uploaded legacy AIAG DFMEA `.xlsx` workbook.
- **Scenario 2 — No Document Provided (RAG):** `production_item_name` — queried from product design vector store via RAG.

## Tool hints

Pick the retrieval skill matching the input scenario, then assemble and validate:

- **Scenario 1:** `parse_pfmea_workbook(file_path)` (or workbook parser).
- **Scenario 2:** `retrieve_from_rag(production_item_name)`.

After retrieval: `excel_builder(mapped_context, draft_fields, document_type="dfmea_aiag_to_vda")` to assemble rows, then `validator`, then `excel_exporter`.

## Default budget

40,000 tokens · 5 tool calls

## Output schema

```json
[
  {
    "higher_level_element":              "string",
    "focus_element":                     "string",
    "lower_level_element":               "string",
    "system_function":                   "string",
    "focus_function":                    "string",
    "design_characteristic":             "string",
    "failure_effect_fe":                 "string",
    "severity_rating":                   "integer",
    "failure_mode_fm":                   "string",
    "special_characteristic_class":      "CC | SC | null",
    "design_cause_fc":                   "string",
    "current_prevention_control":        "string | null",
    "occurrence_rating":                 "integer",
    "current_detection_control":         "string | null",
    "detection_rating":                  "integer",
    "action_priority_ap":                "H | M | L",
    "recommended_design_action":         "string | null",
    "responsible_engineer":              "string | null",
    "target_date":                       "string | null",
    "action_status":                     "string | null"
  }
]
```

## Abstention

Fields that **must remain blank** when not found in source evidence:
- `responsible_engineer`, `target_date`, `action_status` — never fabricate personnel or timelines.
- CAD / CAE drawing numbers — never invent drawing or model IDs.
- Post-action design ratings — never simulate post-mitigation S, O, D without validated FEA or test results.

## Verification rules

| # | Rule | On fail | Description |
|---|---|---|---|
| V1 | 3-Level Breakdown | reject_document | Higher Level (System), Focus Element, and Lower Level (Component) must be populated |
| V2 | Functional Grounding | reject_row | Design causes must relate to physics/material properties (wear, fatigue, thermal expansion) |
| V3 | Action Priority Validity | reject_row | Action Priority must strictly conform to AIAG-VDA $S \times O \times D$ matrix |
| V4 | Special Characteristic Class | reject_row | Any design characteristic with $S \ge 8$ must have CC or SC designation |
| V5 | Honest Abstention | reject_row | No fabricated engineering signoffs or test completion dates |\n