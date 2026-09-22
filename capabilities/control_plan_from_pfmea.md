# Capability Contract: control_plan_from_pfmea

## Consumer
Automotive Quality Engineers, APQP Program Managers, and Plant Quality Assurance teams preparing AIAG 4th Edition compliant Control Plans for OEM PPAP submission.

## Purpose
Derive an authentic, audit-ready 16-column AIAG Control Plan from a Process FMEA (PFMEA) workbook or historical records.
Core question answered: **Given this source PFMEA, what is the exact Control Plan representation — preserving all source context, grounding derived controls, and maintaining honest abstention on unassigned tooling and specifications?**

## Applicable Methodology Skills
- `skills/source_preservation.md` — Invariant of verbatim carry, 1-to-1 row preservation, and zero hallucination.
- `skills/control_plan_mapping.md` — 16-column AIAG Control Plan structure, CARRY vs AUTHOR vs ABSTAIN policies.

## Operational Scenarios
- **Scenario 1 — Document Provided (File Upload):** An existing customer PFMEA (`.xlsx`) is provided. The agent deterministically carries source data, preserves row count, and derives missing control methods.
- **Scenario 2 — Greenfield / Reference Item (RAG):** A production item name is specified without a document. The agent retrieves historical PFMEA evidence to construct the Control Plan.

## 16-Column Canonical Output Schema

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

## Field Derivation & Preservation Policy

1. **CARRY (Source Preservation):**
   - `production_item_name`: Verbatim from source.
   - `process_segment_name`: Verbatim from source. **Must never be dropped or left blank when present in source.**
   - `operation_number`: Verbatim from source.
   - `operation_name`: Verbatim from source.
   - `product_characteristic`: Verbatim from source.
   - `process_characteristic`: Verbatim from source if present; otherwise derived from cause.

2. **AUTHOR (Derived Quality Engineering Fields):**
   - `special_characteristic_class`: Set to `CC` (Critical) or `SC` (Significant) if Severity $S \ge 8$ or designated in source; otherwise `null`.
   - `control_method`: Derived directly from source `preventive_control`.
   - `evaluation_measurement_technique`: Derived directly from source `detective_control`.
   - `reaction_plan`: Standard containment reaction derived only when a detective technique is defined.

3. **ABSTAIN (Honest Blanks for PPAP Audit Compliance):**
   - `specification_tolerance`: Kept blank unless explicitly provided in source drawings.
   - `tool_number`, `tool_name`: Kept blank unless explicitly specified in source tooling data.
   - `gage_number`: Kept blank unless explicitly assigned in calibration records.
   - `sample_size`, `sample_frequency`: Kept blank unless defined in customer sampling plans.
   - *Audit Invariant:* A Control Plan with honest blanks in these columns is fully compliant with AIAG PPAP 4th Edition. Fabricating IDs causes immediate audit failure.

## Verification & Acceptance Criteria

| # | Rule | Enforcement | Description |
|---|---|---|---|
| V1 | Schema Completeness | reject_document | Every row contains all 16 canonical keys with valid data types |
| V2 | Exact Row Preservation | reject_document | Exactly 1-to-1 row count matching source operations and characteristics |
| V3 | Process Segment Preservation | reject_document | `process_segment_name` must be populated on every row if present in source |
| V4 | Mandatory Abstention | reject_row | Zero Hallucination: tooling, gage, and sample fields remain honest blanks |
| V5 | Evidence Grounding | reject_row | Control methods and evaluation techniques must be grounded in source PFMEA controls |
| V6 | Quality Interlocks | reject_row | Reaction plan permitted only when detective control exists |