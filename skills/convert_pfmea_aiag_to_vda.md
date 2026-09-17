# Skill: convert_pfmea_aiag_to_vda

## Signature

`convert_pfmea_aiag_to_vda(canonical_context: CanonicalContext) -> list[dict]`

## When the agent should call it

When fulfilling the `pfmea_aiag_to_vda` capability.
Triggered when the user requests conversion of legacy AIAG 4th Edition PFMEA data into the AIAG-VDA 1st Edition 7-Step format.

## Purpose

The master conversion procedure transforming legacy AIAG 4th Edition PFMEA rows into the harmonized AIAG-VDA 1st Edition 7-Step standard.
Replaces obsolete RPN ($S \times O \times D$) with standard Action Priority (AP: High, Medium, Low) and structures manufacturing operations into 4M work elements.

## Procedure (5 Deterministic Steps)

### Step 1: Map Source Legacy Columns
- Translate source AIAG headers into canonical concepts using `schemas/canonical_context.md`.
- Retain unmapped headers in `unmapped_fields` for audit traceability; never discard raw fields.

### Step 2: Classify Fields (CARRY vs. AUTHOR vs. ABSTAIN)
Divide all output columns into three rigid execution buckets:
- **CARRY (Preserved Engineering Metrics):**
  - `process_item`, `process_step`, `process_function`, `failure_effect`, `failure_mode`, `failure_cause`, `severity_rating`, `occurrence_rating`, `detection_rating`
  - *Rule:* Copied verbatim from source PFMEA. Zero alteration.
- **AUTHOR (Derived AIAG-VDA Standard Fields):**
  - `work_element_4m`: Categorize into Machine, Method, Material, or Man based on failure cause keywords.
  - `action_priority`: Calculate High (H), Medium (M), or Low (L) using the standard AIAG-VDA Action Priority lookup table based on S, O, D.
  - `special_characteristic_class`: Assigned as 'CC' or 'SC' when $S \ge 8$ or explicitly designated in source.
- **ABSTAIN (Zero-Hallucination Invariant):**
  - `responsible_person`, `target_completion_date`, `status`, post-action S/O/D ratings.
  - *Rule:* Permanently `null` unless explicitly provided by engineering team inputs. Never fabricated.

### Step 3: Compute Action Priority (AP)
Apply standard AIAG-VDA Action Priority matrix logic:
- Severity 9-10 with Occurrence $\ge 2$ or Detection $\ge 2$ yields **H** (High Priority).
- Severity 7-8 with moderate Occurrence/Detection yields **H** or **M** (High/Medium Priority).
- Severity 4-6 with moderate Occurrence/Detection yields **M** (Medium Priority).
- Remaining low-risk combinations evaluate to **L** (Low Priority).

### Step 4: Assemble 7-Step Structure
- Construct AIAG-VDA structure:
  - Step 2: Structure Analysis (Item, Step, 4M Work Element)
  - Step 3: Function Analysis (Process Function, Product Characteristic, Process Characteristic)
  - Step 4: Failure Analysis (Failure Effect, Failure Mode, Failure Cause)
  - Step 5: Risk Analysis (Prevention, S, O, Detection, D, AP)
  - Step 6: Optimization (Recommended Actions, Status)
- Invoke `excel_builder(mapped_context, draft_fields, document_type="pfmea_aiag_to_vda")`.

### Step 5: Validate and Export
- Run `validator(rows, capability_id="pfmea_aiag_to_vda")`.
- Export harmonized workbook with `excel_exporter`.

## Returns

`list[dict]` conforming to the AIAG-VDA 7-Step PFMEA schema.
Must achieve 0 violations from `validator` before handing over to `excel_exporter`.

## Cost

Typically 2-3 tool calls, ~10,000–25,000 tokens.

## Failure Handling

If mandatory ratings (S, O, D) are missing in the source:
- Action Priority cannot be computed; flag row violation in `validator`.
- Never guess or fabricate missing severity or occurrence ratings.\n