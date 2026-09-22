---
name: dfmea_to_pfmea_linking
purpose: How to link upstream Product Design FMEA (DFMEA) failure modes and special characteristics into downstream Process FMEA (PFMEA).
applies_when: cascading product design risk into manufacturing process planning, or transferring DFMEA special characteristics to PFMEA
not_for: direct document layout conversions (AIAG to VDA)
---

# DFMEA to PFMEA Risk Cascading

In the automotive APQP and AIAG-VDA process, product design failure risks cascade directly into manufacturing process risks:

1. **Failure Mode Transfer:**
   - A DFMEA failure mode resulting from component tolerance or geometry becomes a `Product Characteristic` or `Process Failure Mode` in the PFMEA.

2. **Special Characteristics Linkage:**
   - Any design feature with Severity $S \ge 8$ or marked as a Special Characteristic (`CC` or `SC`) in the DFMEA must be transferred directly into the PFMEA and downstream Control Plan.

3. **Prevention vs. Process Controls:**
   - DFMEA Prevention Controls represent design rules, material selections, and CAE simulations.
   - PFMEA Prevention Controls represent machine capabilities, fixtures, error-proofing (Poka-Yoke), and operator work instructions.

## Validation Expectations
- Traceability between DFMEA item/function and PFMEA operation/characteristic is preserved.
- Critical and Significant characteristics are preserved without downgrade.
