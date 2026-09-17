# Skill: convert_dfmea_aiag_to_vda

## Signature

`convert_dfmea_aiag_to_vda(canonical_context: CanonicalContext) -> list[dict]`

## When the agent should call it

When fulfilling the `dfmea_aiag_to_vda` capability.
Triggered when the user requests conversion of legacy AIAG Design FMEA data into the AIAG-VDA 1st Edition standard.

## Purpose

Harmonizes legacy AIAG 4th Edition DFMEA data into the AIAG-VDA 1st Edition Design FMEA structure.
Transitions product risk assessment from legacy RPN to standardized Action Priority (AP) tables and establishes clear System / Subsystem / Component hierarchy.

## Procedure (5 Deterministic Steps)

### Step 1: Map Source DFMEA Columns
- Map source columns to canonical definitions using `schemas/canonical_context.md`.
- Retain unmapped attributes in `unmapped_fields`.

### Step 2: Classify Fields (CARRY vs. AUTHOR vs. ABSTAIN)
- **CARRY (Design Evidence):**
  - `higher_level_element`, `focus_element`, `lower_level_element`, `system_function`, `focus_function`, `failure_effect_fe`, `failure_mode_fm`, `design_cause_fc`, `severity_rating`, `occurrence_rating`, `detection_rating`
  - *Rule:* Retained verbatim from source DFMEA.
- **AUTHOR (AIAG-VDA Design Fields):**
  - `action_priority_ap`: Evaluated from standard AIAG-VDA Design Action Priority lookup table based on S, O, D.
  - `special_characteristic_class`: `CC` or `SC` when $S \ge 8$ or flagged in design intent.
- **ABSTAIN (Zero-Hallucination Invariant):**
  - `responsible_engineer`, `target_date`, `action_status`, CAD drawing revisions.
  - *Rule:* Permanently `null` unless explicitly specified.

### Step 3: Compute Action Priority (AP)
- Apply standard AIAG-VDA Design Action Priority matrix logic ($S \times O \times D \to H/M/L$).

### Step 4: Assemble AIAG-VDA Design Structure
- Invoke `excel_builder(mapped_context, draft_fields, document_type="dfmea_aiag_to_vda")`.

### Step 5: Validate and Export
- Run `validator(rows, capability_id="dfmea_aiag_to_vda")`.
- Export harmonized workbook with `excel_exporter`.

## Returns

`list[dict]` formatted for AIAG-VDA Design FMEA validation and export.
Must achieve 0 violations from `validator(rows, "dfmea_aiag_to_vda")`.

## Cost

Typically 2-3 tool calls, ~10,000–25,000 tokens.

## Failure Handling

If design functions or failure chains cannot be parsed:
- State missing elements in validation output.
- Never invent mechanical tolerances or stress calculations.\n