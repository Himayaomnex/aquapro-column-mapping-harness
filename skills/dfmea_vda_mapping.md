---
name: dfmea_vda_mapping
purpose: The column-by-column contract for converting an AIAG 4th Edition Design FMEA into the AIAG-VDA 7-Step layout.
applies_when: converting a Design FMEA from AIAG 4th Edition to AIAG-VDA
not_for: Process FMEAs; Control Plans
---

# DFMEA: AIAG 4th Edition → AIAG-VDA Mapping

Builds on `source_preservation` and `vda_framework`.

## The structural difference between DFMEA and PFMEA conversion

A Process FMEA conversion is primarily a rearrangement — the structure already exists. A Design FMEA conversion requires authoring a 3-level physical hierarchy that the 4th Edition source does not contain. This is the one place in the entire DFMEA conversion where genuine reasoning is required.

## Authoring the 3-level structure — per row

The VDA Design layout requires three levels of physical structure, each with a function:

**Level 1 — Higher Level Element (the system)**
The product as a whole, or the vehicle-level system it belongs to. Derived from the production item name or the top-level function group. This value is identical on every row in the document.

**Level 2 — Focus Element (the subsystem or interface)**
The assembly, module, or interface being analysed. Derived from the source Function Group. All rows that share the same Function Group share the same Focus Element.

**Level 3 — Component Element**
The specific component, material interface, or feature that the failure cause acts on. Derived from the Function and Requirement content of the individual row.

For each of the three levels, author the corresponding function — what that level is for — grounded in the source Function and Requirement text. Level 3 may repeat the source requirement text verbatim. Levels 1 and 2 are summaries, written once per group and repeated consistently.

## What carries — do not re-decide this

| AIAG 4th Edition source column | VDA target column | Note |
|---|---|---|
| Potential Effects of Failure | `failure_effect_fe` | Moved before Failure Mode |
| Severity | `severity_rating` | Moved before Failure Mode |
| Potential Failure Mode | `failure_mode_fm` | |
| Class (CC / SC) | `special_characteristic_class` | |
| Potential Cause(s) / Mechanism(s) | `design_cause_fc` | |
| Current Design Controls — Prevention | `current_prevention_control` | |
| Occurrence | `occurrence_rating` | |
| Current Design Controls — Detection | `current_detection_control` | |
| Detection | `detection_rating` | |
| Function / Requirement | `design_characteristic` | |

**`action_priority_ap`** is authored: computed from the carried S, O, D using the AIAG-VDA Action Priority table. Result is H, M, or L.

## There is no Four M column in a Design FMEA

Four M classifies process work elements. Design FMEAs analyse physical failure mechanisms — wear, fatigue, yield, thermal expansion. Do not add a Four M column to a DFMEA output.

## What remains blank

Optimisation columns (`recommended_design_action`, `responsible_engineer`, `target_date`, `action_status`) remain empty unless the source explicitly provides them. Never author engineering sign-offs or completion dates.

## Validation
- Row count equals source row count.
- All carried cells are byte-identical to source.
- `higher_level_element` is identical on every row.
- `focus_element` is identical across all rows sharing the same Function Group.
- `action_priority_ap` is H, M, or L.
