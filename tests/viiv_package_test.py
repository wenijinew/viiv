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
        theme_filenames_in_package = []
        for theme in themes:
            theme_path = theme["path"]
            theme_filename = theme_path.split("/")[-1]
            theme_full_path = root_path + theme_path
            theme_filenames_in_package.append(theme_filename)
            assert os.path.exists(theme_full_path), f"{theme_path} doesn't exist."
        themes_path_root = root_path + "themes"
        theme_filenames_in_root_path = list(
            filter(
                lambda x: x.endswith("color-theme.json"),
                os.listdir(themes_path_root),
            )
        )
        themes_not_in_package = [
            f"{themes_path_root}{os.sep}{x}"
            for x in theme_filenames_in_root_path
            if x not in theme_filenames_in_package
        ]
        assert (
            len(themes_not_in_package) == 0
        ), f"Themes not in package: {themes_not_in_package}"
