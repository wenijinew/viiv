"""ViiV Basic Test"""
import unittest

from viiv.viiv import normalize_range


class TestRandomRange(unittest.TestCase):
    """Test cases for random range"""

    def test_random_range_start_end_less_than_10(self):
        """Random range less than 10"""
        result = normalize_range(["1", "9"])
        self.assertEqual(
            result,
            ["01", "02", "03", "04", "05", "06", "07", "08"],
        )

    def test_random_range_start_end_greater_than_10(self):
        """Random range great than 10"""
        result = normalize_range(["11", "20"])
        self.assertEqual(result, ["11", "12", "13", "14", "15", "16", "17", "18", "19"])

    def test_random_range_start_end_equal(self):
        """Random range start == end"""
        result = normalize_range(["10", "10"])
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
