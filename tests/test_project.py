import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.models import Dataset, UnitCell
from crystallography.clustering import cluster_datasets
from crystallography.distance import cells_within_tolerance
from crystallography.unit_cell import validate_unit_cell
from datasets.finder import find_target_folders
from datasets.ins_reader import extract_unit_cell, find_ins_file
from datasets.rodhypix import find_first_rodhypix
from output.excel import output_filename


class ProjectTests(unittest.TestCase):
    def test_search_matching_depth_duplicates_and_missing_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "ra3_one").mkdir()
            nested = root / "nested"
            nested.mkdir()
            (nested / "RA3_two").mkdir()
            self.assertEqual([root / "ra3_one"], find_target_folders([root], "RA3", 1, False))
            self.assertEqual(2, len(find_target_folders([root, root, root / "missing"], "RA3", None, False)))

    def test_dataset_files_and_cell(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "RA3"
            frames = folder / "frames"
            frames.mkdir(parents=True)
            (frames / "a.rodhypix").write_text("x")
            (frames / "b.rodhypix").write_text("y")
            insdir = folder / "struct" / "olex2_sample_auto"
            insdir.mkdir(parents=True)
            ins = insdir / "sample.ins"
            ins.write_text("CELL 1.54184 20.839999 20.839999 14.391 90 90 90\n")
            self.assertEqual(frames / "a.rodhypix", find_first_rodhypix(folder))
            self.assertEqual(ins, find_ins_file(folder))
            cell = extract_unit_cell(ins)
            self.assertEqual((20.839999, 20.839999, 14.391, 90, 90, 90),
                             (cell.a, cell.b, cell.c, cell.alpha, cell.beta, cell.gamma))
            self.assertIsNone(find_first_rodhypix(folder / "absent"))
            self.assertIsNone(extract_unit_cell(None))
            ins.write_text("CELL nope\n")
            self.assertIsNone(extract_unit_cell(ins))

    def test_validation_comparison_grouping_and_filename(self):
        one = UnitCell(10, 11, 12, 90, 90, 90)
        close = UnitCell(10.01, 11, 12, 90, 90, 90)
        bad = UnitCell(-1, 11, 12, 90, 90, 90)
        self.assertTrue(validate_unit_cell(one))
        self.assertFalse(validate_unit_cell(bad))
        self.assertTrue(cells_within_tolerance(one, close, 0.02, 0.2))
        datasets = [Dataset("a", Path("a"), unit_cell=one), Dataset("b", Path("b"), unit_cell=close),
                    Dataset("c", Path("c")), Dataset("d", Path("d"), unit_cell=bad)]
        cluster_datasets(datasets, "RA3", 0.02, 0.2)
        self.assertEqual(["RA3-1", "RA3-1", None, None], [d.cluster for d in datasets])
        self.assertEqual(Path("RA3_summary.xlsx"), output_filename(Path("."), "RA3_summary", datetime(2020, 1, 2), False))


if __name__ == "__main__":
    unittest.main()
