#!/usr/bin/env python
"""Functions to help quickly generate customized token colors in VsCode theme file."""

import json
import os
import random
import re


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


def group_color_properties(color_properties):
    """Set colors from the given color properties."""
    _bg_properties = get_color_properties_by_suffix(color_properties, "Background")
    _active_bg_properties = get_color_properties_by_suffix(
        color_properties, "ActiveBackground"
    )
    _inactive_bg_properties = get_color_properties_by_suffix(
        color_properties, "InactiveBackground"
    )
    # remove _active_bg_properties and _inactive_bg_properties from _bg_properties
    for _active_bg_property in _active_bg_properties:
        if _active_bg_property in _bg_properties:
            _bg_properties.remove(_active_bg_property)
    for _inactive_bg_property in _inactive_bg_properties:
        if _inactive_bg_property in _bg_properties:
            _bg_properties.remove(_inactive_bg_property)

    _fg_properties = get_color_properties_by_suffix(color_properties, "Foreground")
    _active_fg_properties = get_color_properties_by_suffix(
        color_properties, "ActiveForeground"
    )
    _inactive_fg_properties = get_color_properties_by_suffix(
        color_properties, "InactiveForeground"
    )
    # remove _active_fg_properties and _inactive_fg_properties from _fg_properties
    for _active_fg_property in _active_fg_properties:
        if _active_fg_property in _fg_properties:
            _fg_properties.remove(_active_fg_property)
    for _inactive_fg_property in _inactive_fg_properties:
        if _inactive_fg_property in _fg_properties:
            _fg_properties.remove(_inactive_fg_property)

    _border_properties = get_color_properties_by_suffix(color_properties, "Border")

    return {
        "bg": _bg_properties,
        "active_bg": _active_bg_properties,
        "inactive_bg": _inactive_bg_properties,
        "fg": _fg_properties,
        "active_fg": _active_fg_properties,
        "inactive_fg": _inactive_fg_properties,
        "border": _border_properties,
    }


def group_scopes(scopes):
    """Group scopes by the prefix.
    
    Parameters:
    ----------
    scopes : dict[scope_name, foreground], e.g. {'scope 1': '#ff0000', 'scope 2': '#'}
    """
    scope_groups = {}
    for scope in scopes.keys():
        _splits = scope.split(".")
        if(len(_splits) == 1):
            group_name = _splits[0]
        else:
            group_name = '.'.join(_splits[0:2])

        if group_name not in scope_groups:
            scope_groups[group_name] = [scope]
        else:
            scope_groups[group_name].append(scope)
    return scope_groups


def _create_color_placeholder(i, j):
    if i < 10:
        i = "0" + str(i)
    if j < 10:
        j = "0" + str(j)
    return f"C_{i}_{j}"

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
    
    # color placeholder value format "C_[0-9]{2}_[0-9]{2}",
    color_placeholders = []
    for i in range(base_colors_range[0], base_colors_range[1]):
        if i < 10:
            i = "0" + str(i)
        for j in range(light_level_range[0], light_level_range[1]):
            if j < 10:
                j = "0" + str(j)
            i = str(i)
            j = str(j)
            color_placeholders.append(f"C_{i}_{j}")

    token_colors = []
    # assign random base colors to scope groups, assign random light colors to scopes in scope group
    base_colors_total = base_colors_range[1]-base_colors_range[0]
    base_color_samples = random.sample(range(base_colors_range[0], base_colors_range[1]), base_colors_total if len(scope_groups) > base_colors_total else len(scope_groups))
    for i,scope_group in enumerate(scope_groups):
        base_color_index = base_color_samples[i%len(base_color_samples)]
        light_level_total = light_level_range[1]-light_level_range[0]
        light_color_samples = random.sample(range(light_level_range[0], light_level_range[1]), light_level_total if len(scope_groups[scope_group]) > light_level_total else len(scope_groups[scope_group]))
        for j,scope in enumerate(scope_groups[scope_group]):
            light_color_index = light_color_samples[j%len(light_color_samples)]
            color_placeholder = _create_color_placeholder(base_color_index, light_color_index)
            _old_foreground = scopes[scope]
            _placeholder_regex = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}"
            _placeholder_with_alpha_regex = r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}[a-zA-Z0-9]{2}"
            _foreground = re.sub(_placeholder_regex, color_placeholder, _old_foreground) 
            for _scope_prefix in ["comment", "docstring"]:
                if scope.find(_scope_prefix) != -1:
                    if not re.match(_placeholder_with_alpha_regex, _old_foreground):
                        _foreground = f"{_foreground}60"
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


if __name__ == "__main__":
    define_token_colors(light_level_range=[25, 45], base_colors_range=[1, 10])
