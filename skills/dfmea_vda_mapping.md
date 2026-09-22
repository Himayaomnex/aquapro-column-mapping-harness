---
name: dfmea_vda_mapping
purpose: Structural alignment methodology for transitioning legacy AIAG 4th Edition Design FMEAs to the AIAG-VDA 7-Step standard.
applies_when: converting a Design FMEA from AIAG 4th Edition to AIAG-VDA
not_for: Process FMEAs; Control Plans
---

# DFMEA: AIAG 4th Edition → AIAG-VDA Alignment

Builds on `source_preservation` and `vda_framework`.

## Methodology Differences from Process FMEA

While a Process FMEA conversion reorganizes established operational steps, a Design FMEA conversion requires establishing a physical system breakdown that does not exist in legacy 4th Edition formats.

## The 3-Level Physical Design Hierarchy

In AIAG-VDA Design FMEAs, structure analysis establishes three discrete physical levels:

### Level 1 — Higher Level Element (System Level)
- Represents the complete product, vehicle system, or top-level assembly.
- Derived from the document title or product identification.
- Remains constant across all rows in the document.

### Level 2 — Focus Element (Subsystem / Interface Level)
- Represents the major subassembly, module, or physical interface under evaluation.
- Derived from the source functional group or sub-assembly designation.
- Remains consistent across all rows within the same functional group.

### Level 3 — Component Element (Part / Feature Level)
- Represents the individual part, material boundary, or physical feature where the failure cause mechanism acts.
- Grounded directly in the specific row's function and requirement context.

## Alignment of Analysis Elements

### Function Analysis
- Each structural level is paired with its intended function:
  - Higher-level function describes system-level performance.
  - Focus function describes subsystem operation.
  - Component characteristic preserves the specific design requirement or specification verbatim from the source.

### Failure Analysis & Reordered Chain
- **Harmonized Failure Sequence:** Potential failure effects and their severity scores are positioned before failure modes, followed by root design causes.
- **Severity Ratings:** Strictly preserved from the source document.
- **No 4M Classification:** The 4M framework applies strictly to manufacturing processes. Design FMEAs evaluate physical mechanics (e.g., fatigue, wear, thermal degradation), so 4M classifications must never be introduced into DFMEA outputs.

### Risk Evaluation & Optimization
- **Action Priority (AP):** Deterministically computed from (S, O, D) using the AIAG-VDA evaluation matrix, replacing legacy RPN values.
- **Optimization Actions:** Fields for mitigation actions, responsible engineers, target dates, and status must remain blank unless documented in the source record.

## Validation Principles
- Exact 1-to-1 row correspondence matching source failure analyses.
- All carried technical content is byte-identical to source.
- Hierarchy consistency: Higher-level element is constant across the entire document; Focus element is constant within each function group.
- Action Priority conforms strictly to High, Medium, or Low.
