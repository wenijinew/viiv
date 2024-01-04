"""Test Package Content"""
import os
import unittest

from viiv.viiv import load_json_file


class TestPackage(unittest.TestCase):
    """Test cases for package"""

    def test_themes_pathes(self):
        """Verify if themes pathes exist"""
        root_path = os.getcwd() + os.sep
        package_file_path = root_path + "package.json"
        package_data = load_json_file(package_file_path)
        themes = package_data["contributes"]["themes"]
        for theme in themes:
            theme_path = theme["path"]
            assert os.path.exists(
                f"{root_path}{theme_path}"
            ), f"{theme_path} doesn't exist."
