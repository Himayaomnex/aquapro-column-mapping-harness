# DFMEA to PFMEA Risk Linkage

## Purpose
Establish formal traceability between product Design FMEA (DFMEA) and manufacturing Process FMEA (PFMEA), as required by the AIAG APQP Phase 2 → Phase 3 handoff.

The output answers one question: **For each critical design characteristic in this DFMEA, what is the corresponding manufacturing process failure mode, required error-proofing, and recommended process control?**

## Methodology Skills
- `source_preservation` — Governs verbatim carry and zero hallucination.
- `dfmea_to_pfmea_linking` — Governs the risk cascade rules, special characteristic inheritance, and Poka-Yoke mandate.

## Output Contract

Every row in the output must conform to the following schema:

| # | Field | Type | Policy |
|---|---|---|---|
| 1 | `dfmea_part_name` | string | CARRY — from DFMEA production item |
| 2 | `design_characteristic` | string | CARRY — from DFMEA function or requirement |
| 3 | `dfmea_severity_rating` | integer | CARRY — must not be downgraded |
| 4 | `special_characteristic_class` | `CC` \| `SC` \| null | CARRY — must not be downgraded |
| 5 | `dfmea_failure_effect` | string | CARRY |
| 6 | `dfmea_design_cause` | string | CARRY |
| 7 | `pfmea_operation_number` | string | AUTHOR — corresponding manufacturing operation |
| 8 | `pfmea_operation_name` | string | AUTHOR — name of the manufacturing operation |
| 9 | `pfmea_process_failure_mode` | string | AUTHOR — manufacturing manifestation of the design cause |
| 10 | `pfmea_process_failure_cause` | string | AUTHOR — process root cause linked to design mechanism |
| 11 | `error_proofing_poka_yoke` | string \| null | AUTHOR — mandatory when S ≥ 8; blank otherwise |
| 12 | `recommended_process_control` | string \| null | AUTHOR — derived from design prevention intent |
| 13 | `recommended_detection_method` | string \| null | AUTHOR — derived from design detection intent |

## Acceptance Criteria

| Rule | Enforcement | Requirement |
|---|---|---|
| V1 | reject_document | Every DFMEA characteristic with S ≥ 8 or CC/SC class has at least one linked PFMEA row |
| V2 | reject_row | `error_proofing_poka_yoke` must be specified when S ≥ 8 |
| V3 | reject_row | `special_characteristic_class` and `dfmea_severity_rating` must not be altered from source |
| V4 | reject_row | `pfmea_process_failure_mode` must logically prevent or address the `dfmea_design_cause` |
| V5 | reject_row | No fabricated machine IDs, tooling serial numbers, or unverified process parameters |