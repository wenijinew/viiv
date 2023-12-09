#!/usr/bin/env python
"""Functions to help quickly generate customized token colors in VsCode theme file."""

def get_scopes(json_file):
    """Get scopes from the given json file which is VsCode theme file.
    
    """
    with open(json_file) as f:
        data = json.load(f)
        scopes = []
        token_colors = data["tokenColors"]
        for token in token_colors:
            if "scope" in token:
                if type(token["scope"]) == str:
                    scopes.append(token["scope"])
                elif type(token["scope"]) == list:
                    scopes.extend(token["scope"])
            else:
                print("No scope in {}.".format(token))
    return scopes
    

def get_scope_groups(scopes):
    """Get prefixes from the given scopes.
    
    """
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
        for j in range(14,23):
            j = str(j)
            color_placeholders.append(f"C_{i}_{j}")
    import random
    samples = random.sample(color_placeholders, len(
        scope_groups
    ))
    token_colors = []
    count = 0
    for i,item in enumerate(scope_groups.items()):
        for scope in item[1]:
            count += 1
            scope_settings = {
                "scope": scope,
                "settings": {
                    "foreground": samples[count%len(samples)],
                }
            }
            token_colors.append(scope_settings)
    import os
    json.dump(token_colors, open(f'{os.getenv("HOME")}/Downloads/token_colors.json', "w"))
    return token_colors