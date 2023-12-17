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

# reserved
TOKEN_COLOR_PREFIX = "T_"
WORKBENCH_COLOR_PREFIX = "W_"
PLACEHOLDER_REGEX = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2,4}"
PLACEHOLDER_REGEX_WITHOUT_ALPHA = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}"
PLACEHOLDER_REGEX_WITH_ALPHA = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}[a-zA-Z0-9]{2}"
RGB_HEX_REGEX = r"#[a-zA-Z0-9]{6,8}"
RGB_HEX_REGEX_WITHOUT_ALPHA = r"#[a-zA-Z0-9]{6}"
RGB_HEX_REGEX_WITH_ALPHA = r"#[a-zA-Z0-9]{8}"

HEX_NUMBER_STR_PATTERN = re.compile(r"^0x[0-9a-zA-Z]+$")
DEBUG_PROPERTY = [
    "editorIndentGuide.activeBackground1",
    "editorIndentGuide.background1",
]


class ColorComponent(Enum):
    """Color component for color range."""

    BASIC = 1
    LIGHT = 2
    ALPHA = 3
    ALL = 4


class MatchRule(Enum):
    """Match rule for color range."""

    EXACT = 1
    ENDSWITH = 2
    STARTSWITH = 3
    FUZZY = 4


def _to_int(value: str) -> int:
    """Convert string to int."""
    if isinstance(value, int):
        return value
    elif isinstance(value, str) and (HEX_NUMBER_STR_PATTERN.match(value)):
        return int(value, 16)
    return int(value)


def _read_config(config_path):
    """Read config.json file and return the content."""
    with open(config_path, "r") as f:
        return json.load(f)


def is_property_area(area):
    """Check if the current theme is a property area."""
    return area in ["background", "foreground", "border"]


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

    def __repr__(self) -> str:
        return super().__repr__()


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
                for basic in _random_range(self.basic_range)
                for light in _random_range(self.light_range)
            ]
        else:
            _head = ["#000000"]

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

        _wrapper = ColorsWrapper(
            _colors, self.area, self.group, self.replace_color_component
        )
        return _wrapper


class ColorConfig(dict):
    """Wrapper class for color config

    Read and parse config.json file located in the current directory.
    """

    def __init__(self, config_path=None):
        """Read config.json file and initialize."""
        if config_path is None:
            config_path = f"{os.getcwd()}/config.json"
        self.config_path = config_path
        self.config = _read_config(config_path)
        self.areas = self.config.keys()
        default_color_config = list(
            filter(
                lambda x: len(x["groups"]) == 1 and x["groups"][0] == "default",
                self.config["default"],
            )
        )[0]
        self.default_color = Color(
            default_color_config["color"], "default", default_color_config["groups"][0]
        )
        super().__init__(
            config=self.config, areas=self.areas, default_color=self.default_color
        )

    def get_color_wrappers(self, target_property) -> list:
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
        # for match_rule_name in MatchRule._member_names_:
        #    color = self._get_color("force", target, match_rule_name)
        #    if color is not None:
        #        break
        # if color is not None:
        #    return [color.create_colors_wrapper()]

        color_wrappers = []
        for area in self.areas:
            if is_property_area(area) and target_property.lower().find(area) == -1:
                continue
            # try to find the configured color in the matching order
            for match_rule_name in MatchRule._member_names_:
                color = self._get_color(area, target_property, match_rule_name)
                if color is not None:
                    break
            if color is not None:
                color_wrappers.append(color.create_colors_wrapper())
        color_wrappers = (
            color_wrappers
            if len(color_wrappers) > 0
            else [self.default_color.create_colors_wrapper()]
        )

        # print(target, len(_final_colors), [f.area for f in _final_colors])
        return color_wrappers

    def _get_color(self, area, target_property, match_rule_name):
        area_config = self.config[area]
        color = None
        color_instance = None
        for config in area_config:
            groups = config["groups"]
            groups.sort(key=lambda x: len(x), reverse=True)
            for group in groups:
                if (
                    match_rule_name == MatchRule.EXACT.name
                    and target_property.lower() == group.lower()
                    or match_rule_name == MatchRule.ENDSWITH.name
                    and target_property.lower().endswith(f".{group.lower()}")
                    or match_rule_name == MatchRule.STARTSWITH.name
                    and target_property.lower().startswith(f"{group.lower()}.")
                    or match_rule_name == MatchRule.FUZZY.name
                    and re.match(group, target_property, re.IGNORECASE)
                ):
                    replace_color_component = config.get("replace_color_component")
                    if replace_color_component is not None and isinstance(
                        replace_color_component, list
                    ):
                        replace_color_component = [
                            ColorComponent[_component]
                            for _component in replace_color_component
                        ]
                    else:
                        replace_color_component = (
                            [ColorComponent.ALL]
                            if area != "status"
                            else [ColorComponent.ALPHA]
                        )
                    color = config["color"]
                    _group = group
                    break
            if color is not None:
                color_instance = Color(color, area, _group, replace_color_component)
        return color_instance

    def __repr__(self) -> str:
        return super().__repr__()


class TemplateConfig(dict):
    """Wrapper class for template config."""

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = f"{os.getcwd()}/themes/viiv-color-theme.template.json"
        self.config_path = config_path
        self.config = _read_config(config_path)
        self.color_properties = list(self.config["colors"].keys())
        super().__init__(config_path=config_path)

    def _append_or_replace_alpha(self, old_color, new_color, component: ColorComponent):
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

    def generate_template(self, color_config: ColorConfig = None):
        """Generate template with color configuration."""
        if color_config is None:
            _color_config_path = f"{os.getcwd()}/config.json"
            color_config = ColorConfig(config_path=_color_config_path)

        workbench_colors = {}
        default_processed_properties = []
        for property in self.color_properties:
            color_wrappers = color_config.get_color_wrappers(property)
            if property in default_processed_properties and "status" not in [
                w.area for w in color_wrappers
            ]:
                continue
            for wrapper in color_wrappers:
                colors = wrapper.colors
                replace_color_component = wrapper.replace_color_component
                group = wrapper.group
                area = wrapper.area
                color = colors[random.randint(0, len(colors) - 1)]
                color_orig = color
                if property in workbench_colors:
                    if area != "status":
                        continue
                    else:
                        old_color = workbench_colors[property]
                        _changed = False
                        if ColorComponent.BASIC in replace_color_component:
                            color = self._append_or_replace_alpha(
                                old_color if not _changed else color,
                                color_orig,
                                ColorComponent.BASIC,
                            )
                            _changed = True
                        if ColorComponent.LIGHT in replace_color_component:
                            color = self._append_or_replace_alpha(
                                old_color if not _changed else color,
                                color_orig,
                                ColorComponent.LIGHT,
                            )
                            _changed = True
                        if ColorComponent.ALPHA in replace_color_component:
                            color = self._append_or_replace_alpha(
                                old_color if not _changed else color,
                                color_orig,
                                ColorComponent.ALPHA,
                            )
                            _changed = True
                if property in DEBUG_PROPERTY:
                    print(
                        f"status: {property} is processed by the area {area} (color matching rule '{group}') - {color} - {replace_color_component} - {[_w.area for _w in color_wrappers]}"
                    )
                if area == "default" and group != "default":
                    default_processed_properties.append(property)
                workbench_colors[property] = color
                if area == "default" and group != "default":
                    if property in DEBUG_PROPERTY:
                        print(
                            f"2 status: {property} is processed by the area {area} (color matching rule '{group}') - {color}"
                        )

        self.config["colors"] = workbench_colors

        # token colors
        token_configs = self.config["tokenColors"]
        new_token_configs = []
        token_color_models = color_config.get_color_wrappers("token_default")[0].colors
        for token_config in token_configs:
            token_color_model = token_color_models[
                random.randint(0, len(token_color_models) - 1)
            ]
            scope = token_config["scope"]
            color_wrapper = color_config.get_color_wrappers(scope)[0]
            _colors = color_wrapper.colors
            new_color = _colors[random.randint(0, len(_colors) - 1)]
            # most tokens are using default area colors which light range might be two dark, so replace light range and alpha range
            new_color = self._append_or_replace_alpha(
                new_color, token_color_model, ColorComponent.LIGHT
            )
            new_color = self._append_or_replace_alpha(
                new_color, token_color_model, ColorComponent.ALPHA
            )
            new_token_configs.append(
                {"scope": scope, "settings": {"foreground": new_color}}
            )
        self.config["tokenColors"] = new_token_configs

        json.dump(self.config, open(self.config_path, "w"), indent=4, sort_keys=True)


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
            TemplateConfig().generate_template()
        elif option in ("-p", "--print_colors"):
            print_colors(value)


def test_color_config():
    color_config = ColorConfig()
    print(color_config.get_color_wrappers("minimap"))


# test_color_config()
