---
name: control_plan_mapping
purpose: The column-by-column contract for deriving a 16-column AIAG Control Plan from a Process FMEA.
applies_when: deriving a Control Plan from a Process FMEA
not_for: Design FMEAs; AIAG-VDA FMEA conversions
---

# Control Plan Derivation from PFMEA

Builds on `source_preservation`. Governed by the AIAG APQP / Control Plan Reference Manual.

## The three column policies

Every column in a Control Plan belongs to exactly one policy:

**CARRY** — Copied verbatim from the source PFMEA. No modification.

**AUTHOR** — Derived from source evidence in the same row. The value must be grounded in what the source PFMEA says about that operation and characteristic — not in general engineering knowledge.

**ABSTAIN** — Left blank. These fields require data that only exists on an approved engineering drawing, calibration record, or sampling plan. Inventing them causes immediate failure in an OEM PPAP audit. A blank is correct; a fabricated value is a defect.

## The 16 columns

| # | Field | Policy | Derivation rule |
|---|---|---|---|
| 1 | `production_item_name` | CARRY | |
| 2 | `process_segment_name` | CARRY | Must never be dropped when present in source |
| 3 | `operation_number` | CARRY | |
| 4 | `operation_name` | CARRY | |
| 5 | `product_characteristic` | CARRY | |
| 6 | `process_characteristic` | CARRY if present in source; AUTHOR from failure cause if absent | Derived from the cause of the failure — the machine parameter or process condition that drives the characteristic |
| 7 | `special_characteristic_class` | AUTHOR | Set to `CC` when S ≥ 8 and the characteristic is safety-critical; `SC` when S ≥ 8 and customer-designated significant; null otherwise |
| 8 | `specification_tolerance` | ABSTAIN | Requires approved engineering drawing |
| 9 | `evaluation_measurement_technique` | AUTHOR | Derived directly from the source detection control |
| 10 | `tool_number` | ABSTAIN | Requires official tooling register |
| 11 | `tool_name` | ABSTAIN | Requires official tooling register |
| 12 | `gage_number` | ABSTAIN | Requires calibration record |
| 13 | `control_method` | AUTHOR | Derived directly from the source prevention control |
| 14 | `sample_size` | ABSTAIN | Requires approved sampling plan |
| 15 | `sample_frequency` | ABSTAIN | Requires approved sampling plan |
| 16 | `reaction_plan` | AUTHOR | Derived only when column 9 (`evaluation_measurement_technique`) is non-null — states the containment action when the measurement detects a nonconformance |

## Why ABSTAIN fields must remain blank

AIAG PPAP 4th Edition permits blank tooling, gage, and sampling columns when those plans have not yet been assigned. It does not permit invented values. An OEM PPAP auditor cross-references these fields against physical records — a fabricated number that does not match any record causes immediate rejection. A blank is auditable; a fiction is not.

## Validation
- Row count equals source row count.
- `process_segment_name` is populated on every row where the source provides it.
- All CARRY cells are byte-identical to source.
- All ABSTAIN cells are null or empty.
- `reaction_plan` is null when `evaluation_measurement_technique` is null.
