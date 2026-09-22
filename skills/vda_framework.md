---
name: vda_framework
purpose: What the AIAG-VDA 1st Edition 7-Step layout introduces over the legacy AIAG 4th Edition layout, applicable to both Process and Design FMEAs.
applies_when: any task involving an AIAG-VDA layout FMEA — reading, writing, converting, or validating
not_for: Control Plans and Process Flows — no VDA layout exists for these documents
---

# The AIAG-VDA 7-Step Framework

## The seven steps

1. **Planning and Preparation** — Scope, boundary, and project identification.
2. **Structure Analysis** — 3-level physical hierarchy (System → Subsystem → Component for DFMEA; Process Item → Process Step → Work Element for PFMEA).
3. **Function Analysis** — Functions and requirements at each structure level.
4. **Failure Analysis** — 3-level failure net: Failure Effect (FE) → Failure Mode (FM) → Failure Cause (FC).
5. **Risk Analysis** — Current prevention and detection controls, S / O / D ratings, and Action Priority (AP).
6. **Optimisation** — Mitigation actions, responsibility, target date, and status.
7. **Results Documentation** — Audit traceability and risk reporting.

## Three structural changes from AIAG 4th Edition

**1. The failure chain is reordered.**
In the 4th Edition the order is: Failure Mode → Failure Effect → Failure Cause.
In the AIAG-VDA layout the order is: **Failure Effect and its Severity → Failure Mode → Failure Cause.**

**2. RPN is replaced by Action Priority.**
The Risk Priority Number (S × O × D) is obsolete. Action Priority evaluates the S / O / D combination against the AIAG-VDA matrix and produces exactly one of three discrete values:
- **H (High)** — mandatory action required.
- **M (Medium)** — action recommended.
- **L (Low)** — action optional; current controls are effective.

**3. Columns are grouped into section bands.**
Structure Analysis, Function Analysis, Failure Analysis, Risk Analysis, and Optimisation are clearly separated column groups.

## The cardinal rule

A layout conversion carries everything it can and authors only what it must. Content the source already has is copied verbatim. Only the columns the source has no equivalent for are authored. Rephrasing, improving, or regenerating source content is the failure mode — not the method.

## Validation
- S, O, D are integers 1–10.
- AP is exactly H, M, or L.
- Row count equals source row count.
- Carried cells are byte-identical to source.
