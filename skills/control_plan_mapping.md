---
name: control_plan_mapping
purpose: How to derive an authentic 16-column AIAG Control Plan from an approved Process FMEA (PFMEA).
applies_when: deriving or generating a Control Plan from an uploaded or referenced PFMEA workbook
not_for: DFMEAs (Control Plans are exclusively manufacturing documents derived from Process FMEAs)
---

# Control Plan Derivation from Process FMEA (PFMEA)

Builds upon `source_preservation`. Governed by the AIAG APQP / Control Plan Reference Manual.

## The 16 Canonical Control Plan Columns
An authentic AIAG Control Plan consists of 16 standard columns divided into three execution categories:

| Column Number | Canonical Name | Execution Policy | Source / Derivation Rule |
| :---: | :--- | :---: | :--- |
| 1 | `production_item_name` | **CARRY** | Part name or assembly name from source PFMEA. |
| 2 | `process_segment_name` | **CARRY** | Manufacturing segment or department from source PFMEA. **Must never be dropped or left blank if present in source.** |
| 3 | `operation_number` | **CARRY** | Manufacturing sequence step number (e.g. `10`, `20`). |
| 4 | `operation_name` | **CARRY** | Name of the process operation (e.g. `CNC Rough Milling`). |
| 5 | `product_characteristic` | **CARRY** | Dimension or feature of the manufactured part (e.g. `Bore Diameter`). |
| 6 | `process_characteristic` | **CARRY/AUTHOR** | Machine parameter controlling the feature (e.g. `Spindle Speed`). Carried if source has it; derived from cause if missing. |
| 7 | `special_characteristic_class` | **AUTHOR** | Marked as `CC` (Critical) or `SC` (Significant) if $S \ge 8$ or designated in source; otherwise `null`. |
| 8 | `specification_tolerance` | **ABSTAIN** | Engineering blueprint specification. Kept honest blank unless present in source. |
| 9 | `evaluation_measurement_technique` | **AUTHOR** | Inspection gage, sensor, or method. Derived directly from source `detective_control`. |
| 10 | `tool_number` | **ABSTAIN** | Specific machine tooling ID. Kept honest blank unless present in source. |
| 11 | `tool_name` | **ABSTAIN** | Name of the tool. Kept honest blank unless present in source. |
| 12 | `gage_number` | **ABSTAIN** | Specific gage inventory identifier. Kept honest blank unless present in source. |
| 13 | `control_method` | **AUTHOR** | In-process operational control. Derived directly from source `preventive_control`. |
| 14 | `sample_size` | **ABSTAIN** | Quality sampling plan size. Kept honest blank unless present in source. |
| 15 | `sample_frequency` | **ABSTAIN** | Quality sampling interval. Kept honest blank unless present in source. |
| 16 | `reaction_plan` | **AUTHOR** | Containment action if defect detected (e.g., `Segregate nonconforming parts and notify supervisor`). Derived when detective control exists. |

## Why Honest Abstention is Required (AIAG PPAP Audit Invariant)
- Fabricating tool numbers, gage numbers, or sampling plans without official process engineering sign-off causes immediate rejection in an OEM PPAP audit.
- AIAG PPAP 4th Edition standard permits blank tooling/gage columns when not yet assigned, but strictly forbids fictitious entries.

## Validation Expectations
- `Process Segment Name` must be populated on every row where the source PFMEA provided it.
- Row count matches source operations/characteristics.
- Carried columns are byte-identical.
- Zero fabricated tooling numbers, gage codes, or engineering tolerances.
