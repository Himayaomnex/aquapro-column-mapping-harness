# Skill: parse_pfmea_workbook

## Signature

`parse_pfmea_workbook(file_path: str) -> EvidenceItem[]`

## When the agent should call it

The user has uploaded a PFMEA `.xlsx` file and the evidence store does not yet contain
mapped operation data for it. This is always the first skill called on a new workbook.

## Procedure

1. `workbook_parser(file_path)` — reads the `.xlsx` file, identifies the header row,
   extracts all data rows as raw key-value dicts with Excel header strings as keys
2. `column_mapper(raw_rows)` — translates raw headers to canonical concept keys using
   the synonym table in `schemas/canonical_context.md`; groups rows by `operation_number`;
   any header not in the synonym table is retained as `unmapped_fields` — not dropped

## Returns

Evidence items, one per (operation x characteristic) pair. Each item carries:
`operation_number`, `operation_name`, `process_segment_name`, and all canonical PFMEA
fields present in that row (`product_characteristic`, `failure_cause`, `severity_rating`,
`occurrence_rating`, `preventive_control`, `detective_control`, etc.), plus `source_sheet`
and `source_row` for traceability, plus `unmapped_fields` listing any unrecognized headers.

**A skill never composes an answer and never authors output fields.**
It gathers and returns evidence. The compose step uses this evidence to write Control Plan rows.

## Cost

2 tool calls. Typically 5,000–15,000 tokens depending on workbook size.

## Failure

If `workbook_parser` returns an empty list:
  return empty with `found_nothing=true`, `reason="no data rows found in workbook"`

If `column_mapper` maps zero recognized canonical concepts:
  return empty with `found_nothing=true`, `reason="no recognized PFMEA headers in workbook"`

Do not attempt to infer rows from an empty or unrecognized workbook.
Do not fall back to a keyword search — the agent can see the budget and decide next steps.
