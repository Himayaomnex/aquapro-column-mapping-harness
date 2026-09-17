# Skill: link_dfmea_to_pfmea

## Signature

`link_dfmea_to_pfmea(canonical_context: CanonicalContext) -> list[dict]`

## When the agent should call it

When fulfilling the `dfmea_to_pfmea` capability.
Triggered when the user requests bridging, linking, or establishing traceability between DFMEA design risk and PFMEA process manufacturing operations.

## Purpose

The master engineering handoff procedure connecting Product Design (APQP Phase 2) with Process Engineering (APQP Phase 3).
Transforms Design FMEA (DFMEA) product functions, failure modes, causes, and special characteristics into Process FMEA (PFMEA) candidate operations, process failure modes, and error-proofing controls.

## Procedure (4 Deterministic Steps)

### Step 1: Map Source DFMEA Columns
- Translate source DFMEA headers and fields into canonical concepts using the synonym dictionary in `schemas/canonical_context.md`.
- Retain unmapped headers in `unmapped_fields` for audit traceability; never discard raw fields.

### Step 2: Classify Fields (CARRY vs. AUTHOR vs. ABSTAIN)
Divide linkage fields into three rigid execution buckets:
- **CARRY (Direct Engineering Inheritance):**
  - `dfmea_part_name`, `design_characteristic`, `dfmea_severity_rating`, `special_characteristic_class`, `dfmea_failure_effect`
  - *Rule:* Inherited verbatim from DFMEA. Zero alteration. Design severity ($S$) cannot be downgraded by manufacturing.
- **AUTHOR (Derived Process Engineering Fields):**
  - `pfmea_operation_number`, `pfmea_operation_name`, `pfmea_process_failure_mode`, `pfmea_process_failure_cause`, `error_proofing_poka_yoke`, `recommended_process_control`, `recommended_detection_method`
  - *Rule:* Derived strictly from DFMEA failure mechanisms and causes.
- **ABSTAIN (Zero-Hallucination Invariant):**
  - `machine_serial_number`, `operator_id`, `tool_serial_number`
  - *Rule:* Permanently `null` unless explicitly present in manufacturing line inputs. Never fabricated.

### Step 3: Engineering Derivation & Linkage Rules
1. **Special Characteristic Inheritance (CC/SC):**
   - Any DFMEA characteristic with `severity_rating >= 8` or tagged as `CC`/`SC` is automatically designated as a mandatory Special Characteristic in PFMEA.
2. **Design Cause to Process Failure Mode Translation:**
   - DFMEA Design Cause (e.g., *"Insufficient bolt clamp load under vibration"*) translates into PFMEA Process Failure Mode at the assembly station (e.g., *"Station 30: Insufficient tightening torque applied"*).
3. **Mandatory Error-Proofing (Poka-Yoke):**
   - For any design characteristic with `severity_rating >= 8`, `error_proofing_poka_yoke` must be flagged as mandatory (e.g., torque-angle monitoring, automated interlock).

### Step 4: Assemble Linkage Rows
- Invoke `excel_builder(mapped_context, draft_fields, document_type="dfmea_to_pfmea")`.
- Verify every critical DFMEA characteristic is linked to at least one manufacturing process operation.

## Returns

`list[dict]` representing the DFMEA-to-PFMEA traceability matrix.
Must achieve 0 violations from `validator(rows, "dfmea_to_pfmea")` before passing to `excel_exporter`.

## Cost

Typically 2-3 tool calls, ~10,000–25,000 tokens.

## Failure Handling

If a DFMEA characteristic has no feasible manufacturing operation mapped:
- Emit record with `pfmea_operation_number = null` and flag in validator.
- Do not invent fictitious assembly stations.\n