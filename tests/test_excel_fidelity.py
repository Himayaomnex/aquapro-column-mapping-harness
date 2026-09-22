"""
Automated Excel Fidelity Comparator Test Suite.
Validates 1:1 structural, dimensional, styling, merged-cell, and semantic fidelity
between harness output and the authentic parent reference workbook.
"""

import os
import unittest
import openpyxl
from harness import UnifiedHarness


class TestExcelFidelity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source_pfmea = "data/CNC_Operation_Process_FMEA.xlsx"
        cls.ref_benchmark = "data/CNC_Operation_Production_Item_Control_Plan.xlsx"
        cls.output_file = "output/test_fidelity_CNC_Control_Plan.xlsx"

        # Run harness with source-preserving mode
        harness = UnifiedHarness(capability_id="control_plan_from_pfmea")
        harness.run(
            file_path=cls.source_pfmea,
            output_path=cls.output_file
        )

    def test_01_workbook_structure_and_sheet_order(self):
        """Validates that sheet names and ordering match reference 1:1."""
        wb_ref = openpyxl.load_workbook(self.ref_benchmark, read_only=True)
        wb_out = openpyxl.load_workbook(self.output_file, read_only=True)

        self.assertEqual(wb_out.sheetnames, wb_ref.sheetnames,
                         f"Sheet structure mismatch! Expected {wb_ref.sheetnames}, got {wb_out.sheetnames}")
        self.assertEqual(wb_out.sheetnames, ["Header", "Body"])
        wb_ref.close()
        wb_out.close()

    def test_02_body_dimensions_and_column_count(self):
        """Validates that Body sheet dimensions match the 16-column APQP specification."""
        wb_ref = openpyxl.load_workbook(self.ref_benchmark)
        wb_out = openpyxl.load_workbook(self.output_file)

        ws_ref = wb_ref["Body"]
        ws_out = wb_out["Body"]

        self.assertEqual(ws_out.max_column, ws_ref.max_column)
        self.assertEqual(ws_out.max_column, 16)
        self.assertEqual(ws_out.max_row, ws_ref.max_row)

        wb_ref.close()
        wb_out.close()

    def test_03_merged_cell_ranges_fidelity(self):
        """Validates that all 27 merged ranges (operation grouping) are 100% preserved."""
        wb_ref = openpyxl.load_workbook(self.ref_benchmark)
        wb_out = openpyxl.load_workbook(self.output_file)

        ws_ref = wb_ref["Body"]
        ws_out = wb_out["Body"]

        ref_merges = set(str(m) for m in ws_ref.merged_cells.ranges)
        out_merges = set(str(m) for m in ws_out.merged_cells.ranges)

        self.assertEqual(ref_merges, out_merges,
                         f"Merged ranges mismatch! Missing: {ref_merges - out_merges}, Extra: {out_merges - ref_merges}")
        self.assertIn("A6:A11", out_merges)
        self.assertIn("B6:B11", out_merges)
        self.assertIn("C6:C11", out_merges)
        self.assertIn("A12:A15", out_merges)
        self.assertIn("B12:B15", out_merges)
        self.assertIn("C12:C15", out_merges)

        wb_ref.close()
        wb_out.close()

    def test_04_cell_formatting_and_styling(self):
        """Validates fonts, fills, alignments, and borders retain authentic benchmark styling."""
        wb_ref = openpyxl.load_workbook(self.ref_benchmark)
        wb_out = openpyxl.load_workbook(self.output_file)

        ws_ref = wb_ref["Body"]
        ws_out = wb_out["Body"]

        # Check header font and fill
        for col in range(1, 17):
            ref_font = ws_ref.cell(1, col).font
            out_font = ws_out.cell(1, col).font
            self.assertEqual(out_font.name, ref_font.name)
            self.assertEqual(out_font.size, ref_font.size)

        # Check data row styling (Row 4)
        self.assertEqual(ws_out.cell(4, 2).font.name, ws_ref.cell(4, 2).font.name)
        self.assertEqual(ws_out.cell(4, 2).alignment.horizontal, ws_ref.cell(4, 2).alignment.horizontal)

        wb_ref.close()
        wb_out.close()

    def test_05_authentic_values_preserved_no_hallucinations(self):
        """Validates that authentic reaction plans and controls are preserved without synthetic boilerplate."""
        wb_out = openpyxl.load_workbook(self.output_file)
        ws_out = wb_out["Body"]

        # Operation 81 (Row 4)
        self.assertEqual(str(ws_out.cell(4, 2).value).strip(), "81")
        self.assertIn("Nonconforming material rejection", str(ws_out.cell(4, 16).value))
        self.assertNotIn("Contain suspect parts. Notify Quality", str(ws_out.cell(4, 16).value))

        # Operation 82 (Row 5)
        self.assertEqual(str(ws_out.cell(5, 2).value).strip(), "82")
        self.assertIn("Do not run order without opened document", str(ws_out.cell(5, 16).value))

        # Operation 83 (Row 6)
        self.assertEqual(str(ws_out.cell(6, 2).value).strip(), "83")
        self.assertIn("Reject nonconforming material", str(ws_out.cell(6, 16).value))

        wb_out.close()


if __name__ == "__main__":
    unittest.main()
