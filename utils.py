#!/usr/bin/env python
"""Functions to help quickly generate customized token colors in VsCode theme file."""

import json
import os


def get_scopes(json_file):
    """Get scopes from the given json file which is VsCode theme file."""
    with open(json_file) as f:
        data = json.load(f)
        scopes = []
        token_colors = data["tokenColors"]
        for token in token_colors:
            if "scope" in token:
                token_scope = token.get("scope", [])
                if isinstance(token_scope, str):
                    scopes.append(token_scope)
                elif isinstance(token_scope, list):
                    scopes.extend(token_scope)
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
    _active_bg_properties = get_color_properties_by_suffix(color_properties, "ActiveBackground")
    _inactive_bg_properties = get_color_properties_by_suffix(color_properties, "InactiveBackground")
    # remove _active_bg_properties and _inactive_bg_properties from _bg_properties
    for _active_bg_property in _active_bg_properties:
        if _active_bg_property in _bg_properties:
            _bg_properties.remove(_active_bg_property)
    for _inactive_bg_property in _inactive_bg_properties:
        if _inactive_bg_property in _bg_properties:            
            _bg_properties.remove(_inactive_bg_property)
    
    _fg_properties = get_color_properties_by_suffix(color_properties, "Foreground")
    _active_fg_properties = get_color_properties_by_suffix(color_properties, "ActiveForeground")
    _inactive_fg_properties = get_color_properties_by_suffix(color_properties, "InactiveForeground")
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
    """Group scopes by the prefix."""
    scope_groups = {}
    for scope in scopes:
        group_name = scope.split(".")[0]
        if group_name not in scope_groups:
            scope_groups[group_name] = [scope]
        else:
            if len(scope_groups[group_name]) < 5:
                scope_groups[group_name].append(scope)
            else:
                if f"{group_name}2" not in scope_groups:
                    scope_groups[f"{group_name}2"] = [scope]
                else:
                    scope_groups[f"{group_name}2"].append(scope)
    return scope_groups


def define_token_colors(scope_groups):
    """for each scope, set its foreground

    Example.
    {
        "scope": ["scope 1", "scope 2"],
        settings: {
            "foreground": "#ff0000"
        }
    }
    """
    # color placeholder value format "C_[0-9]{2}_[0-9]{2}",
    color_placeholders = []
    for i in range(1, 12):
        if i < 10:
            i = "0" + str(i)
        for j in range(14, 23):
            j = str(j)
            color_placeholders.append(f"C_{i}_{j}")
    import random

    samples = random.sample(color_placeholders, len(scope_groups))
    token_colors = []
    count = 0
    for i, item in enumerate(scope_groups.items()):
        for scope in item[1]:
            count += 1
            scope_settings = {
                "scope": scope,
                "settings": {
                    "foreground": samples[count % len(samples)],
                },
            }
            token_colors.append(scope_settings)
    json.dump(
        token_colors, open(f'{os.getenv("HOME")}/Downloads/token_colors.json', "w")
    )
    return token_colors
