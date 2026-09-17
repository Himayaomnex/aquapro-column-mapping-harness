# Agent Harness — First-Principles Design
**Domain:** Manufacturing Quality Engineering (PFMEA to Control Plan Column Mapping)  
**Status:** Design Locked · Implement from this Document  

---

## 1. Core Architecture: One Agent, Many Capabilities

There is **one agent**. One loop, one action space, one termination condition.

PFMEA-to-Control-Plan, DFMEA-to-PFMEA, and Ad-Hoc queries are **not separate agents**. They read the same engineering data, hold the same permissions, use the same parsing and mapping tools, and differ only in *who is reading the output and what schema it takes*. Three functions that differ by output format are not three agents; they are one agent with three contracts.

| Concept | Definition | Count |
|---|---|:---:|
| **Agent** | The loop: plan -> act -> observe -> repeat -> compose -> verify. Has a goal, an action space, and a termination condition. | **1** |
| **Capability** | A consumer + an output contract + verification rules. Determines *who this is for* and *what "correct" means*. | 2 today (`control_plan_from_pfmea`, `ad_hoc`), unbounded |
| **Tool** | One atomic action with a typed signature. No LLM inside. A verb. | ~5 |
| **Skill** | A procedure that composes several tools and reasoning steps to produce a specific artifact. Registered as a tool, but internally a workflow. A recipe. | 1 |

### There is No Router

The router-as-classifier is a crutch. What replaces it is simply the agent's first decision: the model is given the task, the tool list, and the available capability contracts, and it declares its plan — which capability contract it is fulfilling, and which tool it wants first.

The capability declaration binds the verifier: once the agent declares `control_plan_from_pfmea`, the harness knows which 16 columns and which integrity rules to check the output against.

---

## 2. The 6-Stage End-to-End Workflow

```
[1. User Request]
     |-- Uploads PFMEA file (.xlsx) OR Provides Production Item Name
     v
[2. Universal Harness]
     |-- File provided?
     |     |-- YES: Tool 1a (workbook_parser)
     |     \-- NO:  Tool 1b (rag_retriever)
     v
[Standardized Source Data (Canonical Context)]
     v
[3. Skill Execution (convert_pfmea_to_control_plan.md)]
     |-- 1. Map source columns to canonical concepts
     |-- 2. Classify fields (CARRY vs AUTHOR)
     |-- 3. Derive missing control plan fields (from PFMEA content only)
     |-- 4. Preserve existing values verbatim (AI does not overwrite)
     \-- 5. Construct 16-column Control Plan rows (AIAG 4th Edition)
     v
[4. Tool Calls (Discrete Actions)]
     |-- column_mapper -> control_plan_builder -> validator -> excel_exporter
     v
[5. Validation (Against Capability Contract)]
     |-- Asserts all 16 columns present
     |-- Asserts 100% operation number fidelity
     |-- Asserts "Blank = Blank" invariant (zero hallucinated tools/gages)
     |-- If failed: Triggers bounded Self-Repair Loop
     v
[6. Output Delivered]
     \-- Control_Plan.xlsx + execution_log.json
```

---

## 3. The LangGraph Engine (Two Loops)

### 3.1 The Graph

```
                    +------------------------------+
                    |                              |
START ---> plan --->+---> (decision) -> execute_tool
                            |
                            +---> assemble ---> compose ---> verify ---> (decision) ---+---> END (SUCCESS)
                                                  ^                         |
                                                  |-------- repair <--------+
                                                                            |
                                                                            +---> degrade ---> END (DEGRADED)
                 any node ---> fail ---> END (Named Failure Status)
```

**The two loops are the whole point:**
* **Loop 1 (`plan <-> execute_tool`): Agency.** The model decides what to look at next based on what it has already found.
* **Loop 2 (`compose <-> repair`): Verification.** The system is capable of rejecting its own output and self-repairing before delivery.

### 3.2 Nodes

| Node | Owner | What it does |
|---|:---:|---|
| `plan` | **Model** | Inspects task, capability contract, tool list, evidence gathered so far, **budget remaining**, and tool calls remaining. Emits either a tool call or `ready_to_compose`. |
| `execute_tool` | **Code** | Runs the requested tool, measures the result in tokens, stores it in `EvidenceStore`, decrements budget and call count, appends observation. Loops back to `plan`. |
| `assemble` | **Code** | Selects from `EvidenceStore` into the final prompt, **highest relevance first, until the budget is spent**. Records dropped items. |
| `compose` | **Model** | Writes the 16-column rows against the capability's output schema in JSON mode. |
| `verify` | **Code** | Parses against the schema; checks every rule the capability declares (V1-V5); returns `list[Violation]`. Never a boolean. |
| `repair` | **Code -> Model** | Feeds specific violations back to `compose`. Bounded to 2 attempts. |
| `degrade` | **Code** | Ships only verified rows, with failed operations explicitly labelled in the output. |
| `fail` | **Code** | Terminates with an explicit, named status. Never returns an ungrounded answer. |

### 3.3 State

```python
class AgentState(BaseModel):
    task: str
    capability: str | None
    session_id: str
    trace_id: str
    plan_history: list[Thought]
    observations: list[Observation]
    tool_calls_used: int
    evidence: EvidenceStore
    budget: Budget
    draft: dict | None
    violations: list[Violation]
    repair_attempts: int
    status: Status
```

### 3.4 Termination Guards

| Guard | Default | Terminal status |
|---|:---:|---|
| **Max tool calls** | 8 | `BUDGET_EXHAUSTED_CALLS` |
| **Context budget** | 60,000 tokens | `BUDGET_EXHAUSTED_TOKENS` |
| **Repair attempts** | 2 | `VERIFICATION_FAILED` -> `degrade` |
| **Wall clock** | 120 s | `TIMEOUT` |

---

## 4. Context Engineering

### 4.1 Budget is a First-Class, Agent-Visible Object

`budget.remaining` is rendered into the `plan` prompt on every turn. The agent reasons: *"I have 28K tokens remaining and 3 calls; one header mapping call, then compose."*

### 4.2 The Evidence Store

Evidence is never a concatenated blob. It is a keyed store:
```python
class EvidenceItem(BaseModel):
    id: str                 # Stable, citable ID (e.g. "row_op_10_cause_1")
    source: Literal["workbook", "rag", "suggester"]
    origin: dict            # sheet, row, operation_number
    content: str
    tokens: int             # Measured with real tokenizer on arrival
    relevance: float        # 1.0 for file rows, vector score for RAG
```

Properties:
* **Deduplication:** Repeated rows or operations enter context once.
* **Assembly by relevance:** `assemble` sorts by relevance and fills to budget.
* **Citability:** Every Control Plan row links back to source `EvidenceItem.id`.

---

## 5. Prompt Engineering

### 5.1 Three Layers, Assembled Fresh Each Turn
* **Harness prompt (`prompts/00-harness.md`):** Loop contract, tool-calling schema, failure semantics, abstention rule. Never changes.
* **Capability prompt (`capabilities/*.md`):** Consumer, 16-column output schema, verification rules V1-V5. Per capability.
* **Turn prompt (`prompts/10-plan.md`):** Task, plan history, observations, evidence summary, budget remaining. Every turn.

### 5.2 The Enforceability Rule & Mandatory Abstention
* **Enforceability:** Every rule in a prompt must be enforceable by the verifier in code, or be deleted.
* **Mandatory Abstention ("Blank = Blank"):** If tool numbers, gage IDs, or tolerances are absent in the source, the value **must be null**. Fabricating shop-floor parameters is a critical failure.
