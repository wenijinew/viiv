#!/usr/bin/env python
"""Functions to help quickly generate customized token colors in VsCode theme file."""

import getopt
import json
import os
import random
import re
import sys
from peelee import peelee as pe

PLACEHOLDER_REGEX = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}"
PLACEHOLDER_WITH_ALPHA_REGEX = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}[a-zA-Z0-9]{2}"


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


GENERAL_GROUPS = ["background", "foreground", "border", "outline"]
HIGH_PRIORITY_GROUPS_PREFIXES = [
    "active",
    "inactive",
    "hover",
    "match",
    "focus",
    "highlight",
    "highlighttext",
    "highlightstrong",
    "focushighlight",
    "selection",
    "header",
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
    "terminal.ansiBlue": "#2f2841",
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

# more specific, topper
COLOR_RANGE_MAP = {
    "Foreground": ColorRange([1, 12], [15, 20], []),
    "Background": ColorRange([1, 12], [55, 57], []),
    "Border": ColorRange([1, 12], [45, 50], [0x73, 0x93]),
    "Outline": ColorRange([1, 12], [45, 50], [0x30, 0x60]),
    "Highlight": ColorRange([1, 12], [30, 35], [0x30, 0x40]),
    "Stroke": ColorRange([1, 12], [35, 40], [0x60, 0x90]),
    "Shadow": ColorRange([1, 12], [44, 54], []),
    "Panel": ColorRange([1, 12], [50, 53], []),
    "Tree": ColorRange([1, 12], [50, 55], [0x30, 0x40]),
    "Icon": ColorRange([1, 12], [30, 40], []),
    "Breadcrumb": ColorRange([1, 12], [10, 30], []),
    "EditorOverviewRuler": ColorRange([1, 12], [15, 45], [0x35, 0x45]),
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
    "StatusBarBackground": ColorRange([1, 12], [55, 60], []),
    "ActiveBackground": ColorRange([1, 12], [40, 47], [0x99, 0xcc]),
    "ActiveForeground": ColorRange([1, 12], [0, 30], [0xcc, 0xff]),
    "ActiveBorder": ColorRange([1, 12], [40, 45], []),
    "ActiveOutline": ColorRange([1, 12], [40, 45], []),
    "InactiveBackground": ColorRange([1, 12], [57, 60], [0x39, 0x69]),
    "InactiveForeground": ColorRange([1, 12], [15, 19], []),
    "InactiveBorder": ColorRange([1, 12], [50, 55], [0x30, 0x40]),
    "InactiveOutline": ColorRange([1, 12], [50, 55], [0x30, 0x40]),
    "HoverBackground": ColorRange([1, 12], [40, 45], [0x43, 0x47]),
    "HoverForeground": ColorRange([1, 12], [5, 10], []),
    "HoverBorder": ColorRange([1, 12], [35, 40], []),
    "HoverOutline": ColorRange([1, 12], [36, 42], []),
    "MatchBackground": ColorRange([1, 12], [33, 42], [0x30, 0x40]),
    "MatchForeground": ColorRange([1, 12], [13, 23], [0x30, 0x40]),
    "MatchBorder": ColorRange([1, 12], [31, 41], [0x30, 0x40]),
    "MatchOutline": ColorRange([1, 12], [33, 43], [0x30, 0x40]),
    "HeaderBackground": ColorRange([1, 12], [51, 56], []),
    "HighlightBackground": ColorRange([1, 12], [28, 38], [0x30, 0x40]),
    "HighlightForeground": ColorRange([1, 12], [8, 18], []),
    "HighlightBorder": ColorRange([1, 12], [14, 24], [0x20, 0x40]),
    "HighlightOutline": ColorRange([1, 12], [13, 23], [0x30, 0x40]),
    "HighlightStrongBackground": ColorRange([1, 12], [15, 25], [0x20, 0x30]),
    "HighlightStrongForeground": ColorRange([1, 12], [23, 33], [0x60, 0x90]),
    "HighlightStrongBorder": ColorRange([1, 12], [23, 33], [0x90, 0xff]),
    "HighlightTextBackground": ColorRange([1, 12], [37, 47], [0x30, 0x40]),
    "HighlightTextBorder": ColorRange([1, 12], [18, 28], [0x30, 0x40]),
    "FocusHighlightBackground": ColorRange([1, 12], [37, 47], [0x30, 0x40]),
    "FocusHighlightForeground": ColorRange([1, 12], [6, 16], [0x30, 0x40]),
    "FocusHighlightBorder": ColorRange([1, 12], [26, 36], [0x30, 0x40]),
    "FocusHighlightOutline": ColorRange([1, 12], [11, 21], [0x30, 0x40]),
    "SelectionBackground": ColorRange([1, 12], [39, 49], [0x33, 0x66]),
    "SelectionForeground": ColorRange([1, 12], [7, 17], []),
    "SelectionBorder": ColorRange([1, 12], [19, 29], [0x30, 0x40]),
    "SelectionOutline": ColorRange([1, 12], [13, 23], [0x30, 0x40]),
    "Other": DEFAULT_BACKGROUND_COLOR_RANGE,
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
        "sideBar.background",
        "sideBar.foreground",
        "sideBar.border",
        "sideBar.dropBackground",
        "sideBarSectionHeader.background",
        "sideBarSectionHeader.border",
        "statusBar.background",
        "statusBar.border",
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
        "widget.shadow"
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
    # these are most general groups, e.g. background, foreground, etc.
    for color_property in color_properties:
        _splits = color_property.split(".")
        if len(_splits) > 1:
            group_name = _splits[-1]
            if group_name not in _groups:
                _groups[group_name] = [color_property]
            else:
                _groups[group_name].append(color_property)

    # group by prefix, they are more specific
    for color_property in color_properties:
        _splits = color_property.split(".")
        group_name = _splits[0]
        if group_name not in _groups:
            _groups[group_name] = [color_property]
        else:
            _groups[group_name].append(color_property)

    # high priority groups, e.g. activebackground, activeforeground, etc. are handled finally to override others
    high_priority_groups = _create_high_priority_groups()
    for color_property in color_properties:
        for _group_name in high_priority_groups:
            if color_property.lower().endswith(_group_name.lower()):
                group_name = _group_name
                if group_name not in _groups:
                    _groups[group_name] = [color_property]
                else:
                    _groups[group_name].append(color_property)

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


def _create_color_range(group_name):
    """Create color range from the given color properties group.

    If the group name is not found, return None.

    Parameters:
    ----------
    group_name : str, e.g. "Background"

    Returns:
    str

    Examples:
    --------
    _create_color_range("Background")
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
    for k in COLOR_RANGE_MAP.keys():
        if group_name.lower() == k.lower():
            _color_range = COLOR_RANGE_MAP[k]
            break
    return _color_range


def _replace_light_level(color_placeholder, light_level):
    _splits = color_placeholder.split("_")
    _splits_replace_light_level = _splits[0:2]
    _splits_replace_light_level.append(str(light_level))
    return "_".join(_splits_replace_light_level)


def _replace_base_color(color_placeholder, base_color):
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


def define_colors():
    template_json_file = f"{os.getcwd()}/themes/viiv-color-theme.template.json"
    template_data = json.load(open(template_json_file))
    all_color_properties = get_color_properties(template_json_file)
    theme_base_color = "11"
    colors = {}
    color_properties_group = group_color_properties(all_color_properties)
    color_properties_use_default_range = []
    color_group_and_color_placeholders = {}
    for group_name, color_properties in color_properties_group.items():
        color_range = _create_color_range(group_name)
        color_placeholders = _create_color_placeholders(color_range)

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
                        PLACEHOLDER_WITH_ALPHA_REGEX, _old_color_placeholder
                    ) and not re.match(PLACEHOLDER_WITH_ALPHA_REGEX, color_placeholder):
                        color_placeholder = (
                            f"{color_placeholder}{_old_color_placeholder[-2:]}"
                        )

                for k, v in BASE_COLOR_LEVEL_MAP.items():
                    if color_property in v:
                        color_placeholder = _replace_base_color(color_placeholder, k)

                for k, v in LIGHT_COLOR_LEVEL_MAP.items():
                    if color_property in v:
                        color_placeholder = _replace_light_level(color_placeholder, k)

            colors[color_property] = color_placeholder

    template_data["colors"] = dict(sorted(colors.items(), key=lambda x: x[0]))
    json.dump(
        color_properties_group,
        open(os.getenv("USERPROFILE") + r"\Downloads\color_properties_group.json", "w"),
    )
    json.dump(
        color_group_and_color_placeholders,
        open(
            os.getenv("USERPROFILE")
            + r"\Downloads\color_group_and_color_placeholders.json",
            "w",
        ),
    )
    json.dump(
        color_properties_use_default_range,
        open(
            os.getenv("USERPROFILE")
            + r"\Downloads\color_properties_use_default_range.json",
            "w",
        ),
    )
    json.dump(template_data, open(template_json_file, "w"))
    return color_properties_group


def _create_color_placeholder(i, j):
    if i < 10:
        i = "0" + str(i)
    if j < 10:
        j = "0" + str(j)
    return f"C_{i}_{j}"


def _create_color_placeholders(color_range):
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
            color_placeholder = _create_color_placeholder(
                base_color_index, light_color_index
            )
            _old_foreground = scopes[scope]
            _placeholder_regex = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}"
            _placeholder_with_alpha_regex = (
                r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}[a-zA-Z0-9]{2,}"
            )
            _foreground = re.sub(_placeholder_regex, color_placeholder, _old_foreground)
            _foreground = re.sub(_placeholder_with_alpha_regex, color_placeholder, _foreground)
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
                                _placeholder_with_alpha_regex, color_placeholder, _foreground)    
                    break

            scope_settings = {
                "scope": scope,
                "settings": {
                    "foreground": _foreground,
                },
            }
            token_colors.append(scope_settings)

    template_json["tokenColors"] = token_colors
    json.dump(template_json, open(template_json_file, "w"))
    return token_colors


def print_colors(value):
    template_json_file = f"{os.getcwd()}/themes/dynamic-color-theme.json"
    template_json = json.load(open(template_json_file))
    colors = template_json["colors"]
    for k, v in colors.items():
        if k.lower().find(value) != -1:
            print(f"{k}: {v}")
            print(pe.bg(v, f"{k}: {v}"))


if __name__ == "__main__":
    opts, _ = getopt.getopt(
        sys.argv[1:],
        "ctp:",
        [
            "--colors",
            "--token_colors",
            "--print_colors="
        ],
    )
    for option, value in opts:
        if option in ("-c", "--colors"):
            define_colors()
        elif option in ("-t", "--token_colors"):
            define_token_colors(light_level_range=[0, 30], base_colors_range=[1, 10])
        elif option in ("-p", "--print_colors"):
            print_colors(value)
