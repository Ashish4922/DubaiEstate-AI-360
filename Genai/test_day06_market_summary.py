import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "day06_market_summary.md"
EVIDENCE = ROOT / "day06_source_evidence.csv"


class MarketSummaryTests(unittest.TestCase):
    def test_report_contains_required_sections(self):
        report = REPORT.read_text(encoding="utf-8")

        required_sections = [
            "# Dubai Real Estate Transaction Market Summary",
            "## Reporting scope",
            "## Dataset-level findings",
            "## Area comparison",
            "## Methodology",
            "## Source references",
            "## Limitations",
        ]

        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(section, report)

    def test_report_contains_dataset_metrics(self):
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("134,185", report)
        self.assertIn("AED 410,121,700,853.05", report)
        self.assertIn("2026-01-01", report)
        self.assertIn("2026-10-29", report)

    def test_evidence_csv_has_required_columns_and_records(self):
        self.assertTrue(EVIDENCE.exists())

        with EVIDENCE.open(encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            required_columns = {
                "source_file",
                "csv_row",
                "transaction_number",
                "instance_date",
                "area",
                "transaction_value",
                "actual_area_sqm",
                "price_per_sqm",
            }

            self.assertTrue(required_columns.issubset(reader.fieldnames or []))
            first_record = next(reader, None)

        self.assertIsNotNone(first_record)
        self.assertTrue(first_record["source_file"])
        self.assertGreater(int(first_record["csv_row"]), 1)


if __name__ == "__main__":
    unittest.main()
