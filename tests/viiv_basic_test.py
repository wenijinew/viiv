import unittest

from viiv.viiv import _random_range


class TestRandomRange(unittest.TestCase):
    def test_random_range_start_end_less_than_10(self):
        result = _random_range(["1", "12"])
        self.assertEqual(
            result,
            ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11"],
        )

    def test_random_range_start_end_greater_than_10(self):
        result = _random_range(["11", "20"])
        self.assertEqual(
            result, ["11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
        )

    def test_random_range_start_end_equal(self):
        result = _random_range(["10", "10"])
        self.assertEqual(result, ["10"])


if __name__ == "__main__":
    unittest.main()
