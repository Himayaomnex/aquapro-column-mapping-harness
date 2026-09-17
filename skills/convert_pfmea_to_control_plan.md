# Skill: convert_pfmea_to_control_plan

## Signature

`convert_pfmea_to_control_plan(canonical_context: CanonicalContext) -> list[ControlPlanRow]`

## Purpose

The master conversion procedure (Stage 5 in the architecture diagram).
Transforms standardized canonical PFMEA context into AIAG 4th Edition compliant 16-column Control Plan rows.

## Procedure (5 Deterministic Steps)

### Step 1: Map Source Columns
- Translate source headers and fields into canonical concepts using the synonym dictionary in `schemas/canonical_context.md`.
- Retain unmapped headers in `unmapped_fields` for audit traceability; never discard raw fields.

### Step 2: Classify Fields (CARRY vs. AUTHOR vs. ABSTAIN)
Divide all 16 AIAG columns into three rigid execution buckets:
- **CARRY (Identity & Direct Mapping):**
  - `production_item_name`, `process_segment_name`, `operation_number`, `operation_name`, `product_characteristic`
  - *Rule:* Copied verbatim from source. Zero alteration.
- **AUTHOR (Derived Quality Engineering Fields):**
  - `process_characteristic`, `special_characteristic_class`, `evaluation_measurement_technique`, `control_method`, `reaction_plan`
  - *Rule:* Derived strictly from source PFMEA evidence (`failure_cause`, `preventive_control`, `detective_control`, `severity_rating`). If source has no evidence, emit `null`.
- **ABSTAIN (The Invariant of Zero Hallucination):**
  - `specification_tolerance`, `tool_number`, `tool_name`, `gage_number`, `sample_size`, `sample_frequency`
  - *Rule:* Permanently `null` unless explicitly present in source evidence. Never authored or guessed.

### Step 3: Derive Control Plan Data (From Source Evidence Only)
- Derive `special_characteristic_class`: Set to `CC` or `SC` only when `severity_rating >= 8` or marked as special in source.
- Derive `control_method`: Map directly from source `preventive_control`.
- Derive `evaluation_measurement_technique`: Map directly from source `detective_control`.
- Derive `reaction_plan`: Derive standard containment action ONLY when detective control exists; otherwise leave `null`.

### Step 4: Build 16-Column Control Plan Rows
- Invoke generic `excel_builder(mapped_context, draft_fields, document_type="control_plan_from_pfmea")` to construct final rows.
- Ensure exactly one row per (operation x characteristic) pair.
- Ensure all 16 keys exist on every row.

## Returns

`list[ControlPlanRow]` ready for validation by `validator(rows, "control_plan_from_pfmea")`.
Must achieve 0 violations from `validator` before handing over to `excel_exporter`.\n