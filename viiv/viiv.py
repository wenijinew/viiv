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

# reserved constants
TOKEN_COLOR_PREFIX = "T_"
WORKBENCH_COLOR_PREFIX = "W_"
PLACEHOLDER_REGEX = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2,4}"
PLACEHOLDER_REGEX_WITHOUT_ALPHA = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}"
PLACEHOLDER_REGEX_WITH_ALPHA = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}[a-zA-Z0-9]{2}"
RGB_HEX_REGEX = r"#[a-zA-Z0-9]{6,8}"
RGB_HEX_REGEX_WITHOUT_ALPHA = r"#[a-zA-Z0-9]{6}"
RGB_HEX_REGEX_WITH_ALPHA = r"#[a-zA-Z0-9]{8}"


HEX_NUMBER_STR_PATTERN = re.compile(r"^0x[0-9a-zA-Z]+$")

# debug
DEBUG_PROPERTY = []
DEBUG_GROUP = []

THEME_TEMPLATE_JSON_FILE = f"{os.getcwd()}/templates/viiv-color-theme.template.json"
PALETTE_FILE_PATH = f"{os.getcwd()}/output/random-palette.json"
SELECTED_UI_COLOR_FILE_PATH = f"{os.getcwd()}/output/selected-ui-palette.json"
SELECTED_TOKEN_COLOR_FILE_PATH = f"{os.getcwd()}/output/selected-token-palette.json"


def load_json_file(json_file_path):
    """
    Loads the JSON file at the specified path.
    """
    with open(json_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
        return json_data


class ColorComponent(Enum):
    """
    Enum representing different components of a color.

    The enum includes the following values:
        - BASIC: Represents the basic color components (red, green, blue).
        - LIGHT: Represents the components of a lighter version of the color (light red, light green, light blue).
        - ALPHA: Represents the alpha component of the color.
        - ALL: Represents all components of the color.

    Example usage:
        If you want to access the basic color component of a color object:
            color = (255, 128, 0, 255)  # represents a fully opaque orange color
            red_component = color[ColorComponent.BASIC.value]  # returns 255, the value of the red component
    """

    BASIC = 1
    LIGHT = 2
    ALPHA = 3
    ALL = 4


class MatchRule(Enum):
    """Match rule for color range."""

    EXACT = 1
    ENDSWITH = 2
    STARTSWITH = 3
    CONTAINS = 4
    FUZZY = 5


def _to_int(value: str) -> int:
    """Convert string to int."""
    if isinstance(value, int):
        return value
    elif isinstance(value, str) and (HEX_NUMBER_STR_PATTERN.match(value)):
        return int(value, 16)
    return int(value)


def is_property_area(area):
    """Check if the current theme is a property area."""
    return area in ["background", "foreground"]


def normalize_range(range_values: list[str]) -> list[str]:
    """Generate random numbers in string format with the given range values.
    if the random number is less than 10, then add a 0 before the number.

    Example:
    _random_range([1, 12])
    -> ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    """
    _random = []
    _start = _to_int(range_values[0])
    _end = _to_int(range_values[1])
    for i in range(_start, _end):
        _random.append(str(i) if i >= 10 else str("0" + str(i)))
    return _random


class ColorsWrapper(dict):
    """Wrapper class for color."""

    def __init__(
        self,
        colors: list,
        area: str,
        group: str,
        replace_color_component: list = None,
    ):
        self.colors = colors
        self.area = area
        self.group = group
        self.replace_color_component = replace_color_component or [ColorComponent.ALL]
        super().__init__(
            colors=colors,
            group=group,
            area=area,
            replace_color_component=replace_color_component,
        )


class ColorConfig(dict):
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

    def __init__(
        self,
        config,
        area,
        group,
        replace_color_component: list(ColorComponent) = None,
    ):
        self.config = config
        self.area = area
        self.group = group
        self.replace_color_component = replace_color_component or [ColorComponent.ALL]
        self.hex = config.get("hex", None)
        self.alpha_range = config.get("alpha_range", None)
        self.basic_range = config.get("basic_range", None)
        self.light_range = config.get("light_range", None)
        super().__init__(config=self.config)

    def __repr__(self):
        return f"Color({self.config})"

    def create_colors_wrapper(self) -> ColorsWrapper:
        """Generate colors by using hex or basic and light ranges."""
        has_hex = self.hex is not None
        has_alpha = (
            self.alpha_range is not None
            and len(self.alpha_range) == 2
            and self.alpha_range[0] < self.alpha_range[1]
        )
        has_basic = (
            self.basic_range is not None
            and len(self.basic_range) == 2
            and self.basic_range[0] < self.basic_range[1]
        )
        has_light = (
            self.light_range is not None
            and len(self.light_range) == 2
            and self.light_range[0] < self.light_range[1]
        )

        if has_hex:
            _head = [self.hex]
        elif has_basic and has_light:
            _head = [
                "C_" + basic + "_" + light
                for basic in normalize_range(self.basic_range)
                for light in normalize_range(self.light_range)
            ]
        else:
            _head = ["#000000"]

        if has_alpha:
            _tail = []
            for alpha in normalize_range(self.alpha_range):
                alpha = format(int(alpha), "x")
                if len(alpha) == 1:
                    alpha = "0" + alpha
                _tail.append(alpha)
        else:
            _tail = [""]
        _colors = [f"{head}{tail}" for head in _head for tail in _tail]

        _wrapper = ColorsWrapper(
            _colors, self.area, self.group, self.replace_color_component
        )
        return _wrapper


class Config(dict):
    """Wrapper class for color config

    Read and parse config.json file located in the current directory.
    """

    def __init__(self, config_path=None):
        """Read config.json file and initialize."""
        if config_path is None:
            config_path = f"{os.getcwd()}/config.json"
        self.config_path = config_path
        self.config = load_json_file(config_path)
        self.areas = list(
            filter(lambda k: k not in ["options", "themes"], self.config.keys())
        )
        # default color config and token default color config
        default_color_config = list(
            filter(
                lambda x: "default" in x["groups"],
                self.config["default"],
            )
        )[0]
        default_token_color_config = list(
            filter(
                lambda x: len(x["groups"]) == 1 and x["groups"][0] == "token_default",
                self.config["token"],
            )
        )[0]
        self.default_color_config = ColorConfig(
            default_color_config["color"], "default", default_color_config["groups"][0]
        )
        self.default_token_color_config = ColorConfig(
            default_token_color_config["color"],
            "token",
            default_token_color_config["groups"][0],
        )
        self.options = self.config["options"]
        self.random_decoration_color = self.options.get(
            "random_decoration_color", False
        )
        self.random_decoration_color_basic_range = self.options.get(
            "random_decoration_color_basic_range", [1, 11]
        )
        self.static_decoration_color_basic_range = self.options.get(
            "static_decoration_color_basic_range", [1, 11]
        )
        # decoration groups
        self.decoration_groups = []
        for area in self.areas:
            for color_config in self.config[area]:
                groups = color_config["groups"]
                if "decoration" in groups:
                    self.decoration_groups.extend(groups)

        # random base range for decoration groups
        if self.random_decoration_color:
            random_int = random.randint(
                self.random_decoration_color_basic_range[0],
                self.random_decoration_color_basic_range[1],
            )
            self.basic_range_for_decoration_groups = [random_int, random_int + 1]
        else:
            self.basic_range_for_decoration_groups = (
                self.static_decoration_color_basic_range
            )

        super().__init__(
            config=self.config,
            areas=self.areas,
            default_color=self.default_color_config,
            default_token_color=self.default_token_color_config,
            decoration_groups=self.decoration_groups,
        )

    def get_discard_red_dark_color(self):
        """Return value of the option 'discard_dark_red_color'."""
        return self.options["discard_dark_red_color"]

    def get_color_wrappers(self, target_property, target_area=None) -> list:
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

        Parameters:
            target (str): target group or target color perperty


        Retrun :
            Color object include area info, only those color perperty belong to that area can use that color. Color for backkground cannot be used by foreground color perperty.
            If not found, return the default color.
        """
        _matched_color_configs = []
        for area in self.areas:
            if target_area and area != target_area:
                continue
            if is_property_area(area) and target_property.lower().find(area) == -1:
                continue
            # try to find the configured color in the matching order
            _matched_color_config_dict = self._get_color(area, target_property)
            if (
                _matched_color_config_dict
                and _matched_color_config_dict not in _matched_color_configs
            ):
                _matched_color_configs.append(_matched_color_config_dict)

        color_wrappers = []
        if _matched_color_configs:
            if target_property in DEBUG_PROPERTY:
                print(_matched_color_configs)

            default_area_matched_color_configs = list(
                filter(lambda x: x["area"] == "default", _matched_color_configs)
            )
            if default_area_matched_color_configs:
                _matched_color_configs = default_area_matched_color_configs

            # clever cost?
            most_matched_color_config = min(
                (
                    c
                    for c in list(
                        filter(
                            lambda c: c["color_config"] is not None,
                            _matched_color_configs,
                        )
                    )
                ),
                key=lambda x: x["match_rule"].value,
            )

            if most_matched_color_config:
                color_wrappers.append(
                    most_matched_color_config["color_config"].create_colors_wrapper()
                )

        if len(color_wrappers) > 0:
            if target_property in DEBUG_PROPERTY:
                print([c.area for c in color_wrappers])
            return color_wrappers
        if target_area is None or target_area != "token":
            color_wrappers.append(self.default_color_config.create_colors_wrapper())
        else:
            color_wrappers.append(
                self.default_token_color_config.create_colors_wrapper()
            )
        assert (
            len(color_wrappers) > 0
        ), f"no color found ({target_property} - {target_area})"
        return color_wrappers

    def _match(self, groups, target_property):
        """Match the target property with the group.

        By using all MatchRules to check if the target property matches any group in the groups.
        If multiple groups matched the target property, then pick up the one using match rule having the least value(which means highest priority).

        Parameters:
            group (str): group name
            target_property (str): target property

        Returns:
            dict: the matched group and the matched rule

            Example of the return value:
                {
                    "match_rule": MatchRule.FUZZY,
                    "group": "success"
                }
        """
        matched_groups = []
        for match_rule in MatchRule:
            for group in groups:
                if (
                    match_rule == MatchRule.EXACT
                    and target_property.lower() == group.lower()
                    or match_rule == MatchRule.ENDSWITH
                    and target_property.lower().endswith(f".{group.lower()}")
                    or match_rule == MatchRule.STARTSWITH
                    and target_property.lower().startswith(f"{group.lower()}.")
                    or match_rule == MatchRule.CONTAINS
                    and target_property.lower().find(group.lower()) != -1
                    or match_rule == MatchRule.FUZZY
                    and re.match(group, target_property, re.IGNORECASE)
                ):
                    matched_groups.append({"match_rule": match_rule, "group": group})
        if not matched_groups:
            return None

        if target_property in DEBUG_PROPERTY:
            print(matched_groups)

        return min(matched_groups, key=lambda x: x["match_rule"].value)

    def _get_replace_color_component(self, area, groups_config):
        """Get the replace color component.

        replace_color_component is a list of ColorComponent. it's an optional property of the groups config. by default, for all areas except for 'default', it's set to [ColorComponent.ALL] and for 'default' area, it's set to [ColorComponent.ALPHA].
        """
        replace_color_component = groups_config.get("replace_color_component")
        if replace_color_component is not None and isinstance(
            replace_color_component, list
        ):
            replace_color_component = [
                ColorComponent[_component] for _component in replace_color_component
            ]
        else:
            replace_color_component = (
                [ColorComponent.ALL] if area != "default" else [ColorComponent.ALPHA]
            )
        return replace_color_component

    def _get_color(self, area, target_property) -> dict:
        """Get the color config.

        Each area has many color configurations for different groups.
        Each group could match one or many different color properties.
        By going through all color configurations in the given area,
        and then check if any group in each color configuration matched
        the target property by using different matching rules.
        Finally, if multiple groups matched the target property,
        then pick up the one using match rule having the least matching
        rule value (which means highest priority).
        If no any group matched the target property,
        then return None which means there is no color config matching
        the target property in this area. For example, 'background' area
        cannot have any color config to match 'activityBar.foreground'.

        Matching rule will be returned also. Then if many areas have matched
        color config for the target property, then pick up the one with
        the least matching rule. If the same, then print warning for duplicated
        configuration and pickup the first one.

        Parameters:

            area (str): area name
            target_property (str): target property

        Returns:
            dict: the matched group and the matched rule
        """
        area_config = self.config[area]
        _matches = []
        for groups_config in area_config:
            enabled = groups_config.get("enabled", True)
            if not enabled:
                continue
            groups = groups_config["groups"]
            groups.sort(reverse=True)
            _match = self._match(groups, target_property)
            if _match:
                color = groups_config["color"]
                replace_color_component = self._get_replace_color_component(
                    area, groups_config
                )
                _match["color"] = color
                _match["replace_color_component"] = replace_color_component
                _matches.append(_match)

        if not _matches:
            return {}

        _most_matched_config = min(_matches, key=lambda x: x["match_rule"].value)
        color = _most_matched_config["color"]
        group = _most_matched_config["group"]

        # decoration groups use unified basic range which is random but unique
        if group in self.decoration_groups:
            color["basic_range"] = self.basic_range_for_decoration_groups

        replace_color_component = _most_matched_config["replace_color_component"]
        color_config = ColorConfig(color, area, group, replace_color_component)
        return {
            "color_config": color_config,
            "match_rule": _most_matched_config["match_rule"],
            "area": area,
        }


config = Config()


class TemplateConfig(dict):
    """Wrapper class for template config."""

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = THEME_TEMPLATE_JSON_FILE
        self.config_path = config_path
        self.config = load_json_file(config_path)
        self.color_properties = list(self.config["colors"].keys())
        super().__init__(config_path=config_path)

    def append_or_replace_alpha(self, old_color, new_color, component: ColorComponent):
        """
        Append or replace the alpha component of a color.

        Args:
            old_color (str): The original color string.
            new_color (str): The new color string.
            component (ColorComponent): The color component to be replaced or appended.

        Returns:
            str: The updated color string.

        """
        if component == ColorComponent.ALPHA:
            _color = old_color[0:7] + new_color[7:9]
        elif re.match(RGB_HEX_REGEX, old_color):
            # if it's already RGB HEX color, then cannot replace basic and light color with color placeholder. so, return directly
            return old_color
        elif component == ColorComponent.LIGHT:
            _color = old_color[0:5] + new_color[5:7] + old_color[7:]
        elif component == ColorComponent.BASIC:
            _color = old_color[0:2] + new_color[2:5] + old_color[5:]

        return _color

    def generate_template(self, config: Config = None):
        """
        Generates a template based on the provided configuration.

        Args:
            config (Config, optional): The configuration object. Defaults to None.

        Returns:
            None
        """
        if config is None:
            _color_config_path = f"{os.getcwd()}/config.json"
            config = Config(config_path=_color_config_path)

        workbench_colors = {}
        default_processed_properties = []
        customized_properties = []
        # workbench colors
        used_groups = []
        for property_name in self.color_properties:
            color_wrappers = config.get_color_wrappers(property_name)
            if color_wrappers is None or not isinstance(color_wrappers, list):
                print(property_name, type(color_wrappers))
                continue
            color_wrappers_areas = [w.area for w in color_wrappers]
            if (
                property_name in default_processed_properties
                and "default" not in color_wrappers_areas
            ):
                continue
            debug_property_counter = 0
            debug_group_counter = 0
            for wrapper in color_wrappers:
                colors = wrapper.colors
                replace_color_component = wrapper.replace_color_component
                group = wrapper.group
                area = wrapper.area
                # we are not processing the token color here
                if area == "token":
                    continue
                color = colors[random.randint(0, len(colors) - 1)]
                color_orig = color
                if property_name in workbench_colors:
                    if property_name in customized_properties:
                        continue
                    if area not in ["default", "token"]:
                        continue
                    old_color = workbench_colors[property_name]
                    _changed = False
                    if ColorComponent.BASIC in replace_color_component:
                        color = self.append_or_replace_alpha(
                            old_color if not _changed else color,
                            color_orig,
                            ColorComponent.BASIC,
                        )
                        _changed = True
                    if ColorComponent.LIGHT in replace_color_component:
                        color = self.append_or_replace_alpha(
                            old_color if not _changed else color,
                            color_orig,
                            ColorComponent.LIGHT,
                        )
                        _changed = True
                    if ColorComponent.ALPHA in replace_color_component:
                        color = self.append_or_replace_alpha(
                            old_color if not _changed else color,
                            color_orig,
                            ColorComponent.ALPHA,
                        )
                        _changed = True
                    if (
                        ColorComponent.ALL in replace_color_component
                        or property_name == group
                    ):
                        color = color_orig
                if group in DEBUG_GROUP:
                    print(
                        f" (G {debug_group_counter}) >>>: '{property_name}' is processed by the area '{area}' (color matching rule '{group}') - '{color}' - '{replace_color_component}' - {[_w.area for _w in color_wrappers]}\n"
                    )
                    debug_group_counter += 1
                if property_name in DEBUG_PROPERTY:
                    print(
                        f" (P {debug_property_counter}) >>>: '{property_name}' is processed by the area '{area}' (color matching rule '{group}') - '{color}' - '{replace_color_component}' - {[_w.area for _w in color_wrappers]}\n"
                    )
                    debug_property_counter += 1
                if area == "default" and group != "default":
                    default_processed_properties.append(property_name)
                if group == property_name:
                    customized_properties.append(property_name)
                if group not in used_groups:
                    used_groups.append(group)
                workbench_colors[property_name] = color

        workbench_colors = dict(sorted(workbench_colors.items(), key=lambda x: x[0]))
        self.config["colors"] = workbench_colors

        # token colors
        token_configs = self.config["tokenColors"]
        new_token_configs = []
        for token_config in token_configs:
            scope = token_config["scope"]
            color_wrappers = config.get_color_wrappers(scope, target_area="token")
            assert (
                len(color_wrappers) == 1
            ), f"how can we get multiple color wrappers for token ({scope})?"
            color_wrapper = color_wrappers[0]
            _colors = color_wrapper.colors
            new_color = _colors[random.randint(0, len(_colors) - 1)]
            new_token_configs.append(
                {"scope": scope, "settings": {"foreground": new_color}}
            )
            group = color_wrapper.group
            if group not in used_groups:
                used_groups.append(group)
            area = color_wrapper.area
            if scope in DEBUG_PROPERTY:
                print(
                    f"{scope} is processed by the token color {group} in the area {area}"
                )
        new_token_configs.sort(key=lambda x: x["scope"])
        self.config["tokenColors"] = new_token_configs
        _dump_json_file(self.config_path, self.config)
        _dump_json_file("used_groups.json", used_groups)

        # clever code?!
        all_groups = sorted(
            list(
                set(
                    (
                        c
                        for a in config.areas
                        for g in config.config[a]
                        for c in g["groups"]
                    )
                )
            )
        )
        _dump_json_file("all_groups.json", all_groups)

        # good auto-completion
        _dump_json_file(
            "not_used_groups.json", [x for x in all_groups if x not in used_groups]
        )


def _dump_json_file(json_file_path, json_data):
    """
    Writes the given JSON data to a file at the specified path.

    Parameters:
        json_file_path (str): The path to the JSON file.
        json_data (dict): The JSON data to be written to the file.

    Returns:
        None
    """
    if not os.path.exists(os.path.dirname(json_file_path)):
        json_file_path = (
            os.getcwd() + os.path.sep + "output" + os.path.sep + json_file_path
        )
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)


def print_colors(filter_value, theme="random"):
    assert theme is not None, "Please provide theme name."
    random_theme_json_file = f"{os.getcwd()}/themes/viiv-{theme}-color-theme.json"
    random_theme_json = load_json_file(random_theme_json_file)
    theme_template_json = load_json_file(THEME_TEMPLATE_JSON_FILE)
    colors = random_theme_json["colors"]
    for k, v in colors.items():
        if k.lower().find(filter_value) != -1 or re.match(
            f".*{filter_value}.*", k, re.IGNORECASE
        ):
            print(pe.bg(v, f"{k}: {v} ({theme_template_json['colors'][k]})"))


def print_palette(filter_value=None):
    """
    Print the random palette, selected UI palette, and selected token palette.

    This function prints the random palette, selected UI palette, and selected token palette
    to the console. The random palette is loaded from the file "random-palette.json" located
    in the "output" directory. The selected UI palette is loaded from the file specified by
    the constant variable "SELECTED_UI_COLOR_FILE_PATH". The selected token palette is loaded
    from the file specified by the constant variable "SELECTED_TOKEN_COLOR_FILE_PATH".

    Parameters:
    None

    Returns:
    None
    """
    if filter_value is not None and len(filter_value.strip()) == 0:
        filter_value = None
    random_palette_json_file = f"{os.getcwd()}/output/random-palette.json"
    with open(random_palette_json_file, "r", encoding="utf-8") as file:
        random_palette_json = json.load(file)
    for k, v in random_palette_json.items():
        if (
            filter_value
            and k != filter_value
            and not re.match(f".*{filter_value}.*", k, re.IGNORECASE)
        ):
            continue
        print(pe.bg(v, f"{k}: {v}"))

    print("\nSelected UI Palette:")
    with open(SELECTED_UI_COLOR_FILE_PATH, encoding="utf-8") as selected_ui_file:
        selected_ui_palette_json = json.load(selected_ui_file)
        for k, v in selected_ui_palette_json.items():
            if (
                filter_value
                and k != filter_value
                and not re.match(f".*{filter_value}.*", k, re.IGNORECASE)
            ):
                continue
            print(pe.bg(v, f"{k}: {v}"))

    print("\nSelected Token Palette:")
    with open(SELECTED_TOKEN_COLOR_FILE_PATH, encoding="utf-8") as selected_token_file:
        selected_token_palette_json = json.load(selected_token_file)
        for k, v in selected_token_palette_json.items():
            if (
                filter_value
                and k != filter_value
                and not re.match(f".*{filter_value}.*", k, re.IGNORECASE)
            ):
                continue
            print(pe.bg(v, f"{k}: {v}"))


DEFAULT_THEMES_MAP = {
    "dark-black": ["#010101", "#010101", "#010101", "#010101"],
    "dark-red": ["#010000", "#010000", "#010000", "#010000"],
    "dark-yellow": ["#010100", "#010100", "#010100", "#010100"],
    "dark-desaturated-yellow": ["#202313", "#202313", "#202313", "#202313"],
    "dark-olive-yellow": ["#222118", "#222118", "#222118", "#222118"],
    "dark-green": ["#000100", "#000100", "#000100", "#000100"],
    "dark-lime-green": ["#1e2420", "#1e2420", "#1e2420", "#1e2420"],
    "dark-cyan": ["#000101", "#000101", "#000101", "#000101"],
    "dark-grayish-cyan": ["#090c0c", "#090c0c", "#090c0c", "#090c0c"],
    "dark-blue": ["#000001", "#000001", "#000001", "#000001"],
    "dark-desaturated-blue": ["#191f27", "#191f27", "#191f27", "#191f27"],
    "dark-violet": ["#010001", "#010001", "#010001", "#010001"],
    "dark-pink": ["#271622", "#271622", "#271622", "#271622"],
    "dark-magenta": ["#231626", "#231626", "#231626", "#231626"],
    "dark-grayish-violet": ["#18171a", "#18171a", "#18171a", "#18171a"],
    "black": ["#0b0b0b", "#0b0b0b", "#0b0b0b", "#0b0b0b"],
    "red": ["#0c0000", "#0c0000", "#0c0000", "#0c0000"],
    "yellow": ["#0c0c00", "#0c0c00", "#0c0c00", "#0c0c00"],
    "green": ["#000c00", "#000c00", "#000c00", "#000c00"],
    "cyan": ["#000c0c", "#000c0c", "#000c0c", "#000c0c"],
    "blue": ["#00000c", "#00000c", "#00000c", "#00000c"],
    "violet": ["#0c000c", "#0c000c", "#0c000c", "#0c000c"],
    "ericsson-black": ["#0c0c0c", "#0c0c0c", "#0c0c0c", "#0c0c0c"],
    "github-blue": ["#010409", "#010409", "#010409", "#010409"],
    "twitter-dim": ["#0d1319", "#0d1319", "#0d1319", "#0d1319"],
    "random-0": [],
    "random-1": [],
    "random-2": [],
    "random-3": [],
    "random-4": [],
    "random-5": [],
    "random-6": [],
    "random-7": [],
}


def generate_default_themes(target_theme="black"):
    """
    Generates default themes based on the given target theme.

    Parameters:
        target_theme (str): The target theme to generate. If not provided, all default themes will be generated.

    Returns:
        None
    """
    for theme, colors in DEFAULT_THEMES_MAP.items():
        if target_theme and theme != target_theme:
            continue
        generate_random_theme_file(
            workbench_colors=colors, theme_filename_prefix=f"viiv-{theme}"
        )


def generate_themes(target_theme=None):
    """
    Generates configured themes.
    """
    for theme_config in config.config["themes"]:
        theme_name = theme_config["name"]
        if target_theme and (
            theme_name != target_theme
            and not re.match(f".*{target_theme}.*", theme_name, re.IGNORECASE)
        ):
            continue
        workbench_base_color_name = theme_config.get(
            "workbench_base_color_name",
            config.options.get("workbench_base_color_name", pe.ColorName.BLUE.name),
        )
        token_colors_total = theme_config.get(
            "token_colors_total", config.options.get("token_colors_total", 7)
        )
        token_colors_gradations_total = theme_config.get(
            "token_colors_gradations_total",
            config.options.get("token_colors_gradations_total", 60),
        )
        token_colors_min = theme_config.get(
            "token_colors_min", config.options.get("token_colors_min", 120)
        )
        token_colors_max = theme_config.get(
            "token_colors_max", config.options.get("token_colors_max", 180)
        )
        token_colors_saturation = theme_config.get(
            "token_colors_saturation",
            config.options.get("token_colors_saturation", 0.35),
        )
        token_colors_lightness = theme_config.get(
            "token_colors_lightness", config.options.get("token_colors_lightness", 0.15)
        )
        workbench_colors_total = theme_config.get(
            "workbench_colors_total", config.options.get("workbench_colors_total", 7)
        )
        workbench_colors_gradations_total = theme_config.get(
            "workbench_colors_gradations_total",
            config.options.get("workbench_colors_gradations_total", 60),
        )
        workbench_colors_min = theme_config.get(
            "workbench_colors_min", config.options.get("workbench_colors_min", 19)
        )
        workbench_colors_max = theme_config.get(
            "workbench_colors_max", config.options.get("workbench_colors_max", 20)
        )
        workbench_colors_saturation = theme_config.get(
            "workbench_colors_saturation",
            config.options.get("workbench_colors_saturation", 0.08),
        )
        workbench_colors_lightness = theme_config.get(
            "workbench_colors_lightness",
            config.options.get("workbench_colors_lightness", 0.08),
        )
        generate_random_theme_file(
            token_colors_total=token_colors_total,
            token_colors_gradations_total=token_colors_gradations_total,
            token_colors_min=token_colors_min,
            token_colors_max=token_colors_max,
            token_colors_saturation=token_colors_saturation,
            token_colors_lightness=token_colors_lightness,
            workbench_colors_total=workbench_colors_total,
            workbench_colors_gradations_total=workbench_colors_gradations_total,
            workbench_colors_min=workbench_colors_min,
            workbench_colors_max=workbench_colors_max,
            workbench_colors_saturation=workbench_colors_saturation,
            workbench_colors_lightness=workbench_colors_lightness,
            theme_name=theme_name,
            workbench_base_color_name=workbench_base_color_name,
        )


def discard_red_dark_color(palette_color_data):
    """Discard red dark color from palette data - Don't use it as workbench color."""
    workbench_color_index = 14  # TODO
    workbench_color_hex = palette_color_data[f"C_{workbench_color_index}_59"]
    workbench_color_rgb = pe.hex2rgb(workbench_color_hex)
    max_rgb = max(workbench_color_rgb)
    if (max_rgb == workbench_color_rgb[0]) and (max_rgb not in workbench_color_rgb[1:]):
        # Find the replacement in dark colors
        random_dark_base_color = None
        for index in range(8, 13):  # TODO
            index = pe.padding(index)
            random_workbench_color_hex = palette_color_data.get(f"C_{index}_59")
            if random_workbench_color_hex is None:
                continue
            random_workbench_color_rgb = pe.hex2rgb(random_workbench_color_hex)
            random_max_rgb = max(random_workbench_color_rgb)
            if random_max_rgb != random_workbench_color_rgb[0]:
                random_dark_base_color = index
                break
        # If no available replacement, return original palette data
        if random_dark_base_color is None:
            print(
                f"Failed to discard red color {workbench_color_hex} - No availalbe replacement"
            )
            return palette_color_data
        # Replace
        random_dark_color_id = f"C_{random_dark_base_color}_59"
        random_dark_color = palette_color_data[random_dark_color_id]
        print(
            f"Discard red color {workbench_color_hex} - Replace with '{random_dark_color}'"
        )
        for i in range(60):
            i = pe.padding(i)
            palette_color_data[f"C_{workbench_color_index}_{i}"] = palette_color_data[
                f"C_{random_dark_base_color}_{i}"
            ]
    return palette_color_data


def generate_random_theme_file(
    token_colors_total=7,
    token_colors_gradations_total=60,
    token_colors_min=120,
    token_colors_max=180,
    token_colors_saturation=0.35,
    token_colors_lightness=0.15,
    workbench_colors_total=7,
    workbench_colors_gradations_total=60,
    workbench_colors_min=19,
    workbench_colors_max=20,
    workbench_colors_saturation=0.2,
    workbench_colors_lightness=0.09,
    **kwargs,
):
    """
    Generates a random theme file with specified parameters.

    Args:
        colors_total (int): The total number of colors.
        gradations_total (int): The total number of color gradations.
        dark_color_gradations_total (int): The total number of dark color gradations.
        general_min_color (int): The minimum color value. Best value: 60.
        general_max_color (int): The maximum color value. Best value: 180.
        dark_color_min (int): The minimum dark color value.
        dark_color_max (int): The maximum dark color value.
        dark_colors_total (int): The total number of dark colors.
        dark_base_colors (list): The list of dark base colors.
        theme_filename_prefix (str): The prefix for the theme filename.

    Best value values for general min and max: 60, 180.This range can generate full color used for token colors. Therefore, no need to change them or pass other values unless you know what you are doing.

    Good valus for dark colors min and max: 5, 15. The maximum value of dark colors max should be 30. No bigger value should be used unless for light-mode theme. When the range is changed, the values used in config.json might be tuned accordingly. With the configuration in v0.2.31, the best values are 15,20.

    Returns:
        None
    """
    theme_name = kwargs.get("theme_name", "viiv-random-0")
    print(theme_name)
    template_config = TemplateConfig()
    template_config.generate_template()
    template_config_data = template_config.config
    workbench_colors = kwargs.get("workbench_colors", [])
    workbench_base_color_name = kwargs.get(
        "workbench_base_color_name", pe.ColorName.BLUE.name
    )
    palette_data = pe.Palette(
        colors_total=token_colors_total,
        colors_gradations_total=token_colors_gradations_total,
        colors_min=token_colors_min,
        colors_max=token_colors_max,
        colors_saturation=token_colors_saturation,
        colors_lightness=token_colors_lightness,
        dark_colors_total=workbench_colors_total,
        dark_colors_gradations_total=workbench_colors_gradations_total,
        dark_colors_min=workbench_colors_min,
        dark_colors_max=workbench_colors_max,
        dark_colors_saturation=workbench_colors_saturation,
        dark_colors_lightness=workbench_colors_lightness,
        dark_colors=workbench_colors,
        dark_base_color_name=workbench_base_color_name,
    ).generate_palette()
    if config.get_discard_red_dark_color():
        palette_data = discard_red_dark_color(palette_data)

    selected_ui_color = {}
    selected_token_color = {}
    for property_name, color in template_config_data["colors"].items():
        color = template_config_data["colors"][property_name]
        color_placeholder = color[0:7]
        alpha = color[7:9]
        if color_placeholder in palette_data:
            color_replacement = palette_data[color_placeholder] + alpha
            template_config_data["colors"][property_name] = color_replacement
            selected_ui_color[color_placeholder] = color_replacement

    for token_color in template_config_data["tokenColors"]:
        foreground = token_color["settings"]["foreground"]
        color_placeholder = foreground[0:7]
        alpha = foreground[7:9]
        color_replacement = palette_data[color_placeholder] + alpha
        token_color["settings"]["foreground"] = color_replacement
        selected_token_color[color_placeholder] = color_replacement

    random_theme_path = f"{os.getcwd()}/themes/{theme_name.lower()}-color-theme.json"
    _dump_json_file(PALETTE_FILE_PATH, palette_data)
    _dump_json_file(random_theme_path, template_config_data)
    _dump_json_file(SELECTED_UI_COLOR_FILE_PATH, selected_ui_color)
    _dump_json_file(SELECTED_TOKEN_COLOR_FILE_PATH, selected_token_color)


def create_random_theme_file():
    """
    Creates a random theme file with configuration options.
    """
    token_colors_total = config.options.get("token_colors_total", 7)
    token_colors_gradations_total = config.options.get(
        "token_colors_gradations_total", 60
    )
    token_colors_min = config.options.get("token_colors_min", 120)
    token_colors_max = config.options.get("token_colors_max", 180)
    token_colors_saturation = config.options.get("token_colors_saturation", 0.35)
    token_colors_lightness = config.options.get("token_colors_lightness", 0.15)
    workbench_colors_total = config.options.get("workbench_colors_total", 7)
    workbench_colors_gradations_total = config.options.get(
        "workbench_colors_gradations_total", 60
    )
    workbench_colors_min = config.options.get("workbench_colors_min", 19)
    workbench_colors_max = config.options.get("workbench_colors_max", 20)
    workbench_colors_saturation = config.options.get("workbench_colors_saturation", 0.2)
    workbench_colors_lightness = config.options.get("workbench_colors_lightness", 0.09)
    workbench_base_color_name = config.options.get(
        "workbench_base_color_name", pe.ColorName.BLUE.name
    )
    generate_random_theme_file(
        token_colors_total=token_colors_total,
        token_colors_gradations_total=token_colors_gradations_total,
        token_colors_min=token_colors_min,
        token_colors_max=token_colors_max,
        token_colors_saturation=token_colors_saturation,
        token_colors_lightness=token_colors_lightness,
        workbench_colors_total=workbench_colors_total,
        workbench_colors_gradations_total=workbench_colors_gradations_total,
        workbench_colors_min=workbench_colors_min,
        workbench_colors_max=workbench_colors_max,
        workbench_colors_saturation=workbench_colors_saturation,
        workbench_colors_lightness=workbench_colors_lightness,
        workbench_base_color_name=workbench_base_color_name,
    )


def debug_color_config():
    """
    Generates a debug color configuration.

    This function iterates over the configuration settings and prints the area,
    groups, and color information for each area. It checks if the groups contain the
    keywords "background" or "foreground" and modifies the color configuration
    accordingly. The modified color configuration is then printed.

    Parameters:
    None

    Returns:
    None
    """
    for area, area_config in config.config.items():
        print(area)
        for config in area_config:
            groups = config["groups"]
            color = config["color"]
            has_background = (
                len(list(filter(lambda x: x.lower().find("background") != -1, groups)))
                > 0
            )
            has_foreground = (
                len(list(filter(lambda x: x.lower().find("foreground") != -1, groups)))
                > 0
            )
            if has_background:
                color["basic_range"] = [8, 12]
            if has_foreground:
                color["basic_range"] = [1, 8]
                color["light_range"] = [1, 60]

    _dump_json_file(config.config_path, config.config)


def main():
    """
    Parses command line arguments and generates themes or prints colors based on the options provided.

    Parameters:
        None

    Returns:
        None
    """
    opts, _ = getopt.getopt(
        sys.argv[1:],
        "gp:rt:P:",
        [
            "--random_theme",
            "--generate",
            "--print_colors=",
            "--theme=",
            "--print_palette=",
        ],
    )
    to_generate_default_themes = False
    to_print_colors = False
    print_colors_filter = None
    target_theme = None
    for option, value in opts:
        if option in ("-g", "--generate_default_themes"):
            to_generate_default_themes = True
        if option in ("-r", "--random_theme"):
            create_random_theme_file()
        if option in ("-t", "--theme"):
            target_theme = value
        elif option in ("-p", "--print_colors"):
            to_print_colors = True
            print_colors_filter = value
        elif option in ("-P", "--print_palette"):
            print_palette(value)

    if to_generate_default_themes:
        generate_themes(target_theme)

    if to_print_colors:
        print_colors(print_colors_filter, target_theme)


if __name__ == "__main__":
    main()
