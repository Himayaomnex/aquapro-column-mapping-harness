---
name: pfmea_vda_mapping
purpose: Transformation methodology and alignment principles for converting legacy AIAG 4th Edition Process FMEAs to the AIAG-VDA 7-Step standard.
applies_when: converting a Process FMEA from AIAG 4th Edition to AIAG-VDA
not_for: Design FMEAs; Control Plans; Process Flows
---

# PFMEA: AIAG 4th Edition → AIAG-VDA Alignment

Builds on `source_preservation`, `vda_framework`, and `vda_four_m`.

## Structural Alignment Principles

The transition from legacy AIAG 4th Edition to AIAG-VDA 7-Step PFMEA restructures process risk analysis into standardized steps:

### 1. Structure Analysis
- **Process Item:** Carried directly from the header or part identification.
- **Process Step:** Combines operation numbering and operation nomenclature to establish clear station context.
- **Work Element (4M):** Synthesized from the root cause mechanism using the `vda_four_m` standard (`Machine`, `Method`, `Material`, `Man`).

### 2. Function Analysis
- **Process Function:** Defines the intended achievement of the process step. Formulated concisely and maintained uniformly across all rows within the same operation.
- **Characteristics:** Carried directly from source product specifications and process parameters.

### 3. Failure Analysis (The Reordered Failure Net)
- In AIAG-VDA, the failure chain sequence is harmonized to flow from effect to root mechanism:
  - **Failure Effect & Severity:** Placed first in the failure sequence. Severity score is strictly preserved from the source.
  - **Failure Mode:** Carried verbatim.
  - **Failure Cause:** Carried verbatim as the originating mechanism.
  - **Special Characteristics (CC/SC):** Transferred directly without alteration.

### 4. Risk Analysis & Evaluation
- **Controls & Ratings:** Current prevention controls, detection controls, and their respective Occurrence (O) and Detection (D) ratings are carried verbatim.
- **Action Priority (AP):** Replaces the legacy Risk Priority Number (RPN = S × O × D). Evaluated deterministically from the (S, O, D) combination against the standardized AIAG-VDA lookup matrix to assign High (`H`), Medium (`M`), or Low (`L`).

### 5. Optimization & Blanking Policy
- Subsequent mitigation fields (prevention actions, detection actions, responsible owners, target completion dates) are preserved only if documented in the source record. They must never be artificially authored.

## Handling Real-World Workbooks
- **Complex & Hierarchical Headers:** Legacy workbooks frequently utilize multi-tier or merged header bands. Identify the true data header row through column semantics rather than assuming a fixed row index.
- **Header Synonyms & Variants:** Recognize semantic equivalents (e.g., "Occurrence Rating", "O", "Occ") through concept mapping rather than requiring exact string matches.
- **Unmapped Attributes:** Columns outside the standard schema must be logged in the audit trail rather than silently discarded or forced into unrelated targets.

## Validation Criteria
- Exact 1-to-1 row preservation matching source operations.
- Byte-for-byte fidelity across all carried content.
- Work elements strictly conform to the 4M classification.
- Action Priority is strictly evaluated as H, M, or L.
- Process functions remain consistent across each operation group.
