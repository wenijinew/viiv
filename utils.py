#!/usr/bin/env python
"""Functions to help quickly generate customized token colors in VsCode theme file."""

import getopt
import json
import os
import random
import re
import sys


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


def group_color_properties(color_properties):
    """Group color properties by suffix."""
    _groups = {}
    for color_property in color_properties:
        _splits = color_property.split(".")
        if len(_splits) > 1:
            group_name = _splits[-1]
            if group_name not in _groups:
                _groups[group_name] = [color_property]
            else:
                _groups[group_name].append(color_property)

    for color_property in color_properties:
        _splits = color_property.split(".")
        group_name = _splits[0]
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

class ColorRange(dict):
    def __init__(self, base_color_range, light_level_range, alpha_range):
        self.base_color_range = base_color_range
        self.light_level_range = light_level_range
        self.alpha_range = alpha_range
        super().__init__(base_color_range=base_color_range, light_level_range=light_level_range, alpha_range=alpha_range)

    def is_valid(self):
        """Check if the color range is valid.
        Each color range starts from min and ends at max. min is less than max.
        Color range should not be None or empty.
        Alpha range could be None or empty.
        """
        if (
            self.base_color_range is None
            or self.light_level_range is None
            ):
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


DEFAULT_COLOR_RANGE = ColorRange([1, 12], [20, 40], [])

# more specific, topper
COLOR_RANGE_MAP = {
    "editorRuler": ColorRange([1, 12], [0, 30], [30, 40]),
    "editorIndentGuide": ColorRange([1, 12], [40, 50], [30, 40]),
    "editorGutter": ColorRange([1, 12], [20, 30], []),
    "InactiveBackground": ColorRange([1, 12], [57, 60], [60, 90]),
    "activeBackground": ColorRange([1, 12], [53, 55], []),
    "InactiveForeground": ColorRange([1, 12], [20, 30], []),
    "activeForeground": ColorRange([1, 12], [0, 10], []),
    "InactiveBorder": ColorRange([1, 12], [50, 55], [30, 40]),
    "activeBorder": ColorRange([1, 12], [40, 45], [30, 40]),
    "Foreground": ColorRange([1, 12], [10, 20], []),
    "Background": ColorRange([1, 12], [55, 57], []),
    "Border": ColorRange([1, 12], [45, 50], [30, 40]),
    "Outline": ColorRange([1, 12], [45, 50], [30, 60]),
    "Highlight": ColorRange([1, 12], [30, 35], [30, 40]),
    "Stroke": ColorRange([1, 12], [35, 40], [60, 90]),
    "Shadow": ColorRange([1, 12], [50, 60], []),
    "Panel": ColorRange([1, 12], [55, 60], []),
    "Other": DEFAULT_COLOR_RANGE,
}

HIDDEN_PROPERTIES = [
    "tab.activeBorder",
    "tab.unfocusedActiveBorder",
    "contrastActiveBorder",
]


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
    _color_range = DEFAULT_COLOR_RANGE
    for k in COLOR_RANGE_MAP.keys():
        if group_name.lower().find(k.lower()) != -1:
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
    # return color_placeholder_groups["bg"][0].split("_")[1]
    return "11"


LIGHT_LEVEL_MAP = {
    "59": [
        "activityBar.background",
        "statusBar.background",
        "sideBarSectionHeader.background",
        "menu.background",
        "scrollbar.shadow",
    ],
    "58": [
        "activityBar.activeBackground",
        "sideBar.background",
        "terminal.background",
        "panel.background",
        "sideBarSectionHeader.background",
    ],
    "57": ["editor.background", "editorGutter.background", "tab.inactiveBackground"],
    "56": ["tab.activeBackground", "tab.activeBorder", "tab.border", "tab.hoverBorder"],
}

THEME_BASE_COLOR_PROPERTIES = [
    "activityBar.activeBackground",
    "activityBar.activeBorder",
    "activityBar.activeFocusBorder",
    "activityBar.background",
    "activityBar.border",
    "activityBar.foreground",
    "activityBar.inactiveForeground",
    "activityBarBadge.background",
    "activityBarBadge.foreground",
    "badge.background",
    "badge.foreground",
    "banner.background",
    "banner.foreground",
    "breadcrumb.activeSelectionForeground",
    "breadcrumb.background",
    "breadcrumb.focusForeground",
    "breadcrumb.foreground",
    "breadcrumbPicker.background",
    "button.separator",
    "charts.foreground",
    "charts.lines",
    "chat.requestBorder",
    "chat.slashCommandBackground",
    "chat.slashCommandForeground",
    "checkbox.background",
    "checkbox.border",
    "checkbox.foreground",
    "checkbox.selectBackground",
    "checkbox.selectBorder",
    "commandCenter.activeBackground",
    "commandCenter.activeBorder",
    "commandCenter.activeForeground",
    "commandCenter.background",
    "commandCenter.border",
    "commandCenter.foreground",
    "commandCenter.inactiveBorder",
    "commandCenter.inactiveForeground",
    "commentsView.resolvedIcon",
    "contrastActiveBorder",
    "contrastBorder",
    "debugConsole.sourceForeground",
    "debugConsoleInputIcon.foreground",
    "debugTokenExpression.value",
    "debugToolBar.background",
    "debugToolBar.border",
    "debugView.exceptionLabelForeground",
    "debugView.stateLabelForeground",
    "descriptionForeground",
    "diffEditor.border",
    "diffEditor.diagonalFill",
    "diffEditor.insertedTextBorder",
    "diffEditor.removedTextBorder",
    "disabledForeground",
    "dropdown.background",
    "dropdown.border",
    "dropdown.foreground",
    "dropdown.listBackground",
    "editor.background",
    "editor.findRangeHighlightBorder",
    "editor.foldBackground",
    "editor.hoverHighlightBackground",
    "editor.inactiveSelectionBackground",
    "editor.inlineValuesForeground",
    "editor.lineHighlightBackground",
    "editor.lineHighlightBorder",
    "editor.rangeHighlightBackground",
    "editor.rangeHighlightBorder",
    "editor.selectionForeground",
    "editor.selectionHighlightBackground",
    "editor.selectionHighlightBorder",
    "editor.snippetFinalTabstopHighlightBackground",
    "editor.snippetFinalTabstopHighlightBorder",
    "editor.snippetTabstopHighlightBackground",
    "editor.snippetTabstopHighlightBorder",
    "editorBracketHighlight.foreground6",
    "editorCodeLens.foreground",
    "editorCommentsWidget.resolvedBorder",
    "editorCursor.background",
    "editorGhostText.background",
    "editorGhostText.border",
    "editorGhostText.foreground",
    "editorGroup.border",
    "editorGroup.dropBackground",
    "editorGroup.dropIntoPromptBackground",
    "editorGroup.dropIntoPromptBorder",
    "editorGroup.dropIntoPromptForeground",
    "editorGroup.emptyBackground",
    "editorGroup.focusedEmptyBorder",
    "editorGroupHeader.border",
    "editorGroupHeader.noTabsBackground",
    "editorGroupHeader.tabsBackground",
    "editorGroupHeader.tabsBorder",
    "editorGutter.background",
    "editorHint.border",
    "editorHoverWidget.background",
    "editorHoverWidget.border",
    "editorHoverWidget.foreground",
    "editorIndentGuide.activeBackground1",
    "editorIndentGuide.background1",
    "editorInfo.background",
    "editorInfo.border",
    "editorInlayHint.background",
    "editorInlayHint.parameterBackground",
    "editorInlayHint.typeBackground",
    "editorLineNumber.foreground",
    "editorLink.activeForeground",
    "editorMarkerNavigation.background",
    "editorOverviewRuler.background",
    "editorOverviewRuler.border",
    "editorOverviewRuler.commentForeground",
    "editorOverviewRuler.commentUnresolvedForeground",
    "editorOverviewRuler.wordHighlightTextForeground",
    "editorPane.background",
    "editorStickyScroll.background",
    "editorSuggestWidget.background",
    "editorSuggestWidget.border",
    "editorSuggestWidget.foreground",
    "editorSuggestWidget.selectedBackground",
    "editorSuggestWidget.selectedForeground",
    "editorSuggestWidget.selectedIconForeground",
    "editorSuggestWidgetStatus.foreground",
    "editorUnnecessaryCode.border",
    "editorWhitespace.foreground",
    "editorWidget.background",
    "editorWidget.border",
    "extensionBadge.remoteForeground",
    "extensionButton.background",
    "extensionButton.foreground",
    "extensionButton.prominentBackground",
    "extensionButton.prominentForeground",
    "extensionButton.separator",
    "focusBorder",
    "foreground",
    "icon.foreground",
    "inlineChat.background",
    "inlineChat.border",
    "inlineChat.regionHighlight",
    "inlineChat.shadow",
    "inlineChatInput.background",
    "inlineChatInput.border",
    "input.background",
    "input.border",
    "input.foreground",
    "inputOption.activeBackground",
    "inputOption.activeBorder",
    "inputOption.activeForeground",
    "inputOption.hoverBackground",
    "inputValidation.errorForeground",
    "inputValidation.infoForeground",
    "inputValidation.warningForeground",
    "interactive.inactiveCodeBorder",
    "keybindingLabel.background",
    "keybindingLabel.border",
    "keybindingLabel.bottomBorder",
    "keybindingLabel.foreground",
    "keybindingTable.headerBackground",
    "keybindingTable.rowsBackground",
    "list.activeSelectionBackground",
    "list.deemphasizedForeground",
    "list.dropBackground",
    "list.focusBackground",
    "list.focusOutline",
    "list.highlightForeground",
    "list.hoverBackground",
    "list.hoverForeground",
    "list.inactiveFocusBackground",
    "list.inactiveSelectionBackground",
    "list.invalidItemForeground",
    "listFilterWidget.background",
    "listFilterWidget.shadow",
    "menu.background",
    "menu.border",
    "menu.foreground",
    "menu.selectionBackground",
    "menu.selectionBorder",
    "menu.selectionForeground",
    "menu.separatorBackground",
    "menubar.selectionBackground",
    "menubar.selectionBorder",
    "menubar.selectionForeground",
    "merge.border",
    "minimap.background",
    "minimapSlider.background",
    "minimapSlider.hoverBackground",
    "notebook.cellBorderColor",
    "notebook.cellEditorBackground",
    "notebook.cellHoverBackground",
    "notebook.cellStatusBarItemHoverBackground",
    "notebook.editorBackground",
    "notebook.focusedCellBackground",
    "notebook.focusedCellBorder",
    "notebook.focusedEditorBorder",
    "notebook.inactiveFocusedCellBorder",
    "notebook.inactiveSelectedCellBorder",
    "notebook.outputContainerBackgroundColor",
    "notebook.outputContainerBorderColor",
    "notebook.selectedCellBackground",
    "notebook.selectedCellBorder",
    "notebook.symbolHighlightBackground",
    "notebookScrollbarSlider.background",
    "notebookScrollbarSlider.hoverBackground",
    "notebookStatusRunningIcon.foreground",
    "notificationCenter.border",
    "notificationCenterHeader.background",
    "notificationCenterHeader.foreground",
    "notificationToast.border",
    "notifications.background",
    "notifications.border",
    "panel.background",
    "panel.border",
    "panel.dropBorder",
    "panelInput.border",
    "panelSection.border",
    "panelSection.dropBackground",
    "panelSectionHeader.background",
    "panelSectionHeader.border",
    "panelSectionHeader.foreground",
    "panelTitle.activeBorder",
    "panelTitle.activeForeground",
    "panelTitle.inactiveForeground",
    "peekViewEditor.matchHighlightBorder",
    "peekViewResult.fileForeground",
    "peekViewResult.selectionForeground",
    "peekViewTitleDescription.foreground",
    "peekViewTitleLabel.foreground",
    "profileBadge.background",
    "profileBadge.foreground",
    "quickInput.background",
    "quickInput.foreground",
    "quickInputList.focusBackground",
    "quickInputList.focusForeground",
    "quickInputList.focusIconForeground",
    "quickInputTitle.background",
    "sash.hoverBorder",
    "scrollbar.shadow",
    "scrollbarSlider.activeBackground",
    "scrollbarSlider.background",
    "scrollbarSlider.hoverBackground",
    "search.resultsInfoForeground",
    "searchEditor.textInputBorder",
    "selection.background",
    "settings.checkboxBackground",
    "settings.checkboxBorder",
    "settings.dropdownBackground",
    "settings.dropdownBorder",
    "settings.dropdownListBorder",
    "settings.focusedRowBackground",
    "settings.focusedRowBorder",
    "settings.headerBorder",
    "settings.headerForeground",
    "settings.numberInputBackground",
    "settings.numberInputBorder",
    "settings.rowHoverBackground",
    "settings.sashBorder",
    "settings.textInputBackground",
    "settings.textInputBorder",
    "settings.textInputForeground",
    "sideBar.background",
    "sideBar.border",
    "sideBar.dropBackground",
    "sideBar.foreground",
    "sideBarSectionHeader.background",
    "sideBarSectionHeader.border",
    "sideBarSectionHeader.foreground",
    "sideBarTitle.foreground",
    "sideBySideEditor.horizontalBorder",
    "sideBySideEditor.verticalBorder",
    "statusBar.background",
    "statusBar.border",
    "statusBar.debuggingBorder",
    "statusBar.debuggingForeground",
    "statusBar.focusBorder",
    "statusBar.foreground",
    "statusBar.noFolderBorder",
    "statusBar.noFolderForeground",
    "statusBarItem.activeBackground",
    "statusBarItem.compactHoverBackground",
    "statusBarItem.errorForeground",
    "statusBarItem.errorHoverBackground",
    "statusBarItem.errorHoverForeground",
    "statusBarItem.focusBorder",
    "statusBarItem.hoverBackground",
    "statusBarItem.hoverForeground",
    "statusBarItem.offlineForeground",
    "statusBarItem.offlineHoverBackground",
    "statusBarItem.offlineHoverForeground",
    "statusBarItem.prominentForeground",
    "statusBarItem.prominentHoverForeground",
    "statusBarItem.remoteForeground",
    "statusBarItem.remoteHoverBackground",
    "statusBarItem.remoteHoverForeground",
    "statusBarItem.warningForeground",
    "statusBarItem.warningHoverForeground",
    "symbolIcon.arrayForeground",
    "symbolIcon.booleanForeground",
    "symbolIcon.colorForeground",
    "symbolIcon.constantForeground",
    "symbolIcon.fileForeground",
    "symbolIcon.folderForeground",
    "symbolIcon.keyForeground",
    "symbolIcon.keywordForeground",
    "symbolIcon.moduleForeground",
    "symbolIcon.namespaceForeground",
    "symbolIcon.nullForeground",
    "symbolIcon.numberForeground",
    "symbolIcon.objectForeground",
    "symbolIcon.operatorForeground",
    "symbolIcon.packageForeground",
    "symbolIcon.propertyForeground",
    "symbolIcon.referenceForeground",
    "symbolIcon.snippetForeground",
    "symbolIcon.stringForeground",
    "symbolIcon.structForeground",
    "symbolIcon.textForeground",
    "symbolIcon.typeParameterForeground",
    "symbolIcon.unitForeground",
    "tab.activeBackground",
    "tab.activeBorder",
    "tab.activeBorderTop",
    "tab.activeForeground",
    "tab.border",
    "tab.hoverBackground",
    "tab.hoverBorder",
    "tab.inactiveBackground",
    "tab.inactiveForeground",
    "tab.inactiveModifiedBorder",
    "tab.lastPinnedBorder",
    "tab.unfocusedActiveBackground",
    "tab.unfocusedActiveBorder",
    "tab.unfocusedActiveBorderTop",
    "tab.unfocusedActiveForeground",
    "tab.unfocusedHoverBackground",
    "tab.unfocusedHoverBorder",
    "tab.unfocusedHoverForeground",
    "tab.unfocusedInactiveBackground",
    "tab.unfocusedInactiveForeground",
    "tab.unfocusedInactiveModifiedBorder",
    "terminal.background",
    "terminal.border",
    "terminal.dropBackground",
    "terminal.findMatchBorder",
    "terminal.findMatchHighlightBorder",
    "terminal.foreground",
    "terminal.hoverHighlightBackground",
    "terminal.inactiveSelectionBackground",
    "terminal.selectionBackground",
    "terminal.selectionForeground",
    "terminal.tab.activeBorder",
    "terminalCommandDecoration.defaultBackground",
    "testing.message.info.lineBackground",
    "textBlockQuote.border",
    "textCodeBlock.background",
    "textSeparator.foreground",
    "titleBar.activeBackground",
    "titleBar.activeForeground",
    "titleBar.border",
    "titleBar.inactiveBackground",
    "titleBar.inactiveForeground",
    "toolbar.activeBackground",
    "toolbar.hoverBackground",
    "toolbar.hoverOutline",
    "tree.inactiveIndentGuidesStroke",
    "tree.indentGuidesStroke",
    "tree.tableColumnsBorder",
    "tree.tableOddRowsBackground",
    "walkthrough.stepTitle.foreground",
    "welcomePage.background",
    "welcomePage.progress.background",
    "welcomePage.progress.foreground",
    "welcomePage.tileBackground",
    "welcomePage.tileBorder",
    "widget.border",
    "widget.shadow",
    "window.inactiveBorder",
]


def define_colors_for_background_properties(color_properties):
    colors = {}
    for color_property in color_properties:
        colors[color_property] = _get_color(color_property)
    return colors


def define_colors():
    template_json_file = f"{os.getcwd()}/themes/viiv-color-theme.template.json"
    template_data = json.load(open(template_json_file))
    all_color_properties = get_color_properties(template_json_file)
    print(len(all_color_properties))
    theme_base_color = "11"
    colors = {}
    color_placeholders_groups = {}
    color_properties_group = group_color_properties(all_color_properties)
    for group_name, color_properties in color_properties_group.items():
        color_range = _create_color_range(group_name)
        color_placeholders = _create_color_placeholders(color_range)
        color_placeholders = random.sample(
            color_placeholders, min(len(color_placeholders), len(all_color_properties))
        )
        color_placeholders_groups[group_name] = color_placeholders
        for i, color_property in enumerate(color_properties):
            if (color_range == DEFAULT_COLOR_RANGE) and (color_property in colors):
                continue
            #if (color_range == DEFAULT_COLOR_RANGE):
            #    print(f"To use default color range {color_property}")
            if color_property in HIDDEN_PROPERTIES:
                color_placeholder = "#00000000"
            else:
                color_placeholder = color_placeholders[i % len(color_placeholders)]
                if color_property in THEME_BASE_COLOR_PROPERTIES:
                    color_placeholder = _replace_base_color(
                        color_placeholder, theme_base_color
                    )
                for k, v in LIGHT_LEVEL_MAP.items():
                    if color_property in v:
                        color_placeholder = _replace_light_level(color_placeholder, k)

            colors[color_property] = color_placeholder

    template_data["colors"] = dict(sorted(colors.items(), key=lambda x: x[0]))
    json.dump(
        color_properties_group,
        open(os.getenv("USERPROFILE") + r"\Downloads\a.json", "w"),
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
            for k in range(alpha_range[0], alpha_range[1]):
                if k < 10:
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

    # color placeholder value format "C_[0-9]{2}_[0-9]{2}",
    color_placeholders = _create_color_placeholders(
        base_colors_range, light_level_range
    )

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
                r"C_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}[a-zA-Z0-9]{2}"
            )
            _foreground = re.sub(_placeholder_regex, color_placeholder, _old_foreground)

            for _scope_prefix in ["comment", "docstring", "punctuation", "javadoc"]:
                if scope.find(_scope_prefix) != -1:
                    # do not set alpha
                    if re.match(_placeholder_with_alpha_regex, _old_foreground):
                        _foreground = re.sub(
                            _placeholder_with_alpha_regex,
                            color_placeholder,
                            _old_foreground,
                        )
                    # set base color as dark color
                    _foreground = re.sub(r"C_[a-zA-Z0-9]{2}", "C_11", _foreground)
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


if __name__ == "__main__":
    opts, _ = getopt.getopt(
        sys.argv[1:],
        "ct",
        [
            "--colors",
            "--token_colors",
        ],
    )
    for option, value in opts:
        if option in ("-c", "--colors"):
            define_colors()
        elif option in ("-t", "--token_colors"):
            define_token_colors(light_level_range=[25, 35], base_colors_range=[1, 10])
