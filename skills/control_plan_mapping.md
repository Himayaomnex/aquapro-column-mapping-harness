---
name: control_plan_mapping
purpose: Methodology and derivation rules for transforming Process FMEA records into an AIAG Control Plan.
applies_when: deriving a Control Plan from a Process FMEA
not_for: Design FMEAs; AIAG-VDA FMEA conversions
---

# Control Plan Derivation from PFMEA

Builds on `source_preservation`. Governed by the AIAG APQP and Control Plan Reference Manual.

## Core Transformation Policies

Every field in an AIAG Control Plan belongs to exactly one transformation policy:

- **CARRY** — Transferred verbatim from the source PFMEA without modification, rephrasing, or omission.
- **AUTHOR** — Synthesized from verified evidence in the corresponding PFMEA row, grounded in the process mechanisms.
- **ABSTAIN** — Left intentionally blank. Populating these fields without approved engineering drawings, calibration certs, or physical inspection plans constitutes audit non-compliance.

## Derivation Methodology by Functional Area

### 1. Process Identification & Hierarchy (CARRY)
- **Part and Process Identification:** Carried verbatim from the source header and operation details.
- **Process Segment:** Must be preserved on every row where present in the source; never drop or overwrite with a generic label.
- **Operation Number & Name:** Transferred exactly as structured in the source PFMEA.

### 2. Characteristics & Specifications
- **Product Characteristic (CARRY):** Direct transfer of the dimensional, visual, or functional requirement.
- **Process Characteristic (CARRY / AUTHOR):** Transferred directly if defined in source; otherwise derived from the root failure cause (identifying the machine parameter or process condition that influences the characteristic).
- **Special Characteristics (AUTHOR):** Designate Critical (`CC`) or Significant (`SC`) only when Severity rating is 8 or higher, or when explicitly designated in the source. Otherwise remains null.
- **Engineering Specifications & Tolerances (ABSTAIN):** Must remain blank unless verified against an approved engineering drawing.

### 3. Process Controls & Evaluation Methods (AUTHOR)
- **Control Method:** Derived directly from the source PFMEA prevention control, stating the operational method applied at the workstation.
- **Evaluation / Measurement Technique:** Derived directly from the source PFMEA detection control, defining the inspection or measurement gage/tooling principle.

### 4. Reaction Plan & Containment (AUTHOR)
- Author a specific containment and corrective action when an evaluation or measurement technique exists.
- If no measurement technique is specified, the reaction plan must remain blank to prevent ungrounded instructions.

### 5. Physical Records & Sampling (ABSTAIN)
- **Tooling, Fixture, and Gage Identifiers:** Must remain blank unless cross-referenced to an official tooling inventory or calibration record.
- **Sample Size & Frequency:** Must remain blank unless backed by an approved statistical sampling plan.
- Fabricating serial numbers, gage IDs, or sample frequencies violates AIAG PPAP 4th Edition audit standards.

## Validation Principles
- One-to-one row correspondence with source operations.
- Verbatim preservation of all carried source content.
- Strict enforcement of abstention on unverified physical records.
- Reaction plans populated only when detection techniques are present.
