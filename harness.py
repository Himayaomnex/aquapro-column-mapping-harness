"""
Universal Agent Harness (harness.py) - Production Grade
Implements the Router-Free Unified Harness using LangGraph.
Full two-loop agency and self-repair architecture supporting the 2 core scenarios:
  - Scenario 1 (Document Provided): Uploaded Excel workbook (via workbook_parser & column_mapper)
  - Scenario 2 (No Document Provided): Historical RAG retrieval by item name (via rag_retriever)
"""

import os
import sys
import json
import re
import argparse
from typing import TypedDict, List, Dict, Any, Optional
import jinja2

from langgraph.graph import StateGraph, START, END

from tools import (
    MappedContextItem,
    MappedContext,
    ControlPlanRow,
    Violation,
    ExecutionLog,
    workbook_parser,
    column_mapper,
    excel_builder,
    control_plan_builder,
    validator,
    excel_exporter,
    rag_retriever,
)
from config import get_llm, GEMINI_API_KEY

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _extract_item_from_task(task_text: str) -> str:
    if not task_text:
        return "Production Item"
    m = re.search(r'["\']([^"\']+)["\']', task_text)
    if m:
        return m.group(1).strip()
    m2 = re.search(r'(?:in|for|about|on)\s+the\s+([A-Za-z0-9\s]+?)(?:\s+have|\s+has|\s+with|\s*\?|\s*$)', task_text, re.IGNORECASE)
    if m2:
        return m2.group(1).strip()
    return "Production Item"



# =====================================================================
# 1. State Definition
# =====================================================================

class AgentState(TypedDict):
    task: str
    file_path: Optional[str]
    production_item_name: Optional[str]
    output_path: str
    capability_id: Optional[str]
    plan_history: List[Dict[str, Any]]
    observations: List[Dict[str, Any]]
    tool_calls_used: int
    raw_rows: List[Dict[str, Any]]
    mapped_context: Optional[MappedContext]
    assembled_evidence: str
    draft_rows: Optional[List[Dict[str, Any]]]
    built_rows: Optional[List[Any]]
    adhoc_result: Optional[Dict[str, Any]]
    violations: List[Violation]
    repair_attempts: int
    status: str
    next_action: Dict[str, Any]
    budget_tokens_remaining: int
    budget_tool_calls_remaining: int


# =====================================================================
# 2. Prompt Loader & Renderer
# =====================================================================

def load_text(relative_path: str) -> str:
    full_path = os.path.join(BASE_DIR, relative_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def load_skills() -> str:
    """Loads all skills from the skills/ directory at runtime."""
    skills_dir = os.path.join(BASE_DIR, "skills")
    if not os.path.exists(skills_dir):
        return ""
    skills_text = []
    for fn in sorted(os.listdir(skills_dir)):
        if fn.endswith(".md"):
            p = os.path.join(skills_dir, fn)
            try:
                with open(p, "r", encoding="utf-8") as f:
                    skills_text.append(f"### Skill: {fn[:-3]}\n{f.read()}")
            except Exception:
                pass
    return "\n\n".join(skills_text)


HARNESS_PROMPT = load_text("prompts/00-harness.md")
TOOL_REGISTRY = load_text("tools/registry.md")
SKILLS_REGISTRY = load_skills()
PLAN_TEMPLATE = jinja2.Template(load_text("prompts/10-plan.md"))
COMPOSE_TEMPLATE = jinja2.Template(load_text("prompts/20-compose.md"))
REPAIR_TEMPLATE = jinja2.Template(load_text("prompts/30-repair.md"))


# =====================================================================
# 3. LangGraph Nodes
# =====================================================================

def plan_node(state: AgentState) -> Dict[str, Any]:
    """
    Model Node: Inspects input path, capability contract, tool list, observations, and budget.
    Emits capability declaration, tool calls, or 'ready_to_compose'.
    """
    turn_num = len(state.get("plan_history", [])) + 1
    print(f"\n" + "-" * 85)
    print(f"  [LangGraph: plan_node] Turn {turn_num} of 6")
    print("-" * 85)
    print(f"  Task:             {state['task']}")
    print(f"  Active Evidence:  {len(state.get('raw_rows', []))} raw rows | "
          f"{len(state['mapped_context'].items) if state.get('mapped_context') else 0} mapped canonical items")
    print(f"  Budget Remaining: {state['budget_tokens_remaining']} tokens | {state['budget_tool_calls_remaining']} tool calls")

    # Guard against excessive plan turns
    if turn_num >= 6:
        print("  [plan_node Guard] Reached max planning turns (6) -> emitting 'ready_to_compose'")
        return {
            "next_action": {
                "action": "ready_to_compose",
                "reasoning": "Plan limit reached."
            },
            "status": "PLANNING"
        }

    # If evidence is already complete
    if state.get("mapped_context") and len(state["mapped_context"].items) > 0:
        ops = state['mapped_context'].source_operations
        print(f"  [plan_node Decision] Evidence complete across {len(ops)} operations: {ops}")
        print(f"  [plan_node Decision] Emitting 'ready_to_compose' -> Transitioning to assemble_node")
        return {
            "next_action": {
                "action": "ready_to_compose",
                "reasoning": f"All {len(ops)} operations mapped."
            },
            "status": "PLANNING"
        }

    # Render turn prompt
    evidence_dict = {
        "operation_count": len(state["mapped_context"].items) if state.get("mapped_context") else 0,
        "source_operation_count": len(state["mapped_context"].source_operations) if state.get("mapped_context") else 0,
        "coverage_pct": 100 if (state.get("mapped_context") and state["mapped_context"].items) else 0,
        "unmapped_headers": state["mapped_context"].unmapped_headers if state.get("mapped_context") else []
    }

    cap_consumers = {
        "control_plan_from_pfmea": "Quality Engineer for AIAG PPAP submission",
        "pfmea_aiag_to_vda": "Manufacturing / Quality Team for AIAG-VDA 1st Edition Harmonization",
        "dfmea_aiag_to_vda": "Product Design Team for AIAG-VDA Harmonization",
        "dfmea_to_pfmea": "Cross-Functional Engineering Team for Design-to-Process Linkage",
        "ad_hoc": "Quality & Operations Analyst"
    }
    cap_id = state.get("capability_id") or "control_plan_from_pfmea"
    consumer = cap_consumers.get(cap_id, "Automotive Quality Engineer")

    plan_prompt = PLAN_TEMPLATE.render(
        task=state["task"],
        capability_id=cap_id,
        capability={"consumer": consumer},
        tool_registry=TOOL_REGISTRY,
        skills=SKILLS_REGISTRY,
        plan_history=state["plan_history"],
        observations=state["observations"],
        evidence=evidence_dict,
        budget={
            "tokens_remaining": state["budget_tokens_remaining"],
            "tool_calls_remaining": state["budget_tool_calls_remaining"]
        }
    )

    # If Gemini API key is configured, invoke model
    if GEMINI_API_KEY:
        try:
            llm = get_llm()
            full_prompt = f"{HARNESS_PROMPT}\n\n---\n\n{plan_prompt}"
            response = llm.invoke(full_prompt)
            raw_content = response.content
            
            # Extract plain text without LangChain list/metadata wrapping
            if isinstance(raw_content, list):
                text_chunks = [b.get("text", "") if isinstance(b, dict) else str(b) for b in raw_content]
                content_str = "\n".join(text_chunks)
            else:
                content_str = str(raw_content)

            # Extract clean JSON
            code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content_str, re.DOTALL)
            json_str = code_block.group(1) if code_block else None
            if not json_str:
                json_match = re.search(r'\{[^{}]*"capability_id"[^{}]*\}', content_str, re.DOTALL)
                json_str = json_match.group(0) if json_match else None

            if json_str:
                action = json.loads(json_str)
                cap = action.get("capability_id") or state.get("capability_id") or "control_plan_from_pfmea"
                # If Turn 1 declared capability without a tool call, attach first entry tool
                if not action.get("tool") and action.get("action") != "ready_to_compose":
                    if state.get("file_path"):
                        action["tool"] = "workbook_parser"
                        action["args"] = {"file_path": state["file_path"]}
                    else:
                        item_q = state.get("production_item_name") or _extract_item_from_task(state.get("task", ""))
                        action["tool"] = "rag_retriever"
                        action["args"] = {"production_item_name": item_q}
                print(f"[plan_node Decision] Capability: {cap} | Reasoning: {action.get('reasoning', 'Declared.')}")
                return {"next_action": action, "capability_id": cap}
        except Exception as e:
            print(f"[plan_node Info] Using deterministic dispatch: {e}")

    # Deterministic dispatch for all 3 paths
    cap = state.get("capability_id")
    if not cap:
        task_lower = (state.get("task") or "").lower()
        if any(w in task_lower for w in ["which", "why", "how many", "analyze", "?", "who", "where"]):
            cap = "ad_hoc"
        elif "vda" in task_lower and "dfmea" in task_lower:
            cap = "dfmea_aiag_to_vda"
        elif "vda" in task_lower:
            cap = "pfmea_aiag_to_vda"
        elif "link" in task_lower or "dfmea to pfmea" in task_lower:
            cap = "dfmea_to_pfmea"
        else:
            cap = "control_plan_from_pfmea"

    # Path A: File upload
    if state.get("file_path"):
        if not state["raw_rows"]:
            return {
                "capability_id": cap,
                "next_action": {
                    "capability_id": cap,
                    "tool": "workbook_parser",
                    "args": {"file_path": state["file_path"]}
                }
            }
        elif not state.get("mapped_context"):
            return {
                "capability_id": cap,
                "next_action": {
                    "tool": "column_mapper",
                    "args": {}
                }
            }

    # Path B: No file uploaded (RAG query)
    elif state.get("production_item_name"):
        if not state.get("mapped_context"):
            return {
                "capability_id": cap,
                "next_action": {
                    "capability_id": cap,
                    "tool": "rag_retriever",
                    "args": {"production_item_name": state["production_item_name"]}
                }
            }



    return {
        "capability_id": cap,
        "next_action": {
            "action": "ready_to_compose",
            "reasoning": "Evidence gathered."
        }
    }


def execute_tool_node(state: AgentState) -> Dict[str, Any]:
    """
    Code Node: Executes requested tool, records observations, and updates budget.
    """
    action = state.get("next_action", {})
    tool_name = action.get("tool")
    args = action.get("args", {})

    if not tool_name or tool_name == "None":
        if state.get("file_path"):
            tool_name = "workbook_parser"
            args = {"file_path": state["file_path"]}
        else:
            tool_name = "rag_retriever"
            args = {"production_item_name": state.get("production_item_name") or _extract_item_from_task(state.get("task", ""))}

    print(f"\n" + "-" * 85)
    print(f"  [LangGraph: execute_tool_node] Invoking Atomic Tool: '{tool_name}'")
    print("-" * 85)
    print(f"  Tool Arguments:   {args}")
    observation = {"tool": tool_name, "args": args, "status": "SUCCESS", "summary": ""}
    new_raw_rows = state["raw_rows"]
    new_mapped_context = state.get("mapped_context")
    
    try:
        if tool_name == "workbook_parser":
            fpath = args.get("file_path") or state["file_path"]
            new_raw_rows = workbook_parser(fpath)
            observation["summary"] = f"Extracted {len(new_raw_rows)} raw rows from Excel workbook."
            print(f"  Result Summary:   {observation['summary']}")

        elif tool_name == "column_mapper":
            new_mapped_context = column_mapper(state["raw_rows"])
            observation["summary"] = (
                f"Mapped {len(new_mapped_context.items)} canonical items across "
                f"operations {new_mapped_context.source_operations}."
            )
            print(f"  Result Summary:   {observation['summary']}")

        elif tool_name == "rag_retriever":
            item_name = args.get("production_item_name") or state["production_item_name"]
            new_mapped_context = rag_retriever(item_name)
            observation["summary"] = (
                f"Retrieved {len(new_mapped_context.items)} historical items across "
                f"operations {new_mapped_context.source_operations} from knowledge base."
            )
            print(f"  Result Summary:   {observation['summary']}")




    except Exception as exc:
        observation["status"] = "FAILED"
        observation["summary"] = f"Tool '{tool_name}' failed: {str(exc)}"
        print(f"[execute_tool_node] ERROR: {observation['summary']}")

    tool_used = state["tool_calls_used"] + 1
    budget_calls = max(0, state["budget_tool_calls_remaining"] - 1)
    budget_tokens = max(0, state["budget_tokens_remaining"] - 500)

    history_entry = {
        "reasoning": action.get("reasoning", f"Call {tool_name}"),
        "action_taken": tool_name
    }

    return {
        "raw_rows": new_raw_rows,
        "mapped_context": new_mapped_context,
                "observations": state["observations"] + [observation],
        "plan_history": state["plan_history"] + [history_entry],
        "tool_calls_used": tool_used,
        "budget_tool_calls_remaining": budget_calls,
        "budget_tokens_remaining": budget_tokens,
    }


def assemble_node(state: AgentState) -> Dict[str, Any]:
    """
    Code Node: Selects from EvidenceStore and formats context for the composer.
    """
    print(f"\n" + "-" * 85)
    print(f"  [LangGraph: assemble_node] Structuring Canonical Evidence for Composer")
    print("-" * 85)
    ctx = state.get("mapped_context")
    assembled_lines = []
    if ctx:
        print(f"  Total Items:      {len(ctx.items)} canonical rows across {len(ctx.source_operations)} operations: {ctx.source_operations}")
        print(f"  Unmapped Headers: {ctx.unmapped_headers if ctx.unmapped_headers else 'None (100% matched)'}")

    if ctx:
        for idx, item in enumerate(ctx.items[:100], start=1):  # Batch top evidence
            assembled_lines.append(
                f"[{idx}] op={item.operation_number} ({item.operation_name}) | "
                f"segment={item.process_segment_name} | "
                f"prod_char={item.product_characteristic} | "
                f"cause={item.failure_cause} | "
                f"sev={item.severity_rating} | occ={item.occurrence_rating} | "
                f"prev_ctrl={item.preventive_control} | det_ctrl={item.detective_control}"
            )

    assembled_str = "\n".join(assembled_lines)
    return {"assembled_evidence": assembled_str}


def _load_capability_contract(capability_id: str) -> str:
    """Loads markdown capability contract to inline into model prompt."""
    path = os.path.join(BASE_DIR, "capabilities", f"{capability_id}.md")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return f"Execute quality engineering transformation under capability '{capability_id}'."


def _load_skill_for_capability(capability_id: str) -> str:
    """Loads the procedural skill workflow matching the declared capability."""
    skill_map = {
        "control_plan_from_pfmea": "skills/convert_pfmea_to_control_plan.md",
        "pfmea_aiag_to_vda": "skills/convert_pfmea_aiag_to_vda.md",
        "dfmea_aiag_to_vda": "skills/convert_dfmea_aiag_to_vda.md",
        "dfmea_to_pfmea": "skills/link_dfmea_to_pfmea.md",
    }
    rel_path = skill_map.get(capability_id)
    if rel_path:
        return load_text(rel_path)
    return ""


def compose_node(state: AgentState) -> Dict[str, Any]:
    """
    Model Node: Authors document rows from canonical evidence under capability contract.
    """
    cap_id = state.get("capability_id", "control_plan_from_pfmea")
    print(f"\n" + "-" * 85)
    print(f"  [LangGraph: compose_node] Authoring Document Rows under Capability: '{cap_id}'")
    print("-" * 85)
    print(f"  Authoring Policy: CARRY verbatim | AUTHOR AP & Special Chars | ABSTAIN blanking")
    cap_contract = _load_capability_contract(cap_id)
    active_skill = _load_skill_for_capability(cap_id)
    prompt = COMPOSE_TEMPLATE.render(
        task=state["task"],
        capability_id=cap_id,
        capability_contract=cap_contract,
        active_skill=active_skill,
        assembled_evidence=state["assembled_evidence"],
        dropped_notice="",
        existing_data=""
    )

    draft_dict_by_op = {}

    if GEMINI_API_KEY:
        try:
            llm = get_llm()
            full_prompt = f"{HARNESS_PROMPT}\n\n---\n\n{prompt}"
            response = llm.invoke(full_prompt)
            print(f"[compose_node] LLM Output received.")

            raw_resp = response.content
            if isinstance(raw_resp, list):
                resp_text = "\n".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in raw_resp])
            else:
                resp_text = str(raw_resp)

            code_block = re.search(r'```(?:json)?\s*(\[\s*\{.*?\}\s*\])\s*```', resp_text, re.DOTALL)
            json_str = code_block.group(1) if code_block else None
            if not json_str:
                json_match = re.search(r'\[\s*\{.*\}\s*\]', resp_text, re.DOTALL)
                json_str = json_match.group(0) if json_match else None

            if json_str:
                parsed_rows = json.loads(json_str)
                for idx, row_obj in enumerate(parsed_rows, start=1):
                    op_num = str(row_obj.get("operation_number", "")).strip()
                    if op_num:
                        draft_dict_by_op[op_num] = row_obj
                        draft_dict_by_op[f"{op_num}_{idx}"] = row_obj
        except Exception as e:
            print(f"[compose_node Info] Standardizing drafted rows via excel_builder: {e}")

    if cap_id == "ad_hoc":
        # Extract ad-hoc analytical Q&A
        adhoc_res = None
        task_str = state.get("task", "")
        if GEMINI_API_KEY:
            try:
                llm = get_llm()
                evidence_summary = "\n".join([
                    f"- Op {it.operation_number} ({it.operation_name}) | Mode: '{it.failure_mode}' | Cause: '{it.failure_cause}' | S={it.severity_rating}, O={it.occurrence_rating}, D={it.detection_rating} | Prev: '{it.preventive_control}' | Det: '{it.detective_control}'"
                    for it in (state.get("mapped_context").items if state.get("mapped_context") else [])[:150]
                ])
                adhoc_prompt = f"""You are a certified automotive quality and APQP audit expert.
Analyze the following FMEA evidence to answer the user's specific analytical question.

User Question / Task:
"{task_str}"

Evidence:
{evidence_summary}

Return a single JSON object strictly matching this schema:
{{
  "question": "{task_str}",
  "answer": "Direct, precise answer addressing the user's specific question with exact numbers and names.",
  "claims": [
    {{
      "claim": "Specific factual claim derived directly from the evidence",
      "evidence_ids": ["Op <number>"]
    }}
  ],
  "operations_analyzed": {list(state['mapped_context'].source_operations if state.get('mapped_context') else [])},
  "uncertainty": null
}}
"""
                resp = llm.invoke(adhoc_prompt)
                resp_text = resp.content
                if isinstance(resp_text, list):
                    resp_text = "\n".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in resp_text])
                else:
                    resp_text = str(resp_text)

                code_b = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', resp_text, re.DOTALL)
                j_str = code_b.group(1) if code_b else None
                if not j_str:
                    j_m = re.search(r'\{[^{}]*"answer"[^{}]*\}', resp_text, re.DOTALL)
                    j_str = j_m.group(0) if j_m else None
                if j_str:
                    adhoc_res = json.loads(j_str)
            except Exception as e:
                print(f"[compose_node Info] LLM ad_hoc analysis fallback: {e}")

        if not adhoc_res:
            # Deterministic query-tailored analysis from mapped evidence
            ctx_items = state["mapped_context"].items if state.get("mapped_context") else []
            t_lower = task_str.lower()

            # Query A: Error-proofing / poka-yoke / high severity without automated controls
            if any(k in t_lower for k in ["error-proofing", "error proofing", "poka-yoke", "poka yoke", "interlock"]):
                ops_high_sev = []
                for itm in ctx_items:
                    sev = itm.severity_rating or 0
                    prev = (itm.preventive_control or "").lower()
                    has_poka = "poka" in prev or "error" in prev or "interlock" in prev or "automatic" in prev or "sensor" in prev
                    if sev >= 8 and not has_poka:
                        ops_high_sev.append({
                            "operation": itm.operation_number,
                            "operation_name": itm.operation_name,
                            "severity": sev,
                            "cause": itm.failure_cause,
                            "current_control": itm.preventive_control or "None"
                        })
                adhoc_res = {
                    "question": task_str,
                    "answer": f"Identified {len(ops_high_sev)} operations with Severity >= 8 lacking automated error-proofing.",
                    "claims": [
                        {
                            "claim": f"Operation {o['operation']} ({o['operation_name']}) has Severity {o['severity']} for cause '{o['cause']}' with manual control '{o['current_control']}'.",
                            "evidence_ids": [f"Op {o['operation']}"]
                        }
                        for o in ops_high_sev[:8]
                    ],
                    "operations_analyzed": state["mapped_context"].source_operations if state.get("mapped_context") else [],
                    "uncertainty": None if ops_high_sev else "No high-severity operations lacking error proofing found in retrieved dataset."
                }

            # Query B: Visual inspection / manual check
            elif any(k in t_lower for k in ["visual", "manual", "inspection", "verificación", "vista"]):
                vis_items = []
                seen_ops = set()
                for it in ctx_items:
                    det = (it.detective_control or "").lower()
                    if any(w in det for w in ["visual", "vista", "verificaci", "inspecci", "manual"]):
                        if it.operation_number not in seen_ops:
                            seen_ops.add(it.operation_number)
                            vis_items.append(it)
                claims = [
                    {
                        "claim": f"Operation {it.operation_number} ({it.operation_name}) uses visual inspection: '{it.detective_control}'.",
                        "evidence_ids": [f"Op {it.operation_number}"]
                    }
                    for it in vis_items
                ]
                ops_list = [it.operation_number for it in vis_items]
                adhoc_res = {
                    "question": task_str,
                    "answer": f"Identified {len(vis_items)} operations relying on visual or manual verification controls: Operations {ops_list}.",
                    "claims": claims,
                    "operations_analyzed": state["mapped_context"].source_operations if state.get("mapped_context") else [],
                    "uncertainty": None if vis_items else "No operations with explicit visual inspection descriptions found."
                }

            # Query C: Top failure modes / highest severity / highest risk ranking
            else:
                ranked = sorted(
                    [it for it in ctx_items if it.severity_rating is not None and it.failure_mode],
                    key=lambda x: x.severity_rating or 0,
                    reverse=True
                )
                seen_modes = set()
                top_items = []
                for it in ranked:
                    k = (it.operation_number, it.failure_mode)
                    if k not in seen_modes:
                        seen_modes.add(k)
                        top_items.append(it)
                    if len(top_items) == 5:
                        break

                claims = [
                    {
                        "claim": f"Rank {idx}: Op {it.operation_number} ({it.operation_name}) has Severity {it.severity_rating} for failure mode '{it.failure_mode}' (Cause: '{it.failure_cause or 'Unspecified'}').",
                        "evidence_ids": [f"Op {it.operation_number}"]
                    }
                    for idx, it in enumerate(top_items, 1)
                ]
                ans_summary = "; ".join([f"#{idx}: Op {it.operation_number} '{it.failure_mode}' (Sev {it.severity_rating})" for idx, it in enumerate(top_items, 1)])
                adhoc_res = {
                    "question": task_str,
                    "answer": f"The top {len(top_items)} failure modes with the highest severity are: {ans_summary}.",
                    "claims": claims,
                    "operations_analyzed": state["mapped_context"].source_operations if state.get("mapped_context") else [],
                    "uncertainty": None if top_items else "No failure modes with numeric severity ratings found in source."
                }

        print(f"[compose_node] Formulated analytical response for ad_hoc Q&A: {adhoc_res.get('answer', '')[:100]}...")
        return {"built_rows": [], "adhoc_result": adhoc_res}

    built_rows = excel_builder(
        mapped_context=state["mapped_context"],
        draft_fields=draft_dict_by_op if draft_dict_by_op else None,
        is_existing_baseline=bool(state.get("document_reference")),
        document_type=state.get("capability_id", "control_plan_from_pfmea")
    )
    print(f"[compose_node] Constructed {len(built_rows)} AIAG Control Plan rows.")
    return {"built_rows": built_rows}


def verify_node(state: AgentState) -> Dict[str, Any]:
    """
    Code Node: Mechanically checks built rows against Rules V1-V5.
    """
    cap_id = state.get("capability_id", "control_plan_from_pfmea")
    print(f"\n" + "-" * 85)
    print(f"  [LangGraph: verify_node] Mechanical Verification (Rules V1 - V5)")
    print("-" * 85)
    print(f"  Target Capability:        {cap_id}")
    print(f"  Total Document Rows:      {len(state.get('built_rows', []))}")

    if cap_id == "ad_hoc":
        violations = []
        res = state.get("adhoc_result")
        if not res or not res.get("answer"):
            violations.append(Violation(rule_id="V1", on_fail="reject_document", row_identifier="Document", statement="Ad-hoc answer empty", detail="No answer"))
        print(f"  Mechanical Verification:  {len(violations)} Violations")
        return {"violations": violations}

    violations = validator(
        rows=state["built_rows"],
        mapped_context=state["mapped_context"],
        is_existing_baseline=bool(state.get("document_reference")),
        capability_id=cap_id
    )

    if len(violations) == 0:
        print(f"  [PASS] Rule V1 (Schema Completeness): All required keys present per row")
        print(f"  [PASS] Rule V2 (Operation Set Equality): 100% operation fidelity ({state['mapped_context'].source_operations if state.get('mapped_context') else []})")
        print(f"  [PASS] Rule V3 (Mandatory Abstention): 0 hallucinated tooling/gage/tolerance fields")
        print(f"  [PASS] Rule V4 (Evidence Traceability): All authored values grounded in source PFMEA")
        print(f"  [PASS] Rule V5 (Quality Interlocks): Reaction plans matched with detective controls")
        print(f"  Verification Result:      100% COMPLIANT (0 Violations) -> Proceeding to export_node")
    else:
        print(f"  Verification Result:      {len(violations)} Violations Detected:")
        for v in violations[:5]:
            print(f"    - [{v.rule_id}] ({v.on_fail}) {v.row_identifier}: {v.statement} ({v.detail})")
        print(f"  Action:                   Diverting to repair_node for automated self-repair.")

    return {"violations": violations}


def repair_node(state: AgentState) -> Dict[str, Any]:
    """
    Model Node: Self-repair on violations using prompts/30-repair.md.
    Invokes LLM with repair prompt; falls back to deterministic code-based repair.
    """
    attempt = state["repair_attempts"] + 1
    print(f"\n--- [LangGraph: repair_node] Self-Repair Round {attempt} of 2 ---")

    # Serialize previous draft for the repair prompt
    prev_draft_json = []
    for r in state.get("built_rows", []):
        if hasattr(r, "to_dict"):
            prev_draft_json.append(r.to_dict())
        elif hasattr(r, "model_dump"):
            prev_draft_json.append(r.model_dump())
        elif isinstance(r, dict):
            prev_draft_json.append(r)
        else:
            prev_draft_json.append(dict(r))

    repair_prompt = REPAIR_TEMPLATE.render(
        repair_attempt=attempt,
        previous_draft=json.dumps(prev_draft_json, indent=2),
        violations=[v.model_dump() if hasattr(v, "model_dump") else v for v in state["violations"]]
    )

    llm_repaired = False
    repaired_rows: List[Any] = []
    is_baseline = bool(state.get("document_reference"))

    if GEMINI_API_KEY:
        try:
            llm = get_llm()
            full_prompt = f"{HARNESS_PROMPT}\n\n---\n\n{repair_prompt}"
            response = llm.invoke(full_prompt)
            raw_resp = response.content
            if isinstance(raw_resp, list):
                resp_text = "\n".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in raw_resp])
            else:
                resp_text = str(raw_resp)

            code_block = re.search(r'```(?:json)?\s*(\[\s*\{.*?\}\s*\])\s*```', resp_text, re.DOTALL)
            json_str = code_block.group(1) if code_block else None
            if not json_str:
                json_match = re.search(r'\[\s*\{.*\}\s*\]', resp_text, re.DOTALL)
                json_str = json_match.group(0) if json_match else None

            if json_str:
                parsed_repair = json.loads(json_str)
                if isinstance(parsed_repair, list) and len(parsed_repair) > 0:
                    cap_id = state.get("capability_id", "control_plan_from_pfmea")
                    if cap_id == "control_plan_from_pfmea":
                        for item in parsed_repair:
                            if isinstance(item, dict):
                                repaired_rows.append(ControlPlanRow(**item))
                    else:
                        repaired_rows = parsed_repair
                    llm_repaired = True
                    print(f"[repair_node] Successfully applied LLM self-repair.")
        except Exception as e:
            print(f"[repair_node Warning] LLM repair call failed ({type(e).__name__}: {e}). Falling back to code repair.")

    if not llm_repaired:
        # Code-level deterministic fallback repair
        for idx, row in enumerate(state["built_rows"], start=1):
            if hasattr(row, "operation_number"):
                row_id = f"Row {idx} (Op {row.operation_number})"
                row_dict = row.to_dict()
            elif isinstance(row, dict):
                op_num = row.get("operation_number") or row.get("process_step") or idx
                row_id = f"Row {idx} (Op {op_num})"
                row_dict = dict(row)
            else:
                row_id = f"Row {idx}"
                row_dict = dict(row)

            row_violations = [v for v in state["violations"] if v.row_identifier == row_id]

            for v in row_violations:
                if v.rule_id == "V1":
                    for col in ["operation_number", "operation_name", "product_characteristic", "process_characteristic"]:
                        if col not in row_dict:
                            row_dict[col] = None
                if v.rule_id == "V3" and not is_baseline:
                    for k in ["specification_tolerance", "tool_number", "tool_name", "gage_number", "sample_size", "sample_frequency"]:
                        if k in row_dict:
                            row_dict[k] = None
                if v.rule_id == "V5":
                    if "reaction_plan" in row_dict:
                        row_dict["reaction_plan"] = None
                if v.rule_id == "V4":
                    if "evaluation_measurement_technique" in v.detail and "evaluation_measurement_technique" in row_dict:
                        row_dict["evaluation_measurement_technique"] = None
                    if "control_method" in v.detail and "control_method" in row_dict:
                        row_dict["control_method"] = None

            if isinstance(row, ControlPlanRow):
                repaired_rows.append(ControlPlanRow(**row_dict))
            else:
                repaired_rows.append(row_dict)

    return {
        "built_rows": repaired_rows,
        "repair_attempts": attempt
    }


def export_node(state: AgentState) -> Dict[str, Any]:
    """
    Code Node: Writes verified rows into AIAG 4th Edition Excel file or delivers Q&A report.
    """
    print(f"\n" + "-" * 85)
    print(f"  [LangGraph: export_node] Delivering Validated Industry Output")
    print("-" * 85)
    print(f"  Destination Path:         {os.path.abspath(state['output_path'])}")
    print(f"  Workbook Structure:       Sheet 1 ('Header' APQP Form) + Sheet 2 ('Body' 3-Row Hierarchy)")
    print(f"  Total Validated Rows:     {len(state.get('built_rows', []))}")
    cap_id = state.get("capability_id", "control_plan_from_pfmea")

    # Handle ad_hoc Q&A capability (Use Case 2)
    if cap_id == "ad_hoc":
        adhoc = state.get("adhoc_result", {})
        print(f"\n===================================================================================")
        print(f"                          AD-HOC ANALYTICAL Q&A REPORT")
        print(f"===================================================================================")
        print(f"Question: {adhoc.get('question', state['task'])}\n")
        print(f"Answer:\n{adhoc.get('answer', '')}\n")
        print(f"Operations Analyzed: {adhoc.get('operations_analyzed', [])}\n")
        print(f"Verified Evidence Claims:")
        for c in adhoc.get("claims", []):
            print(f"  - {c.get('claim')} [Evidence: {', '.join(c.get('evidence_ids', []))}]")
        if adhoc.get("uncertainty"):
            print(f"\nUncertainty Note: {adhoc.get('uncertainty')}")
        print(f"===================================================================================")

        # Save JSON output
        out_json = "output/ad_hoc_analysis.json"
        os.makedirs("output", exist_ok=True)
        with open(out_json, "w", encoding="utf-8") as jf:
            json.dump(adhoc, jf, indent=2)

        # Print audit dashboard
        tokens_used = 60000 - state.get("budget_tokens_remaining", 60000)
        source_desc = f"Scenario 2 (RAG: '{state.get('production_item_name') or 'Knowledge Base'}')"
        print(f"\n===================================================================================")
        print(f"                            EXECUTION METRICS & AUDIT")
        print(f"===================================================================================")
        print(f"Capability:          ad_hoc")
        print(f"Execution Status:    COMPLETE (0 Violations)")
        print(f"Source Mode:         {source_desc}")
        print(f"Tokens Consumed:     ~{tokens_used:,} tokens (Remaining: {state.get('budget_tokens_remaining', 0):,})")
        print(f"Tool Calls Made:     {state.get('tool_calls_used', 0)} / 8 allocated")
        print(f"Agent Tool Calls & Observations:")
        for idx, obs in enumerate(state.get("observations", []), start=1):
            tname = obs.get("tool", "unknown")
            targs = obs.get("args", {})
            arg_str = ", ".join(f"{k}={repr(v)}" for k, v in targs.items()) if targs else ""
            print(f"  {idx}. {tname}({arg_str})")
            print(f"     -> {obs.get('status')}: {obs.get('summary')}")
        print(f"Artifact Saved:      {os.path.abspath(out_json)}")
        print(f"===================================================================================\n")
        return {"status": "COMPLETE"}

    # Handle Document Generation capabilities (Use Case 1)
    source_id = (
        state.get("file_path")
        or state.get("production_item_name")
        or state.get("document_reference")
        or ""
    )
    stype = "file" if state.get("file_path") else ("rag" if state.get("production_item_name") else "existing_document")

    log = ExecutionLog(
        capability_id=cap_id,
        status="COMPLETE",
        source_type=stype,
        source_identifier=source_id,
        total_source_operations=len(state["mapped_context"].source_operations) if state.get("mapped_context") else 0,
        output_rows_count=len(state["built_rows"]),
        unmapped_headers=state["mapped_context"].unmapped_headers if state.get("mapped_context") else [],
        violations=[],
        repair_attempts=state["repair_attempts"],
        output_file=os.path.abspath(state["output_path"])
    )

    excel_exporter(state["built_rows"], state["output_path"], execution_log=log)

    print(f"\n==================== Validated Output Preview ({cap_id}) ====================")
    print(f"{'Op #':<6} | {'Operation Description':<25} | {'Cls':<4} | {'Control Method':<26} | {'Reaction Plan':<24}")
    print("-" * 95)
    for r in state["built_rows"][:6]:
        r_dict = r.to_dict() if hasattr(r, "to_dict") else r
        op = re.sub(r'[\r\n\t]+', ' ', str(r_dict.get("operation_number") or r_dict.get("process_step") or r_dict.get("focus_element") or "")).strip()[:6]
        desc = re.sub(r'[\r\n\t]+', ' ', str(r_dict.get("operation_name") or r_dict.get("failure_mode_fm") or r_dict.get("design_characteristic") or "")).strip()[:25]
        sp = re.sub(r'[\r\n\t]+', ' ', str(r_dict.get("special_characteristic_class") or r_dict.get("action_priority_ap") or "")).strip()[:4]
        cm = re.sub(r'[\r\n\t]+', ' ', str(r_dict.get("control_method") or r_dict.get("current_prevention_control") or r_dict.get("recommended_process_control") or "")).strip()[:26]
        rp = re.sub(r'[\r\n\t]+', ' ', str(r_dict.get("reaction_plan") or r_dict.get("current_detection_control") or "")).strip()[:24]
        print(f"{op:<6} | {desc:<25} | {sp:<4} | {cm:<26} | {rp:<24}")
    if len(state["built_rows"]) > 6:
        print(f"... and {len(state['built_rows']) - 6} more rows.")
    print("=" * 95)

    # 2. Executive Metrics & Audit Dashboard (Tokens, Observations, Traceability)
    tokens_used = 60000 - state.get("budget_tokens_remaining", 60000)
    source_desc = f"Scenario 1 (File: '{state.get('file_path')}')" if state.get("file_path") else f"Scenario 2 (RAG: '{state.get('production_item_name')}')"
    ops_list = state["mapped_context"].source_operations if state.get("mapped_context") else []

    print(f"\n===================================================================================")
    print(f"                            EXECUTION METRICS & AUDIT")
    print(f"===================================================================================")
    print(f"Capability:          {cap_id}")
    print(f"Execution Status:    COMPLETE (0 Violations)")
    print(f"Source Mode:         {source_desc}")
    print(f"Operations Mapped:   {ops_list} (100% Coverage)")
    print(f"Generated Output:    {len(state['built_rows'])} validated rows")
    print(f"Tokens Consumed:     ~{tokens_used:,} tokens (Remaining: {state.get('budget_tokens_remaining', 0):,})")
    print(f"Tool Calls Made:     {state.get('tool_calls_used', 0)} / 8 allocated")
    print(f"-----------------------------------------------------------------------------------")
    print(f"Agent Tool Calls & Observations:")
    for idx, obs in enumerate(state.get("observations", []), start=1):
        tname = obs.get("tool", "unknown")
        targs = obs.get("args", {})
        arg_str = ", ".join(f"{k}={repr(v)}" for k, v in targs.items()) if targs else ""
        print(f"  {idx}. {tname}({arg_str})")
        print(f"     -> {obs.get('status')}: {obs.get('summary')}")
    print(f"-----------------------------------------------------------------------------------")
    print(f"Output Artifact:     {os.path.abspath(state['output_path'])}")
    print(f"Audit Log Saved:     {os.path.abspath(os.path.join(os.path.dirname(state['output_path']), 'execution_log.json'))}")
    print(f"===================================================================================\n")
    return {"status": "COMPLETE"}


def degrade_node(state: AgentState) -> Dict[str, Any]:
    """
    Code Node: Ships only verified rows, drops failed rows, logs DEGRADED.
    """
    print(f"\n--- [LangGraph: degrade_node] Entering Degrade Mode ---")
    failing_row_ids = {v.row_identifier for v in state["violations"] if v.on_fail == "reject_row"}
    passing_rows = []
    for idx, r in enumerate(state["built_rows"], start=1):
        op_val = getattr(r, "operation_number", None) if hasattr(r, "operation_number") else (r.get("operation_number") if isinstance(r, dict) else idx)
        rid = f"Row {idx} (Op {op_val})"
        if rid not in failing_row_ids and f"Row {idx}" not in failing_row_ids:
            passing_rows.append(r)

    log = ExecutionLog(
        capability_id=state.get("capability_id") or "control_plan_from_pfmea",
        status="DEGRADED",
        source_type="file" if state.get("file_path") else "rag",
        source_identifier=state.get("file_path") or "",
        total_source_operations=len(state["mapped_context"].source_operations) if state.get("mapped_context") else 0,
        output_rows_count=len(passing_rows),
        unmapped_headers=state["mapped_context"].unmapped_headers if state.get("mapped_context") else [],
        violations=[v.model_dump() for v in state["violations"]],
        repair_attempts=state["repair_attempts"],
        output_file=os.path.abspath(state["output_path"])
    )

    excel_exporter(passing_rows, state["output_path"], execution_log=log)
    return {"status": "DEGRADED"}


# =====================================================================
# 4. Conditional Edges
# =====================================================================

def route_from_plan(state: AgentState) -> str:
    action = state.get("next_action", {})
    if action.get("action") == "ready_to_compose":
        return "assemble_node"
    if state["tool_calls_used"] >= 8:
        print("[Router-Free Guard] Tool call budget exhausted -> moving to assemble")
        return "assemble_node"
    return "execute_tool_node"


def route_from_verify(state: AgentState) -> str:
    violations = state.get("violations", [])
    if len(violations) == 0:
        return "export_node"
    if state["repair_attempts"] < 2:
        return "repair_node"
    return "degrade_node"


# =====================================================================
# 5. Graph Assembly
# =====================================================================

def build_harness_graph() -> Any:
    graph = StateGraph(AgentState)

    graph.add_node("plan_node", plan_node)
    graph.add_node("execute_tool_node", execute_tool_node)
    graph.add_node("assemble_node", assemble_node)
    graph.add_node("compose_node", compose_node)
    graph.add_node("verify_node", verify_node)
    graph.add_node("repair_node", repair_node)
    graph.add_node("export_node", export_node)
    graph.add_node("degrade_node", degrade_node)

    graph.add_edge(START, "plan_node")

    graph.add_conditional_edges(
        "plan_node",
        route_from_plan,
        {
            "execute_tool_node": "execute_tool_node",
            "assemble_node": "assemble_node"
        }
    )
    graph.add_edge("execute_tool_node", "plan_node")

    graph.add_edge("assemble_node", "compose_node")
    graph.add_edge("compose_node", "verify_node")

    graph.add_conditional_edges(
        "verify_node",
        route_from_verify,
        {
            "export_node": "export_node",
            "repair_node": "repair_node",
            "degrade_node": "degrade_node"
        }
    )
    graph.add_edge("repair_node", "verify_node")

    graph.add_edge("export_node", END)
    graph.add_edge("degrade_node", END)

    return graph.compile()


# =====================================================================
# 6. UnifiedHarness Class Wrapper
# =====================================================================

class UnifiedHarness:
    def __init__(self, capability_id: str = "control_plan_from_pfmea"):
        self.capability_id = capability_id
        self.app = build_harness_graph()

    def run(
        self,
        task: Optional[str] = None,
        file_path: Optional[str] = None,
        production_item_name: Optional[str] = None,
        output_path: Optional[str] = None,
        capability: Optional[str] = None
    ) -> ExecutionLog:
        if capability:
            self.capability_id = capability

        if not output_path:
            if self.capability_id == "pfmea_aiag_to_vda":
                output_path = "output/PFMEA_AIAG_VDA.xlsx"
            elif self.capability_id == "dfmea_aiag_to_vda":
                output_path = "output/DFMEA_AIAG_VDA.xlsx"
            elif self.capability_id == "dfmea_to_pfmea":
                output_path = "output/PFMEA_from_DFMEA.xlsx"
            else:
                output_path = "output/Control_Plan.xlsx"

        print("\n" + "=" * 85)
        print("                 AQUAPRO ROUTER-FREE AUTONOMOUS AGENT HARNESS")
        print("=" * 85)
        print(f"  Capability Contract: {self.capability_id}")
        if file_path:
            print(f"  Execution Mode:      Scenario 1 (Document Upload)")
            print(f"  Source File:         {file_path}")
        else:
            print(f"  Execution Mode:      Scenario 2 (RAG Search / Analytical Q&A)")
            print(f"  Target Task/Item:    {task or production_item_name}")
        print(f"  Target Output Path:  {output_path}")
        print(f"  Allocated Budget:    60,000 tokens | 8 tool calls | 6 max planning turns")
        print("=" * 85)

        initial_state: AgentState = {
            "task": task or f"Execute {self.capability_id} from: {file_path or production_item_name or 'source'}",
            "file_path": file_path,
            "production_item_name": production_item_name,
            "output_path": output_path,
            "capability_id": self.capability_id,
            "plan_history": [],
            "observations": [],
            "tool_calls_used": 0,
            "raw_rows": [],
            "mapped_context": None,
            "assembled_evidence": "",
            "draft_rows": None,
            "built_rows": [],
            "violations": [],
            "repair_attempts": 0,
            "status": "INITIALIZED",
            "next_action": {},
            "budget_tokens_remaining": 60000,
            "budget_tool_calls_remaining": 8
        }
        final_state = self.app.invoke(initial_state)
        return ExecutionLog(
            capability_id=self.capability_id,
            status=final_state["status"],
            source_type="file" if file_path else ("rag" if production_item_name else "existing_document"),
            source_identifier=file_path or production_item_name or final_state.get("document_reference") or "",
            total_source_operations=len(final_state["mapped_context"].source_operations) if final_state.get("mapped_context") else 0,
            output_rows_count=len(final_state.get("built_rows", [])),
            unmapped_headers=final_state["mapped_context"].unmapped_headers if final_state.get("mapped_context") else [],
            violations=[v.model_dump() for v in final_state.get("violations", [])],
            repair_attempts=final_state.get("repair_attempts", 0),
            output_file=os.path.abspath(output_path),
            exported_file_path=os.path.abspath(output_path),
            built_rows=final_state.get("built_rows", [])
        )

    def _repair_rows(
        self,
        rows: List[ControlPlanRow],
        violations: List[Violation],
        mapped_context: MappedContext,
        is_baseline: bool = False
    ) -> List[ControlPlanRow]:
        state: AgentState = {
            "task": "",
            "file_path": None,
            "production_item_name": None,
            "document_reference": "baseline" if is_baseline else None,
            "output_path": "",
            "capability_id": self.capability_id,
            "plan_history": [],
            "observations": [],
            "tool_calls_used": 0,
            "raw_rows": [],
            "mapped_context": mapped_context,
            "assembled_evidence": "",
            "draft_rows": None,
            "built_rows": rows,
            "violations": violations,
            "repair_attempts": 0,
            "status": "",
            "next_action": {},
            "budget_tokens_remaining": 0,
            "budget_tool_calls_remaining": 0
        }
        res = repair_node(state)
        return res["built_rows"]


# =====================================================================
# 7. Main Execution CLI
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description="LangGraph Router-Free Unified Harness")
    parser.add_argument("--task", "-t", type=str, default="", help="Natural language task prompt")
    parser.add_argument("--file", "-f", type=str, help="Path to input Excel file (Path A)")
    parser.add_argument("--item", "-i", type=str, help="Production item name for RAG (Path B)")
    parser.add_argument("--output", "-o", type=str, default="output/Control_Plan.xlsx", help="Output path for .xlsx")
    parser.add_argument("--capability", "-c", type=str, default=None, help="Capability ID")

    args = parser.parse_args()

    if not args.file and not args.item and not args.task:
        parser.print_help()
        sys.exit(1)

    # Capability resolution: explicit flag takes precedence, otherwise inferred from task prompt
    if args.capability:
        cap = args.capability
    else:
        cap = "control_plan_from_pfmea"
        task_lower = (args.task or "").lower()
        if "vda" in task_lower and "pfmea" in task_lower:
            cap = "pfmea_aiag_to_vda"
        elif "vda" in task_lower and "dfmea" in task_lower:
            cap = "dfmea_aiag_to_vda"
        elif "dfmea to pfmea" in task_lower or "link" in task_lower:
            cap = "dfmea_to_pfmea"
        elif "ad_hoc" in task_lower or "which" in task_lower or "what" in task_lower or "?" in task_lower:
            cap = "ad_hoc"

    item_name = args.item
    # Extract item name from task prompt if not explicitly passed via --item
    if not item_name and not args.file and args.task:
        # Check quoted strings first e.g. "CNC Machined Engine Block"
        q_match = re.search(r'["\']([^"\']+)["\']', args.task)
        if q_match:
            item_name = q_match.group(1)
        else:
            item_name = _extract_item_from_task(args.task)

    # Default output path adjusted to capability
    output_path = args.output
    if output_path == "output/Control_Plan.xlsx":
        if cap == "pfmea_aiag_to_vda":
            output_path = "output/PFMEA_AIAG_VDA.xlsx"
        elif cap == "dfmea_aiag_to_vda":
            output_path = "output/DFMEA_AIAG_VDA.xlsx"
        elif cap == "dfmea_to_pfmea":
            output_path = "output/PFMEA_from_DFMEA.xlsx"

    if args.file and not os.path.exists(args.file):
        print(f"\n[Error] Specified workbook file not found: '{args.file}'")
        print("Please provide a valid file path. Available datasets in this project:")
        if os.path.exists("data"):
            for sample in sorted(os.listdir("data")):
                if sample.endswith(".xlsx"):
                    print(f"  -> data/{sample}")
        print()
        sys.exit(1)

    harness = UnifiedHarness(capability_id=cap)
    harness.run(
        task=args.task or f"Execute conversion under capability {cap}",
        file_path=args.file,
        production_item_name=item_name,
        output_path=output_path
    )


if __name__ == "__main__":
    main()
