# Plan Prompt (Rendered Fresh Every Planning Turn)

## Task
{{ task }}

## Declared Capability
{{ capability_id | default("NOT YET DECLARED -- this is your Turn 1, you must declare now") }}

{% if capability_id %}
## Active Capability Contract
- Capability: {{ capability_id }}
- Consumer: {{ capability.consumer | default("Quality / Process Engineer") }}
- Contract: `capabilities/{{ capability_id }}.md`
- Required tool order: workbook_parser -> column_mapper -> excel_builder -> validator -> excel_exporter
{% endif %}

## Tool Registry
{{ tool_registry }}

## Available Skills
{{ skills }}

## Plan History (Your Prior Reasoning)
{% for turn in plan_history %}
Turn {{ loop.index }}: {{ turn.reasoning }} -> {{ turn.action_taken }}
{% endfor %}

## Observations (Completed Tool Outputs)
{% for obs in observations %}
- `{{ obs.tool }}`: {{ obs.status }} | {{ obs.summary }}
{% endfor %}

## Evidence Summary
Operations mapped so far: {{ evidence.operation_count }}
Operations in source: {{ evidence.source_operation_count }}
Coverage: {{ evidence.coverage_pct }}%
Unmapped headers: {{ evidence.unmapped_headers | default("none") }}

## Budget
Tokens remaining: {{ budget.tokens_remaining }}
Tool calls remaining: {{ budget.tool_calls_remaining }} of 8

---

## Your Turn

State your reasoning in ONE sentence, then emit exactly one action.

**If this is Turn 1:** Declare your capability before anything else.
**If evidence coverage is < 100%:** Do not say ready_to_compose.
**If all operations are mapped:** Say ready_to_compose.

Actions:
- Tool call: `{ "tool": "tool_name", "args": { ... } }`
- Declare capability: `{ "capability_id": "{{ capability_id | default('control_plan_from_pfmea') }}", "reasoning": "..." }`
- Ready: `{ "action": "ready_to_compose", "reasoning": "All N operations mapped." }`\n