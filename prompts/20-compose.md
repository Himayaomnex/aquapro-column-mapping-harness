# Compose Prompt (Rendered Once on `ready_to_compose`)

## Task
{{ task }}

## Capability contract
{{ capability_contract }}

## Assembled evidence
{{ assembled_evidence }}

Each item appears as:
```
[id]  operation={{ operation_number }}  source_row={{ source_row }}
canonical fields: operation_name, process_segment_name, product_characteristic,
                  failure_cause, severity_rating, occurrence_rating,
                  preventive_control, detective_control, unmapped_fields
```

{{ dropped_notice }}

*(Present only if evidence was dropped to fit budget: "N items dropped; lowest relevance
admitted was X." A non-null `coverage_note` in your output is required if this appears.)*

---

## Write now

Output a JSON array only. No prose, no markdown fences, no explanation.
One object per evidence item.

---

## Column-by-column rules (for Control Plan)

### CARRY — copy verbatim from evidence, no modification

| Key | Source field in evidence |
|-----|--------------------------|
| `production_item_name` | `production_item_name` |
| `process_segment_name` | `process_segment_name` — if absent in source, write `null`; do not invent |
| `operation_number` | `operation_number` |
| `operation_name` | `operation_name` |
| `product_characteristic` | `product_characteristic` |

---

### FIXED NULL — always null, no exceptions

`specification_tolerance`, `tool_number`, `tool_name`, `gage_number`,
`sample_size`, `sample_frequency`

Write these as JSON `null`. Not the string "null". Not "N/A". Not "TBD".
Rule V3 rejects any non-null value here regardless of content.

---

### AUTHOR — derive only from this row's evidence, never from domain knowledge

**`process_characteristic`**
- If the evidence row has a non-null `process_characteristic`: copy it verbatim (treat as CARRY).
- If null in source: derive a concise process parameter name from `failure_cause`.
  Example: `failure_cause` = "Insufficient torque applied" → `process_characteristic` = "Torque application"
- If both are null: write `null`.

**`special_characteristic_class`**
Use only `severity_rating` and `occurrence_rating` from this evidence row.
Do not use industry knowledge. Do not reason about real-world risk. Look up the table:

| Severity | Occurrence | Write |
|----------|------------|-------|
| >= 9     | any        | `"CC"` |
| 7 or 8   | any        | `"SC"` |
| <= 6     | >= 7       | `"SC"` |
| <= 6     | <= 6       | `null` |

If either rating is missing from the row: write `null`.

**`evaluation_measurement_technique`**
- Source field: `detective_control`
- Restate in Control Plan measurement language — short, specific, no "Detective Controls:" prefix.
  Example: "Detective Controls: CMM at final inspection" → `"CMM dimensional inspection"`
- Max 6 words.
- If `detective_control` is null in evidence: write `null`.

**`control_method`**
- Source field: `preventive_control`
- Restate in Control Plan method language — short, actionable, no "Preventive Controls:" prefix.
  Example: "Preventive Controls: Torque wrench calibrated to 25 Nm" → `"Calibrated torque wrench, 25 Nm"`
- If `preventive_control` is null in evidence: write `null`.

**`reaction_plan`**
- Derivation rule: derive a standard containment action ONLY if `detective_control` is non-null.
  Example: "Contain suspect parts. Notify Quality Lead and adjust process parameters."
- If `detective_control` is null: write `null` unconditionally. Rule V5 rejects reaction plan without detective control.\n