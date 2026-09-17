# AquaPro Router-Free Autonomous Agent Harness

**Domain:** Autonomous Manufacturing Quality Engineering (FMEA Harmonization & Control Plan Generation)  
**Architecture:** Router-Free State Machine with Dual-Loop Agency & Mechanical Verification  
**Core Framework:** LangGraph (`StateGraph`), OpenPyXL, Jinja2, Pydantic, Gemini LLM  

---

## 1. Architectural Philosophy: One Agent, Many Capabilities

Modern agent systems often suffer from fragile routing trees and ungrounded hallucinations. AquaPro solves this through a **Router-Free Single-Agent State Machine**:

- **No Routers:** The agent does not use a secondary classifier to "route" user requests. Instead, the model's first planning turn inspects the task and declares its capability contract and initial tool choice.
- **One Loop, Dynamic Contracts:** Whether authoring an AIAG 4th Edition Control Plan, harmonizing PFMEAs into AIAG-VDA 7-Step formats, or executing DFMEA-to-PFMEA linkage, the same agent loop executes under distinct, strongly-typed capability contracts.
- **Strictly Two Input Scenarios:**
  1. **Scenario 1 (Document Provided):** User uploads an Excel workbook (`--file`). Handled via deterministic `workbook_parser` and `column_mapper`.
  2. **Scenario 2 (No Document Provided):** User provides a part name or asks an analytical question (`--task` / `--item`). Handled via vector/historical `rag_retriever`.

```
                    +------------------------------+
                    |                              |
START ---> plan --->+---> (decision) -> execute_tool
                            |
                            +---> assemble ---> compose ---> verify ---> (decision) ---+---> export ---> END (SUCCESS)
                                                  ^                         |
                                                  |-------- repair <--------+
                                                                            |
                                                                            +---> degrade ---> END (DEGRADED)
```

---

## 2. The Two LangGraph Loops

The harness organizes execution into two distinct, decoupled loops:

1. **Loop 1: The Agency Loop (`plan_node` <-> `execute_tool_node`)**
   - The model inspects the current evidence store, tool registry, token/call budgets, and history.
   - Decides what action to take next based on what it has discovered (e.g., parse workbook -> map columns).
   - Once all source operations are covered, it emits `ready_to_compose`.

2. **Loop 2: The Verification & Self-Repair Loop (`verify_node` <-> `repair_node`)**
   - Authorship in `compose_node` is strictly separated from verification.
   - `verify_node` runs mechanical, zero-LLM rule checks (Rules V1–V5).
   - If any violation is detected, `repair_node` isolates the failing operations and re-authors them with targeted error feedback (bounded to 2 self-repair rounds).

---

## 3. Zero-Hallucination Invariant (Rule V3)

Automotive manufacturing requires zero tolerance for hallucinated quality controls:
- **CARRY Fields:** Operation numbers, descriptions, and characteristics are preserved verbatim.
- **AUTHOR Fields:** Special characteristics (`CC`/`SC`), Action Priorities (`H`/`M`/`L`), and Reaction Plans are derived strictly from PFMEA severity/occurrence ratings and controls.
- **ABSTAIN Fields:** Tool numbers, tool descriptions, gage numbers, blueprint tolerances, sample sizes, and sample frequencies **must remain blank (`None`)** unless present in the source input. The mechanical verifier rejects any output that invents synthetic tooling or measurement specifications.

---

## 4. Supported Capabilities

| Capability ID | Output Specification | Verification Rules |
| :--- | :--- | :--- |
| `control_plan_from_pfmea` | AIAG 4th Edition 16-Column Control Plan | Rules V1–V5 (Key completeness, operation set equality, Rule V3 abstention, reaction plan interlocks) |
| `pfmea_aiag_to_vda` | AIAG-VDA 1st Edition Harmonized 7-Step PFMEA | 4M element structure, 3-tier failure chain, Action Priority ($S \times O \times D \to H/M/L$) |
| `dfmea_aiag_to_vda` | AIAG-VDA 1st Edition Harmonized 7-Step DFMEA | System/subsystem focus, failure modes, design controls, Design Action Priority |
| `dfmea_to_pfmea` | Engineering Linkage Traceability Matrix | Special characteristic flow-down, product-to-process parameter alignment |
| `ad_hoc` | Analytical Manufacturing Quality Q&A | Grounded evidence claims, high-severity gap analysis, uncertainty boundaries |

---

## 5. Tool Registry (Atomic Action Space)

Every tool is an atomic, deterministic Python function with typed input/output models (zero internal LLM calls):

- `workbook_parser(file_path: str) -> List[Dict[str, Any]]`: Profile-based Excel workbook parser that detects real automotive table headers and extracts raw data rows.
- `column_mapper(raw_rows: List[Dict]) -> MappedContext`: Maps raw headers against canonical engineering concepts using standard automotive synonym tables. Retains unmapped headers without data loss.
- `excel_builder(mapped_context: MappedContext, ...) -> List[Any]`: Unified document builder implementing CARRY, AUTHOR, and ABSTAIN semantics across all document schemas.
- `validator(rows: List[Any], mapped_context: MappedContext, ...) -> List[Violation]`: Deterministic mechanical verifier that checks capability contract rules.
- `excel_exporter(rows: List[Any], output_path: str, ...) -> str`: Exports validated rows to styled Excel workbooks and writes companion `execution_log.json` audit logs.
- `rag_retriever(production_item_name: str) -> MappedContext`: Dynamically queries local and knowledge repository fixtures when no file is uploaded.

---

## 6. Installation & Usage

### Prerequisites
- Python 3.10+
- `openpyxl`, `jinja2`, `langgraph`, `google-genai`

Install dependencies:
```bash
pip install -r requirements.txt
```

### Running Scenarios via CLI

#### Scenario 1: Document Upload (Autonomous PFMEA to Control Plan)
```bash
python harness.py --file "data/CNC_Operation_Process_FMEA.xlsx"
```

#### Scenario 2: Historical RAG / Analytical Q&A (No File Uploaded)
```bash
python harness.py --task "What are the failure causes for CNC Machined Engine Block?"
```

#### Explicit Capability Conversion (e.g. AIAG-VDA 7-Step Harmonization)
```bash
python harness.py --file "data/CNC_Operation_Process_FMEA.xlsx" --capability pfmea_aiag_to_vda --output "output/PFMEA_AIAG_VDA.xlsx"
```

---

## 7. Verification & Automated Test Suite

Run the full end-to-end unit and integration test suite:
```bash
python -m unittest discover -s tests
```

**Test Coverage (10/10 Passed):**
- Real Excel workbook parsing and header classification
- Canonical column mapping and synonym resolution
- 16-Column AIAG Control Plan assembly and Rule V3 abstention
- Action Priority ($S \times O \times D \to H/M/L$) validation
- Injection and resolution of self-repair feedback loops
- Full end-to-end multi-conversion pipeline execution
