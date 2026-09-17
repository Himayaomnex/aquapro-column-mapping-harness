# Skill: retrieve_from_rag

## Signature

`retrieve_from_rag(production_item_name: str, top_k: int = 20) -> EvidenceItem[]`

## When the agent should call it

The user has provided a production item name but has NOT uploaded a PFMEA file.
The evidence store is empty and there is no `file_path` to parse.
This is Path B — the no-file input path.

## Procedure

1. `rag_retriever(production_item_name, top_k)` — queries the Qdrant PFMEA vector store
   by production item name; returns the top_k most relevant PFMEA records stored from
   previous runs. Each record carries canonical fields already mapped from its original
   source workbook. Tag all returned items: `source = rag_data`.

2. **Process retrieved records:** inspect the returned items for L1-L4 Engineering Tree
   fields (`process_segment_name`, `operation`, `characteristic`, `failure_cause`).
   Tag all returned items: `source = rag_data`.

## Returns

Evidence items grouped by `operation_number`. Each item carries the canonical PFMEA fields
available for that operation, plus `source` tag (`rag_data` or `ai_suggestion`) and
`confidence` (`confirmed` or `inferred`). Items tagged `ai_suggestion` are always lower
priority than `rag_data` items — the compose step must not treat them as equivalent.

**A skill never composes an answer.** It gathers and returns evidence only.

## Cost

Path B (RAG hit): 1 tool call, ~8,000–20,000 tokens depending on result size.
Path B (RAG miss + hierarchy fallback): 2 tool calls, ~12,000–25,000 tokens.

## Failure

If `rag_retriever` returns an empty list:
  return empty with `found_nothing=true`, `reason="no PFMEA records found for this item in knowledge repository"`

If `rag_retriever` returns items but zero recognized canonical fields are present:
  return empty with `found_nothing=true`, `reason="RAG records exist but contain no mappable PFMEA fields"`

Tag all returned items with source_type='rag_data' to guarantee complete audit traceability.
