#!/usr/bin/env python
"""Functions to help quickly generate customized token colors in VsCode theme file."""

import time
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

# debug
DEBUG_PROPERTY = ["testing.runAction"]
DEBUG_GROUP = [""]

THEME_TEMPLATE_JSON_FILE = f"{os.getcwd()}/templates/viiv-color-theme.template.json"
PALETTE_FILE_PATH = f"{os.getcwd()}/output/dynamic-palette.json"
SELECTED_UI_COLOR_FILE_PATH = f"{os.getcwd()}/output/selected-ui-palette.json"
SELECTED_TOKEN_COLOR_FILE_PATH = f"{os.getcwd()}/output/selected-token-palette.json"


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
    CONTAINS = 4
    FUZZY = 5


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
    return area in ["background", "foreground"]


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


class Config(dict):
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
                lambda x: 'default' in x["groups"],
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
        super().__init__(
            config=self.config,
            areas=self.areas,
            default_color=self.default_color_config,
            default_token_color=self.default_token_color_config,
        )

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
            if _matched_color_config_dict and _matched_color_config_dict not in _matched_color_configs:
                _matched_color_configs.append(_matched_color_config_dict)

        color_wrappers = []
        if _matched_color_configs:
            if target_property in DEBUG_PROPERTY:
                print(_matched_color_configs)
            
            default_area_matched_color_configs = list(filter(lambda x: x["area"] == "default", _matched_color_configs))
            if default_area_matched_color_configs:
                _matched_color_configs = default_area_matched_color_configs
            most_matched_color_config = min([c for c in list(filter(lambda c: c["color_config"] is not None, _matched_color_configs))], key=lambda x: x["match_rule"].value)

            if most_matched_color_config:
                color_wrappers.append(most_matched_color_config["color_config"].create_colors_wrapper())

        if len(color_wrappers) > 0:
            if target_property in DEBUG_PROPERTY:
                print([c.area for c in color_wrappers])
            return color_wrappers
        if target_area is None or target_area != "token":
            color_wrappers.append(self.default_color_config.create_colors_wrapper())
        else:
            color_wrappers.append(self.default_token_color_config.create_colors_wrapper())
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
                    matched_groups.append({
                        "match_rule": match_rule,
                        "group": group
                    })
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
                ColorComponent[_component]
                for _component in replace_color_component
            ]
        else:
            replace_color_component = (
                [ColorComponent.ALL]
                if area != "default"
                else [ColorComponent.ALPHA])
        return replace_color_component



    def _get_color(self, area, target_property) -> dict:
        """Get the color config.

        Each area has many color configurations for different groups. each group could match one or many different color properties.
        By going through all color configurations in the given area, and then check if any group in each color configuration matched the target property by using different matching rules.
        Finally, if multiple groups matched the target property, then pick up the one using match rule having the least matching rule value(which means highest priority).
        If no any group matched the target property, then return None which means there is no color config matching the targe property in this area. For example, 'background' area cannot have any color config to match 'activityBar.foreground'.

        Matching rule will be returned also. Then if many areas have matched color config for the target property, then pick up the one with the least matching rule. If the same, then print warning for duplicated configuration and pickup the first one.

        Parameters:

            area (str): area name
            target_property (str): target property
        
        Returns:
            dict: the matched group and the matched rule
        """
        area_config = self.config[area]
        _matches = []
        for groups_config in area_config:
            groups = groups_config["groups"]
            groups.sort(key=lambda x: len(x), reverse=True)
            _match = self._match(groups, target_property)
            if _match:
                color = groups_config["color"]
                replace_color_component = self._get_replace_color_component(area, groups_config)
                _match["color"] = color
                _match["replace_color_component"] = replace_color_component
                _matches.append(_match)

        
        if not _matches:
            return {}

        _most_matched_config = min(_matches, key=lambda x: x["match_rule"].value)
        color = _most_matched_config["color"]
        group = _most_matched_config["group"]
        replace_color_component = _most_matched_config["replace_color_component"]
        color_config = ColorConfig(
            color,
            area,
            group,
            replace_color_component
        )
        return {"color_config":color_config, "match_rule":_most_matched_config["match_rule"], "area":area}

    def __repr__(self) -> str:
        return super().__repr__()


class TemplateConfig(dict):
    """Wrapper class for template config."""

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = THEME_TEMPLATE_JSON_FILE
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

    def generate_template(self, config: Config = None):
        """Generate template with color configuration."""
        if config is None:
            _color_config_path = f"{os.getcwd()}/config.json"
            config = Config(config_path=_color_config_path)

        workbench_colors = {}
        default_processed_properties = []
        customized_properties = []

        # workbench colors
        used_groups = []
        for property in self.color_properties:
            color_wrappers = config.get_color_wrappers(property)
            if color_wrappers is None or not isinstance(color_wrappers, list):
                print(property, type(color_wrappers))
                continue
            color_wrappers_areas = [w.area for w in color_wrappers]
            if (
                property in default_processed_properties
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
                if property in workbench_colors:
                    if property in customized_properties:
                        continue
                    if area not in ["default", "token"]:
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
                        if (
                            ColorComponent.ALL in replace_color_component
                            or property == group
                        ):
                            color = color_orig
                if group in DEBUG_GROUP:
                    print(
                        f" (G {debug_group_counter}) >>>: '{property}' is processed by the area '{area}' (color matching rule '{group}') - '{color}' - '{replace_color_component}' - {[_w.area for _w in color_wrappers]}\n"
                    )
                    debug_group_counter += 1
                if property in DEBUG_PROPERTY:
                    print(
                        f" (P {debug_property_counter}) >>>: '{property}' is processed by the area '{area}' (color matching rule '{group}') - '{color}' - '{replace_color_component}' - {[_w.area for _w in color_wrappers]}\n"
                    )
                    debug_property_counter += 1
                if area == "default" and group != "default":
                    default_processed_properties.append(property)
                if group == property:
                    customized_properties.append(property)
                if group not in used_groups:
                    used_groups.append(group)
                workbench_colors[property] = color

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
        self.config["tokenColors"] = new_token_configs
        json.dump(self.config, open(self.config_path, "w"), indent=4)
        _dump_json_file("used_groups.json", used_groups)

        # clever code?!
        all_groups = sorted(
            list(
                set(
                    [
                        c
                        for v in config.config.values()
                        for g in v
                        for c in g["groups"]
                    ]
                )
            )
        )
        _dump_json_file("all_groups.json", all_groups)

        # good auto-completion
        _dump_json_file("not_used_groups.json", [x for x in all_groups if x not in used_groups])


def _dump_json_file(json_file_path, json_data):
    if not os.path.exists(os.path.dirname(json_file_path)):
        json_file_path = (
            os.getcwd() + os.path.sep + "output" + os.path.sep + json_file_path
        )
    with open(json_file_path, "w") as f:
        json.dump(json_data, f, indent=4)


def print_colors(value, theme="dynamic"):
    dynamic_theme_json_file = f"{os.getcwd()}/themes/viiv-{theme}-color-theme.json"
    dynamic_theme_json = json.load(open(dynamic_theme_json_file))
    theme_template_json = json.load(open(THEME_TEMPLATE_JSON_FILE))
    colors = dynamic_theme_json["colors"]
    for k, v in colors.items():
        if k.lower().find(value) != -1 or re.match(f".*{value}.*", k, re.IGNORECASE):
            print(pe.bg(v, f"{k}: {v} ({theme_template_json['colors'][k]})"))


def print_palette():
    print("Dynamic palette:")
    dynamic_palette_json_file = f"{os.getcwd()}/output/dynamic-palette.json"
    dynamic_palette_json = json.load(open(dynamic_palette_json_file))
    for k, v in dynamic_palette_json.items():
        print(pe.bg(v, f"{k}: {v}"))

    print("Selected UI palette:")
    selected_ui_palette_json = json.load(open(SELECTED_UI_COLOR_FILE_PATH))
    for k, v in selected_ui_palette_json.items():
        print(pe.bg(v, f"{k}: {v}"))

    print("Selected Token palette:")
    selected_token_palette_json = json.load(open(SELECTED_TOKEN_COLOR_FILE_PATH))
    for k, v in selected_token_palette_json.items():
        print(pe.bg(v, f"{k}: {v}"))


DEFAULT_THEMES_MAP = {
    "black": ["#0c0c0c", "#0d0d0d", "#0e0e0e", "#0f0f0f"],
    "red": ["#020000", "#040000", "#060000", "#080000"],
    "orange": ["#020100","#040200", "#080400", "#090400" ],
    "yellow": ["#0c0c00", "#0d0d00", "#0e0e00", "#0f0f00"],
    "green": ["#000c00", "#000d00", "#000e00", "#000f00"],
    "cyan": ["#000c0c", "#000d0d", "#000e0e", "#000f0f"],
    "blue": ["#00000c", "#00000d", "#00000e", "#00000f"],
    "violet": ["#0c000c", "#0d000d", "#0e000e", "#0f000f"],
    "pink": ["#0c0c00", "#0d0d00", "#0e0e00", "#0f0f00"],
}


def pirnt_default_themes():
    for theme, colors in DEFAULT_THEMES_MAP.items():
        print(pe.bg(colors, f"{theme}"))

def generate_default_themes(target_theme="black"):
    for theme, colors in DEFAULT_THEMES_MAP.items():
        if target_theme and theme != target_theme:
            continue
        generate_random_theme_file(
            dark_base_colors=colors, theme_filename_prefix=f"viiv-{theme}"
        )
        time.sleep(5)


def generate_random_theme_file(
    colors_total=7,
    gradations_total=60,
    dark_color_gradations_total=60,
    general_min_color=50,
    general_max_color=160,
    dark_color_min=5,
    dark_color_max=15,
    dark_colors_total=4,
    dark_base_colors=None,
    theme_filename_prefix="viiv-dynamic",
):
    """Generate random theme file."""
    template_config = TemplateConfig()
    template_config.generate_template()
    template_config_data = template_config.config
    palette_data = pe.Palette(
        colors_total=colors_total,
        gradations_total=gradations_total,
        dark_color_gradations_total=dark_color_gradations_total,
        color_min=general_min_color,
        color_max=general_max_color,
        dark_color_min=dark_color_min,
        dark_color_max=dark_color_max,
        dark_colors_total=dark_colors_total,
        dark_colors=dark_base_colors,
    ).generate_palette()

    selected_ui_color = {}
    selected_token_color = {}
    for property, color in template_config_data["colors"].items():
        color = template_config_data["colors"][property]
        color_placeholder = color[0:7]
        alpha = color[7:9]
        if color_placeholder in palette_data:
            color_replacement = palette_data[color_placeholder] + alpha
            template_config_data["colors"][property] = color_replacement
            selected_ui_color[color_placeholder] = color_replacement

    for token_color in template_config_data["tokenColors"]:
        foreground = token_color["settings"]["foreground"]
        color_placeholder = foreground[0:7]
        alpha = foreground[7:9]
        color_replacement = palette_data[color_placeholder] + alpha
        token_color["settings"]["foreground"] = color_replacement
        selected_token_color[color_placeholder] = color_replacement

    DYNAMIC_THEME_PATH = (
        f"{os.getcwd()}/themes/{theme_filename_prefix}-color-theme.json"
    )
    json.dump(
        palette_data,
        open(PALETTE_FILE_PATH, "w"),
        indent=4,
        sort_keys=True,
    )
    json.dump(
        template_config_data,
        open(DYNAMIC_THEME_PATH, "w"),
        indent=4,
        sort_keys=True,
    )
    json.dump(
        selected_ui_color,
        open(SELECTED_UI_COLOR_FILE_PATH, "w"),
        indent=4,
        sort_keys=True,
    )
    json.dump(
        selected_token_color,
        open(SELECTED_TOKEN_COLOR_FILE_PATH, "w"),
        indent=4,
        sort_keys=True,
    )

if __name__ == "__main__":
    opts, _ = getopt.getopt(
        sys.argv[1:],
        "dgp:t:P",
        [
            "--dynamic_theme",
            "--generate",
            "--print_colors=",
            "--theme=",
            "--print_palette",
        ],
    )
    to_generate_default_themes = False
    to_print_colors = False
    print_colors_filter = None
    target_theme = None
    for option, value in opts:
        if option in ("-g", "--generate_default_themes"):
            to_generate_default_themes = True
        if option in ("-d", "--dynamic_theme"):
            generate_random_theme_file()
        if option in ("-t", "--theme"):
            target_theme = value
        elif option in ("-p", "--print_colors"):
            to_print_colors = True
            print_colors_filter = value
        elif option in ("-P", "--print_palette"):
            print_palette()

    if to_generate_default_themes:
        generate_default_themes(target_theme)

    if to_print_colors:
        print_colors(print_colors_filter, target_theme)

def test_color_config():
    config = Config()
    for area, area_config in config.config.items():
        print(area)
        for config in area_config:
            groups = config["groups"]
            color = config["color"]
            print(groups, json.dumps(color, indent=4, sort_keys=True))
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
            print("new", json.dumps(color, indent=4, sort_keys=True))

    json.dump(
        config.config,
        open(config.config_path, "w"),
        indent=4,
        sort_keys=True,
    )



def test_config():
    config = Config()
    print(len(config.config.keys()))
    for area in config.areas:
        print(area)
        print(len(config.config[area]))

