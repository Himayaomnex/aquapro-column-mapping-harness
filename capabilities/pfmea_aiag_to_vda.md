# Capability: pfmea_aiag_to_vda

## Consumer

Manufacturing Quality Engineers, APQP Program Managers, and Tier-1 Automotive Suppliers transitioning legacy AIAG 4th Edition PFMEAs to the AIAG-VDA 1st Edition 7-Step Harmonized standard.

## Purpose

Produce a fully compliant AIAG-VDA 1st Edition 7-Step PFMEA document from legacy AIAG 4th Edition source evidence.
Answer: **given this legacy PFMEA, how is it correctly restructured into the 7-step harmonized standard — with 4M work elements, function nets, failure chains, and Action Priority (AP) replacing obsolete RPN?**

The 7-Step Structure:
- **Step 1 (Planning & Preparation):** Scope definition, boundary identification.
- **Step 2 (Structure Analysis):** Process Item, Process Step, Process Work Element (4M: Machine, Method, Material, Man).
- **Step 3 (Function Analysis):** Functions and characteristics for each structure level.
- **Step 4 (Failure Analysis):** 3-level failure chain linking Failure Effects (FE), Failure Modes (FM), and Failure Causes (FC).
- **Step 5 (Risk Analysis):** Prevention Controls, Severity (S), Occurrence (O), Detection Controls, Detection (D), Action Priority (AP: High, Medium, Low).
- **Step 6 (Optimization):** Preventive/Detective recommendations, responsible person, target completion date, status.
- **Step 7 (Results Documentation):** Audit traceability and executive risk summary.

## Inputs (Strictly 2 Scenarios)

The agent picks exactly one path based on user input:

- **Scenario 1 — Document Provided (File upload):** `file_path` — uploaded legacy AIAG 4th Edition `.xlsx` workbook.
- **Scenario 2 — No Document Provided (RAG):** `production_item_name` — user specifies a manufacturing item/part; queried from historical PFMEA vector store via RAG.

## Tool hints

Pick the retrieval skill matching the input scenario, then assemble and validate:

- **Scenario 1:** `parse_pfmea_workbook(file_path)` — parses uploaded `.xlsx`, maps headers to canonical concepts.
- **Scenario 2:** `retrieve_from_rag(production_item_name)` — queries historical records via RAG.

After retrieval: `excel_builder(mapped_context, draft_fields, document_type="pfmea_aiag_to_vda")` to assemble rows, then `validator`, then `excel_exporter`.
`excel_exporter` must never run before `validator` returns an empty violation list.

## Default budget

40,000 tokens · 5 tool calls

## Output schema

```json
[
  {
    "process_item":                      "string",
    "process_step":                      "string",
    "work_element_4m":                   "Machine | Method | Material | Man",
    "process_function":                  "string",
    "product_characteristic":            "string | null",
    "process_characteristic":            "string | null",
    "failure_effect_fe":                 "string",
    "severity_rating":                   "integer",
    "failure_mode_fm":                   "string",
    "special_characteristic_class":      "CC | SC | null",
    "failure_cause_fc":                  "string",
    "current_prevention_control":        "string | null",
    "occurrence_rating":                 "integer",
    "current_detection_control":         "string | null",
    "detection_rating":                  "integer",
    "action_priority_ap":                "H | M | L",
    "prevention_action":                 "string | null",
    "detection_action":                  "string | null",
    "responsible_person":                "string | null",
    "target_completion_date":            "string | null",
    "status":                            "string | null"
  }
]
```

## Abstention

Fields that **must remain blank** when not found in source evidence:
- `responsible_person`, `target_completion_date`, `status` — never invent personnel or project schedules.
- Post-action S/O/D ratings — never predict future ratings without verified physical test data.
- Optimization actions (`prevention_action`, `detection_action`) — if AP is Low (L), optimization is optional; do not author ungrounded actions.
- `special_characteristic_class` — must remain `null` if $S < 8$ and source has no explicit special designation.

## Verification rules

| # | Rule | On fail | Description |
|---|---|---|---|
| V1 | Schema Completeness | reject_document | Every row contains all mandatory AIAG-VDA 7-Step keys |
| V2 | Operation Coverage | reject_document | Every process operation from source is represented |
| V3 | Action Priority Validity | reject_row | Action Priority must be strictly 'H', 'M', or 'L' matching the standard AIAG-VDA table |
| V4 | 4M Categorization | reject_row | `work_element_4m` must be categorized into Machine, Method, Material, or Man |
| V5 | Special Characteristic Class | reject_row | Rows with $S \ge 8$ must be evaluated for 'CC' or 'SC' designation |
| V6 | Honest Abstention | reject_row | No fabricated names, dates, or post-action ratings |\n