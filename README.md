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
|11|29|Status bar background|
|11|15|Status bar foreground|
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

## Status
