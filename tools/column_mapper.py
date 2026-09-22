"""
Column Mapper Tool (Production Grade).
Translates raw Excel headers into canonical concept keys using the synonym table.
Handles real automotive PFMEA headers from parent codebase fixtures.
Deterministic, zero LLM calls.
"""

from typing import List, Dict, Any, Tuple
import re
import unicodedata
from .models import MappedContextItem, MappedContext


# Synonym table matching real automotive PFMEA exports & parent codebase schemas
SYNONYM_MAP: Dict[str, List[str]] = {
    "production_item_name": [
        "production item name", "production item", "part name", "part description",
        "item name", "product name", "component name", "part/process", "cd6 fr",
        "nombre de la pieza", "nombre de parte", "producto", "parte", "pieza",
        "número de parte", "numero de parte", "teilename", "bauteil"
    ],
    "process_segment_name": [
        "process segment name", "process segment", "process step", "process stage",
        "segment", "system / subsystem", "spine node", "process function"
    ],
    "operation_number": [
        "operation number", "op number", "op no", "op #", "operation #",
        "op num", "operation no", "process step / op #",
        "column_1", "step #", "número de operación", "numero de operacion",
        "no. de operación", "no de operacion", "operación #", "operacion #",
        "prozessschritt nr", "arbeitsgang nr"
    ],
    "op_grp_sequence": [
        "op. grp. sequence", "op grp sequence", "operation group sequence", "op group sequence"
    ],
    "characteristic_id": [
        "characteristic id", "characteristic no", "characteristic number",
        "char id", "char no", "char #", "characteristic_id",
        "pc id", "requirements: pc id", "pc / pd", "pc/pd"
    ],
    "csr": [
        "csr", "ccs", "customer specific requirement", "customer specific requirements"
    ],
    "responsibility": [
        "responsibility", "responsibility to control", "resp"
    ],
    "operation_name": [
        "operation name", "operation description", "process description",
        "operation", "process step description",
        "2b. process step station name of focus element",
        "station name of focus element", "process step station name", "station name",
        "operación", "operacion", "nombre de la operación", "nombre de operacion",
        "descripción de la operación", "descripcion de la operacion",
        "descripción del proceso", "descripcion del proceso", "paso del proceso",
        "estación", "estacion", "prozessschritt bezeichnung", "arbeitsgang name", "prozessbeschreibung"
    ],
    "product_characteristic": [
        "product characteristics", "product characteristic", "product char",
        "product specs", "product",
        "2b. function of the process step and prod. char.- desc",
        "prod. char.- desc", "prod. char",
        "característica de producto", "caracteristica de producto",
        "características del producto", "caracteristicas del producto",
        "especificación de producto", "especificacion de producto", "produktmerkmal"
    ],
    "process_characteristic": [
        "process characteristics", "process characteristic", "process char",
        "process parameter", "process",
        "3. function of the process work element and proc. char.",
        "proc. char.",
        "característica de proceso", "caracteristica de proceso",
        "características del proceso", "caracteristicas del proceso",
        "parámetro de proceso", "parametro de proceso", "parámetro", "parametro",
        "prozessmerkmal", "prozessparameter"
    ],
    "failure_mode": [
        "potential failure mode", "failure mode", "failure",
        "2. failure mode (fm)", "failure mode (fm)",
        "modo de falla", "modo potencial de falla", "falla", "fehlerart", "potentielle fehlerart"
    ],
    "failure_effect": [
        "potential effects of failure", "potential effect(s) of failure",
        "failure effect", "effects of failure", "effect", "potential effects of failure: sev",
        "efecto de falla", "efecto potencial de falla", "efectos", "efecto", "fehlerfolge", "potentielle fehlerfolge"
    ],
    "severity_rating": [
        "severity rating: failure mode effect", "severity rating", "severity",
        "sev", "s", "severity (s) of fe", "sev (s)", "severity (s)",
        "severidad", "gravedad", "bedeutung", "b"
    ],
    "failure_cause": [
        "potential causes of failure", "potential cause(s) of failure",
        "failure cause", "cause of failure", "cause",
        "3. failure cause (fc)", "failure cause (fc)",
        "causa de falla", "causa potencial de falla", "causa", "fehlerursache", "potentielle fehlerursache"
    ],
    "occurrence_rating": [
        "cause: occurence rating", "cause: occurrence rating", "occurrence rating",
        "preventive controls: occurence rating", "preventive controls: occurrence rating",
        "preventive controls: occurence", "preventive controls: occurrence",
        "occurrence", "occ", "o", "occ (o) of fc", "occ (o)",
        "ocurrencia", "ocurr", "auftretenswahrscheinlichkeit", "a"
    ],
    "preventive_control": [
        "preventive controls", "current process controls: prevention",
        "current process controls prevention", "prevention controls",
        "preventative control", "preventive control",
        "current prevention control (pc) of fc", "prevention control (pc)",
        "control preventivo", "controles preventivos", "control de prevención",
        "control de prevencion", "controles de prevención", "controles de prevencion",
        "prevención", "prevencion", "vermeidungsmaßnahme", "präventive steuerung"
    ],
    "detective_control": [
        "detective controls", "current process controls: detection",
        "current process controls detection", "detection controls",
        "detective control", "current detection control (dc) of fc or fm",
        "detection control (dc)",
        "control de detección", "control de deteccion", "controles de detección",
        "controles de deteccion", "control de inspección", "control de inspeccion",
        "detección", "deteccion", "entdeckungsmaßnahme", "prüfmaßnahme"
    ],
    "detection_rating": [
        "detective controls: rating", "detection rating", "detection", "det", "d",
        "det (d) of fc/ fm", "det (d)",
        "detección", "deteccion", "entdeckungswahrscheinlichkeit", "e"
    ],
    # DFMEA & AIAG-VDA 7-Step specific concepts
    "process_work_element": [
        "3. process work element", "process work element", "work element",
        "work element 4m", "4m", "num ,machine, device, jig, tools, for manufacturing",
        "machine, device, jig, tools", "machine", "device", "jig", "tools",
        "machine / device", "tools for manufacturing"
    ],
    "focus_element": [
        "focus element", "item / function", "system / subsystem / component",
        "system element", "process item", "component / part"
    ],

    "function_name": [
        "function of item", "function", "item function", "process function",
        "function of process item", "function of focus element"
    ],
    "action_priority": [
        "action priority", "ap", "rpn", "risk priority number"
    ],
    "special_characteristic_class": [
        "class", "classification", "special char", "special characteristic",
        "special characteristic class", "cc/sc", "característica especial", "caracteristica especial", "besonderes merkmal"
    ],
    "optimization_prevention": [
        "prevention action", "recommended action(s) - prevention", "optimization prevention", "vermeidungsmaßnahme"
    ],
    "optimization_detection": [
        "detection action", "recommended action(s) - detection", "optimization detection", "entdeckungsmaßnahme"
    ],
    # Control Plan & Process Specification specific concepts
    "specification_tolerance": [
        "product/process specification/tolerance", "specification / tolerance", "specification/tolerance",
        "spec / tolerance", "spec/tolerance", "specification", "tolerance", "spec",
        "especificación / tolerancia", "especificación/tolerancia", "especificacion / tolerancia",
        "especificacion/tolerancia", "tolerancia", "especificación", "especificacion",
        "spezifikation / toleranz", "spezifikation/toleranz", "spezifikation", "toleranz"
    ],
    "evaluation_measurement_technique": [
        "evaluation/measurement technique", "evaluation / measurement technique", "evaluation measurement technique",
        "measurement technique", "gage / test equipment", "test equipment", "gage", "measuring equipment",
        "técnica de evaluación / medición", "técnica de evaluación/medición", "tecnica de medicion",
        "método de medición", "calibre", "prüfmittel", "messmethode"
    ],
    "control_method": [
        "control method", "control methods", "control plan method", "method of control",
        "método de control", "metodo de control", "control", "lenkungsmethode", "prüfmethode"
    ],
    "sample_size": [
        "sample size", "size", "sample", "tamaño de muestra", "tamano de muestra", "muestra",
        "stichprobenumfang", "stichprobengröße"
    ],
    "sample_frequency": [
        "sample frequency", "frequency", "freq", "frecuencia de muestra", "frecuencia",
        "stichprobenhäufigkeit", "prüfhäufigkeit"
    ],
    "reaction_plan": [
        "reaction plan", "reaction", "reaction plan / corrective action", "plan de reacción",
        "plan de reaccion", "reaktionsplan"
    ],
    "tool_number": [
        "tool number", "tool #", "tool no", "machine no", "device no", "número de herramienta",
        "numero de herramienta", "dispositivo", "werkzeug-nr"
    ],
    "tool_name": [
        "tool name", "machine name", "device name", "nombre de herramienta", "máquina", "maquina", "werkzeug"
    ],
    "gage_number": [
        "gage number", "gage #", "gage no", "gauge number", "gauge #", "gauge no", "calibre #"
    ],
}


def _strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', str(s)) if not unicodedata.combining(c))


def _clean_header(header: str) -> str:
    """Normalizes header string for comparison, stripping accents and whitespace."""
    header = _strip_accents(header)
    header = re.sub(r'[\r\n\t]+', ' ', header).strip().lower()
    return header


def map_headers(raw_headers: List[str]) -> Tuple[Dict[str, str], List[str]]:
    """
    Matches raw Excel header names to canonical concepts.
    Returns:
        header_to_canonical: dict mapping raw_header -> canonical_key
        unmapped_headers: list of unrecognized raw headers
    """
    header_to_canonical: Dict[str, str] = {}
    unmapped_headers: List[str] = []

    for raw_header in raw_headers:
        if raw_header.startswith("_"):
            continue

        clean = _clean_header(raw_header)
        clean_alphanumeric = re.sub(r'[^a-z0-9]+', ' ', clean).strip()
        matched = False

        for canonical_key, aliases in SYNONYM_MAP.items():
            for alias in aliases:
                alias_clean = _clean_header(alias)
                alias_alphanumeric = re.sub(r'[^a-z0-9]+', ' ', alias_clean).strip()
                if clean == alias_clean or clean == alias_clean.replace(":", "") or clean_alphanumeric == alias_alphanumeric:
                    header_to_canonical[raw_header] = canonical_key
                    matched = True
                    break
            if matched:
                break

        if not matched:
            # Substring / partial matching fallback for minor phrasing variations
            # (skip short aliases like 's', 'o', 'd' to prevent false positive collisions)
            for canonical_key, aliases in SYNONYM_MAP.items():
                for alias in aliases:
                    alias_clean = _clean_header(alias)
                    if len(alias_clean) >= 5 and (alias_clean in clean or clean in alias_clean):
                        header_to_canonical[raw_header] = canonical_key
                        matched = True
                        break
                if matched:
                    break

        if not matched:
            unmapped_headers.append(raw_header)

    return header_to_canonical, unmapped_headers


def _parse_int(val: Any) -> Any:
    """Safely extracts an integer rating (1-10) from cell values."""
    if val is None:
        return None
    try:
        num = int(float(str(val).strip()))
        if 1 <= num <= 10:
            return num
    except (ValueError, TypeError):
        pass
    return None


def column_mapper(raw_rows: List[Dict[str, Any]]) -> MappedContext:
    """
    Translates raw Excel row dicts into canonical MappedContext.
    Preserves all unrecognized headers in unmapped_fields.
    """
    if not raw_rows:
        return MappedContext()

    all_headers: List[str] = []
    seen = set()
    for row in raw_rows:
        for k in row.keys():
            if k not in seen:
                seen.add(k)
                all_headers.append(k)

    header_to_canonical, unmapped_headers = map_headers(all_headers)

    items: List[MappedContextItem] = []
    source_ops = set()

    active_op_num = None
    active_op_name = None
    active_proc_segment = None
    active_item_name = None
    auto_op_counter = 0

    op_prefix_regex = re.compile(
        r"^(?:(?:op|operation|step|estacion|estación|station|operacion|operación)\s*[-#:]?\s*)?(\d+(?:[_\.\-][a-zA-Z0-9]+)?)(?:[_\s:\-]+(.*))?$",
        re.IGNORECASE
    )

    for row in raw_rows:
        canonical_values: Dict[str, Any] = {}
        row_unmapped: List[str] = []

        for raw_k, val in row.items():
            if raw_k.startswith("_"):
                continue
            if raw_k in header_to_canonical:
                canonical_k = header_to_canonical[raw_k]
                canonical_values[canonical_k] = val
            elif val is not None and str(val).strip() != "":
                row_unmapped.append(raw_k)

        op_num = str(canonical_values.get("operation_number") or "").strip()
        op_name = str(canonical_values.get("operation_name") or "").strip()
        item_name = str(canonical_values.get("production_item_name") or "").strip()
        proc_segment = str(canonical_values.get("process_segment_name") or "").strip() or None

        # Intelligent prefix disambiguation: e.g. '81 Material allocation...', 'Op 10: Cutting', 'Step 2 - Heat treat'
        candidates = [
            ("op_name", op_name),
            ("item_name", item_name),
            ("focus_element", str(canonical_values.get("focus_element") or "").strip()),
            ("process_step", str(canonical_values.get("process_step") or "").strip()),
            ("raw_process_item", str(row.get("Process Item") or "").strip()),
            ("raw_process_step", str(row.get("Process Step") or "").strip()),
            ("raw_op_desc", str(row.get("Operation Description") or "").strip()),
        ]
        # Also check any raw row key that resembles an operation column
        for raw_k, raw_v in row.items():
            if raw_v and not raw_k.startswith("_"):
                k_clean = _clean_header(raw_k)
                if any(kw in k_clean for kw in ["operacion", "operation", "station", "estacion", "step", "paso"]):
                    candidates.append((raw_k, str(raw_v).strip()))
        for candidate_field, candidate_val in candidates:
            if not candidate_val:
                continue
            m = op_prefix_regex.match(candidate_val)
            if m:
                extracted_op = m.group(1)
                remainder = (m.group(2) or "").strip()
                if not op_num or op_num != extracted_op:
                    if not proc_segment and op_num:
                        proc_segment = op_num
                    op_num = extracted_op
                if remainder:
                    if not op_name or op_name == f"Operation {op_num}" or candidate_field in ("op_name", "raw_op_desc"):
                        op_name = remainder
                    elif candidate_field in ("focus_element", "raw_process_item", "raw_process_step"):
                        if not op_name or op_name.strip() == remainder or op_name.startswith("Operation"):
                            op_name = remainder
                    if candidate_field == "item_name" and item_name == candidate_val:
                        item_name = remainder
                break

        # Check if new operation declared or inherit active operation for continuation rows
        if op_num:
            active_op_num = op_num
            active_op_name = op_name or (active_op_name if op_num == active_op_num else f"Operation {op_num}")
            active_proc_segment = proc_segment or active_proc_segment or "1"
            active_item_name = item_name or active_item_name or "Production Item"
            op_name = active_op_name
            proc_segment = active_proc_segment
            item_name = active_item_name
        elif op_name:
            # Operation name is present, but operation number is not
            if not active_op_name or op_name.lower() != active_op_name.lower():
                auto_op_counter += 10
                active_op_num = str(auto_op_counter)
            op_num = active_op_num
            active_op_name = op_name
            active_proc_segment = proc_segment or active_proc_segment or "1"
            active_item_name = item_name or active_item_name or "Production Item"
            proc_segment = active_proc_segment
            item_name = active_item_name
        else:
            has_row_data = any([
                canonical_values.get("product_characteristic"),
                canonical_values.get("process_characteristic"),
                canonical_values.get("failure_mode"),
                canonical_values.get("failure_cause"),
                canonical_values.get("preventive_control"),
                canonical_values.get("detective_control"),
                canonical_values.get("function_name"),
                canonical_values.get("focus_element"),
                canonical_values.get("specification_tolerance"),
                canonical_values.get("control_method"),
            ])
            if has_row_data and active_op_num:
                op_num = active_op_num
                op_name = active_op_name
                proc_segment = active_proc_segment
                item_name = active_item_name
            elif has_row_data:
                # In DFMEAs or documents without explicit manufacturing operation numbers,
                # use function_name, focus_element, or item_name as the functional element
                func_val = canonical_values.get("function_name") or canonical_values.get("focus_element")
                active_op_name = str(func_val or item_name or "Design Function").strip()
                auto_op_counter += 10
                active_op_num = str(auto_op_counter)
                active_proc_segment = proc_segment or "1"
                active_item_name = item_name or "Design Item"
                op_num = active_op_num
                op_name = active_op_name
                proc_segment = active_proc_segment
                item_name = active_item_name

        if not op_num and not op_name:
            continue
        if not op_num:
            op_num = "10"
        if not op_name:
            op_name = f"Operation {op_num}"
        if not item_name:
            item_name = "Production Item"

        source_ops.add(op_num)

        item = MappedContextItem(
            operation_number=op_num,
            operation_name=op_name,
            production_item_name=item_name,
            process_segment_name=proc_segment,
            process_work_element=str(canonical_values.get("process_work_element")).strip() if canonical_values.get("process_work_element") else None,
            product_characteristic=str(canonical_values.get("product_characteristic")).strip() if canonical_values.get("product_characteristic") else None,
            process_characteristic=str(canonical_values.get("process_characteristic")).strip() if canonical_values.get("process_characteristic") else None,
            failure_mode=str(canonical_values.get("failure_mode")).strip() if canonical_values.get("failure_mode") else None,
            failure_effect=str(canonical_values.get("failure_effect")).strip() if canonical_values.get("failure_effect") else None,
            failure_cause=str(canonical_values.get("failure_cause")).strip() if canonical_values.get("failure_cause") else None,
            severity_rating=_parse_int(canonical_values.get("severity_rating")),
            occurrence_rating=_parse_int(canonical_values.get("occurrence_rating")),
            preventive_control=str(canonical_values.get("preventive_control")).strip() if canonical_values.get("preventive_control") else None,
            detective_control=str(canonical_values.get("detective_control")).strip() if canonical_values.get("detective_control") else None,
            detection_rating=_parse_int(canonical_values.get("detection_rating")),
            characteristic_id=str(canonical_values.get("characteristic_id")).strip() if canonical_values.get("characteristic_id") else None,
            special_characteristic_class=str(canonical_values.get("special_characteristic_class")).strip() if canonical_values.get("special_characteristic_class") else None,
            csr=str(canonical_values.get("csr")).strip() if canonical_values.get("csr") else None,
            responsibility=str(canonical_values.get("responsibility")).strip() if canonical_values.get("responsibility") else None,
            specification_tolerance=str(canonical_values.get("specification_tolerance")).strip() if canonical_values.get("specification_tolerance") else None,
            evaluation_measurement_technique=str(canonical_values.get("evaluation_measurement_technique")).strip() if canonical_values.get("evaluation_measurement_technique") else None,
            control_method=str(canonical_values.get("control_method")).strip() if canonical_values.get("control_method") else None,
            sample_size=str(canonical_values.get("sample_size")).strip() if canonical_values.get("sample_size") else None,
            sample_frequency=str(canonical_values.get("sample_frequency")).strip() if canonical_values.get("sample_frequency") else None,
            reaction_plan=str(canonical_values.get("reaction_plan")).strip() if canonical_values.get("reaction_plan") else None,
            tool_number=str(canonical_values.get("tool_number")).strip() if canonical_values.get("tool_number") else None,
            tool_name=str(canonical_values.get("tool_name")).strip() if canonical_values.get("tool_name") else None,
            gage_number=str(canonical_values.get("gage_number")).strip() if canonical_values.get("gage_number") else None,
            source_sheet=str(row.get("_source_sheet") or "Body"),
            source_row=int(row.get("_source_row", 0)),
            source_type="file",
            unmapped_fields=row_unmapped,
        )
        items.append(item)

    return MappedContext(
        items=items,
        unmapped_headers=unmapped_headers,
        raw_row_count=len(raw_rows),
        source_operations=sorted(list(source_ops), key=lambda x: (len(x), x))
    )
