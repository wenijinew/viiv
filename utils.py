#!/usr/bin/env python
"""Functions to help quickly generate customized token colors in VsCode theme file."""

import getopt
import json
import os
import random
import re
import sys
from enum import Enum
from peelee import peelee as pe

PLACEHOLDER_REGEX = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2,4}"
PLACEHOLDER_REGEX_WITHOUT_ALPHA = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}"
PLACEHOLDER_REGEX_WITH_ALPHA = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}[a-zA-Z0-9]{2}"
RGB_HEX_REGEX_WITHOUT_ALPHA = r"#[a-zA-Z0-9]{6}"
RGB_HEX_REGEX_WITH_ALPHA = r"#[a-zA-Z0-9]{8}"

HEX_NUMBER_STR_PATTERN = re.compile(r"^[0-9a-zA-Z]+$")


class MatchRule(Enum):
    """Match rule for color range."""

    EXACT = 1
    ENDSWITH = 2
    STARTSWITH = 3
    FUZZY = 4


def _to_int(value: str) -> int:
    """Convert string to int."""
    if isinstance(value, int) == int:
        return value
    elif isinstance(value, str) and HEX_NUMBER_STR_PATTERN.match(value):
        return int(value, 16)
    return int(value)


def _read_config(config_path):
    """Read config.json file and return the content."""
    with open(config_path, "r") as f:
        return json.load(f)


def _random_range(range_values: list[str]) -> list[str]:
    """Generate random numbers in string format with the given range values.
    if the random number is less than 10, then add a 0 before the number.

    Example:
    _random_range([1, 12])
    -> ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    """
    _random = []
    _start = _to_int(range_values[0])
    _end = _to_int(range_values[1])
    for i in range(_to_int(range_values[0]), _to_int(range_values[1])):
        _random.append(str(i) if i >= 10 else str("0" + str(i)))
    return _random


class Colors(dict):
    """Wrapper class for color."""
    def __init__(self, colors: list, area: str):
        self.colors = colors
        self.area = area
        super().__init__(colors=colors, area = area)


class Color(dict):
    """Wrapper class for color.

    One color consists of hex, color ranges for basic, light, and alpha.
    If hex is given, then basic and light ranges will be ignored.
    One color can generate multiple colors by using hex or basic and light ranges, together with alpha range.

    If the hex is given, then the generated color hex values could be "#efefef3e". Otherwise, it could be "C_11_343e".
    The first format is used directly in final theme config file.
    The 2nd one is used in theme template file and will be replaced with the auto-generated color hex value.

    The Color is configured in config.json file. It's content could be like:
    {
        "hex": "#008000",
        "alpha_range": [
            "0x99",
            "0xcc"
        ]
    }
    or
    {
        "basic_range": [
            11,
            12
        ],
        "light_range": [
            59,
            60
        ],
        "alpha_range": [
            "0x99",
            "0xcc"
        ]
    }
    """

    def __init__(self, config, area):
        self.config = config
        self.area = area
        self.hex = config.get("hex", None)
        self.alpha_range = config.get("alpha_range", None)
        self.basic_range = config.get("basic_range", None)
        self.light_range = config.get("light_range", None)
        super().__init__(config=self.config)

    def __repr__(self):
        return f"Color({self.config})"

    def create_colors(self) -> Colors:
        """Generate colors by using hex or basic and light ranges."""
        has_hex = self.hex is not None
        has_alpha = self.alpha_range is not None and len(self.alpha_range) == 2
        has_basic = self.basic_range is not None and len(self.basic_range) == 2
        has_light = self.light_range is not None and len(self.light_range) == 2

        if has_hex:
            _head = [self.hex]
        elif has_basic and has_light:
            _head = [
                "C_" + basic + "_" + light
                for basic, light in zip(
                    _random_range(self.basic_range), _random_range(self.light_range)
                )
            ]
        else:
            raise ValueError(f"Invalid config: {self.config}.")

        if has_alpha:
            _tail = []
            for alpha in _random_range(self.alpha_range):
                alpha = format(int(alpha), "x")
                if len(alpha) == 1:
                    alpha = "0" + alpha
                _tail.append(alpha) 
        else:
            _tail = [""]
        _colors = [f"{head}{tail}" for head in _head for tail in _tail]
        return Colors(_colors, self.area)


class ColorConfig(dict):
    """Wrapper class for color config

    Read and parse config.json file located in the current directory.
    """

    def __init__(self, config_path):
        """Read config.json file and initialize."""
        self.config_path = config_path
        self.config = _read_config(config_path)
        self.areas = list(list(filter(lambda x: x != "default" and x != "basic", self.config.keys())))
        self.default_color = Color(self.config["default"], "default")
        super().__init__(
            config=self.config, areas=self.areas, default_color=self.default_color
        )

    def get_colors(self, target_group) -> Colors:
        color = self.get_color(target_group)
        print(target_group, color)
        return color.create_colors()

    def get_color(self, target):
        """Go through the config items in the basic groups and set the color by checking if the given 'group' contains the key of the groups.

        content example of basic groups:
        {
            "group": [
                "success",
                "add"
            ],
            "color": {
                "hex": "#008000",
                "alpha_range": [
                    "0x99",
                    "0xcc"
                ]
            }
        }

        colors config are divided by areas
        basic, background, foreground, border, outline, shadow

        basic: fuzzy matching

        background, foreground, border, outline, shadow: need 3 different matching rules.
        1. endswith '[group]background'
        2. startswith '[group]background'
        3. contains '[group]'


        Parameters:
            target (str): target group or target color perperty


        Retrun :
            Color object include area info, only those color perperty belong to that area can use that color. Color for backkground cannot be used by foreground color perperty.
            If not found, return the default color.
        """
        # basic has higher priority
        color = self._get_color(
            "basic", target, MatchRule.FUZZY.name
        )
        if color is not None:
            return color
        for area in self.areas:
            # try to find the configured color in the matching order
            for match_rule_name in MatchRule._member_names_:
                color = self._get_color(
                    area, target, match_rule_name
                )
                if color is not None:
                    break
            if color is not None:
                break
        return color if color is not None else self.default_color

    def _get_color(self, area, target_group, match_rule_name):
        area_config = self.config[area]
        for config in area_config:
            groups = config["groups"]
            for _group in groups:
                if (
                    match_rule_name == MatchRule.ENDSWITH.name
                    and target_group.endswith(_group.lower())
                ):
                    color = config["color"]
                    return Color(color, area)
                elif (
                    match_rule_name == MatchRule.STARTSWITH.name
                    and target_group.lower().startswith(_group.lower())
                ):
                    color = config["color"]
                    return Color(color, area)
                elif match_rule_name == MatchRule.EXACT.name and target_group == _group:
                    color = config["color"]
                    return Color(color, area)
                elif match_rule_name == MatchRule.FUZZY.name and re.match(
                    _group, target_group, re.IGNORECASE
                ):
                    color = config["color"]
                    return Color(color, area)
        return None

    def __repr__(self) -> str:
        return super().__repr__()


class TemplateConfig(dict):
    """Wrapper class for template config."""

    def __init__(self, config_path = None):
        if config_path is None:
            config_path = f"{os.getcwd()}/themes/viiv-color-theme.template.json"
        self.config_path = config_path
        self.config = _read_config(config_path)
        self.color_properties = list(self.config["colors"].keys())
        super().__init__(config_path=config_path)

    def get_basic_groups(self):
        """Get suffix groups."""
        # these are the basic groups, e.g. background, foreground, etc.
        basic_groups = ["foreground", "background", "border", "outline", "shadow"]
        _groups = {}
        for _property in self.color_properties:
            _splits = _property.split(".")
            if len(_splits) == 1:
                continue
            suffix = _splits[-1]
            for _group in basic_groups:
                if suffix.lower().find(_group.lower()) != -1:
                    if _group not in _groups:
                        _groups[_group] = [_property]
                    else:
                        _groups[_group].append(_property)
        return dict(sorted(_groups.items(), key=lambda x: x[0]))

    def get_prefix_groups(self):
        _groups = {}
        for _property in self.color_properties:
            _splits = _property.split(".")
            component = _splits[0]
            if component not in _groups:
                _groups[component] = [_property]
            else:
                _groups[component].append(_property)
        return dict(sorted(_groups.items(), key=lambda x: x[0]))

    def get_status_groups(self):
        """Get status group."""
        _groups = {}
        statuses = [
            "active",
            "focus",
            "fold",
            "select",
            "selected",
            "selection",
            "hover",
            "inactive",
            "disabled",
            "offline",
        ]
        for _property in self.color_properties:
            for _status in statuses:
                if _property.find(_status) != -1:
                    if _status not in _groups:
                        _groups[_status] = [_property]
                    else:
                        _groups[_status].append(_property)
        return dict(sorted(_groups.items(), key=lambda x: x[0]))


    def _append_or_replace_alpha(self, color, alpha):
        if alpha is None or not re.match(r"[0-9a-zA-Z]{2}", alpha):
            return color
        if re.match(PLACEHOLDER_REGEX_WITH_ALPHA, color) or re.match(
            RGB_HEX_REGEX_WITH_ALPHA, color
        ):
            _color = color[0:-2] + alpha 
        elif re.match(
            PLACEHOLDER_REGEX_WITHOUT_ALPHA, color
        ) or re.match(RGB_HEX_REGEX_WITHOUT_ALPHA, color):
            _color = color + alpha 
        return _color 


    def regenerate_template_colors(self, color_config: ColorConfig = None):
        """Generate template with color configuration.

        The template color could be color placeholder in the format 'C_11_343e' or the real color in hex format such as "#efefef3e".


        Parameters:
            color_config (dict): ColorConfig object.
        """
        if color_config is None:
            _color_config_path = f"{os.getcwd()}/config.json"
            color_config = ColorConfig(config_path=_color_config_path)
        _basic_groups = self.get_basic_groups()
        _prefix_groups = self.get_prefix_groups()
        _status_groups = self.get_status_groups()

        template_colors = {}
        # the priority order: suffix, prefix, status
        print("suffix", _basic_groups.keys())
        for _group in _basic_groups:
            colors = color_config.get_colors(_group)
            _colors = colors.colors
            _area = colors.area
            _group_color_properties = _basic_groups[_group]
            for index, _property in enumerate(_group_color_properties):
                if _property.lower().find(_area.lower()) == -1 and _area != "basic" and _area != "default":
                    continue
                _color = _colors[index % len(_colors)]
                template_colors[_property] = _color

        print("prefix", _prefix_groups.keys())
        for _group in _prefix_groups:
            colors = color_config.get_colors(_group)
            _colors = colors.colors
            _area = colors.area
            _group_color_properties = _prefix_groups[_group]
            for index, _property in enumerate(_group_color_properties):
                if _property.lower().find(_area.lower()) == -1 and _area != "basic" and _area != "default":
                    continue
                _color = _colors[index % len(_colors)]
                template_colors[_property] = _color

        print("status", _status_groups.keys())
        for _group in _status_groups:
            colors = color_config.get_colors(_group)
            _colors = colors.colors
            _area = colors.area
            _group_color_properties = _status_groups[_group]
            for index, _property in enumerate(_group_color_properties):
                if _property.lower().find(_area.lower()) == -1 and _area != "basic" and _area != "default":
                    continue
                _color = _colors[index % len(_colors)]
                if _property in template_colors:
                    _old_color = template_colors[_property]
                    alpha = _color[-2:] 
                    _color = self._append_or_replace_alpha(_old_color, alpha)
                template_colors[_property] = _color

        self.config["colors"] = template_colors
        json.dump(self.config, open(self.config_path, "w"), indent=4, sort_keys=True)


class ColorRange(dict):
    """Wrapper class for color ranges.

    Code range is used to construct code placeholders. Code placeholder is in the format: "C_[0-9]{2}_[0-9]{2}([a-zA-Z0-9]{2})?".
    The first 2 digits are used to indicate the base color group, the 2nd 2 digits are used to indicate the color lightness level, the last 2 digits(hexadecimal) are used to indicate the real alpha value range(0x0 - 0xff).
    """

    def __init__(self, base_color_range, light_level_range, alpha_range):
        self.base_color_range = base_color_range
        self.light_level_range = light_level_range
        self.alpha_range = alpha_range
        super().__init__(
            base_color_range=base_color_range,
            light_level_range=light_level_range,
            alpha_range=alpha_range,
        )

    def is_valid(self):
        """Check if the color range is valid.
        Each color range starts from min and ends at max. min is less than max.
        Color range should not be None or empty.
        Alpha range could be None or empty.
        """
        if self.base_color_range is None or self.light_level_range is None:
            return False
        if not self.base_color_range or not self.light_level_range:
            return False
        if self.base_color_range[0] >= self.base_color_range[1]:
            return False
        if self.light_level_range[0] >= self.light_level_range[1]:
            return False
        if self.alpha_range and self.alpha_range[0] >= self.alpha_range[1]:
            return False
        return True

    def __repr__(self) -> str:
        return super().__repr__()


GENERAL_GROUPS = ["Background", "Foreground", "Border", "Outline"]
HIGH_PRIORITY_GROUPS_PREFIXES = [
    "Active",
    "ActiveSelection",
    "Inactive",
    "InactiveSelection",
    "Hover",
    "Match",
    "Focus",
    "FocusHighlight",
    "Header",
    "Highlight",
    "HighlightText",
    "HighlightStrong",
    "Selection",
]


DEFAULT_BACKGROUND_COLOR_RANGE = ColorRange([1, 12], [50, 60], [])
DEFAULT_FOREGROUND_COLOR_RANGE = ColorRange([1, 12], [5, 25], [])
DEFAULT_BORDER_COLOR_RANGE = ColorRange([1, 12], [55, 60], [30, 40])
DEFAULT_COLOR_RANGE = ColorRange([1, 12], [25, 45], [])
DEFAULT_COLOR_RANGES = [
    DEFAULT_BACKGROUND_COLOR_RANGE,
    DEFAULT_FOREGROUND_COLOR_RANGE,
    DEFAULT_BORDER_COLOR_RANGE,
    DEFAULT_COLOR_RANGE,
]

CUSTOMIZED_COLOR_PLACEHOLDERS = {
    "editorWarning.background": "#ffb73300",
    "editorWarning.border": "#ffb73300",
    "editorWarning.foreground": "#ffb733",
    "editorError.background": "#ff4d4d00",
    "editorError.border": "#ff4d4d00",
    "editorError.foreground": "#ff4d4d",
    "problemsErrorIcon.foreground": "#ff4d4d",
    "problemsWarningIcon.foreground": "#ffb733",
    "testing.iconErrored": "#ff4d4d",
    "testing.iconFailed": "#ff1a1a",
    "testing.iconPassed": "#009a00",
    "testing.iconQueued": "#6767ff",
    "testing.iconSkipped": "#a6a6a6",
    "testing.iconUnset": "#635a50",
    "terminal.ansiBlack": "#0c0c0c",
    "terminal.ansiBrightBlack": "#333333",
    "terminal.ansiBlue": "#73639f",
    "terminal.ansiBrightBlue": "#514570",
    "terminal.ansiCyan": "#008b8b",
    "terminal.ansiBrightCyan": "#00a5a5",
    "terminal.ansiGreen": "#008000",
    "terminal.ansiBrightGreen": "#009a00",
    "terminal.ansiMagenta": "#670067",
    "terminal.ansiBrightMagenta": "#b400b4",
    "terminal.ansiRed": "#cd3300",
    "terminal.ansiBrightRed": "#ff1a1a",
    "terminal.ansiWhite": "#cecece",
    "terminal.ansiBrightWhite": "#f4f4f4",
    "terminal.ansiYellow": "#808000",
    "terminal.ansiBrightYellow": "#b3b300",
}

# More specific groups, put it in topper position. The reason is that if the given group is not equal to the group in the list, it will try to use endwith to find the most matching group.
# The groups having more words are more specific.
COLOR_RANGE_MAP = {
    "WordHighlightTextBackground": ColorRange([7, 9], [5, 15], [0x35, 0x45]),
    "WordHighlightStrongBackground": ColorRange([7, 9], [5, 15], [0x65, 0x95]),
    "WordHighlightStrongBorder": ColorRange([1, 12], [23, 33], [0x90, 0xFF]),
    "InactiveSelectionBackground": ColorRange([11, 12], [39, 49], [0x33, 0x66]),
    "InactiveSelectionForeground": ColorRange([9, 10], [15, 19], [0x45, 0x65]),
    "EditorOverviewRuler": ColorRange([1, 12], [15, 45], [0x35, 0x45]),
    "HighlightStrongBackground": ColorRange([1, 12], [15, 25], [0x20, 0x30]),
    "HighlightStrongForeground": ColorRange([1, 12], [23, 33], [0x60, 0x90]),
    "HighlightStrongBorder": ColorRange([1, 12], [23, 33], [0x90, 0xFF]),
    "HighlightTextBackground": ColorRange([1, 12], [37, 47], [0x30, 0x40]),
    "HighlightTextBorder": ColorRange([1, 12], [18, 28], [0x30, 0x40]),
    "FocusHighlightBackground": ColorRange([1, 12], [37, 47], [0x30, 0x40]),
    "FocusHighlightForeground": ColorRange([1, 12], [6, 16], [0x30, 0x40]),
    "FocusHighlightBorder": ColorRange([1, 12], [26, 36], [0x30, 0x40]),
    "FocusHighlightOutline": ColorRange([1, 12], [11, 21], [0x30, 0x40]),
    "ActiveSelectionBackground": ColorRange([7, 9], [39, 49], [0x66, 0x99]),
    "ActiveSelectionForeground": ColorRange([7, 9], [5, 15], []),
    "SelectionHighlightBackground": ColorRange([7, 9], [5, 15], [0x33, 0x45]),
    "WordHighlightBackground": ColorRange([1, 12], [13, 23], [0x30, 0x40]),
    "MatchBorder": ColorRange([1, 12], [31, 41], [0x30, 0x40]),
    "MatchOutline": ColorRange([1, 12], [33, 43], [0x30, 0x40]),
    "HeaderBackground": ColorRange([1, 12], [51, 56], []),
    "HighlightBackground": ColorRange([1, 12], [28, 38], [0x30, 0x40]),
    "HighlightForeground": ColorRange([1, 12], [8, 18], []),
    "HighlightBorder": ColorRange([1, 12], [14, 24], [0x20, 0x40]),
    "HighlightOutline": ColorRange([1, 12], [13, 23], [0x30, 0x40]),
    "SelectionBackground": ColorRange([1, 12], [39, 49], [0x63, 0x86]),
    "SelectionForeground": ColorRange([1, 12], [7, 17], []),
    "SelectionBorder": ColorRange([1, 12], [19, 29], [0x30, 0x40]),
    "SelectionOutline": ColorRange([1, 12], [13, 23], [0x30, 0x40]),
    "ActiveBackground": ColorRange([1, 12], [40, 47], [0x99, 0xCC]),
    "ActiveForeground": ColorRange([11, 12], [0, 30], [0xCC, 0xFF]),
    "ActiveBorder": ColorRange([1, 12], [40, 45], []),
    "ActiveOutline": ColorRange([1, 12], [40, 45], []),
    "InactiveBackground": ColorRange([11, 12], [39, 49], [0x33, 0x66]),
    "InactiveForeground": ColorRange([9, 10], [15, 19], [0x89, 0xCA]),
    "InactiveBorder": ColorRange([1, 12], [50, 55], [0x30, 0x40]),
    "InactiveOutline": ColorRange([1, 12], [50, 55], [0x30, 0x40]),
    "StatusBarBackground": ColorRange([11, 12], [55, 60], []),
    "HoverBackground": ColorRange([1, 2], [40, 45], [0x43, 0x47]),
    "HoverForeground": ColorRange([2, 3], [5, 10], []),
    "HoverBorder": ColorRange([1, 2], [35, 40], []),
    "HoverOutline": ColorRange([2, 3], [36, 42], []),
    "MatchBackground": ColorRange([1, 12], [33, 42], [0x30, 0x40]),
    "MatchForeground": ColorRange([1, 12], [13, 23], [0x30, 0x40]),
    "EditorRuler": ColorRange([1, 12], [0, 30], [0x30, 0x40]),
    "EditorWarning": ColorRange([1, 12], [25, 30], [0x30, 0x40]),
    "EditorError": ColorRange([1, 12], [20, 25], [0x30, 0x40]),
    "EditorBracketMatch": ColorRange([1, 12], [20, 25], [0x30, 0x40]),
    "EditorLineNumber": ColorRange([1, 12], [10, 20], [0x60, 0x80]),
    "EditorIndentGuide": ColorRange([1, 12], [0, 30], [0x30, 0x40]),
    "EditorGutter": ColorRange([1, 12], [20, 30], []),
    "EditorCodeLens": ColorRange([1, 12], [20, 30], [0x50, 0x70]),
    "FocusBackground": ColorRange([1, 12], [20, 30], [0x50, 0x70]),
    "InputOption": ColorRange([1, 12], [20, 30], [0x50, 0x70]),
    "ScrollbarSlider": ColorRange([1, 12], [35, 45], [0x90, 0x99]),
    "Foreground": ColorRange([1, 12], [15, 20], []),
    "Background": ColorRange([1, 12], [55, 57], []),
    "Border": ColorRange([11, 12], [35, 45], [0x93, 0x96]),
    "Outline": ColorRange([1, 12], [45, 50], [0x30, 0x60]),
    "Highlight": ColorRange([1, 12], [30, 35], [0x30, 0x40]),
    "Stroke": ColorRange([1, 12], [35, 40], [0x60, 0x90]),
    "Panel": ColorRange([1, 12], [50, 53], []),
    "Tree": ColorRange([1, 12], [50, 55], [0x30, 0x40]),
    "Icon": ColorRange([1, 12], [30, 40], []),
    "Breadcrumb": ColorRange([1, 12], [10, 30], []),
    "Shadow": ColorRange([1, 12], [13, 23], [0x0, 0x1]),
}

HIDDEN_PROPERTIES = [
    "tab.border",
    "tab.activeBorder",
    "tab.unfocusedActiveBorder",
    "contrastActiveBorder",
    "editorGroup.border",
    "editorGroupHeader.border",
    "editorGroupHeader.tabsBorder",
    "editor.lineHighlightBorder",
    "scrollbar.shadow",
]

LIGHT_COLOR_LEVEL_MAP = {
    "59": [
        "activityBar.background",
        "statusBar.background",
        "titleBar.activeBackground",
    ],
    "58": ["menu.background"],
    "57": [
        "activityBar.activeBackground",
        "sideBar.background",
        "badge.foreground",
        "terminal.background",
        "panel.background",
        "sideBarSectionHeader.background",
        "editorGroupHeader.tabsBackground",
        "editorGroupHeader.noTabsBackground",
        "tileBackground",
        "minimap.background",
        "editorHoverWidget.background",
        "dropdown.background",
        "settings.dropdownBackground",
    ],
    "56": [
        "editor.background",
        "editorGutter.background",
        "editorGroup.emptyBackground",
        "notebook.cellEditorBackground",
        "notebook.editorBackground",
        "tab.inactiveBackground",
    ],
    "55": [
        "tab.border",
        "tab.hoverBorder",
        "tree.tableOddRowsBackground",
        "tileHoverBackground",
    ],
    "54": ["keybindingTable.rowsBackground", "activityBarBadge.foreground"],
    "52": ["tab.activeBackground", "breadcrumb.background"],
    "40": ["scrollbar.shadow"],
    "35": ["scrollbarSlider.background"],
    "30": ["scrollbarSlider.hoverBackground"],
    "25": ["scrollbarSlider.activeBackground"],
    "10": ["activityBarBadge.background", "badge.background"],
}

BASE_COLOR_LEVEL_MAP = {
    "11": [
        "activityBar.activeBackground",
        "activityBar.background",
        "activityBar.foreground",
        "activityBar.border",
        "breadcrumb.background",
        "breadcrumbPicker.background",
        "button.background",
        "commandCenter.background",
        "dropdown.background",
        "dropdown.listBackground",
        "editor.background",
        "editorGroup.emptyBackground",
        "editorGroupHeader.noTabsBackground",
        "editorGroupHeader.tabsBackground",
        "editorGutter.background",
        "editorHoverWidget.background",
        "editorInfo.background",
        "editorInlayHint.background",
        "editorOverviewRuler.foreground",
        "editorOverviewRuler.background",
        "editor.lineHighlightBackground",
        "editorLineNumber.foreground",
        "input.background",
        "titleBar.activeForeground",
        "menu.background",
        "menu.foreground",
        "minimap.background",
        "notebook.cellEditorBackground",
        "notebook.editorBackground",
        "notebook.focusedCellBackground",
        "notebook.selectedCellBackground",
        "notificationCenterHeader.background",
        "notifications.background",
        "panel.background",
        "panel.border",
        "panelSection.dropBackground",
        "panelSectionHeader.background",
        "panelSectionHeader.border",
        "quickInput.background",
        "quickInputTitle.background",
        "sideBar.background",
        "sideBar.foreground",
        "sideBar.border",
        "sideBar.dropBackground",
        "sideBarSectionHeader.background",
        "sideBarSectionHeader.border",
        "statusBar.background",
        "statusBar.border",
        "settings.checkboxBackground",
        "settings.dropdownBackground",
        "settings.focusedRowBackground",
        "settings.numberInputBackground",
        "settings.rowHoverBackground",
        "settings.textInputBackground",
        "tab.activeBackground",
        "tab.hoverBackground",
        "tab.inactiveBackground",
        "tab.unfocusedActiveBackground",
        "tab.unfocusedHoverBackground",
        "tab.unfocusedInactiveBackground",
        "terminal.foreground",
        "terminal.background",
        "terminal.dropBackground",
        "titleBar.activeBackground",
        "titleBar.border",
        "tree.tableOddRowsBackground",
        "widget.shadow",
    ]
}


def get_scopes(json_file):
    """Get scopes from the given json file which is VsCode theme file."""
    with open(json_file) as f:
        data = json.load(f)
        scopes = {}
        token_colors = data["tokenColors"]
        for token in token_colors:
            if "scope" in token:
                foreground = token.get("settings", {}).get("foreground", "#000000")
                token_scopes = token.get("scope", [])
                if isinstance(token_scopes, str):
                    token_scopes = token_scopes.split(" ")
                for token_scope in token_scopes:
                    scopes[token_scope] = foreground
            else:
                print("No scope in {}.".format(token))
    return scopes


def get_color_properties(theme_json_file):
    """Get color properties from the given json file which is VsCode theme file."""
    with open(theme_json_file) as f:
        data = json.load(f)
        color_properties = data["colors"].keys()
    return color_properties


def get_color_properties_by_suffix(color_properties, suffix):
    """Get color properties which ends with the given suffix."""
    color_properties_by_suffix = []
    for color_property in color_properties:
        if color_property.lower().endswith(suffix.lower()):
            color_properties_by_suffix.append(color_property)
    return color_properties_by_suffix


def get_color_properties_by_prefix(color_properties, prefix):
    """Get color properties which starts with the given suffix."""
    color_properties_by_prefix = []
    for color_property in color_properties:
        if color_property.lower().startswith(prefix.lower()):
            color_properties_by_prefix.append(color_property)
    return color_properties_by_prefix


def _create_high_priority_groups():
    priority_groups = []
    for prefix in HIGH_PRIORITY_GROUPS_PREFIXES:
        for group in GENERAL_GROUPS:
            priority_groups.append(prefix + group)

    return priority_groups


def group_color_properties(color_properties):
    """Group color properties by suffix."""
    _groups = {}

    # group by suffix
    # these are the basic groups, e.g. background, foreground, etc.
    basic_groups = ["foreground", "background", "border", "outline"]
    for color_property in color_properties:
        _splits = color_property.split(".")
        if len(_splits) > 1:
            suffix = _splits[-1]
            for _group in basic_groups:
                if suffix.lower().find(_group.lower()) != -1:
                    if _group not in _groups:
                        _groups[_group] = [color_property]
                    else:
                        _groups[_group].append(color_property)

    # group by prefix
    # these are the component groups, e.g. editor, list, etc.
    for color_property in color_properties:
        _splits = color_property.split(".")
        component = _splits[0]
        if component not in _groups:
            _groups[component] = [color_property]
        else:
            _groups[component].append(color_property)

    # high priority groups, e.g. activebackground, activeforeground, etc. are handled finally to override others
    high_priority_groups = _create_high_priority_groups()
    for color_property in color_properties:
        for _group_name in high_priority_groups:
            if color_property.lower() == (_group_name.lower()):
                suffix = _group_name
                if suffix not in _groups:
                    _groups[suffix] = [color_property]
                else:
                    _groups[suffix].append(color_property)

    return _groups


def group_scopes(scopes):
    """Group scopes by the prefix.

    Parameters:
    ----------
    scopes : dict[scope_name, foreground], e.g. {'scope 1': '#ff0000', 'scope 2': '#'}
    """
    scope_groups = {}
    for scope in scopes.keys():
        _splits = scope.split(".")
        if len(_splits) == 1:
            group_name = _splits[0]
        else:
            group_name = ".".join(_splits[0:2])

        if group_name not in scope_groups:
            scope_groups[group_name] = [scope]
        else:
            scope_groups[group_name].append(scope)
    return scope_groups


def create_color_range(group_name):
    """Create color range from the given color properties group.

    If the group name is not found, return None.

    Parameters:
    ----------
    group_name : str, e.g. "Background"

    Returns:
    str

    Examples:
    --------
    create_color_range("Background")
    """
    _default_color_range = (
        DEFAULT_BACKGROUND_COLOR_RANGE
        if group_name.lower().find("background") != -1
        else DEFAULT_FOREGROUND_COLOR_RANGE
        if group_name.lower().find("foreground") != -1
        else DEFAULT_BORDER_COLOR_RANGE
        if group_name.lower().find("border") != -1
        else DEFAULT_COLOR_RANGE
    )
    _color_range = _default_color_range
    for k, v in COLOR_RANGE_MAP.items():
        assert v not in DEFAULT_COLOR_RANGES, f"{k}'s value is in DEFAULT_COLOR_RANGES"
        if group_name.lower() == k.lower():
            _color_range = COLOR_RANGE_MAP[k]
            break
    # if didn't find the fully matched group, then try to use endswith or startswith
    if _color_range in DEFAULT_COLOR_RANGES:
        for k, v in COLOR_RANGE_MAP.items():
            if group_name.lower().endswith(k.lower()) or group_name.lower().startswith(
                k.lower()
            ):
                _color_range = COLOR_RANGE_MAP[k]
                break
    if (group_name.lower() in ["shadow", "list"]) and (
        _color_range in DEFAULT_COLOR_RANGES
    ):
        print(
            f"create_color_range({group_name}) = {_color_range} - defualt code range is used."
        )
    return _color_range


def _replace_light_level(color_placeholder, light_level):
    _splits = color_placeholder.split("_")
    _splits_replace_light_level = _splits[0:2]
    _splits_replace_light_level.append(str(light_level))
    return "_".join(_splits_replace_light_level)


def _replace_base_color(color_placeholder, base_color):
    if not re.match(PLACEHOLDER_REGEX, color_placeholder):
        return color_placeholder
    else:
        _splits = color_placeholder.split("_")
        return "_".join([_splits[0], base_color, _splits[2]])


def _get_theme_base_color(color_placeholder_groups):
    """Return base color for background groups.

    Go through the color_placeholder_groups and get the base color of the group "bg".

    Parameters:
    ----------
    color_placeholder_groups : dict["group_name", ["color_placeholder"]], e.g. {
        "bg": ["C_11_59"],
    }
    """
    return color_placeholder_groups["bg"][0].split("_")[1]


def define_colors_for_background_properties(color_properties):
    colors = {}
    for color_property in color_properties:
        colors[color_property] = _get_color(color_property)
    return colors


def get_color_config():
    config_path = f"{os.getcwd()}/config.json"
    return ColorConfig(config_path)


def define_colors():
    color_config = get_color_config()
    template_json_file = f"{os.getcwd()}/themes/viiv-color-theme.template.json"
    template_data = json.load(open(template_json_file))
    all_color_properties = get_color_properties(template_json_file)
    theme_base_color = "11"
    colors = {}
    color_properties_group = group_color_properties(all_color_properties)
    color_properties_use_default_range = []
    color_group_and_color_placeholders = {}
    for group_name, color_properties in color_properties_group.items():
        color = color_config.get_color(group_name)
        if color == color_config.default_color:
            color_range = create_color_range(group_name)
            color_placeholders = create_color_placeholders(color_range)
        else:
            color_placeholders = color.create_colors()

        color_group_and_color_placeholders[group_name] = color_placeholders
        color_placeholders = random.sample(
            color_placeholders, min(len(color_placeholders), len(color_properties))
        )

        for i, color_property in enumerate(color_properties):
            if color_property in CUSTOMIZED_COLOR_PLACEHOLDERS:
                color_placeholder = CUSTOMIZED_COLOR_PLACEHOLDERS[color_property]
                colors[color_property] = color_placeholder
                continue
            if (color_range in DEFAULT_COLOR_RANGES) and (color_property in colors):
                continue
            if color_range in DEFAULT_COLOR_RANGES:
                color_properties_use_default_range.append({color_property: group_name})
            if color_property in HIDDEN_PROPERTIES:
                color_placeholder = "#00000000"
            else:
                color_placeholder = color_placeholders[i % len(color_placeholders)]
                # try to extract the alpha value from the old color placeholder
                if color_property in colors:
                    _old_color_placeholder = colors[color_property]
                    if re.match(
                        PLACEHOLDER_REGEX_WITH_ALPHA, _old_color_placeholder
                    ) and not re.match(PLACEHOLDER_REGEX_WITH_ALPHA, color_placeholder):
                        color_placeholder = (
                            f"{color_placeholder}{_old_color_placeholder[-2:]}"
                        )

                for k, v in BASE_COLOR_LEVEL_MAP.items():
                    if color_property in v:
                        color_placeholder = _replace_base_color(color_placeholder, k)

                for k, v in LIGHT_COLOR_LEVEL_MAP.items():
                    if color_property in v:
                        color_placeholder = _replace_light_level(color_placeholder, k)
            if group_name.lower() == "inactiveforeground":
                print(f"group {group_name}, {color_property} = {color_placeholder}")
            colors[color_property] = color_placeholder

    template_data["colors"] = dict(sorted(colors.items(), key=lambda x: x[0]))
    json.dump(
        color_properties_group,
        open(os.getenv("USERPROFILE") + r"\Downloads\color_properties_group.json", "w"),
        indent=4,
        sort_keys=True,
    )
    json.dump(
        color_group_and_color_placeholders,
        open(
            os.getenv("USERPROFILE")
            + r"\Downloads\color_group_and_color_placeholders.json",
            "w",
        ),
        indent=4,
        sort_keys=True,
    )
    json.dump(
        color_properties_use_default_range,
        open(
            os.getenv("USERPROFILE")
            + r"\Downloads\color_properties_use_default_range.json",
            "w",
        ),
        indent=4,
        sort_keys=True,
    )
    json.dump(template_data, open(template_json_file, "w"), indent=4, sort_keys=True)
    return color_properties_group


def create_color_placeholder(i, j):
    if i < 10:
        i = "0" + str(i)
    if j < 10:
        j = "0" + str(j)
    return f"C_{i}_{j}"


def create_color_placeholders(color_range):
    """Create color placeholders.
    olor placeholder value format "C_[0-9]{2}_[0-9]{2}",
    """
    assert (
        isinstance(color_range, ColorRange) and color_range.is_valid()
    ), f"Invalid arguments: {color_range}"
    color_placeholders = []
    base_color_range = color_range.base_color_range
    light_level_range = color_range.light_level_range
    alpha_range = color_range.alpha_range
    for i in range(base_color_range[0], base_color_range[1]):
        _placeholder = ""
        if i < 10:
            i = "0" + str(i)
        for j in range(light_level_range[0], light_level_range[1]):
            if j < 10:
                j = "0" + str(j)
            i = str(i)
            j = str(j)
            _placeholder = f"C_{i}_{j}"
            if alpha_range is not None and len(alpha_range) > 0:
                for _k in range(alpha_range[0], alpha_range[1]):
                    k = format(_k, "x")
                    if len(k) == 1:
                        k = "0" + str(k)
                    _placeholder = f"C_{i}_{j}{k}"
                    color_placeholders.append(_placeholder)
            else:
                color_placeholders.append(_placeholder)

    return color_placeholders


def define_token_colors(
    scopes=None, base_colors_range=[1, 12], light_level_range=[14, 23]
):
    """for each scope, set its foreground

    Example.
    {
        "scope": ["scope 1", "scope 2"],
        settings: {
            "foreground": "#ff0000"
        }
    }

    Parameters
    ----------
    scope_groups : dict
    base_colors_range : list, not includ the 2nd value.
    light_level_range : list, not includ the 2nd value.
    """
    # if not passed scope_groups, then read from json file
    template_json_file = f"{os.getcwd()}/themes/viiv-color-theme.template.json"
    if not os.path.exists(template_json_file):
        print(f"Template json file {template_json_file} does not exist.")
        return None
    template_json = json.load(open(template_json_file))
    if not scopes:
        scopes = get_scopes(template_json_file)
        print(f"Read {len(scopes)} scopes from json file {template_json_file}.")
    scope_groups = group_scopes(scopes)
    print(scope_groups.keys())

    token_colors = []
    # assign random base colors to scope groups, assign random light colors to scopes in scope group
    base_colors_total = base_colors_range[1] - base_colors_range[0]
    base_color_samples = random.sample(
        range(base_colors_range[0], base_colors_range[1]),
        base_colors_total
        if len(scope_groups) > base_colors_total
        else len(scope_groups),
    )

    for i, scope_group in enumerate(scope_groups):
        base_color_index = base_color_samples[i % len(base_color_samples)]
        light_level_total = light_level_range[1] - light_level_range[0]
        light_color_samples = random.sample(
            range(light_level_range[0], light_level_range[1]),
            light_level_total
            if len(scope_groups[scope_group]) > light_level_total
            else len(scope_groups[scope_group]),
        )

        for j, scope in enumerate(scope_groups[scope_group]):
            light_color_index = light_color_samples[j % len(light_color_samples)]
            color_placeholder = create_color_placeholder(
                base_color_index, light_color_index
            )
            _old_foreground = scopes[scope]
            _placeholder_regex = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}"
            _placeholder_with_alpha_regex = (
                r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}[a-zA-Z0-9]{2,}"
            )
            _foreground = re.sub(_placeholder_regex, color_placeholder, _old_foreground)
            _foreground = re.sub(
                _placeholder_with_alpha_regex, color_placeholder, _foreground
            )
            # if not re.match(_placeholder_with_alpha_regex, _old_foreground):
            #    _foreground = f"{_foreground}"
            for _scope_prefix in ["comment", "docstring", "punctuation", "javadoc"]:
                if scope.find(_scope_prefix) != -1:
                    # set base color as dark color
                    _foreground = re.sub(r"C_[a-zA-Z0-9]{2}", "C_11", _foreground)
                    if True:
                        if not re.match(_placeholder_with_alpha_regex, _old_foreground):
                            _foreground = f"{_foreground}70"
                    else:
                        if re.match(_placeholder_with_alpha_regex, _old_foreground):
                            _foreground = re.sub(
                                _placeholder_with_alpha_regex,
                                color_placeholder,
                                _foreground,
                            )
                    break

            scope_settings = {
                "scope": scope,
                "settings": {
                    "foreground": _foreground,
                },
            }
            token_colors.append(scope_settings)

    template_json["tokenColors"] = token_colors
    json.dump(template_json, open(template_json_file, "w"), indent=4, sort_keys=True)
    return token_colors


def print_colors(value):
    dynamic_theme_json_file = f"{os.getcwd()}/themes/dynamic-color-theme.json"
    dynamic_theme_json = json.load(open(dynamic_theme_json_file))
    theme_template_json_file = f"{os.getcwd()}/themes/viiv-color-theme.template.json"
    theme_template_json = json.load(open(theme_template_json_file))
    colors = dynamic_theme_json["colors"]
    for k, v in colors.items():
        if k.lower().find(value) != -1:
            print(pe.bg(v, f"{k}: {v} ({theme_template_json['colors'][k]})"))


if __name__ == "__main__":
    opts, _ = getopt.getopt(
        sys.argv[1:],
        "cg:tp:",
        ["--colors", "--token_colors", "--print_colors=", "--group_name="],
    )
    for option, value in opts:
        if option in ("-c", "--colors"):
            # define_colors()
            TemplateConfig().regenerate_template_colors()
        elif option in ("-t", "--token_colors"):
            define_token_colors(light_level_range=[0, 30], base_colors_range=[1, 10])
        elif option in ("-p", "--print_colors"):
            print_colors(value)
        elif option in ("-g", "--group_name"):
            color_range = create_color_range(value)
            color_placeholders = create_color_placeholders(color_range)
            print(color_range, color_placeholders)


color_1 = {
    "basic_range": [11, 12],
    "light_range": [59, 60],
    "alpha_range": ["0x99", "0xcc"],
}

color_2 = {"hex": "#0f6f99", "alpha_range": ["0x99", "0xcc"]}


#config_path = f"{os.getcwd()}/config.json"
#color_config = ColorConfig(config_path)
#color = color_config.get_color("activeBorder")
#print(color.create_colors())
#color = color_config.get_color("error")
#print(color.create_colors())

template_config_path = f"{os.getcwd()}/themes/viiv-color-theme.template.json"
config = TemplateConfig(template_config_path)
config.regenerate_template_colors()
