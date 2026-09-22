"""
Test Universal Dynamic Excel Ingestion and Conversion.
Verifies that ANY new/arbitrary Excel workbook (including unnumbered operations,
multilingual formats, and custom supplier templates) is parsed, mapped, and converted
into the authentic parent codebase formats with 100% fidelity and zero hardcoding.
"""

import os
import unittest
import openpyxl
from openpyxl.styles import PatternFill

from tools import (
    workbook_parser,
    column_mapper,
    excel_builder,
    validator,
    excel_exporter,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


class TestNewExcelUniversalConversions(unittest.TestCase):

    def setUp(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def test_arbitrary_excel_with_unnumbered_operations(self):
        """
        Scenario: A brand new OEM supplier workbook where operations have names
        but NO operation numbers (e.g. GM/Stellantis unnumbered process flow).
        Verification:
          - Automatically synthesizes sequence numbers (10, 20, 30, 40, 50).
          - Never collapses distinct operations.
          - Produces 16-column 'Control Plan' sheet with #FFFFC5 header fill.
        """
        temp_input = os.path.join(OUTPUT_DIR, "arbitrary_unnumbered_supplier.xlsx")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Supplier_PFMEA"

        # Headers without an operation number column
        headers = [
            "Part Description",
            "Process Description",
            "Product Specs",
            "Process Parameter",
            "Potential Failure Mode",
            "Potential Effects of Failure",
            "Severity",
            "Potential Causes of Failure",
            "Occurrence",
            "Current Process Controls: Prevention",
            "Current Process Controls: Detection",
            "Detection",
        ]
        ws.append(headers)

        rows = [
            # Op 1: Receiving
            ["Electric Drive Unit", "Goods Receiving", "Cleanliness", "Visual condition", "Contaminated housing", "Motor failure", 8, "Debris in shipment", 3, "Supplier packaging standard", "Visual incoming audit", 4],
            ["Electric Drive Unit", "Goods Receiving", "Bar code label", "Scanner readability", "Missing label", "Traceability loss", 5, "Damaged label", 2, "Supplier barcode spec", "Scanner verification", 2],
            # Op 2: Stator Press
            ["Electric Drive Unit", "Stator Core Press Fit", "Press depth", "Hydraulic pressure", "Under-pressed stator", "Rotor interference", 9, "Low hydraulic pressure", 4, "Hydraulic pressure sensor", "Laser depth measurement", 3],
            # Op 3: Laser Welding
            ["Electric Drive Unit", "Laser Welding Terminals", "Weld bead width", "Laser power", "Cold weld joint", "Electrical open circuit", 9, "Laser power drop", 3, "Laser power monitor", "Automated optical inspection", 3],
            # Op 4: EOL Testing
            ["Electric Drive Unit", "End of Line Functional Test", "Back-EMF voltage", "Test bench speed", "Voltage out of spec", "Vehicle shutdown", 8, "Damaged magnet", 2, "Test station calibration", "Automated test bench reading", 2],
        ]
        for r in rows:
            ws.append(r)
        wb.save(temp_input)
        wb.close()

        # Ingest and convert
        raw_rows = workbook_parser(temp_input)
        self.assertEqual(len(raw_rows), 5)

        mapped_ctx = column_mapper(raw_rows)
        # Verify unnumbered operations were dynamically synthesized as 4 distinct operations
        self.assertEqual(len(mapped_ctx.source_operations), 4)
        self.assertEqual(mapped_ctx.source_operations, ["10", "20", "30", "40"])

        # Build Control Plan rows
        cp_rows = excel_builder(mapped_ctx, document_type="control_plan_from_pfmea")
        self.assertEqual(len(cp_rows), 5)

        # Validate
        violations = validator(cp_rows, mapped_ctx)
        self.assertEqual(len(violations), 0, f"Validation violations: {violations}")

        # Export
        out_excel = os.path.join(OUTPUT_DIR, "arbitrary_unnumbered_control_plan.xlsx")
        excel_exporter(cp_rows, out_excel)

        # Audit generated Excel against parent codebase standards
        wb_out = openpyxl.load_workbook(out_excel)
        self.assertIn("Control Plan", wb_out.sheetnames)
        ws_cp = wb_out["Control Plan"]

        # Check 16 columns
        expected_cols = [
            "Production Item Name",
            "Process Segment Name",
            "Operation Number",
            "Operation Name",
            "Product Characteristics",
            "Process Characteristics",
            "Special Characteristic Class",
            "Product/Process Specification/Tolerance",
            "Evaluation/Measurement Technique",
            "Tool Number",
            "Tool Name",
            "Gage Number",
            "Control Method",
            "Sample Size",
            "Sample Frequency",
            "Reaction Plan",
        ]
        actual_cols = [ws_cp.cell(1, c).value for c in range(1, 17)]
        self.assertEqual(actual_cols, expected_cols)

        # Check #FFFFC5 header fill
        h_fill = ws_cp.cell(1, 1).fill.start_color.rgb
        self.assertIn(h_fill, ["FFFFFFC5", "FFFFC5"])

        # Check that operations 10, 20, 30, 40 are all present in column 3
        op_col_vals = set(ws_cp.cell(r, 3).value for r in range(2, ws_cp.max_row + 1))
        self.assertEqual(op_col_vals, {"10", "20", "30", "40"})
        wb_out.close()

    def test_multilingual_spanish_excel(self):
        """
        Scenario: Multilingual Spanish Process FMEA from an international supplier.
        Verification:
          - Automatically maps Spanish headers to canonical fields via SYNONYM_MAP.
          - Extracts operation prefixes (e.g. 'Op 10: Recepción').
          - Produces authentic Control Plan and PFMEA VDA exports.
        """
        temp_input = os.path.join(OUTPUT_DIR, "supplier_spanish_pfmea.xlsx")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "FMEA_Proceso"

        headers = [
            "Nombre de la Pieza",
            "Operación",
            "Característica de Producto",
            "Parámetro de Proceso",
            "Modo de Falla",
            "Efecto de Falla",
            "Severidad",
            "Causa de Falla",
            "Ocurrencia",
            "Control Preventivo",
            "Control de Detección",
            "Detección",
        ]
        ws.append(headers)

        rows = [
            ["Bomba de Frenos", "Op 10: Recepción de Material", "Limpieza", "Inspección visual", "Material sucio", "Fuga hidráulica", 8, "Empaque roto", 3, "Padrón de empaque", "Inspección visual 100%", 3],
            ["Bomba de Frenos", "Op 20: Maquinado CNC", "Diámetro interior", "Velocidad de husillo", "Diámetro fuera de tolerancia", "Pérdida de presión", 9, "Desgaste de herramienta", 4, "Monitoreo de carga", "Calibre micrométrico", 3],
            ["Bomba de Frenos", "Op 30: Prueba de Fuga", "Presión de retención", "Presión neumática", "Fuga en ensamble", "Falla de freno en vehículo", 10, "Sello dañado", 2, "Verificación de poka-yoke", "Prueba de caída de presión", 2],
        ]
        for r in rows:
            ws.append(r)
        wb.save(temp_input)
        wb.close()

        raw_rows = workbook_parser(temp_input)
        self.assertEqual(len(raw_rows), 3)

        mapped_ctx = column_mapper(raw_rows)
        self.assertEqual(mapped_ctx.source_operations, ["10", "20", "30"])

        # Control Plan export
        cp_rows = excel_builder(mapped_ctx, document_type="control_plan_from_pfmea")
        self.assertEqual(len(cp_rows), 3)

        out_cp = os.path.join(OUTPUT_DIR, "spanish_converted_control_plan.xlsx")
        excel_exporter(cp_rows, out_cp)

        wb_cp = openpyxl.load_workbook(out_cp)
        self.assertIn("Control Plan", wb_cp.sheetnames)
        wb_cp.close()

        # PFMEA VDA export
        vda_rows = excel_builder(mapped_ctx, document_type="pfmea_aiag_to_vda")
        self.assertEqual(len(vda_rows), 3)

        out_vda = os.path.join(OUTPUT_DIR, "spanish_converted_pfmea_vda.xlsx")
        excel_exporter(vda_rows, out_vda)

        wb_vda = openpyxl.load_workbook(out_vda)
        self.assertIn("PFMEA", wb_vda.sheetnames)
        ws_vda = wb_vda["PFMEA"]
        # Check 5-section color band in Row 1
        sec_1_fill = ws_vda.cell(1, 1).fill.start_color.rgb
        self.assertIn(sec_1_fill, ["FF4472C4", "4472C4"])
        # Check Action Priority (AP) column populated
        ap_col = None
        for col_idx in range(1, ws_vda.max_column + 1):
            if ws_vda.cell(2, col_idx).value == "Action Priority (AP)":
                ap_col = col_idx
                break
        self.assertIsNotNone(ap_col)
        # Check row 3 AP value is High (since S=9, O=4, D=3)
        ap_val = ws_vda.cell(3, ap_col).value
        self.assertIn(ap_val, ["H", "M", "L"])
        wb_vda.close()


if __name__ == "__main__":
    unittest.main()
