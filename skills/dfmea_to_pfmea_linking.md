---
name: dfmea_to_pfmea_linking
purpose: Rules for cascading product design risk from a DFMEA into a manufacturing PFMEA.
applies_when: linking Design FMEA characteristics to Process FMEA operations
not_for: standalone FMEA conversions; Control Plans
---

# DFMEA to PFMEA Risk Linkage

Builds on `source_preservation`.

## The engineering logic

A Design FMEA identifies what can go wrong with the product. A Process FMEA identifies what can go wrong during manufacturing that would produce that product defect. The linkage between them is mandatory in AIAG APQP and is the primary mechanism by which design risk is controlled at the shop floor.

## What must carry without change

- The design characteristic, as named in the DFMEA.
- The severity rating — it must not be reduced in the linked PFMEA row.
- The special characteristic class (CC / SC) — it must not be downgraded.
- The failure effect, as worded in the DFMEA.
- The design cause, as stated in the DFMEA.

## What is authored in the linked PFMEA row

**Manufacturing operation** — Identify the specific assembly, machining, or handling operation where the design cause can manifest as a process defect. Ground this in the manufacturing sequence, not in general knowledge.

**Process failure mode** — State how the design cause appears as a detectable manufacturing defect at that operation. The wording must be specific to the operation, not a paraphrase of the design cause.

**Process failure cause** — State the process-side root mechanism: the operator action, machine condition, material variation, or method gap that could produce the defect.

**Error-proofing (Poka-Yoke)** — When the severity rating is 8 or higher, a Poka-Yoke or automated detection method must be specified. This is not optional. When S < 8, this field may be blank.

**Recommended process control** — Derived from the intent of the design prevention control, translated into manufacturing terms.

**Recommended detection method** — Derived from the intent of the design detection control, translated into manufacturing terms.

## What must never be authored

Machine serial numbers, fixture IDs, operator badge numbers, or unverified process parameters. These require physical records and must not be fabricated.

## Validation
- Every DFMEA characteristic with S ≥ 8 or CC/SC class has at least one linked PFMEA row.
- Severity and special characteristic class are unchanged from the DFMEA source.
- Error-proofing is specified for every row where S ≥ 8.
- No fabricated shop-floor asset identifiers.
