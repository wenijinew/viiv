# ViiV

<div></div>

Might be the most attractive VsCode theme.

![preview](preview.png)

# General Convensions

|Prefix|Suffix|Theme Property Category|
|------|------|-----------------------|
|11|29|Activity bar background|
|11|29|Button background|
|11|28|Side bar background|
|11|28|Panel bar background|
|11|28|Terminal bar background|
|11|28|Minimap bar background|
|11|27|Editor bar background|
|11|25|Hover background|
|11|29|default bar background|
|11|15|default bar foreground|
|11|15|Tab activie border top|
|11|15|Activity bar active border|


# Configuration

## Matching rule:

When matching a color property with color property group, the following rules are applied:

* EXACT = 1
* ENDSWITH = 2
* STARTSWITH = 3
* FUZZY = 4

Therefore, to customize the specific color property, use property full value as group value in config.json file.
```
{
    "colors": {
        "editor.foreground": "#a4ac7f"
    }
}```

## Areas

The color properties are divided into several areas: default, background, foreground, border, token

The 'default' area has highest priority and it can override other areas configurations when the 'group' value is the same as the color property value - the specific color property could be customized.

The areas background, foreground, and border are mainly used for general purpose to define general color code for color properties falling in those areas.

In each area, we can define color code for color properties 'groups'. Each group could be the full name of the color property, prefix or suffix of the color property, regular expression which is used to match all the relevant color properties.

## Default

The default purpose for 'default' area is to change the ALPHA value of the color for different status like active, inactive, highlight as such.

It might need to reset BASIC, LIGHT, ALPHA ranges for some color perperties. For example, if "editor" is set in 'background' area, then all color properties color of "editor.*Background" will follow the colors defined in 'background' area for 'editor'. So, when it need to set color for "editor.wordHighlightBackground", the basic color will still the same with the editor basic color which is dark color. If we want to use other color, then we need to be allowed to change the basic color. 

"default" area in config.json has highest priority and can override any previous configuration.

Note:
If any property need customization, it's better to do it in 'default' area, especially when it contains 'status' keywords like 'active', 'focus' as such.

## Static color

To use static color for property, use the below format:

```
    {
        "groups": [
            ".*foreground.*"
        ],
        "color": {
            "hex": "#b7b7ff",
            "alpha_range": [
                "0xdf",
                "0xe1"
            ]
        }
    }
```

## Dynamic color

To use dynamic color, use the below format:

```
{
    "groups": [
        ".*editorSuggestWidget.*"
    ],
    "color": {
        "basic_range": [
            1,
            11
        ],
        "light_range": [
            10,
            35
        ],
        "alpha_range": [
            "0x95",
            "0xa5"
        ]
    }
}
```

# Usage

To generate new theme, run the command under the directory of the project:

```
python utils.py -t && pwsh.exe -nop -File viiv.ps1
```


