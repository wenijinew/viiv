#!/usr/bin/env python3

import unittest
from my_module import ColorComponent

class TestColorMethods(unittest.TestCase):

    def test_append_or_replace_alpha(self):
        old_color = "#FFB6C1"
        new_color = "#00FF7F"
        
        # Test appending alpha component
        alpha_color = ColorComponent.ALPHA
        expected_alpha_result = "#00FF7FFF"
        self.assertEqual(_append_or_replace_alpha(old_color, new_color, alpha_color), expected_alpha_result)

        # Test replacing light component
        light_color = ColorComponent.LIGHT
        expected_light_result = "#00FF7F01"
        self.assertEqual(_append_or_replace_alpha(old_color, new_color, light_color), expected_light_result)

        # Test replacing basic component
        basic_color = ColorComponent.BASIC
        expected_basic_result = "#00B6C1"
        self.assertEqual(_append_or_replace_alpha(old_color, new_color, basic_color), expected_basic_result)

if __name__ == '__main__':
    unittest.main()