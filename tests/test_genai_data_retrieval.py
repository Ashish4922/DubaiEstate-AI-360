import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path

from Genai.data_retrieval import get_transaction_metrics


class TransactionMetricsTests(unittest.TestCase):
    def write_csv(self, directory, name, rows, columns=None):
        path = Path(directory, name)
        columns = columns or ["INSTANCE_DATE", "AREA_EN", "TRANS_VALUE"]
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_aggregates_across_files_without_mutating_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.write_csv(directory, "one.csv", [
                {"INSTANCE_DATE": "2026-01-01 10:00:00", "AREA_EN": "A", "TRANS_VALUE": "100"},
            ])
            second = self.write_csv(directory, "two.csv", [
                {"INSTANCE_DATE": "2026-01-02 10:00:00", "AREA_EN": "A", "TRANS_VALUE": "250"},
            ])
            before = (first.read_bytes(), second.read_bytes())
            result = get_transaction_metrics([first, second], area="A")
            self.assertEqual(result["transaction_count"], 2)
            self.assertEqual(str(result["total_value"]), "350")
            self.assertEqual(str(result["average_value"]), "175")
            self.assertEqual((first.read_bytes(), second.read_bytes()), before)

    def test_inclusive_date_filter_and_empty_result(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(directory, "data.csv", [
                {"INSTANCE_DATE": "2026-01-01 23:59:59", "AREA_EN": "A", "TRANS_VALUE": "10"},
                {"INSTANCE_DATE": "2026-01-03 00:00:00", "AREA_EN": "A", "TRANS_VALUE": "30"},
            ])
            filtered = get_transaction_metrics([path], start_date=date(2026, 1, 1), end_date=date(2026, 1, 2))
            empty = get_transaction_metrics([path], area="Unknown")
            self.assertEqual(filtered["transaction_count"], 1)
            self.assertEqual(str(filtered["total_value"]), "10")
            self.assertEqual(empty, {"transaction_count": 0, "total_value": 0, "average_value": None})

    def test_rejects_invalid_date_range_and_missing_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(directory, "data.csv", [], columns=["AREA_EN"])
            with self.assertRaisesRegex(ValueError, "start_date"):
                get_transaction_metrics([path], start_date=date(2026, 2, 1), end_date=date(2026, 1, 1))
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                get_transaction_metrics([path])


if __name__ == "__main__":
    unittest.main()
