"""
Generic Excel / Tabular Document Builder Tool.
Assembles structured tabular rows from MappedContext according to document type contracts.
Enforces CARRY verbatim copy, AUTHOR derivation, and mechanical ABSTAIN blanking.

Generic primitive that supports multiple document types:
  - 'control_plan_from_pfmea': AIAG 4th Edition 16-column Control Plan
  - 'pfmea_aiag_to_vda': AIAG-VDA 1st Edition 7-Step Harmonized PFMEA
  - 'dfmea_aiag_to_vda': AIAG-VDA 1st Edition 7-Step Harmonized DFMEA
  - 'dfmea_to_pfmea': DFMEA to PFMEA Engineering Linkage
  - Generic / Extensible tabular document types
"""

from typing import List, Dict, Any, Optional
import re
from .models import MappedContext, MappedContextItem, ControlPlanRow


# =====================================================================
# Document Derivation Utilities
# =====================================================================

def _derive_special_characteristic(severity: Optional[int], occurrence: Optional[int]) -> Optional[str]:
    """
    Standard AIAG / APQP special characteristic classification:
    Severity >= 9 -> 'CC' (Critical Characteristic - Safety/Government Reg)
    Severity in {7, 8} -> 'SC' (Significant Characteristic - Fit/Function)
    Severity <= 6 and Occurrence >= 7 -> 'SC'
    Otherwise None.
    """
    if severity is None:
        return None
    if severity >= 9:
        return "CC"
    if severity in (7, 8):
        return "SC"
    if occurrence is not None and severity <= 6 and occurrence >= 7:
        return "SC"
    return None


def calculate_action_priority(s: Optional[int], o: Optional[int], d: Optional[int]) -> str:
    """
    AIAG-VDA 1st Edition Standard Action Priority (AP) Table:
    Replaces legacy RPN (Risk Priority Number) with High (H), Medium (M), Low (L).
    Evaluates risk based on Severity (S), Occurrence (O), and Detection (D).
    """
    if s is None or o is None or d is None:
        return "M"
    
    # Severity 9-10 (Safety / Regulatory)
    if s >= 9:
        if o >= 8:
            return "H"
        elif o in (6, 7):
            return "H" if d >= 5 else "H"
        elif o in (4, 5):
            return "H" if d >= 5 else "M"
        elif o in (2, 3):
            return "H" if d >= 7 else ("M" if d >= 5 else "L")
        else: # o == 1
            return "L"

    # Severity 7-8 (Primary Function Loss / Fit-Finish)
    elif s in (7, 8):
        if o >= 8:
            return "H"
        elif o in (6, 7):
            return "H" if d >= 5 else "M"
        elif o in (4, 5):
            return "H" if d >= 7 else "M"
        elif o in (2, 3):
            return "M" if d >= 7 else "L"
        else: # o == 1
            return "L"

    # Severity 4-6 (Secondary Function Loss / Minor Defect)
    elif s in (4, 5, 6):
        if o >= 8:
            return "H" if d >= 7 else "M"
        elif o in (6, 7):
            return "M" if d >= 5 else "L"
        elif o in (4, 5):
            return "M" if d >= 7 else "L"
        else:
            return "L"

    # Severity 1-3 (Insignificant)
    else:
        return "L"


def _clean_control_text(text: Optional[str], prefixes: List[str]) -> Optional[str]:
    """Cleans up raw control descriptions, stripping common redundant prefixes."""
    if not text:
        return None
    cleaned = text.strip()
    for prefix in prefixes:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].strip(" :-")
            break
    words = cleaned.split()
    if len(words) > 10:
        cleaned = " ".join(words[:10])
    return cleaned if cleaned else None


# =====================================================================
# Core Generic Excel Builder
# =====================================================================

def excel_builder(
    mapped_context: MappedContext,
    draft_fields: Optional[Dict[str, Dict[str, Any]]] = None,
    is_existing_baseline: bool = False,
    document_type: str = "control_plan_from_pfmea"
) -> List[Any]:
    """
    Generic Tabular Document Builder:
    Builds tabular document rows from canonical context according to the target document_type.
    """
    doc_norm = document_type.lower().replace("-", "_")
    print(f"[Excel Builder] Assembling document rows for document_type='{document_type}' ({len(mapped_context.items)} source items)...")

    if "control_plan" in doc_norm:
        return _build_control_plan_rows(mapped_context, draft_fields, is_existing_baseline)
    elif "pfmea" in doc_norm and "vda" in doc_norm:
        return _build_pfmea_vda_rows(mapped_context, draft_fields)
    elif "dfmea" in doc_norm and "vda" in doc_norm:
        return _build_dfmea_vda_rows(mapped_context, draft_fields)
    elif "dfmea_to_pfmea" in doc_norm or "link" in doc_norm:
        return _build_dfmea_to_pfmea_rows(mapped_context, draft_fields)
    
    # Generic fallback builder for arbitrary tabular document types
    return _build_generic_rows(mapped_context, draft_fields, is_existing_baseline)


def _build_control_plan_rows(
    mapped_context: MappedContext,
    draft_fields: Optional[Dict[str, Dict[str, Any]]] = None,
    is_existing_baseline: bool = False
) -> List[ControlPlanRow]:
    """
    Assembles AIAG 4th Edition 16-Column Control Plan rows.
    """
    rows: List[ControlPlanRow] = []

    for idx, item in enumerate(mapped_context.items, start=1):
        row_key = f"{item.operation_number}_{idx}"
        draft = (draft_fields or {}).get(row_key, {})

        # 1. CARRY Fields
        prod_item = item.production_item_name
        proc_segment = item.process_segment_name
        op_num = item.operation_number
        op_name = item.operation_name
        prod_char = item.product_characteristic

        # 2. AUTHOR Fields
        proc_char = draft.get("process_characteristic")
        if proc_char is None:
            if item.process_characteristic:
                proc_char = item.process_characteristic
            elif item.failure_cause:
                cause_clean = re.sub(
                    r'^(insufficient|improper|incorrect|lack of|excessive)\s+',
                    '',
                    item.failure_cause,
                    flags=re.IGNORECASE
                ).strip()
                proc_char = cause_clean.capitalize()
            else:
                proc_char = None

        spec_class = draft.get("special_characteristic_class")
        if spec_class is None:
            spec_class = _derive_special_characteristic(item.severity_rating, item.occurrence_rating)

        eval_tech = draft.get("evaluation_measurement_technique")
        if eval_tech is None:
            eval_tech = _clean_control_text(
                item.detective_control,
                ["detective controls:", "detective control:", "detection:", "current process controls: detection"]
            )

        ctrl_method = draft.get("control_method")
        if ctrl_method is None:
            ctrl_method = _clean_control_text(
                item.preventive_control,
                ["preventive controls:", "preventive control:", "prevention:", "current process controls: prevention"]
            )

        reaction_plan = draft.get("reaction_plan")
        if reaction_plan is None:
            if item.detective_control and str(item.detective_control).strip():
                reaction_plan = "Contain suspect parts. Notify Quality. Disposition per MRB."
            else:
                reaction_plan = None
        else:
            if not item.detective_control or not str(item.detective_control).strip():
                reaction_plan = None

        # 3. ABSTAIN Fields
        spec_tol = draft.get("specification_tolerance") if is_existing_baseline else None
        t_num = draft.get("tool_number") if is_existing_baseline else None
        t_name = draft.get("tool_name") if is_existing_baseline else None
        g_num = draft.get("gage_number") if is_existing_baseline else None
        s_size = draft.get("sample_size") if is_existing_baseline else None
        s_freq = draft.get("sample_frequency") if is_existing_baseline else None

        row = ControlPlanRow(
            production_item_name=prod_item,
            process_segment_name=proc_segment,
            operation_number=op_num,
            operation_name=op_name,
            product_characteristic=prod_char,
            process_characteristic=proc_char,
            special_characteristic_class=spec_class,
            specification_tolerance=spec_tol,
            evaluation_measurement_technique=eval_tech,
            tool_number=t_num,
            tool_name=t_name,
            gage_number=g_num,
            control_method=ctrl_method,
            sample_size=s_size,
            sample_frequency=s_freq,
            reaction_plan=reaction_plan,
        )
        rows.append(row)

    return rows


def _build_pfmea_vda_rows(
    mapped_context: MappedContext,
    draft_fields: Optional[Dict[str, Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Assembles AIAG-VDA 1st Edition Harmonized 7-Step PFMEA Rows:
      - Step 2: Structure Analysis (Process Item, Process Step, Process Work Element)
      - Step 3: Function Analysis (Function of Item, Function of Step, Function of Work Element)
      - Step 4: Failure Analysis (Failure Effects FE, Failure Mode FM, Failure Cause FC)
      - Step 5: Risk Analysis (PC, Sev, Occ, DC, Det, Action Priority AP)
      - Step 6: Optimization (Prevention Action, Detection Action, Resp, Target Date, Status)
    """
    rows: List[Dict[str, Any]] = []

    for idx, item in enumerate(mapped_context.items, start=1):
        row_key = f"{item.operation_number}_{idx}"
        draft = (draft_fields or {}).get(row_key, {})

        s = item.severity_rating or 5
        o = item.occurrence_rating or 3
        d = item.detection_rating or 4
        ap = calculate_action_priority(s, o, d)

        row = {
            # Step 2: Structure Analysis
            "process_item_system": item.production_item_name or "Production Item",
            "process_step": f"Op {item.operation_number}: {item.operation_name}",
            "process_work_element_4m": draft.get("work_element") or "Machine / Operator Workstation",
            
            # Step 3: Function Analysis
            "function_of_item": item.process_segment_name or "Manufacturing System Function",
            "function_of_step": f"Execute {item.operation_name} to engineering specification",
            "function_of_work_element": item.product_characteristic or "Maintain dimensional and process tolerance",
            
            # Step 4: Failure Analysis
            "failure_effects_fe": item.failure_effect or "Impact on next operation or end customer",
            "failure_mode_fm": item.failure_mode or f"Process defect during Op {item.operation_number}",
            "failure_cause_fc": item.failure_cause or "Process parameter deviation or tool wear",
            
            # Step 5: Risk Analysis
            "current_prevention_control": item.preventive_control or "Standard Operating Procedure (SOP)",
            "severity_s": s,
            "occurrence_o": o,
            "current_detection_control": item.detective_control or "Visual Inspection / In-line Gage",
            "detection_d": d,
            "action_priority_ap": ap,
            "special_characteristic": _derive_special_characteristic(s, o) or "None",
            
            # Step 6: Optimization
            "optimization_prevention": draft.get("optimization_prevention") or ("Implement error-proofing" if ap == "H" else "Maintain current controls"),
            "optimization_detection": draft.get("optimization_detection") or ("100% automated inspection" if ap == "H" else "Standard check"),
            "status": "Open" if ap == "H" else "Completed"
        }
        rows.append(row)

    return rows


def _build_dfmea_vda_rows(
    mapped_context: MappedContext,
    draft_fields: Optional[Dict[str, Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Assembles AIAG-VDA 1st Edition Harmonized 7-Step DFMEA Rows:
      - Step 2: Structure Analysis (Higher Level System, Focus Element, Lower Level Component)
      - Step 3: Function Analysis (System Function, Focus Element Function, Component Characteristic)
      - Step 4: Failure Analysis (Failure Effect FE, Failure Mode FM, Failure Cause FC)
      - Step 5: Risk Analysis (Prevention Control, S, Occ, Detection Control, Det, AP)
      - Step 6: Optimization
    """
    rows: List[Dict[str, Any]] = []

    for idx, item in enumerate(mapped_context.items, start=1):
        s = item.severity_rating or 6
        o = item.occurrence_rating or 3
        d = item.detection_rating or 4
        ap = calculate_action_priority(s, o, d)

        row = {
            # Step 2: Structure Analysis
            "higher_level_system": item.process_segment_name or "Vehicle System / Assembly",
            "focus_element": item.production_item_name or "Design Component",
            "lower_level_element": item.operation_name or "Component Sub-part",
            
            # Step 3: Function Analysis
            "function_system": "Fulfill system-level durability and safety criteria",
            "function_focus_element": item.product_characteristic or "Provide mechanical integrity and functional envelope",
            "function_lower_level": item.process_characteristic or "Maintain material properties and structural stiffness",
            
            # Step 4: Failure Analysis
            "failure_effect_fe": item.failure_effect or "Degraded vehicle performance or loss of subsystem function",
            "failure_mode_fm": item.failure_mode or "Structural deformation or fatigue fracture",
            "failure_cause_fc": item.failure_cause or "Stress concentration exceeding design endurance limit",
            
            # Step 5: Risk Analysis
            "design_prevention_control": item.preventive_control or "FEA Simulation / Material Selection Standards",
            "severity_s": s,
            "occurrence_o": o,
            "design_detection_control": item.detective_control or "Prototype Durability Rig Testing",
            "detection_d": d,
            "action_priority_ap": ap,
            "special_characteristic": _derive_special_characteristic(s, o) or "None",
            
            # Step 6: Optimization
            "optimization_prevention": "Optimize geometry / increase wall thickness" if ap == "H" else "Design verified",
            "optimization_detection": "Accelerated life cycle test" if ap == "H" else "Standard bench test",
            "status": "In Review" if ap == "H" else "Approved"
        }
        rows.append(row)

    return rows


def _build_dfmea_to_pfmea_rows(
    mapped_context: MappedContext,
    draft_fields: Optional[Dict[str, Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Assembles DFMEA -> PFMEA Linkage Rows:
    Derives process failure modes and process characteristics from design characteristics and failure causes.
    """
    rows: List[Dict[str, Any]] = []

    for idx, item in enumerate(mapped_context.items, start=1):
        s = item.severity_rating or 7
        spec_class = _derive_special_characteristic(s, item.occurrence_rating)

        row = {
            "source_dfmea_item": item.production_item_name,
            "design_characteristic": item.product_characteristic or item.operation_name,
            "dfmea_failure_mode": item.failure_mode or "Functional performance degraded",
            "dfmea_severity": s,
            "special_characteristic_class": spec_class or "Standard",
            # Linked PFMEA counterparts
            "linked_process_step": f"Op {item.operation_number or idx * 10}: Fabricate / Assemble {item.production_item_name}",
            "linked_process_failure_mode": f"Manufacturing variation causing: {item.failure_mode or 'out of tolerance'}",
            "derived_process_characteristic": f"Torque / Clamping / Feed Rate for {item.product_characteristic or 'Feature'}",
            "recommended_process_control": "100% Poka-Yoke / Error-Proofing" if s >= 8 else "Standard In-process Gage"
        }
        rows.append(row)

    return rows


def _build_generic_rows(
    mapped_context: MappedContext,
    draft_fields: Optional[Dict[str, Dict[str, Any]]] = None,
    is_existing_baseline: bool = False
) -> List[Dict[str, Any]]:
    """
    Generic tabular row builder for extensible document types.
    """
    rows: List[Dict[str, Any]] = []
    for idx, item in enumerate(mapped_context.items, start=1):
        row_dict = item.model_dump()
        row_key = f"{item.operation_number}_{idx}"
        draft = (draft_fields or {}).get(row_key, {})
        row_dict.update(draft)
        rows.append(row_dict)
    return rows


# Backwards compatibility alias
control_plan_builder = excel_builder
