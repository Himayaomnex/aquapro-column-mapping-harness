---
name: pfmea_vda_mapping
purpose: The column-by-column contract for converting an AIAG 4th Edition Process FMEA into the AIAG-VDA 7-Step layout.
applies_when: converting a Process FMEA from AIAG 4th Edition to AIAG-VDA
not_for: Design FMEAs; Control Plans; Process Flows
---

# PFMEA: AIAG 4th Edition → AIAG-VDA Mapping

Builds on `source_preservation`, `vda_framework`, and `vda_four_m`.

## What carries — do not re-decide this

All fifteen core 4th Edition columns carry to the VDA layout. Column placement is declared here — it is never a matter of judgement.

| AIAG 4th Edition source column | VDA target column | Note |
|---|---|---|
| Production Item Name | `process_item` | |
| Operation Number | `process_step` | Combined with Operation Name |
| Operation Name | `process_step` | Combined with Operation Number |
| Potential Effects of Failure | `failure_effect_fe` | Moved before Failure Mode |
| Severity | `severity_rating` | Moved before Failure Mode |
| Potential Failure Mode | `failure_mode_fm` | |
| Class (CC / SC) | `special_characteristic_class` | |
| Potential Cause(s) / Mechanism(s) of Failure | `failure_cause_fc` | |
| Current Process Controls — Prevention | `current_prevention_control` | |
| Occurrence | `occurrence_rating` | |
| Current Process Controls — Detection | `current_detection_control` | |
| Detection | `detection_rating` | |
| Product Characteristic | `product_characteristic` | |
| Process Characteristic | `process_characteristic` | |

## What is authored — per row

**`work_element_4m`** — Apply the `vda_four_m` skill to the failure cause. The result is exactly one of: Man, Machine, Material, Method.

**`process_function`** — State what the overall process step achieves. This is one sentence, derived from the operation name and its characteristics. It must be identical on every row belonging to the same operation.

**`action_priority_ap`** — Computed deterministically from the carried S, O, D values using the AIAG-VDA Action Priority table. Result is H, M, or L. RPN is not used.

## What remains blank

Optimisation columns (`prevention_action`, `detection_action`, `responsible_person`, `target_completion_date`) remain empty unless the source explicitly provides them. Never author project schedules or personnel names.

## Special cases

Two-tier headers are common in customer files (a merged band row above the real header row). Identify the actual header row from the sheet structure before mapping. The presence of merged cells above the header does not change which row the column names are taken from.

When a source file uses alias column names (e.g. "Occurrence Rating" instead of "Occurrence"), identify the canonical concept from the content and map accordingly. Genuinely unresolved columns are reported as unmapped — never silently guessed.

## Validation
- Row count equals source row count.
- All carried cells are byte-identical to source.
- `work_element_4m` is one of the four permitted values.
- `action_priority_ap` is H, M, or L.
- `process_function` is identical across all rows of the same operation.
