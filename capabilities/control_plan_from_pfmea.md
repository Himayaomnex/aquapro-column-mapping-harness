# Control Plan from PFMEA

## Purpose
Produce an authentic, audit-ready 16-column AIAG Control Plan from a Process FMEA workbook.

The output answers one question: **For each process operation and characteristic in this PFMEA, what is the exact control plan — what must be preserved verbatim, what must be derived from process evidence, and what must remain blank?**

## Methodology Skills
- `source_preservation` — Governs verbatim carry and row-count fidelity.
- `control_plan_mapping` — Governs the 16-column structure, derivation rules, and abstention policy.

## Output Contract

Every row in the output must conform to the following 16-column schema:

| # | Field | Type | Policy |
|---|---|---|---|
| 1 | `production_item_name` | string | CARRY |
| 2 | `process_segment_name` | string | CARRY — must never be dropped when present in source |
| 3 | `operation_number` | string | CARRY |
| 4 | `operation_name` | string | CARRY |
| 5 | `product_characteristic` | string | CARRY |
| 6 | `process_characteristic` | string | CARRY if present; AUTHOR from cause if absent |
| 7 | `special_characteristic_class` | `CC` \| `SC` \| null | AUTHOR — `CC` or `SC` only when S ≥ 8 or source designates it; otherwise null |
| 8 | `specification_tolerance` | string \| null | ABSTAIN |
| 9 | `evaluation_measurement_technique` | string \| null | AUTHOR — derived from source detection control |
| 10 | `tool_number` | string \| null | ABSTAIN |
| 11 | `tool_name` | string \| null | ABSTAIN |
| 12 | `gage_number` | string \| null | ABSTAIN |
| 13 | `control_method` | string \| null | AUTHOR — derived from source prevention control |
| 14 | `sample_size` | string \| null | ABSTAIN |
| 15 | `sample_frequency` | string \| null | ABSTAIN |
| 16 | `reaction_plan` | string \| null | AUTHOR — derived only when a detection technique exists |

**ABSTAIN fields must remain blank.** A Control Plan with honest blanks is fully AIAG PPAP 4th Edition compliant. Fabricated tooling IDs, gage numbers, or sampling plans cause immediate OEM PPAP audit failure.

## Acceptance Criteria

| Rule | Enforcement | Requirement |
|---|---|---|
| V1 | reject_document | All 16 fields present on every row |
| V2 | reject_document | Output row count equals source row count exactly (1-to-1) |
| V3 | reject_document | `process_segment_name` populated on every row where source provides it |
| V4 | reject_row | ABSTAIN fields contain no authored values |
| V5 | reject_row | `control_method` and `evaluation_measurement_technique` grounded in source PFMEA controls |
| V6 | reject_row | `reaction_plan` appears only when `evaluation_measurement_technique` is non-null |